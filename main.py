"""
Main Entry Point for Chatbot with Sentiment Analysis
Production-ready MVP with CLI interface
"""

import sys
import os
from pathlib import Path
from typing import Optional
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.sentiment import SentimentEngine
from src.conversation import Conversation
from src.chatbot import Chatbot
from src.analyzer import TrendAnalyzer
from src.emotion import EmotionDetector
from src.utils import (
    setup_logging, validate_text, sanitize_text, 
    format_duration, ensure_directory, load_config,
    export_to_csv
)

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Create dummy color objects
    class Fore:
        GREEN = YELLOW = RED = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

logger = logging.getLogger(__name__)


class ChatbotApp:
    """Main application class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the chatbot application
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        if config_path is None:
            config_path = "config/config.yaml"
        
        self.config = load_config(config_path)
        if not self.config:
            self.config = self._get_default_config()
        
        # Setup logging
        log_config = self.config.get('logging', {})
        setup_logging(
            log_level=log_config.get('level', 'INFO'),
            log_file=log_config.get('log_file')
        )
        
        # Initialize components
        sentiment_config = self.config.get('sentiment', {})
        self.sentiment_engine = SentimentEngine(
            analyzer_type=sentiment_config.get('analyzer_type', 'vader')
        )
        
        chatbot_config = self.config.get('chatbot', {})
        self.chatbot = Chatbot(
            name=chatbot_config.get('name', 'Assistant'),
            personality=chatbot_config.get('personality', 'helpful')
        )
        
        self.trend_analyzer = TrendAnalyzer()
        self.conversation = Conversation()
        
        # Emotion detector (bonus feature)
        if self.config.get('features', {}).get('emotion_detection', False):
            self.emotion_detector = EmotionDetector()
        else:
            self.emotion_detector = None
        
        # Feature flags
        self.features = self.config.get('features', {})
        self.ui_config = self.config.get('ui', {})
        
        logger.info("Chatbot application initialized")
    
    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'sentiment': {'analyzer_type': 'vader'},
            'chatbot': {'name': 'Assistant', 'personality': 'helpful'},
            'ui': {'use_colors': True, 'show_confidence_scores': True},
            'data': {'save_conversations': True, 'export_format': 'json'},
            'logging': {'level': 'INFO'},
            'features': {
                'real_time_sentiment': True,
                'trend_analysis': True,
                'visualization': True,
                'export_reports': True
            }
        }
    
    def print_colored(self, text: str, color: str = ""):
        """Print colored text if colorama is available"""
        if self.ui_config.get('use_colors', True) and HAS_COLORAMA:
            print(f"{color}{text}{Style.RESET_ALL}")
        else:
            print(text)
    
    def display_welcome(self):
        """Display welcome message"""
        self.print_colored("=" * 60, Fore.CYAN)
        self.print_colored("=== Sentiment Analysis Chatbot ===", Fore.CYAN + Style.BRIGHT)
        self.print_colored("=" * 60, Fore.CYAN)
        print()
        self.print_colored(f"Bot: Hello! I'm {self.chatbot.name}. I'm here to chat with you.", Fore.GREEN)
        self.print_colored("     Type 'quit', 'exit', or 'bye' to end the conversation.", Fore.YELLOW)
        print()
    
    def display_sentiment_indicator(self, sentiment: dict):
        """Display sentiment indicator for a message"""
        label = sentiment.get('label', 'Neutral')
        score = sentiment.get('score', 0.0)
        confidence = sentiment.get('confidence', 0.0)
        
        # Choose emoji and color based on sentiment
        if label == 'Positive':
            emoji = "😊"
            color = Fore.GREEN
        elif label == 'Negative':
            emoji = "😞"
            color = Fore.RED
        else:
            emoji = "😐"
            color = Fore.YELLOW
        
        score_str = f"{score:+.2f}" if self.ui_config.get('show_confidence_scores', True) else ""
        
        # Add emotion info if available in sentiment dict
        emotion_str = ""
        if sentiment.get('emotion'):
            emotion_result = sentiment['emotion']
            if emotion_result.get('primary_emotion') != 'neutral':
                if self.emotion_detector:
                    emotion_emoji = self.emotion_detector.get_emotion_emoji(
                        emotion_result['primary_emotion']
                    )
                    emotion_str = f" | Emotion: {emotion_emoji} {emotion_result['primary_emotion'].title()}"
        
        self.print_colored(f"💭 Sentiment: {label} {score_str}{emotion_str}", color)
    
    def run(self):
        """Run the main chatbot loop"""
        self.display_welcome()
        
        try:
            while True:
                # Get user input
                try:
                    user_input = input(f"{Fore.BLUE}You: {Style.RESET_ALL}").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n")
                    break
                
                # Validate input
                is_valid, error = validate_text(user_input)
                if not is_valid:
                    if error:
                        self.print_colored(f"Error: {error}", Fore.RED)
                    continue
                
                user_input = sanitize_text(user_input)
                
                # Analyze sentiment (Tier 2)
                sentiment = None
                if self.features.get('real_time_sentiment', True):
                    sentiment = self.sentiment_engine.analyze_text(user_input)
                    
                    # Add emotion detection if enabled
                    if self.emotion_detector and self.features.get('emotion_detection', False):
                        emotion_result = self.emotion_detector.detect_emotions(
                            user_input, sentiment_score=sentiment.get('score', 0.0)
                        )
                        sentiment['emotion'] = emotion_result
                    
                    self.display_sentiment_indicator(sentiment)
                
                # Add user message to conversation
                self.conversation.add_message(user_input, 'user', sentiment)
                
                # Check for exit
                if self.chatbot._is_exit_command(user_input):
                    break
                
                # Generate bot response
                bot_response = self.chatbot.generate_response(
                    user_input,
                    sentiment,
                    self.conversation.get_all_messages()
                )
                
                # Add bot message to conversation
                self.conversation.add_message(bot_response, 'bot')
                
                # Display bot response
                self.print_colored(f"Bot: {bot_response}", Fore.GREEN)
                print()
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            self.print_colored(f"An error occurred: {e}", Fore.RED)
        
        finally:
            self._end_conversation()
    
    def _end_conversation(self):
        """Handle conversation end and display analysis"""
        self.conversation.end_conversation()
        
        print()
        self.print_colored("=" * 60, Fore.CYAN)
        self.print_colored("=== Conversation Analysis ===", Fore.CYAN + Style.BRIGHT)
        self.print_colored("=" * 60, Fore.CYAN)
        print()
        
        # Get user messages for analysis
        user_messages = self.conversation.get_user_messages()
        
        if not user_messages:
            self.print_colored("No messages to analyze.", Fore.YELLOW)
            return
        
        # Tier 1: Overall conversation sentiment
        overall_sentiment = self.sentiment_engine.analyze_conversation(
            [msg.to_dict() for msg in user_messages]
        )
        
        # Display statistics
        self.print_colored(f"📊 Total Messages: {self.conversation.get_user_message_count()}", Fore.CYAN)
        self.print_colored(f"⏱️  Duration: {format_duration(self.conversation.get_duration())}", Fore.CYAN)
        print()
        
        # Tier 2: Trend analysis
        trend_analysis = None
        if self.features.get('trend_analysis', True) and len(user_messages) > 1:
            sentiment_scores = []
            sentiment_labels = []
            
            for msg in user_messages:
                if msg.sentiment:
                    sentiment_scores.append(msg.sentiment.get('score', 0.0))
                    sentiment_labels.append(msg.sentiment.get('label', 'Neutral'))
            
            if sentiment_scores:
                trend_analysis = self.trend_analyzer.analyze_trend(
                    sentiment_scores, sentiment_labels
                )
                
                self.print_colored(f"📈 Sentiment Trend: {trend_analysis['description']}", Fore.MAGENTA)
                print()
        
        # Overall sentiment
        overall_label = overall_sentiment.get('overall_sentiment', 'Neutral')
        reasoning = overall_sentiment.get('reasoning', '')
        
        # Color based on sentiment
        if overall_label == 'Positive':
            color = Fore.GREEN
        elif overall_label == 'Negative':
            color = Fore.RED
        else:
            color = Fore.YELLOW
        
        self.print_colored(f"⚖️  Overall Sentiment: {overall_label}", color + Style.BRIGHT)
        self.print_colored(f"   {reasoning}", Fore.WHITE)
        print()
        
        # Emotion analysis (bonus feature)
        if self.emotion_detector and self.features.get('emotion_detection', False):
            emotion_data = [
                {
                    'text': msg.text,
                    'sentiment': msg.sentiment
                }
                for msg in user_messages if msg.sentiment
            ]
            
            if emotion_data:
                emotion_analysis = self.emotion_detector.analyze_conversation_emotions(emotion_data)
                
                self.print_colored("😊 Emotion Analysis:", Fore.MAGENTA)
                self.print_colored(
                    f"   Dominant Emotion: {emotion_analysis['dominant_emotion'].title()} "
                    f"{self.emotion_detector.get_emotion_emoji(emotion_analysis['dominant_emotion'])}",
                    Fore.WHITE
                )
                
                if emotion_analysis.get('emotion_distribution'):
                    dist_str = ", ".join([
                        f"{emotion.title()}: {count}"
                        for emotion, count in emotion_analysis['emotion_distribution'].items()
                        if count > 0
                    ])
                    self.print_colored(f"   Distribution: {dist_str}", Fore.WHITE)
                print()
        
        # Key insights
        if self.features.get('trend_analysis', True) and len(user_messages) > 1:
            insights = self.trend_analyzer.summarize_insights(
                trend_analysis, overall_sentiment
            )
            
            if insights:
                self.print_colored("🔍 Key Insights:", Fore.CYAN)
                for insight in insights:
                    self.print_colored(f"   - {insight}", Fore.WHITE)
                print()
        
        # Visualization (Bonus feature)
        if self.features.get('visualization', False) and HAS_MATPLOTLIB:
            self._create_sentiment_visualization(user_messages)
        
        # Save conversation
        if self.config.get('data', {}).get('save_conversations', True):
            filepath = self.conversation.save_to_json()
            self.print_colored(f"💾 Conversation saved to: {filepath}", Fore.CYAN)
            
            # Export to CSV if configured
            export_format = self.config.get('data', {}).get('export_format', 'json')
            if export_format in ['csv', 'both']:
                csv_path = filepath.replace('.json', '.csv')
                self._export_conversation_csv(csv_path)
                self.print_colored(f"💾 Conversation exported to CSV: {csv_path}", Fore.CYAN)
        
        # Export report (Bonus feature)
        if self.features.get('export_reports', False):
            self._export_report(overall_sentiment, trend_analysis if len(user_messages) > 1 else None)
    
    def _create_sentiment_visualization(self, messages: list):
        """Create sentiment trend visualization"""
        try:
            sentiment_scores = []
            message_numbers = []
            
            for i, msg in enumerate(messages):
                if msg.sentiment:
                    sentiment_scores.append(msg.sentiment.get('score', 0.0))
                    message_numbers.append(i + 1)
            
            if len(sentiment_scores) < 2:
                return
            
            plt.figure(figsize=(10, 6))
            plt.plot(message_numbers, sentiment_scores, marker='o', linewidth=2, markersize=8)
            plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            plt.fill_between(message_numbers, sentiment_scores, 0, alpha=0.3)
            plt.xlabel('Message Number', fontsize=12)
            plt.ylabel('Sentiment Score', fontsize=12)
            plt.title('Sentiment Trend Throughout Conversation', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save plot
            ensure_directory('data')
            plot_path = f"data/sentiment_trend_{self.conversation.conversation_id}.png"
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.print_colored(f"📊 Sentiment visualization saved to: {plot_path}", Fore.CYAN)
            logger.info(f"Sentiment visualization saved to {plot_path}")
        
        except Exception as e:
            logger.error(f"Error creating visualization: {e}", exc_info=True)
    
    def _export_conversation_csv(self, filepath: str):
        """Export conversation to CSV"""
        try:
            data = []
            for msg in self.conversation.get_all_messages():
                row = {
                    'timestamp': msg.timestamp.isoformat(),
                    'sender': msg.sender,
                    'text': msg.text,
                    'sentiment_label': msg.sentiment.get('label', 'N/A') if msg.sentiment else 'N/A',
                    'sentiment_score': msg.sentiment.get('score', 0.0) if msg.sentiment else 0.0
                }
                data.append(row)
            
            export_to_csv(data, filepath)
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}", exc_info=True)
    
    def _export_report(self, overall_sentiment: dict, trend_analysis: Optional[dict]):
        """Export detailed conversation report"""
        try:
            ensure_directory('data')
            report_path = f"data/report_{self.conversation.conversation_id}.txt"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("CONVERSATION SENTIMENT ANALYSIS REPORT\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Conversation ID: {self.conversation.conversation_id}\n")
                f.write(f"Start Time: {self.conversation.start_time.isoformat()}\n")
                f.write(f"End Time: {self.conversation.end_time.isoformat() if self.conversation.end_time else 'N/A'}\n")
                f.write(f"Duration: {format_duration(self.conversation.get_duration())}\n")
                f.write(f"Total Messages: {self.conversation.get_message_count()}\n\n")
                
                f.write("OVERALL SENTIMENT ANALYSIS\n")
                f.write("-" * 60 + "\n")
                f.write(f"Overall Sentiment: {overall_sentiment.get('overall_sentiment', 'N/A')}\n")
                f.write(f"Average Score: {overall_sentiment.get('average_score', 0.0):.3f}\n")
                f.write(f"Reasoning: {overall_sentiment.get('reasoning', 'N/A')}\n\n")
                
                if trend_analysis:
                    f.write("TREND ANALYSIS\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"Trend: {trend_analysis.get('trend', 'N/A')}\n")
                    f.write(f"Description: {trend_analysis.get('description', 'N/A')}\n")
                    f.write(f"Volatility: {trend_analysis.get('volatility', 0.0):.3f}\n\n")
                
                f.write("MESSAGE DETAILS\n")
                f.write("-" * 60 + "\n")
                for i, msg in enumerate(self.conversation.get_all_messages(), 1):
                    f.write(f"\n[{i}] {msg.sender.upper()}: {msg.text}\n")
                    if msg.sentiment:
                        f.write(f"    Sentiment: {msg.sentiment.get('label', 'N/A')} "
                               f"({msg.sentiment.get('score', 0.0):+.3f})\n")
            
            self.print_colored(f"📄 Detailed report saved to: {report_path}", Fore.CYAN)
            logger.info(f"Report exported to {report_path}")
        
        except Exception as e:
            logger.error(f"Error exporting report: {e}", exc_info=True)


def main():
    """Main entry point"""
    try:
        app = ChatbotApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

