from os import getenv
from dotenv import load_dotenv
from brain import PersistentMemory
from celery_config import celery_app
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message, Conversation
from sqlalchemy.sql import func 

# --- Load environment variables ---
load_dotenv()
PINECONE_API_KEY = getenv("PINECONE_API_KEY")

# --- Initialize Persistent Memory ---
# The worker needs its own instance of the memory system
print("Initializing Persistent Memory for Worker...")
try:
    memory = PersistentMemory(api_key=PINECONE_API_KEY)
    print("Worker Memory Initialized.")
except Exception as e:
    print(f"Failed to initialize Pinecone memory for Worker: {e}")
    memory = None

# --- HELPER FUNCTION: Saves message to SQL DB ---
def save_to_sql_db(conversation_id: int, text: str, role: str, user_id: str):
    """Saves the message text to the SQLite database for chat history."""
    db: Session = SessionLocal()
    try:
        # 1. Create and add the new message record
        new_message = Message(
            conversation_id=conversation_id,
            role=role,
            content=text
        )
        db.add(new_message)
        
        # 2. If this is the *first* user message, update the conversation title
        if role == "user":
            convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if convo and convo.title == "New Chat":
                # Use the first 5 words as the title
                convo.title = " ".join(text.split()[:5])
                convo.user_id = user_id 
        
        # 3. Update the conversation timestamp to bring it to the top of the conversation list
        convo_to_update = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if convo_to_update:
            convo_to_update.updated_at = func.now()
        
        db.commit()
    except Exception as e:
        print(f"Error saving to SQL DB: {e}")
        db.rollback()
    finally:
        db.close()

# --- Define the Celery Task ---
@celery_app.task(name='worker.embed_and_save_task')
def embed_and_save_task(text_to_embed, user_id, role, conversation_id: int):
    """
    Celery task signature. Runs in the background (non-blocking).
    
    1. Saves message to SQL history (fast).
    2. Generates vector embedding and saves to Pinecone (slow, background work).
    """
    
    # 1. Save to SQL DB (Fast)
    # This ensures the chat history updates immediately for the user
    save_to_sql_db(conversation_id, text_to_embed, role, user_id)

    # 2. Run Pinecone Embedding (Slow, runs in background)
    if not memory:
        return "Error: Memory not initialized."
    
    if not user_id:
        return "Error: user_id missing."

    try:
        print(f"Worker: Starting embedding for user '{user_id}'...")
        # Note: Passes user_id to brain.py for Pinecone Namespace isolation
        memory.add_memory(text_to_embed, user_id, role=role) 
        print(f"Worker: Embedding task completed.")
        return f"Saved: {text_to_embed[:20]}... for user {user_id}"
    except Exception as e:
        print(f"Worker: Error during embedding task for user {user_id}: {e}")
        return f"Error: {e}"











# import os
# from dotenv import load_dotenv
# from brain import PersistentMemory
# from celery_config import celery_app

# # --- Load environment variables ---
# load_dotenv()
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# if not PINECONE_API_KEY:
#     raise ValueError("Missing Pinecone API key in worker.")

# # --- Initialize components ---
# # The worker needs its own instance of the memory system
# print("Initializing Persistent Memory for Worker...")
# try:
#     memory = PersistentMemory(api_key=PINECONE_API_KEY)
#     print("Worker Memory Initialized.")
# except Exception as e:
#     print(f"Failed to initialize Pinecone memory for Worker: {e}")
#     memory = None

# # --- Define the Celery Task ---
# @celery_app.task(name='worker.embed_and_save_task')
# def embed_and_save_task(text_to_embed, role):
#     """
#     This is the background task that runs the slow embedding and saving.
#     """
#     if not memory:
#         print("Worker: No memory backend. Skipping save.")
#         return "Error: Memory not initialized."
    
#     if not text_to_embed or not role:
#         print("Worker: No text or role provided. Skipping save.")
#         return "Error: No text or role."

#     try:
#         print(f"Worker: Starting task for role '{role}'...")
#         memory.add_memory(text_to_embed, role=role)
#         print(f"Worker: Task completed for role '{role}'.")
#         return f"Saved: {text_to_embed[:20]}..."
#     except Exception as e:
#         print(f"Worker: Error during embedding task: {e}")
#         return f"Error: {e}"