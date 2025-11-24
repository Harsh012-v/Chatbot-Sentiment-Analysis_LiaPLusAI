"""
Flask Web Application for Chatbot with Sentiment Analysis
Modern web interface with real-time sentiment analysis
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sys
from pathlib import Path
from datetime import datetime
import uuid
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.sentiment import SentimentEngine
from src.conversation import Conversation
from src.chatbot import Chatbot
from src.analyzer import TrendAnalyzer
from src.emotion import EmotionDetector
from src.utils import setup_logging

app = Flask(__name__)
app.secret_key = 'chatbot-sentiment-analysis-secret-key-2024'
CORS(app)

# Initialize components
sentiment_engine = SentimentEngine(analyzer_type="vader")
chatbot = Chatbot(name="Assistant", personality="helpful")
trend_analyzer = TrendAnalyzer()
emotion_detector = EmotionDetector()

# Store conversations in memory (in production, use database)
conversations = {}

# Setup logging
setup_logging(log_level="INFO", log_file=None)


@app.route('/')
def index():
    """Render main chat interface"""
    # Generate unique session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    
    # Initialize conversation for this session
    if session_id not in conversations:
        conversations[session_id] = Conversation(conversation_id=f"web_{session_id[:8]}")
    
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return bot response with sentiment"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        # Get or create conversation
        if session_id not in conversations:
            conversations[session_id] = Conversation(conversation_id=f"web_{session_id[:8]}")
        
        conversation = conversations[session_id]
        
        # Check for exit commands
        if chatbot._is_exit_command(user_message):
            # End conversation and return final analysis
            conversation.end_conversation()
            return jsonify({
                'type': 'end_conversation',
                'message': chatbot._get_exit_response(),
                'analysis': get_conversation_analysis(conversation)
            })
        
        # Analyze sentiment
        sentiment = sentiment_engine.analyze_text(user_message)
        
        # Add emotion detection
        emotion_result = emotion_detector.detect_emotions(
            user_message, sentiment_score=sentiment.get('score', 0.0)
        )
        sentiment['emotion'] = emotion_result
        
        # Add user message to conversation
        conversation.add_message(user_message, 'user', sentiment)
        
        # Generate bot response
        bot_response = chatbot.generate_response(
            user_message,
            sentiment,
            conversation.get_all_messages()
        )
        
        # Add bot message to conversation
        conversation.add_message(bot_response, 'bot')
        
        # Prepare response
        response_data = {
            'type': 'message',
            'user_message': user_message,
            'bot_message': bot_response,
            'sentiment': {
                'label': sentiment.get('label', 'Neutral'),
                'score': sentiment.get('score', 0.0),
                'confidence': sentiment.get('confidence', 0.0),
                'emotion': emotion_result.get('primary_emotion', 'neutral'),
                'emotion_emoji': emotion_detector.get_emotion_emoji(emotion_result.get('primary_emotion', 'neutral'))
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/end_conversation', methods=['POST'])
def end_conversation():
    """End conversation and return final analysis"""
    try:
        session_id = session.get('session_id')
        
        if session_id and session_id in conversations:
            conversation = conversations[session_id]
            conversation.end_conversation()
            
            analysis = get_conversation_analysis(conversation)
            
            # Save conversation
            filepath = conversation.save_to_json()
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'saved_to': filepath
            })
        else:
            return jsonify({
                'error': 'No active conversation'
            }), 400
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation for current session"""
    try:
        session_id = session.get('session_id')
        
        if session_id and session_id in conversations:
            # Save old conversation before resetting
            old_conv = conversations[session_id]
            if old_conv.get_message_count() > 0:
                old_conv.end_conversation()
                old_conv.save_to_json()
            del conversations[session_id]
        
        # Create new conversation
        new_session_id = str(uuid.uuid4())
        session['session_id'] = new_session_id
        conversations[new_session_id] = Conversation(conversation_id=f"web_{new_session_id[:8]}")
        
        return jsonify({
            'success': True,
            'message': 'Conversation reset'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


def get_conversation_analysis(conversation):
    """Get comprehensive conversation analysis"""
    user_messages = conversation.get_user_messages()
    
    if not user_messages:
        return {
            'overall_sentiment': 'Neutral',
            'total_messages': 0,
            'duration': 0
        }
    
    # Overall sentiment
    overall_sentiment = sentiment_engine.analyze_conversation(
        [msg.to_dict() for msg in user_messages]
    )
    
    # Trend analysis
    trend_analysis = None
    if len(user_messages) > 1:
        sentiment_scores = []
        sentiment_labels = []
        
        for msg in user_messages:
            if msg.sentiment:
                sentiment_scores.append(msg.sentiment.get('score', 0.0))
                sentiment_labels.append(msg.sentiment.get('label', 'Neutral'))
        
        if sentiment_scores:
            trend_analysis = trend_analyzer.analyze_trend(sentiment_scores, sentiment_labels)
            insights = trend_analyzer.summarize_insights(trend_analysis, overall_sentiment)
            trend_analysis['insights'] = insights
    
    # Emotion analysis
    emotion_analysis = None
    emotion_data = [
        {
            'text': msg.text,
            'sentiment': msg.sentiment
        }
        for msg in user_messages if msg.sentiment
    ]
    
    if emotion_data:
        emotion_analysis = emotion_detector.analyze_conversation_emotions(emotion_data)
    
    return {
        'overall_sentiment': overall_sentiment.get('overall_sentiment', 'Neutral'),
        'average_score': overall_sentiment.get('average_score', 0.0),
        'total_messages': conversation.get_user_message_count(),
        'duration': conversation.get_duration(),
        'reasoning': overall_sentiment.get('reasoning', ''),
        'label_distribution': overall_sentiment.get('label_distribution', {}),
        'trend_analysis': trend_analysis,
        'emotion_analysis': emotion_analysis,
        'sentiment_scores': overall_sentiment.get('scores', []),
        'sentiment_labels': overall_sentiment.get('labels', [])
    }


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Chatbot Web Application")
    print("=" * 60)
    print("📱 Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

