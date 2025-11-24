"""
Chatbot Logic Module
Handles response generation with empathetic and context-aware responses
"""

from typing import List, Optional, Dict
import logging
import random

logger = logging.getLogger(__name__)


class Chatbot:
    """Main chatbot class with empathetic response generation"""
    
    def __init__(self, name: str = "Assistant", personality: str = "helpful"):
        """
        Initialize chatbot
        
        Args:
            name: Bot name
            personality: Bot personality type
        """
        self.name = name
        self.personality = personality
        self.conversation_context: List[str] = []
        logger.info(f"Chatbot {name} initialized with {personality} personality")
    
    def generate_response(self, user_message: str, sentiment: Optional[Dict] = None, 
                         conversation_history: Optional[List] = None) -> str:
        """
        Generate contextual and empathetic response
        
        Args:
            user_message: User's message
            sentiment: Sentiment analysis result for the message
            conversation_history: Previous conversation messages
            
        Returns:
            Bot response string
        """
        # Update context
        self.conversation_context.append(user_message)
        if len(self.conversation_context) > 10:
            self.conversation_context.pop(0)
        
        # Check for exit commands
        if self._is_exit_command(user_message):
            return self._get_exit_response()
        
        # Generate empathetic response based on sentiment
        if sentiment:
            return self._generate_empathetic_response(user_message, sentiment, conversation_history)
        else:
            return self._generate_default_response(user_message, conversation_history)
    
    def _is_exit_command(self, message: str) -> bool:
        """Check if message is an exit command"""
        exit_commands = ['quit', 'exit', 'bye', 'goodbye', 'end', 'stop']
        return message.lower().strip() in exit_commands
    
    def _get_exit_response(self) -> str:
        """Generate exit response"""
        responses = [
            "Thank you for chatting! Have a great day!",
            "It was nice talking with you. Goodbye!",
            "Thanks for the conversation. Take care!",
            "Goodbye! Feel free to come back anytime."
        ]
        return random.choice(responses)
    
    def _generate_empathetic_response(self, message: str, sentiment: Dict, 
                                     history: Optional[List]) -> str:
        """Generate response that acknowledges sentiment"""
        label = sentiment.get('label', 'Neutral')
        score = sentiment.get('score', 0.0)
        confidence = sentiment.get('confidence', 0.0)
        
        # Very negative sentiment
        if label == 'Negative' and score < -0.5:
            responses = [
                "I'm really sorry to hear that. I understand this is frustrating. Can you tell me more about what went wrong?",
                "I sense you're quite upset about this. I want to help resolve this. What can I do?",
                "I apologize for the negative experience. Let's work together to fix this. What happened?",
                "I'm sorry this has been disappointing. Your feedback is important to us. Can you share more details?"
            ]
            return random.choice(responses)
        
        # Moderately negative
        elif label == 'Negative':
            responses = [
                "I understand your concern. Let me help address this issue.",
                "I'm sorry to hear that. Can you provide more details so I can assist you better?",
                "I appreciate you sharing this. Let's work on finding a solution together.",
                "Thank you for your feedback. I'll make sure this is addressed properly."
            ]
            return random.choice(responses)
        
        # Very positive sentiment
        elif label == 'Positive' and score > 0.5:
            responses = [
                "I'm so glad to hear that! It makes me happy to know you're satisfied.",
                "That's wonderful! I'm thrilled that you're having a positive experience.",
                "Great to hear! I'm delighted that things are working well for you.",
                "That's fantastic! Thank you for the positive feedback."
            ]
            return random.choice(responses)
        
        # Moderately positive
        elif label == 'Positive':
            responses = [
                "I'm glad to hear that! Is there anything else I can help with?",
                "That's good to know! How else can I assist you today?",
                "Great! I'm happy to help. What would you like to know more about?",
                "Wonderful! Feel free to ask if you need anything else."
            ]
            return random.choice(responses)
        
        # Neutral sentiment
        else:
            return self._generate_default_response(message, history)
    
    def _generate_default_response(self, message: str, history: Optional[List]) -> str:
        """Generate default contextual response"""
        message_lower = message.lower()
        
        # Greeting detection
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm here to help. How can I assist you today?"
        
        # Question detection
        if '?' in message:
            responses = [
                "That's an interesting question. Let me help you with that.",
                "I'd be happy to help answer that. Can you provide a bit more context?",
                "Good question! Let me think about how best to assist you.",
                "I understand you're asking about that. Here's what I can tell you..."
            ]
            return random.choice(responses)
        
        # Thank you detection
        if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! I'm here if you need anything else."
        
        # Default responses
        responses = [
            "I understand. Can you tell me more about that?",
            "That's interesting. How can I help you with this?",
            "I see. What would you like to know more about?",
            "Got it. Is there something specific you'd like me to help with?",
            "I'm here to help. What can I do for you?",
            "Thanks for sharing. How can I assist you further?"
        ]
        return random.choice(responses)
    
    def reset_context(self):
        """Reset conversation context"""
        self.conversation_context = []
        logger.debug("Chatbot context reset")

