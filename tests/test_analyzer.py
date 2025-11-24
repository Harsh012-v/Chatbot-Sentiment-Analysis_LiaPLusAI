"""
Unit tests for trend analyzer module
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.analyzer import TrendAnalyzer


class TestTrendAnalyzer:
    """Test TrendAnalyzer class"""
    
    def test_analyzer_initialization(self):
        """Test trend analyzer initialization"""
        analyzer = TrendAnalyzer()
        assert analyzer is not None
    
    def test_analyze_trend_improving(self):
        """Test trend analysis for improving sentiment"""
        analyzer = TrendAnalyzer()
        scores = [-0.5, -0.3, 0.1, 0.3, 0.5]
        labels = ['Negative', 'Negative', 'Neutral', 'Positive', 'Positive']
        
        result = analyzer.analyze_trend(scores, labels)
        
        assert result['trend'] == 'improving'
        assert result['first_half_avg'] < result['second_half_avg']
        assert 'description' in result
    
    def test_analyze_trend_declining(self):
        """Test trend analysis for declining sentiment"""
        analyzer = TrendAnalyzer()
        scores = [0.5, 0.3, 0.1, -0.3, -0.5]
        labels = ['Positive', 'Positive', 'Neutral', 'Negative', 'Negative']
        
        result = analyzer.analyze_trend(scores, labels)
        
        assert result['trend'] == 'declining'
        assert result['first_half_avg'] > result['second_half_avg']
    
    def test_analyze_trend_stable(self):
        """Test trend analysis for stable sentiment"""
        analyzer = TrendAnalyzer()
        scores = [0.1, 0.0, -0.1, 0.0, 0.1]
        labels = ['Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral']
        
        result = analyzer.analyze_trend(scores, labels)
        
        assert result['trend'] == 'stable'
    
    def test_analyze_trend_insufficient_data(self):
        """Test trend analysis with insufficient data"""
        analyzer = TrendAnalyzer()
        scores = [0.5]
        labels = ['Positive']
        
        result = analyzer.analyze_trend(scores, labels)
        
        assert result['trend'] == 'insufficient_data'
    
    def test_identify_key_moments(self):
        """Test identification of key sentiment moments"""
        analyzer = TrendAnalyzer()
        scores = [0.1, 0.2, -0.6, 0.3, 0.8]
        labels = ['Neutral', 'Positive', 'Negative', 'Positive', 'Positive']
        
        result = analyzer.analyze_trend(scores, labels)
        
        assert 'key_moments' in result
        # Should detect significant shift at index 2
        assert len(result['key_moments']) > 0
    
    def test_calculate_volatility(self):
        """Test volatility calculation"""
        analyzer = TrendAnalyzer()
        scores_high_vol = [0.8, -0.7, 0.6, -0.5, 0.4]
        scores_low_vol = [0.1, 0.0, 0.1, 0.0, 0.1]
        
        result_high = analyzer.analyze_trend(scores_high_vol, ['Positive'] * 5)
        result_low = analyzer.analyze_trend(scores_low_vol, ['Neutral'] * 5)
        
        assert result_high['volatility'] > result_low['volatility']
    
    def test_summarize_insights(self):
        """Test insight summarization"""
        analyzer = TrendAnalyzer()
        trend_analysis = {
            'trend': 'improving',
            'description': 'Started negative → Shifted positive',
            'volatility': 0.2,
            'key_moments': [
                {'type': 'significant_shift', 'message_index': 3}
            ]
        }
        overall_sentiment = {
            'overall_sentiment': 'Positive',
            'label_distribution': {'Positive': 3, 'Negative': 1, 'Neutral': 1}
        }
        
        insights = analyzer.summarize_insights(trend_analysis, overall_sentiment)
        
        assert len(insights) > 0
        assert isinstance(insights, list)
        assert all(isinstance(insight, str) for insight in insights)

