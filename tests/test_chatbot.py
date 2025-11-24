"""
Unit tests for chatbot module
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.chatbot import Chatbot


class TestChatbot:
    """Test Chatbot class"""
    
    def test_chatbot_initialization(self):
        """Test chatbot initialization"""
        bot = Chatbot(name="TestBot", personality="helpful")
        
        assert bot.name == "TestBot"
        assert bot.personality == "helpful"
        assert len(bot.conversation_context) == 0
    
    def test_exit_command_detection(self):
        """Test exit command detection"""
        bot = Chatbot()
        
        assert bot._is_exit_command("quit") == True
        assert bot._is_exit_command("exit") == True
        assert bot._is_exit_command("bye") == True
        assert bot._is_exit_command("goodbye") == True
        assert bot._is_exit_command("hello") == False
        assert bot._is_exit_command("QUIT") == True  # Case insensitive
    
    def test_generate_response_greeting(self):
        """Test response generation for greetings"""
        bot = Chatbot()
        response = bot.generate_response("Hello!")
        
        assert len(response) > 0
        assert isinstance(response, str)
    
    def test_generate_response_question(self):
        """Test response generation for questions"""
        bot = Chatbot()
        response = bot.generate_response("What is this?")
        
        assert len(response) > 0
        assert "?" in response or len(response) > 0
    
    def test_generate_response_with_sentiment_positive(self):
        """Test empathetic response for positive sentiment"""
        bot = Chatbot()
        sentiment = {'label': 'Positive', 'score': 0.7, 'confidence': 0.7}
        response = bot.generate_response("I love this!", sentiment)
        
        assert len(response) > 0
        # Should acknowledge positive sentiment
        assert any(word in response.lower() for word in ['glad', 'happy', 'wonderful', 'great'])
    
    def test_generate_response_with_sentiment_negative(self):
        """Test empathetic response for negative sentiment"""
        bot = Chatbot()
        sentiment = {'label': 'Negative', 'score': -0.7, 'confidence': 0.7}
        response = bot.generate_response("This is terrible!", sentiment)
        
        assert len(response) > 0
        # Should acknowledge negative sentiment
        assert any(word in response.lower() for word in ['sorry', 'apologize', 'concern', 'help'])
    
    def test_generate_response_with_sentiment_neutral(self):
        """Test response for neutral sentiment"""
        bot = Chatbot()
        sentiment = {'label': 'Neutral', 'score': 0.0, 'confidence': 0.0}
        response = bot.generate_response("The weather is okay.", sentiment)
        
        assert len(response) > 0
    
    def test_reset_context(self):
        """Test context reset"""
        bot = Chatbot()
        bot.conversation_context = ["message1", "message2"]
        bot.reset_context()
        
        assert len(bot.conversation_context) == 0
    
    def test_context_management(self):
        """Test conversation context management"""
        bot = Chatbot()
        
        # Add messages
        bot.generate_response("Hello")
        bot.generate_response("How are you?")
        
        assert len(bot.conversation_context) == 2
        
        # Context should be limited
        for i in range(15):
            bot.generate_response(f"Message {i}")
        
        assert len(bot.conversation_context) <= 10

