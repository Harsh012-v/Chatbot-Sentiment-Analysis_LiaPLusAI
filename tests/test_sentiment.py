"""
Unit tests for sentiment analysis module
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.sentiment import SentimentEngine, VADERAnalyzer


class TestVADERAnalyzer:
    """Test VADER sentiment analyzer"""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection"""
        analyzer = VADERAnalyzer()
        result = analyzer.analyze("I love this product! It's amazing!")
        
        assert result['label'] == 'Positive'
        assert result['score'] > 0
        assert 'confidence' in result
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection"""
        analyzer = VADERAnalyzer()
        result = analyzer.analyze("This is terrible. I hate it.")
        
        assert result['label'] == 'Negative'
        assert result['score'] < 0
        assert 'confidence' in result
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        analyzer = VADERAnalyzer()
        result = analyzer.analyze("The weather is okay today.")
        
        assert result['label'] == 'Neutral'
        assert abs(result['score']) < 0.05
    
    def test_empty_text(self):
        """Test handling of empty text"""
        analyzer = VADERAnalyzer()
        result = analyzer.analyze("")
        
        assert result['label'] == 'Neutral'
        assert result['score'] == 0.0
    
    def test_whitespace_only(self):
        """Test handling of whitespace-only text"""
        analyzer = VADERAnalyzer()
        result = analyzer.analyze("   ")
        
        assert result['label'] == 'Neutral'


class TestSentimentEngine:
    """Test sentiment analysis engine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = SentimentEngine(analyzer_type="vader")
        assert engine.analyzer_type == "vader"
        assert engine.analyzer is not None
    
    def test_analyze_text(self):
        """Test text analysis"""
        engine = SentimentEngine(analyzer_type="vader")
        result = engine.analyze_text("I'm very happy!")
        
        assert 'label' in result
        assert 'score' in result
        assert result['label'] in ['Positive', 'Negative', 'Neutral']
    
    def test_analyze_conversation(self):
        """Test conversation-level analysis"""
        engine = SentimentEngine(analyzer_type="vader")
        messages = [
            {'text': "I love this!"},
            {'text': "This is great!"},
            {'text': "Amazing product!"}
        ]
        
        result = engine.analyze_conversation(messages)
        
        assert 'overall_sentiment' in result
        assert 'average_score' in result
        assert 'total_messages' in result
        assert result['total_messages'] == 3
        assert result['overall_sentiment'] == 'Positive'
    
    def test_analyze_conversation_mixed(self):
        """Test conversation with mixed sentiments"""
        engine = SentimentEngine(analyzer_type="vader")
        messages = [
            {'text': "I love this!"},
            {'text': "This is terrible."},
            {'text': "It's okay."}
        ]
        
        result = engine.analyze_conversation(messages)
        
        assert 'overall_sentiment' in result
        assert 'reasoning' in result
        assert result['total_messages'] == 3
    
    def test_analyze_empty_conversation(self):
        """Test handling of empty conversation"""
        engine = SentimentEngine(analyzer_type="vader")
        result = engine.analyze_conversation([])
        
        assert result['overall_sentiment'] == 'Neutral'
        assert result['total_messages'] == 0


class TestSentimentEdgeCases:
    """Test edge cases for sentiment analysis"""
    
    def test_very_long_text(self):
        """Test handling of very long text"""
        engine = SentimentEngine(analyzer_type="vader")
        long_text = "This is great! " * 100
        result = engine.analyze_text(long_text)
        
        assert 'label' in result
        assert 'score' in result
    
    def test_special_characters(self):
        """Test handling of special characters"""
        engine = SentimentEngine(analyzer_type="vader")
        text = "I'm so happy!!! 😊🎉"
        result = engine.analyze_text(text)
        
        assert 'label' in result
    
    def test_numbers_and_symbols(self):
        """Test handling of numbers and symbols"""
        engine = SentimentEngine(analyzer_type="vader")
        text = "Score: 10/10! Best product ever!"
        result = engine.analyze_text(text)
        
        assert 'label' in result
    
    def test_multiple_sentences(self):
        """Test handling of multiple sentences"""
        engine = SentimentEngine(analyzer_type="vader")
        text = "I love this. It's amazing. Best purchase ever!"
        result = engine.analyze_text(text)
        
        assert result['label'] == 'Positive'

