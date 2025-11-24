"""
Sentiment Analysis Engine with Strategy Pattern
Supports multiple sentiment analysis libraries: VADER, TextBlob, and Transformers
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer(ABC):
    """Abstract base class for sentiment analyzers (Strategy Pattern)"""
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment scores and label
        """
        pass
    
    @abstractmethod
    def get_label(self, score: float) -> str:
        """
        Convert sentiment score to label
        
        Args:
            score: Sentiment score
            
        Returns:
            Sentiment label (Positive/Negative/Neutral)
        """
        pass


class VADERAnalyzer(SentimentAnalyzer):
    """VADER (Valence Aware Dictionary and sEntiment Reasoner) analyzer"""
    
    def __init__(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.analyzer = SentimentIntensityAnalyzer()
            logger.info("VADER analyzer initialized successfully")
        except ImportError:
            logger.error("vaderSentiment not installed. Install with: pip install vaderSentiment")
            raise
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        if not text or not text.strip():
            return {
                'compound': 0.0,
                'positive': 0.0,
                'neutral': 0.0,
                'negative': 0.0,
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0
            }
        
        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']
        
        return {
            'compound': compound,
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'score': compound,
            'label': self.get_label(compound),
            'confidence': abs(compound)
        }
    
    def get_label(self, score: float) -> str:
        """Convert VADER compound score to label"""
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'


class TextBlobAnalyzer(SentimentAnalyzer):
    """TextBlob sentiment analyzer"""
    
    def __init__(self):
        try:
            from textblob import TextBlob
            self.TextBlob = TextBlob
            logger.info("TextBlob analyzer initialized successfully")
        except ImportError:
            logger.error("textblob not installed. Install with: pip install textblob")
            raise
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        if not text or not text.strip():
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0
            }
        
        blob = self.TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'score': polarity,
            'label': self.get_label(polarity),
            'confidence': abs(polarity)
        }
    
    def get_label(self, score: float) -> str:
        """Convert TextBlob polarity score to label"""
        if score > 0.1:
            return 'Positive'
        elif score < -0.1:
            return 'Negative'
        else:
            return 'Neutral'


class TransformersAnalyzer(SentimentAnalyzer):
    """Hugging Face Transformers-based sentiment analyzer"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        try:
            from transformers import pipeline
            self.model_name = model_name
            self.analyzer = pipeline("sentiment-analysis", model=model_name)
            logger.info(f"Transformers analyzer initialized with model: {model_name}")
        except ImportError:
            logger.error("transformers not installed. Install with: pip install transformers torch")
            raise
        except Exception as e:
            logger.warning(f"Failed to load transformers model: {e}. Falling back to VADER.")
            raise
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using Transformers"""
        if not text or not text.strip():
            return {
                'label': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0
            }
        
        try:
            result = self.analyzer(text)[0]
            label = result['label']
            score = result['score']
            
            # Convert POSITIVE/NEGATIVE to standard format
            if label == 'POSITIVE':
                normalized_score = score
                label_str = 'Positive'
            elif label == 'NEGATIVE':
                normalized_score = -score
                label_str = 'Negative'
            else:
                normalized_score = 0.0
                label_str = 'Neutral'
            
            return {
                'label': label_str,
                'score': normalized_score,
                'confidence': score,
                'raw_label': label,
                'raw_score': score
            }
        except Exception as e:
            logger.error(f"Error in transformers analysis: {e}")
            return {
                'label': 'Neutral',
                'score': 0.0,
                'confidence': 0.0
            }
    
    def get_label(self, score: float) -> str:
        """Convert transformers score to label"""
        if score > 0.5:
            return 'Positive'
        elif score < -0.5:
            return 'Negative'
        else:
            return 'Neutral'


class SentimentEngine:
    """Main sentiment analysis engine with strategy pattern"""
    
    def __init__(self, analyzer_type: str = "vader"):
        """
        Initialize sentiment engine
        
        Args:
            analyzer_type: Type of analyzer ('vader', 'textblob', 'transformers')
        """
        self.analyzer_type = analyzer_type.lower()
        self.analyzer = self._create_analyzer(analyzer_type)
        
        # Comparative patterns that indicate negative sentiment about current state
        # These patterns detect when something past/before is described as better than current
        self.negative_comparative_patterns = [
            # "better than this/that/current/now/this one"
            r'\b(better|good|great|excellent|superior|improved)\s+than\s+(this|that|current|now|today|this\s+one|that\s+one)',
            # "better than it/they is/are now"
            r'\b(better|good|great|excellent|superior|improved)\s+than\s+(it|they|we|you)\s+(is|are|was|were|now)',
            # "last/previous experience/time was better than"
            r'\b(last|previous|earlier|before)\s+(experience|time|one|service|product)\s+(was|were)\s+(better|good|great|excellent)\s+than',
            # "previous/last time/experience was better" (implies comparison)
            r'\b(previous|last|earlier|before)\s+(time|experience)\s+was\s+better',
            # "not as good as before/previous/last"
            r'\b(not|isn\'t|aren\'t|wasn\'t|weren\'t)\s+(as|so)\s+(good|great|excellent|nice|well)\s+as\s+(before|previously|earlier|last|it|they)',
            # "this/that/it is not as good"
            r'\b(this|that|it|they)\s+(is|are|was|were)\s+not\s+(as|so)\s+(good|great|excellent|nice|well)',
            # "worse than before"
            r'\b(worse|worsened|declined|deteriorated)\s+than\s+(before|previously|earlier|last)',
            # "used to be better"
            r'\b(used\s+to\s+be)\s+(better|good|great)',
            # "didn't/don't find... interesting/good/great" (more flexible pattern)
            r'\b(didn\'t|don\'t|doesn\'t|didnt|dont|doesnt|did\s+not|do\s+not|does\s+not)\s+find.*?(interesting|good|great|excellent|nice|enjoyable|engaging)',
            # "not interesting/not good/not great"
            r'\b(not|isn\'t|aren\'t|wasn\'t|weren\'t)\s+(interesting|good|great|excellent|nice|enjoyable|engaging|worthwhile)',
            # Negative phrases like "rubbish", "nonsense", "stupid", etc.
            r'\b(rubbish|nonsense|stupid|idiotic|ridiculous|terrible|awful|horrible|disgusting|pathetic)',
            # "don't talk rubbish/nonsense"
            r'\b(don\'t|do\s+not)\s+talk\s+(rubbish|nonsense|garbage|trash|crap)',
        ]
        
        # Positive comparative patterns (less common but possible)
        self.positive_comparative_patterns = [
            r'\b(better|good|great|excellent|improved)\s+than\s+(before|previously|earlier|last)',
            r'\b(improved|improving|better)\s+(than|from)\s+(before|previously|earlier|last)',
        ]
        
        self.negative_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.negative_comparative_patterns]
        self.positive_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.positive_comparative_patterns]
        
        logger.info(f"SentimentEngine initialized with {analyzer_type} analyzer")
    
    def _create_analyzer(self, analyzer_type: str) -> SentimentAnalyzer:
        """Factory method to create appropriate analyzer"""
        analyzer_type = analyzer_type.lower()
        
        if analyzer_type == "vader":
            return VADERAnalyzer()
        elif analyzer_type == "textblob":
            return TextBlobAnalyzer()
        elif analyzer_type == "transformers":
            return TransformersAnalyzer()
        else:
            logger.warning(f"Unknown analyzer type: {analyzer_type}. Defaulting to VADER.")
            return VADERAnalyzer()
    
    def _detect_comparative_sentiment(self, text: str, base_result: Dict[str, float]) -> Dict[str, float]:
        """
        Detect and adjust sentiment for comparative statements and negative phrases
        
        Args:
            text: Input text
            base_result: Base sentiment analysis result
            
        Returns:
            Adjusted sentiment result
        """
        text_lower = text.lower()
        
        # Check for negative comparative patterns (e.g., "better than this", "was better")
        for pattern in self.negative_patterns:
            if pattern.search(text):
                # This is a negative statement about current state
                # Adjust score to be more negative
                original_score = base_result.get('score', 0.0)
                
                # Special handling for very negative phrases like "rubbish", "don't talk rubbish"
                if any(phrase in text_lower for phrase in ['rubbish', 'nonsense', 'garbage', 'trash', 'crap', 'stupid', 'idiotic']):
                    # Very strong negative adjustment
                    adjusted_score = -0.7
                elif any(phrase in text_lower for phrase in ["didn't find", "don't find", "not find", "didnt find", "dont find"]):
                    # "didn't find interesting" type statements - these are negative
                    if any(word in text_lower for word in ['interesting', 'good', 'great', 'enjoyable', 'engaging']):
                        adjusted_score = -0.6
                    else:
                        adjusted_score = -0.4
                elif original_score > 0:
                    # Strong negative adjustment for comparative statements
                    adjusted_score = -abs(original_score) - 0.4
                else:
                    # Make it more negative
                    adjusted_score = original_score - 0.4
                
                # Clamp to valid range
                adjusted_score = max(-1.0, min(1.0, adjusted_score))
                
                base_result['score'] = adjusted_score
                base_result['compound'] = adjusted_score if 'compound' in base_result else adjusted_score
                base_result['label'] = self.analyzer.get_label(adjusted_score)
                base_result['confidence'] = abs(adjusted_score)
                base_result['adjusted_for_comparison'] = True
                
                logger.debug(f"Adjusted sentiment for negative statement: {text[:50]}... (score: {original_score:.2f} -> {adjusted_score:.2f})")
                return base_result
        
        # Check for positive comparative patterns (less common)
        for pattern in self.positive_patterns:
            if pattern.search(text):
                # This is a positive statement about improvement
                original_score = base_result.get('score', 0.0)
                if original_score < 0:
                    # If negative but we detected positive comparison, adjust upward
                    adjusted_score = abs(original_score) + 0.2
                else:
                    adjusted_score = original_score + 0.2
                
                adjusted_score = max(-1.0, min(1.0, adjusted_score))
                base_result['score'] = adjusted_score
                base_result['compound'] = adjusted_score if 'compound' in base_result else adjusted_score
                base_result['label'] = self.analyzer.get_label(adjusted_score)
                base_result['confidence'] = abs(adjusted_score)
                base_result['adjusted_for_comparison'] = True
                
                logger.debug(f"Adjusted sentiment for positive comparison: {text[:50]}... (score: {original_score:.2f} -> {adjusted_score:.2f})")
                return base_result
        
        return base_result
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Get base sentiment analysis
            result = self.analyzer.analyze(text)
            
            # Apply comparative statement detection and adjustment
            result = self._detect_comparative_sentiment(text, result)
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0
            }
    
    def analyze_conversation(self, messages: list) -> Dict[str, any]:
        """
        Analyze overall sentiment of a conversation
        
        Args:
            messages: List of message dictionaries with 'text' key
            
        Returns:
            Dictionary with overall sentiment analysis
        """
        if not messages:
            return {
                'overall_sentiment': 'Neutral',
                'average_score': 0.0,
                'total_messages': 0,
                'reasoning': 'No messages to analyze'
            }
        
        scores = []
        labels = []
        
        for msg in messages:
            if isinstance(msg, dict) and 'text' in msg:
                result = self.analyze_text(msg['text'])
                scores.append(result.get('score', 0.0))
                labels.append(result.get('label', 'Neutral'))
            elif isinstance(msg, str):
                result = self.analyze_text(msg)
                scores.append(result.get('score', 0.0))
                labels.append(result.get('label', 'Neutral'))
        
        if not scores:
            return {
                'overall_sentiment': 'Neutral',
                'average_score': 0.0,
                'total_messages': 0,
                'reasoning': 'No valid messages to analyze'
            }
        
        avg_score = sum(scores) / len(scores)
        
        # Count label distribution
        label_counts = {
            'Positive': labels.count('Positive'),
            'Negative': labels.count('Negative'),
            'Neutral': labels.count('Neutral')
        }
        
        # Improved overall sentiment determination
        # Consider label distribution more heavily than just average score
        total = len(labels)
        positive_count = label_counts['Positive']
        negative_count = label_counts['Negative']
        neutral_count = label_counts['Neutral']
        
        # Determine overall sentiment based on label distribution and scores
        # Priority: If clear majority of one label, use that
        # Otherwise, consider average score and presence of strong sentiments
        
        # Check for strong negative indicators
        strong_negative_count = sum(1 for score in scores if score < -0.3)
        strong_positive_count = sum(1 for score in scores if score > 0.3)
        
        # Decision logic:
        # 1. If negative messages > positive messages by 2 or more, it's negative
        # 2. If positive messages > negative messages by 2 or more, it's positive
        # 3. If strong negative indicators exist and negative >= positive, it's negative
        # 4. Otherwise, use average score
        
        if negative_count > positive_count and (negative_count - positive_count >= 1 or strong_negative_count > 0):
            overall_label = 'Negative'
        elif positive_count > negative_count and (positive_count - negative_count >= 2):
            overall_label = 'Positive'
        elif strong_negative_count > 0 and negative_count >= positive_count:
            overall_label = 'Negative'
        elif strong_positive_count > 0 and positive_count > negative_count:
            overall_label = 'Positive'
        elif avg_score < -0.1:
            overall_label = 'Negative'
        elif avg_score > 0.1:
            overall_label = 'Positive'
        else:
            overall_label = 'Neutral'
        
        # Generate reasoning
        reasoning = self._generate_reasoning(avg_score, label_counts, total, overall_label)
        
        return {
            'overall_sentiment': overall_label,
            'average_score': avg_score,
            'total_messages': total,
            'label_distribution': label_counts,
            'reasoning': reasoning,
            'scores': scores,
            'labels': labels
        }
    
    def _generate_reasoning(self, avg_score: float, label_counts: Dict[str, int], total: int, overall_label: str) -> str:
        """Generate human-readable reasoning for sentiment"""
        positive_count = label_counts['Positive']
        negative_count = label_counts['Negative']
        neutral_count = label_counts['Neutral']
        
        if overall_label == 'Negative':
            if negative_count > positive_count:
                return f"Generally negative conversation with {negative_count}/{total} negative messages. User expressed dissatisfaction or concerns."
            elif negative_count == positive_count:
                return f"Mixed conversation with negative tone. Equal negative and positive messages ({negative_count} each), but overall sentiment is negative."
            else:
                return f"Conversation with negative overall tone despite {positive_count} positive messages. Strong negative statements influenced the assessment."
        elif overall_label == 'Positive':
            if positive_count > negative_count:
                return f"Generally positive conversation with {positive_count}/{total} positive messages. User expressed satisfaction or positive feedback."
            elif positive_count == negative_count:
                return f"Mixed conversation with positive tone. Equal positive and negative messages ({positive_count} each), but overall sentiment is positive."
            else:
                return f"Conversation with positive overall tone. Average sentiment score of {avg_score:.3f} indicates positive engagement."
        else:
            return f"Neutral conversation with balanced sentiment. Distribution: {positive_count} positive, {negative_count} negative, {neutral_count} neutral messages."

