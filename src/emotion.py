"""
Emotion Detection Module (Bonus Feature)
Detects specific emotions beyond positive/negative sentiment
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EmotionDetector:
    """Detects specific emotions in text"""
    
    def __init__(self):
        """Initialize emotion detector"""
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'delighted', 'excited', 'thrilled', 'ecstatic', 
                   'wonderful', 'amazing', 'fantastic', 'great', 'love', 'adore'],
            'sadness': ['sad', 'depressed', 'unhappy', 'miserable', 'disappointed', 
                       'upset', 'down', 'sorrow', 'grief', 'melancholy'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'annoyed', 'irritated', 
                     'frustrated', 'outraged', 'livid', 'hate'],
            'fear': ['afraid', 'scared', 'fearful', 'worried', 'anxious', 'nervous', 
                    'terrified', 'panic', 'dread', 'concerned'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'wow', 
                        'unexpected', 'incredible', 'unbelievable'],
            'disgust': ['disgusted', 'revolted', 'sickened', 'repulsed', 'nauseated']
        }
        logger.info("EmotionDetector initialized")
    
    def detect_emotions(self, text: str, sentiment_score: Optional[float] = None) -> Dict[str, any]:
        """
        Detect emotions in text
        
        Args:
            text: Input text
            sentiment_score: Optional sentiment score for context
            
        Returns:
            Dictionary with detected emotions and confidence scores
        """
        if not text or not text.strip():
            return {
                'primary_emotion': 'neutral',
                'emotions': {},
                'confidence': 0.0
            }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # Count emotion keyword matches
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score / len(keywords)  # Normalize
        
        # Use sentiment score to refine emotion detection
        if sentiment_score is not None:
            if sentiment_score > 0.3 and 'joy' in emotion_scores:
                emotion_scores['joy'] *= 1.5
            elif sentiment_score < -0.3:
                if 'anger' in emotion_scores:
                    emotion_scores['anger'] *= 1.5
                elif 'sadness' in emotion_scores:
                    emotion_scores['sadness'] *= 1.5
        
        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            confidence = emotion_scores[primary_emotion]
        else:
            primary_emotion = 'neutral'
            confidence = 0.0
        
        return {
            'primary_emotion': primary_emotion,
            'emotions': emotion_scores,
            'confidence': min(confidence, 1.0)
        }
    
    def get_emotion_emoji(self, emotion: str) -> str:
        """Get emoji for emotion"""
        emoji_map = {
            'joy': '😊',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'surprise': '😲',
            'disgust': '🤢',
            'neutral': '😐'
        }
        return emoji_map.get(emotion, '😐')
    
    def analyze_conversation_emotions(self, messages: List[Dict]) -> Dict[str, any]:
        """
        Analyze emotion distribution across conversation
        
        Args:
            messages: List of message dictionaries with sentiment data
            
        Returns:
            Dictionary with emotion analysis
        """
        emotion_counts = {}
        emotion_scores = {emotion: [] for emotion in self.emotion_keywords.keys()}
        emotion_scores['neutral'] = []
        
        for msg in messages:
            text = msg.get('text', '')
            sentiment = msg.get('sentiment', {})
            sentiment_score = sentiment.get('score', 0.0)
            
            emotion_result = self.detect_emotions(text, sentiment_score)
            primary = emotion_result['primary_emotion']
            
            emotion_counts[primary] = emotion_counts.get(primary, 0) + 1
            emotion_scores[primary].append(emotion_result['confidence'])
        
        # Calculate average confidence per emotion
        avg_confidence = {}
        for emotion, scores in emotion_scores.items():
            if scores:
                avg_confidence[emotion] = sum(scores) / len(scores)
        
        # Find dominant emotion
        if emotion_counts:
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        else:
            dominant_emotion = 'neutral'
        
        return {
            'emotion_distribution': emotion_counts,
            'dominant_emotion': dominant_emotion,
            'average_confidence': avg_confidence,
            'total_emotions_detected': len([e for e in emotion_counts.values() if e > 0])
        }

