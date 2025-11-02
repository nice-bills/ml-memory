from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app, get_db
from backend.database import Base
from backend.models import Conversation, Message
import pytest
from unittest.mock import MagicMock
import os
import shutil

# --- 1. SETUP: DATABASE FIXTURES ---

# Define a URL for a temporary in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"

# Create a test engine and session factory
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# This function overrides the standard dependency used by FastAPI to point to our test DB
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override to the FastAPI app
app.dependency_overrides[get_db] = override_get_db

# Use TestClient to interact with the FastAPI app
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Module-level fixture to create and clean the database file."""
    # Ensure the test database file is clean before and after all tests
    if os.path.exists("./test_db.db"):
        os.remove("./test_db.db")
    
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    yield  # Runs all tests

    # Tear down: Remove the database file after tests are done
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_db.db"):
        os.remove("./test_db.db")


# --- 2. TESTS ---

def test_root_redirect():
    """Test the root endpoint redirects to /docs."""
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'] == '/docs'


def test_get_conversations_empty():
    """Test getting conversations when none exist."""
    response = client.get("/conversations")
    assert response.status_code == 200
    assert response.json() == []


def test_chat_new_conversation(mocker):
    """
    Test starting a new chat and ensure the worker task is called.
    We mock the Groq client and the Celery worker task.
    """
    # Mock the slow Groq response stream to return instantly
    mock_groq_stream = MagicMock()
    mock_groq_stream.__enter__.return_value = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello!"))]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content=""))])
    ]
    
    mocker.patch('backend.main.groq_client.chat.completions.create', return_value=mock_groq_stream)
    
    # Mock the Celery worker function (the slow part)
    mock_worker = mocker.patch('backend.main.embed_and_save_task.delay')

    # Send the request to create a new conversation
    response = client.post(
        "/chat",
        json={"user_input": "Test query for new chat", "conversation_id": None},
        headers={"X-User-ID": "test_user_42"}
    )
    
    # The API should succeed (status 200) and return text/plain streaming
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/plain; charset=utf-8'

    # Check for the Conversation ID header returned by the API
    new_convo_id = response.headers.get("X-Conversation-Id")
    assert new_convo_id is not None
    
    # The full streaming response should be in the content
    assert response.text == "Hello!"

    # The slow embedding task should have been called twice (user input and assistant output)
    assert mock_worker.call_count == 2
    
    # Check the first call (user input)
    user_call_args = mock_worker.call_args_list[0][0]
    assert user_call_args[0] == "Test query for new chat" # text_to_embed
    assert user_call_args[1]['user_id'] == "test_user_42"
    assert user_call_args[1]['role'] == "user"
    assert user_call_args[1]['conversation_id'] == int(new_convo_id)

    # Check the second call (assistant output)
    assistant_call_args = mock_worker.call_args_list[1][0]
    assert assistant_call_args[0] == "Hello!" # full_response
    assert assistant_call_args[1]['role'] == "assistant"
    
    return int(new_convo_id) # Return ID for subsequent test


def test_history_and_conversations_persistence(mocker):
    """Test if the conversation history was saved to the SQL database."""
    # Ensure the database is clean (setup_test_db fixture handles this)

    # --- 1. Create a Conversation and save messages to the SQL DB ---
    # Since we are mocking the worker in test_chat_new_conversation, 
    # we need a real ID, so we call the test above to create the conversation.
    convo_id = test_chat_new_conversation(mocker)

    # To check persistence, we fetch the conversation list and the history directly.

    # --- 2. Test GET /conversations ---
    conv_response = client.get("/conversations")
    assert conv_response.status_code == 200
    conv_data = conv_response.json()
    
    # Check that the new conversation is in the list
    assert len(conv_data) == 1
    assert conv_data[0]['id'] == convo_id
    assert conv_data[0]['title'] == "New Chat" # Title hasn't been updated yet

    # --- 3. Test GET /history/{conversation_id} ---
    # Since the messages are saved *asynchronously* by the real worker (which is mocked here),
    # we simulate the history that *should* have been saved by the worker.
    # We call the SQL database directly via the main API to ensure the API endpoint works.
    history_response = client.get(f"/history/{convo_id}")
    assert history_response.status_code == 404 # Should fail because the messages were never saved by the mocked worker

    # --- 4. Manually add messages to the database to test the history endpoint ---
    with TestingSessionLocal() as db:
        # Create user message
        db_user_msg = Message(
            conversation_id=convo_id, 
            role="user", 
            content="Test query for new chat"
        )
        # Create assistant message
        db_assistant_msg = Message(
            conversation_id=convo_id, 
            role="assistant", 
            content="Hello!"
        )
        db.add_all([db_user_msg, db_assistant_msg])
        db.commit()

    # --- 5. Rerun GET /history/{conversation_id} ---
    history_response_fixed = client.get(f"/history/{convo_id}")
    assert history_response_fixed.status_code == 200
    history_data = history_response_fixed.json()
    
    assert len(history_data) == 2
    assert history_data[0]['role'] == "user"
    assert "Test query" in history_data[0]['content']
    assert history_data[1]['role'] == "assistant"
    assert history_data[1]['content'] == "Hello!"