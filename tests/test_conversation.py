"""
Unit tests for conversation management module
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
import json
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.conversation import Conversation, Message


class TestMessage:
    """Test Message class"""
    
    def test_message_creation(self):
        """Test message creation"""
        msg = Message("Hello", "user")
        
        assert msg.text == "Hello"
        assert msg.sender == "user"
        assert isinstance(msg.timestamp, datetime)
        assert msg.sentiment is None
    
    def test_message_to_dict(self):
        """Test message to dictionary conversion"""
        msg = Message("Hello", "user")
        msg.sentiment = {'label': 'Positive', 'score': 0.5}
        
        data = msg.to_dict()
        
        assert data['text'] == "Hello"
        assert data['sender'] == "user"
        assert 'timestamp' in data
        assert data['sentiment'] == {'label': 'Positive', 'score': 0.5}
    
    def test_message_from_dict(self):
        """Test message creation from dictionary"""
        data = {
            'text': 'Hello',
            'sender': 'user',
            'timestamp': datetime.now().isoformat(),
            'sentiment': {'label': 'Positive', 'score': 0.5}
        }
        
        msg = Message.from_dict(data)
        
        assert msg.text == "Hello"
        assert msg.sender == "user"
        assert msg.sentiment == {'label': 'Positive', 'score': 0.5}


class TestConversation:
    """Test Conversation class"""
    
    def test_conversation_creation(self):
        """Test conversation initialization"""
        conv = Conversation()
        
        assert conv.conversation_id is not None
        assert len(conv.messages) == 0
        assert isinstance(conv.start_time, datetime)
        assert conv.end_time is None
    
    def test_add_message(self):
        """Test adding messages"""
        conv = Conversation()
        sentiment = {'label': 'Positive', 'score': 0.5}
        
        msg = conv.add_message("Hello", "user", sentiment)
        
        assert len(conv.messages) == 1
        assert msg.text == "Hello"
        assert msg.sender == "user"
        assert msg.sentiment == sentiment
    
    def test_get_user_messages(self):
        """Test retrieving user messages"""
        conv = Conversation()
        conv.add_message("Hello", "user")
        conv.add_message("Hi there!", "bot")
        conv.add_message("How are you?", "user")
        
        user_messages = conv.get_user_messages()
        
        assert len(user_messages) == 2
        assert all(msg.sender == "user" for msg in user_messages)
    
    def test_get_bot_messages(self):
        """Test retrieving bot messages"""
        conv = Conversation()
        conv.add_message("Hello", "user")
        conv.add_message("Hi there!", "bot")
        conv.add_message("How are you?", "user")
        conv.add_message("I'm good!", "bot")
        
        bot_messages = conv.get_bot_messages()
        
        assert len(bot_messages) == 2
        assert all(msg.sender == "bot" for msg in bot_messages)
    
    def test_message_count(self):
        """Test message counting"""
        conv = Conversation()
        conv.add_message("Hello", "user")
        conv.add_message("Hi", "bot")
        conv.add_message("How are you?", "user")
        
        assert conv.get_message_count() == 3
        assert conv.get_user_message_count() == 2
    
    def test_end_conversation(self):
        """Test ending conversation"""
        conv = Conversation()
        conv.end_conversation()
        
        assert conv.end_time is not None
        assert isinstance(conv.end_time, datetime)
    
    def test_get_duration(self):
        """Test conversation duration calculation"""
        conv = Conversation()
        import time
        time.sleep(0.1)  # Small delay
        conv.end_conversation()
        
        duration = conv.get_duration()
        assert duration > 0
    
    def test_to_dict(self):
        """Test conversation to dictionary conversion"""
        conv = Conversation()
        conv.add_message("Hello", "user")
        conv.add_message("Hi", "bot")
        conv.end_conversation()
        
        data = conv.to_dict()
        
        assert 'conversation_id' in data
        assert 'start_time' in data
        assert 'end_time' in data
        assert 'message_count' in data
        assert 'messages' in data
        assert len(data['messages']) == 2
    
    def test_save_and_load_json(self):
        """Test saving and loading conversation from JSON"""
        # Create test directory
        test_dir = Path("data/test")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create and save conversation
        conv1 = Conversation()
        conv1.add_message("Hello", "user", {'label': 'Positive'})
        conv1.add_message("Hi", "bot")
        conv1.end_conversation()
        
        filepath = test_dir / "test_conv.json"
        saved_path = conv1.save_to_json(str(filepath))
        
        assert os.path.exists(saved_path)
        
        # Load conversation
        conv2 = Conversation.load_from_json(saved_path)
        
        assert conv2.conversation_id == conv1.conversation_id
        assert len(conv2.messages) == 2
        assert conv2.messages[0].text == "Hello"
        assert conv2.messages[0].sentiment == {'label': 'Positive'}
        
        # Cleanup
        os.remove(saved_path)

