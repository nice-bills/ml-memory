from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base # Note the dot-import for modularity

class Conversation(Base):
    """Represents a single chat session."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    # Using 'guest_session' as a placeholder until real auth is implemented
    user_id = Column(String, index=True, default="guest_session") 
    title = Column(String, index=True, default="New Chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship to Messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Represents a single message (user or assistant) within a conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    
    role = Column(String, index=True) # 'user' or 'assistant'
    content = Column(String)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship back to Conversation
    conversation = relationship("Conversation", back_populates="messages")
