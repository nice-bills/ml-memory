# ==============================================
# 🧠 brain.py — Conversational Memory Core (Persistent via Pinecone + HF fallback)
# ==============================================
import os
import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
# === START OF FIX: Correct imports ===
from pinecone import Pinecone, ServerlessSpec
# === END OF FIX ===
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# === START OF FIX: Define model dimension ===
# This is the dimension of 'sentence-transformers/all-MiniLM-L6-v2'
MODEL_DIMENSION = 384
# === END OF FIX ===


class PersistentMemory:
    def __init__(self, index_name="persistent-memory", api_key=None):
        print("\nInitializing persistent memory...")

        # ------------------------------
        # Initialize Pinecone client
        # ------------------------------
        self.api_key = api_key or PINECONE_API_KEY
        if not self.api_key:
            raise ValueError("Missing Pinecone API key. Please set PINECONE_API_KEY in your .env file.")
        self.index_name = index_name

        self.pc = Pinecone(api_key=self.api_key)

        # ------------------------------
        # Create or connect to index
        # ------------------------------
        existing_indexes = [i["name"] for i in self.pc.list_indexes()]

        # === START OF FIX: Corrected index creation ===
        if self.index_name not in existing_indexes:
            print(f"Creating new Pinecone index '{self.index_name}' with {MODEL_DIMENSION} dimensions...")
            self.pc.create_index(
                name=self.index_name,
                dimension=MODEL_DIMENSION,  # Use the correct 384 dimension
                metric="cosine",            # 'cosine' is recommended for this model
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"      # Ensure this is your desired region
                )
            )
            print("Index creation initiated. Waiting for index to be ready...")
            time.sleep(10) # Give it a moment to initialize
        else:
            print(f"Using existing index '{self.index_name}'")
        # === END OF FIX ===
            
        self.index = self.pc.Index(self.index_name)

        # ------------------------------
        # Load Hugging Face embedding model (local fallback)
        # ------------------------------
        print("Loading embedding model (local fallback)...")
        for _ in tqdm(range(3), desc="Loading embeddings"):
            time.sleep(0.5)
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("Embedding model loaded successfully.\n")

    # ======================================================
    # Core memory functions (This section was already correct)
    # ======================================================
    def add_memory(self, text, role="user"):
        """Store a text with embeddings into Pinecone."""
        if not text.strip():
            return
        print(f"Storing new {role} message...")

        # Encode locally using HF model
        vector = self.embedder.encode(text).tolist()
        vector_id = f"mem-{int(time.time())}"

        self.index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": {"text": text, "role": role, "timestamp": time.time()},
                }
            ]
        )
        print("Memory stored in Pinecone.\n")

    def search_memory(self, query, top_k=3):
        """Retrieve the most relevant stored memories."""
        print("Searching persistent memory...")
        query_vector = self.embedder.encode(query).tolist()
        results = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)

        memories = []
        if results and "matches" in results:
            for match in tqdm(results["matches"], desc="Retrieving matches"):
                meta = match.get("metadata", {})
                if meta.get("text"):
                    memories.append((meta["text"], float(match["score"])))

        return memories


# =====================================================
# Run brain.py standalone (This section was already correct)
# =====================================================
if __name__ == "__main__":
    print("\n=== Running brain.py in standalone mode ===")
    memory = PersistentMemory(api_key=PINECONE_API_KEY)

    while True:
        user_input = input("\nEnter query (or 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Exiting memory session.")
            break

        # Store input
        memory.add_memory(user_input)

        # Retrieve relevant memories
        results = memory.search_memory(user_input)
        if results:
            print("\nRecalled from memory:")
            for text, score in results:
                print(f"- {text} (score: {score:.2f})")
        else:
            print("No relevant memory found.")



# # ==============================================
# # 🧠 brain.py — Conversational Memory Core (Persistent via Pinecone + HF fallback)
# # ==============================================
# import os
# import time
# from tqdm import tqdm
# from sentence_transformers import SentenceTransformer
# from pinecone import Pinecone, ServerlessSpec
# from dotenv import load_dotenv

# load_dotenv()
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


# class PersistentMemory:
#     def __init__(self, index_name="persistent-memory", api_key=None):
#         print("\nInitializing persistent memory...")

#         # ------------------------------
#         # Initialize Pinecone client
#         # ------------------------------
#         self.api_key = api_key or PINECONE_API_KEY
#         if not self.api_key:
#             raise ValueError("Missing Pinecone API key. Please set PINECONE_API_KEY in your .env file.")
#         self.index_name = index_name

#         self.pc = Pinecone(api_key=self.api_key)

#         # ------------------------------
#         # Create or connect to index
#         # ------------------------------
#         existing_indexes = [i["name"] for i in self.pc.list_indexes()]
#         if self.index_name not in existing_indexes:
#             print(f"Creating new Pinecone index '{self.index_name}'...")
#             self.pc.create_index_for_model(
#                 name=self.index_name,
#                 cloud="aws",
#                 region="us-east-1",
#                 embed={"model": "llama-text-embed-v2", "field_map": {"text": "chunk_text"}},
#             )
#             time.sleep(5)
#         else:
#             print(f"Using existing index '{self.index_name}'")

#         self.index = self.pc.Index(self.index_name)

#         # ------------------------------
#         # Load Hugging Face embedding model (local fallback)
#         # ------------------------------
#         print("Loading embedding model (local fallback)...")
#         for _ in tqdm(range(3), desc="Loading embeddings"):
#             time.sleep(0.5)
#         self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#         print("Embedding model loaded successfully.\n")

#     # ======================================================
#     # Core memory functions
#     # ======================================================
#     def add_memory(self, text, role="user"):
#         """Store a text with embeddings into Pinecone."""
#         if not text.strip():
#             return
#         print(f"Storing new {role} message...")

#         # Encode locally using HF model
#         vector = self.embedder.encode(text).tolist()
#         vector_id = f"mem-{int(time.time())}"

#         self.index.upsert(
#             vectors=[
#                 {
#                     "id": vector_id,
#                     "values": vector,
#                     "metadata": {"text": text, "role": role, "timestamp": time.time()},
#                 }
#             ]
#         )
#         print("Memory stored in Pinecone.\n")

#     def search_memory(self, query, top_k=3):
#         """Retrieve the most relevant stored memories."""
#         print("Searching persistent memory...")
#         query_vector = self.embedder.encode(query).tolist()
#         results = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)

#         memories = []
#         if results and "matches" in results:
#             for match in tqdm(results["matches"], desc="Retrieving matches"):
#                 meta = match.get("metadata", {})
#                 if meta.get("text"):
#                     memories.append((meta["text"], float(match["score"])))

#         return memories


# # =====================================================
# # Run brain.py standalone
# # =====================================================
# if __name__ == "__main__":
#     print("\n=== Running brain.py in standalone mode ===")
#     memory = PersistentMemory(api_key=PINECONE_API_KEY)

#     while True:
#         user_input = input("\nEnter query (or 'exit' to quit): ").strip()
#         if user_input.lower() == "exit":
#             print("Exiting memory session.")
#             break

#         # Store input
#         memory.add_memory(user_input)

#         # Retrieve relevant memories
#         results = memory.search_memory(user_input)
#         if results:
#             print("\nRecalled from memory:")
#             for text, score in results:
#                 print(f"- {text} (score: {score:.2f})")
#         else:
#             print("No relevant memory found.")





