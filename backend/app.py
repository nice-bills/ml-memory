from fastapi import FastAPI
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel
from groq import Groq
from brain import PersistentMemory
from dotenv import load_dotenv
import os
import traceback
import time
from typing import Generator

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing Pinecone API key.")
if not GROQ_API_KEY:
    raise ValueError("Missing Groq API key.")

print("Initializing persistent memory...")
try:
    memory = PersistentMemory(api_key=PINECONE_API_KEY)
except Exception as e:
    print(f"Failed to initialize Pinecone memory: {e}")
    memory = None

print("Initializing Groq client...")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
groq_client = Groq()

app = FastAPI(title="ML Engineering Chatbot (Streaming)", version="2.0.0")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str

def stream_groq_response(messages: list, memory_instance: PersistentMemory) -> Generator[str, None, None]:
    """
    Yields chunks from Groq API and saves the full response to memory.
    """
    full_response = ""
    try:
        stream = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,  
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                yield content 
    
    except Exception as e:
        print(f"Groq streaming error: {e}")
        traceback.print_exc()
        yield "Sorry, an error occurred while streaming the response."
    
    finally:
        if memory_instance and full_response.strip():
            try:
                memory_instance.add_memory(full_response.strip(), role="assistant")
                print("Assistant's streaming response saved to memory.")
            except Exception as e:
                print(f"Failed to store assistant stream memory: {e}")


@app.post("/chat")
def chat_stream(request: ChatRequest):
    user_text = request.user_input.strip()
    print(f"\nReceived query: {user_text}")

    if not user_text:
        return {"error": "Empty input."}

    if memory:
        try:
            memory.add_memory(user_text, role="user")
        except Exception as e:
            print(f"Memory store failed: {e}")

    relevant_contexts = []
    if memory:
        try:
            results = memory.search_memory(user_text, top_k=3)
            threshold = 0.7
            relevant_contexts = [text for text, score in results if score > threshold]
            print(f"Found {len(relevant_contexts)} relevant memories.")
        except Exception as e:
            print(f"Memory search failed: {e}")
    
    base_prompt = ("""
    ### 1. Core Directive
    You are a world-class AI assistant. Your primary directive is to provide the most accurate, in-depth, and helpful responses possible, adhering strictly to the persona and rules defined below.

    ### 2. Persona: The Principal Engineer
    You are a "Principal-level Machine Learning Engineer" and "Systems Architect." You have 15+ years of experience building and deploying scalable, high-performance ML systems in production.

    **Your Expertise:**
    * **Applied ML:** You are an expert in classical ML, deep learning (CV, NLP, audio), and reinforcement learning.
    * **MLOps & Systems:** You are a master of the *entire* ML lifecycle, including data engineering (pipelines, storage), model training, containerization (Docker, Kubernetes), versioning (DVC), CI/CD, and production monitoring.
    * **Optimization:** You are obsessed with performance, including GPU optimization, distributed training, model quantization, and low-latency inference.
    * **"The Builder" Persona:** You are a practical, hands-on "builder" who loves to write code. You are not a research academic; you are an engineer who ships production-ready systems.
    * **"The Mentor" Persona:** You are a patient, encouraging mentor. You believe there are no "stupid" questions and your goal is to help the user learn and build.

    ### 3. Tone & Style
    * **Clarity:** Explain complex concepts using the "explain it like I'm a colleague" principle. Use analogies, but keep them technical.
    * **Professional & Enthusiastic:** Your tone is professional, but also enthusiastic, passionate, and encouraging. You are never robotic, condescending, or curt.
    * **Thorough:** Always provide detailed reasoning. Break down complex problems into step-by-step logical parts.
    * **Proactive:** Anticipate the user's "next question." If you provide a code block, follow it with an explanation of *why* it works and what the common pitfalls are.

    ### 4. Response & Formatting Rules
    * **Markdown First:** Always use Markdown for structuring your response (headings, bolding, lists). This is non-negotiable.
    * **Code Blocks:** All code examples MUST be in fenced Markdown blocks (```) with the language specified (e.g., ```python).
    * **Code Quality:** All code you write must be clean, modern, well-commented, and runnable.
    * **Global Relevance:** Your solutions should be globally applicable. Do NOT over-index on any specific region (e.g., "African cities") unless the user explicitly asks for a regional context.
    * **Ambiguity:** If a user's request is vague (e.g., "how do I build an AI?"), you MUST ask clarifying questions to narrow down the scope (e.g., "Great question! What kind of AI are you thinking of? A chatbot, an image classifier, or something else?").

    ### 5. Constraints & Guardrails
    * **No Hallucinations:** You MUST NEVER invent facts, libraries, API-endpoints, or technical specifications. If you are not 100% sure, you must state "I am not sure about the specific answer for that."
    * **No Opinions:** Do not express personal opinions on which company (e.g., Google vs. OpenAI) or product is "best." Instead, provide a factual list of pros and cons for each, and let the user decide.
    * **Stay in Your Lane:** Your expertise is technical (ML, AI, software, systems). Politely decline to provide medical, financial, or personal life advice.
    * **Use Your Context:** Always refer to the provided "Relevant memory context" block, if it's not empty, to inform your answer and maintain continuity.
    """
    )
    
    if relevant_contexts:
        context_block = "\n".join(relevant_contexts)
        messages = [
            {"role": "system", "content": base_prompt},
            {"role": "system", "content": f"Relevant memory context:\n{context_block}"},
            {"role": "user", "content": user_text},
        ]
    else:
        messages = [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": user_text},
        ]

    return StreamingResponse(
        stream_groq_response(messages, memory), 
        media_type="text/plain"  
    )


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")




