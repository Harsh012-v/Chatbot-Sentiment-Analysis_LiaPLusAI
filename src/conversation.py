"""
Conversation Management Module
Handles conversation history, message storage, and retrieval
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Message:
    """Represents a single message in the conversation"""
    
    def __init__(self, text: str, sender: str, timestamp: Optional[datetime] = None):
        """
        Initialize a message
        
        Args:
            text: Message content
            sender: 'user' or 'bot'
            timestamp: Message timestamp (defaults to now)
        """
        self.text = text
        self.sender = sender
        self.timestamp = timestamp or datetime.now()
        self.sentiment: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return {
            'text': self.text,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'sentiment': self.sentiment
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create message from dictionary"""
        msg = cls(
            text=data['text'],
            sender=data['sender'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        msg.sentiment = data.get('sentiment')
        return msg


class Conversation:
    """Manages conversation history and state"""
    
    def __init__(self, conversation_id: Optional[str] = None):
        """
        Initialize a conversation
        
        Args:
            conversation_id: Optional unique identifier
        """
        self.conversation_id = conversation_id or self._generate_id()
        self.messages: List[Message] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        logger.info(f"Conversation {self.conversation_id} initialized")
    
    def _generate_id(self) -> str:
        """Generate unique conversation ID"""
        return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_message(self, text: str, sender: str, sentiment: Optional[Dict] = None) -> Message:
        """
        Add a message to the conversation
        
        Args:
            text: Message content
            sender: 'user' or 'bot'
            sentiment: Optional sentiment analysis result
            
        Returns:
            Created Message object
        """
        message = Message(text, sender)
        if sentiment:
            message.sentiment = sentiment
        self.messages.append(message)
        logger.debug(f"Added {sender} message: {text[:50]}...")
        return message
    
    def get_user_messages(self) -> List[Message]:
        """Get all user messages"""
        return [msg for msg in self.messages if msg.sender == 'user']
    
    def get_bot_messages(self) -> List[Message]:
        """Get all bot messages"""
        return [msg for msg in self.messages if msg.sender == 'bot']
    
    def get_all_messages(self) -> List[Message]:
        """Get all messages in chronological order"""
        return self.messages.copy()
    
    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.messages)
    
    def get_user_message_count(self) -> int:
        """Get number of user messages"""
        return len(self.get_user_messages())
    
    def end_conversation(self):
        """Mark conversation as ended"""
        self.end_time = datetime.now()
        logger.info(f"Conversation {self.conversation_id} ended")
    
    def get_duration(self) -> float:
        """Get conversation duration in seconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict:
        """Convert conversation to dictionary"""
        return {
            'conversation_id': self.conversation_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.get_duration(),
            'message_count': self.get_message_count(),
            'messages': [msg.to_dict() for msg in self.messages]
        }
    
    def save_to_json(self, filepath: Optional[str] = None) -> str:
        """
        Save conversation to JSON file
        
        Args:
            filepath: Optional file path (defaults to data/ directory)
            
        Returns:
            Path to saved file
        """
        if filepath is None:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            filepath = data_dir / f"{self.conversation_id}.json"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Conversation saved to {filepath}")
        return str(filepath)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'Conversation':
        """
        Load conversation from JSON file
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Conversation object
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conv = cls(conversation_id=data['conversation_id'])
        conv.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            conv.end_time = datetime.fromisoformat(data['end_time'])
        
        for msg_data in data.get('messages', []):
            conv.messages.append(Message.from_dict(msg_data))
        
        logger.info(f"Conversation loaded from {filepath}")
        return conv

