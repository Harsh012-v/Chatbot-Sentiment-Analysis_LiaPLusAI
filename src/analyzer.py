"""
Trend Analysis Module
Analyzes sentiment progression and trends throughout conversations
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyzes sentiment trends and shifts in conversations"""
    
    def __init__(self):
        """Initialize trend analyzer"""
        logger.info("TrendAnalyzer initialized")
    
    def analyze_trend(self, sentiment_scores: List[float], 
                     sentiment_labels: List[str]) -> Dict[str, any]:
        """
        Analyze sentiment trend across conversation
        
        Args:
            sentiment_scores: List of sentiment scores in chronological order
            sentiment_labels: List of sentiment labels in chronological order
            
        Returns:
            Dictionary with trend analysis results
        """
        if not sentiment_scores or len(sentiment_scores) < 2:
            return {
                'trend': 'insufficient_data',
                'description': 'Not enough messages to analyze trend',
                'first_half_avg': 0.0,
                'second_half_avg': 0.0,
                'progression': []
            }
        
        # Split into halves
        mid_point = len(sentiment_scores) // 2
        first_half = sentiment_scores[:mid_point]
        second_half = sentiment_scores[mid_point:]
        
        first_half_avg = sum(first_half) / len(first_half) if first_half else 0.0
        second_half_avg = sum(second_half) / len(second_half) if second_half else 0.0
        
        # Determine trend
        trend = self._determine_trend(first_half_avg, second_half_avg)
        description = self._generate_trend_description(trend, first_half_avg, second_half_avg)
        
        # Calculate progression
        progression = self._calculate_progression(sentiment_scores, sentiment_labels)
        
        # Identify key moments
        key_moments = self._identify_key_moments(sentiment_scores, sentiment_labels)
        
        return {
            'trend': trend,
            'description': description,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'progression': progression,
            'key_moments': key_moments,
            'volatility': self._calculate_volatility(sentiment_scores)
        }
    
    def _determine_trend(self, first_avg: float, second_avg: float) -> str:
        """Determine overall trend direction"""
        threshold = 0.1
        
        if second_avg - first_avg > threshold:
            return 'improving'
        elif first_avg - second_avg > threshold:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_trend_description(self, trend: str, first_avg: float, 
                                   second_avg: float) -> str:
        """Generate human-readable trend description"""
        if trend == 'improving':
            if first_avg < -0.1:
                return f"Started negative → Shifted positive (improved from {first_avg:.2f} to {second_avg:.2f})"
            else:
                return f"Became increasingly positive (improved from {first_avg:.2f} to {second_avg:.2f})"
        elif trend == 'declining':
            if second_avg < -0.1:
                return f"Started positive/neutral → Shifted negative (declined from {first_avg:.2f} to {second_avg:.2f})"
            else:
                return f"Became less positive (declined from {first_avg:.2f} to {second_avg:.2f})"
        else:
            return f"Remained relatively stable (around {first_avg:.2f})"
    
    def _calculate_progression(self, scores: List[float], 
                              labels: List[str]) -> List[Dict[str, any]]:
        """Calculate sentiment progression over time"""
        progression = []
        
        for i, (score, label) in enumerate(zip(scores, labels)):
            progression.append({
                'message_index': i + 1,
                'score': score,
                'label': label,
                'cumulative_avg': sum(scores[:i+1]) / (i + 1)
            })
        
        return progression
    
    def _identify_key_moments(self, scores: List[float], 
                             labels: List[str]) -> List[Dict[str, any]]:
        """Identify significant sentiment shifts or key emotional moments"""
        key_moments = []
        
        if len(scores) < 2:
            return key_moments
        
        for i in range(1, len(scores)):
            change = abs(scores[i] - scores[i-1])
            
            # Significant shift (change > 0.3)
            if change > 0.3:
                direction = "positive" if scores[i] > scores[i-1] else "negative"
                key_moments.append({
                    'message_index': i + 1,
                    'type': 'significant_shift',
                    'direction': direction,
                    'magnitude': change,
                    'from_score': scores[i-1],
                    'to_score': scores[i],
                    'from_label': labels[i-1],
                    'to_label': labels[i]
                })
            
            # Extreme sentiment (very positive or very negative)
            if abs(scores[i]) > 0.7:
                key_moments.append({
                    'message_index': i + 1,
                    'type': 'extreme_sentiment',
                    'sentiment': labels[i],
                    'score': scores[i]
                })
        
        return key_moments
    
    def _calculate_volatility(self, scores: List[float]) -> float:
        """Calculate sentiment volatility (standard deviation)"""
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5
    
    def summarize_insights(self, trend_analysis: Dict, 
                          overall_sentiment: Dict) -> List[str]:
        """
        Generate key insights from trend and overall sentiment analysis
        
        Args:
            trend_analysis: Result from analyze_trend()
            overall_sentiment: Overall sentiment analysis result
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Trend insights
        if trend_analysis['trend'] == 'improving':
            insights.append("Conversation mood improved over time")
        elif trend_analysis['trend'] == 'declining':
            insights.append("Conversation mood declined over time")
        else:
            insights.append("Sentiment remained relatively consistent")
        
        # Key moments
        if trend_analysis.get('key_moments'):
            significant_shifts = [m for m in trend_analysis['key_moments'] 
                                if m['type'] == 'significant_shift']
            if significant_shifts:
                insights.append(f"Detected {len(significant_shifts)} significant sentiment shift(s)")
        
        # Distribution insights
        if overall_sentiment.get('label_distribution'):
            dist = overall_sentiment['label_distribution']
            total = sum(dist.values())
            if dist['Positive'] > dist['Negative']:
                insights.append(f"Predominantly positive messages ({dist['Positive']}/{total})")
            elif dist['Negative'] > dist['Positive']:
                insights.append(f"Predominantly negative messages ({dist['Negative']}/{total})")
            else:
                insights.append("Balanced mix of positive and negative messages")
        
        # Volatility insights
        volatility = trend_analysis.get('volatility', 0.0)
        if volatility > 0.3:
            insights.append("High sentiment volatility - mood changed frequently")
        elif volatility < 0.1:
            insights.append("Low sentiment volatility - consistent emotional tone")
        
        return insights

