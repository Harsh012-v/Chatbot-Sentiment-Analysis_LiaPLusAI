"""
Vercel Serverless Function Handler for Chatbot Web Application
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
from datetime import datetime
import uuid
import json

# Add parent directory to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.sentiment import SentimentEngine
from src.conversation import Conversation
from src.chatbot import Chatbot
from src.analyzer import TrendAnalyzer
from src.emotion import EmotionDetector
from src.utils import setup_logging

# Initialize Flask app
app = Flask(__name__, 
            template_folder=str(project_root / "templates"),
            static_folder=str(project_root / "static"))
app.secret_key = os.environ.get('SECRET_KEY', 'chatbot-sentiment-analysis-secret-key-2024-vercel')
CORS(app)

# Initialize components (singleton pattern for serverless)
sentiment_engine = None
chatbot = None
trend_analyzer = None
emotion_detector = None
conversations = {}

def get_components():
    """Lazy initialization of components"""
    global sentiment_engine, chatbot, trend_analyzer, emotion_detector
    
    if sentiment_engine is None:
        sentiment_engine = SentimentEngine(analyzer_type="vader")
        chatbot = Chatbot(name="Assistant", personality="helpful")
        trend_analyzer = TrendAnalyzer()
        emotion_detector = EmotionDetector()
        setup_logging(log_level="INFO", log_file=None)
    
    return sentiment_engine, chatbot, trend_analyzer, emotion_detector


@app.route('/', methods=['GET'])
def index():
    """Render main chat interface"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return bot response with sentiment"""
    try:
        sentiment_engine, chatbot, trend_analyzer, emotion_detector = get_components()
        
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id') or str(uuid.uuid4())
        
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
                'analysis': get_conversation_analysis(conversation, sentiment_engine, trend_analyzer, emotion_detector),
                'session_id': session_id
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
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
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
        sentiment_engine, chatbot, trend_analyzer, emotion_detector = get_components()
        
        data = request.json
        session_id = data.get('session_id')
        
        if session_id and session_id in conversations:
            conversation = conversations[session_id]
            conversation.end_conversation()
            
            analysis = get_conversation_analysis(conversation, sentiment_engine, trend_analyzer, emotion_detector)
            
            # Note: File saving disabled on Vercel (read-only filesystem)
            # In production, use a database or external storage
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'session_id': session_id
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
        data = request.json
        session_id = data.get('session_id')
        
        if session_id and session_id in conversations:
            # Remove old conversation
            del conversations[session_id]
        
        # Create new session ID
        new_session_id = str(uuid.uuid4())
        conversations[new_session_id] = Conversation(conversation_id=f"web_{new_session_id[:8]}")
        
        return jsonify({
            'success': True,
            'message': 'Conversation reset',
            'session_id': new_session_id
        })
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


def get_conversation_analysis(conversation, sentiment_engine, trend_analyzer, emotion_detector):
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


# Vercel serverless function handler
# Vercel will automatically detect the Flask app
# No need for explicit handler function

