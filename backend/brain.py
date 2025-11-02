import os
import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec 
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# This is the dimension of 'sentence-transformers/all-MiniLM-L6-v2'
MODEL_DIMENSION = 384

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

        if self.index_name not in existing_indexes:
            print(f"Creating new Pinecone index '{self.index_name}' with {MODEL_DIMENSION} dimensions...")
            self.pc.create_index(
                name=self.index_name,
                dimension=MODEL_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print("Index creation initiated. Waiting...")
            time.sleep(10)
        else:
            print(f"Using existing index '{self.index_name}'")
            
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
    # Core memory functions
    # ======================================================
    def add_memory(self, text, user_id, role="user"):
        """Store a text with embeddings into Pinecone using user_id as namespace."""
        # Use a hardcoded ID if none is provided (for the guest_session scenario)
        if not user_id:
            user_id = "guest_session" 
            
        if not text.strip():
            return
        
        namespace = user_id 
        print(f"Storing new {role} message for user '{user_id}' in namespace '{namespace}'...")

        # Encode locally using HF model
        vector = self.embedder.encode(text).tolist()
        vector_id = f"mem-{user_id}-{int(time.time())}"

        self.index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": {"text": text, "role": role, "timestamp": time.time()},
                }
            ],
            namespace=namespace  # Pinecone uses the user_id namespace
        )
        print(f"Memory stored in Pinecone.\n")

    def search_memory(self, query, user_id, top_k=3):
        """Retrieve the most relevant stored memories for a specific user_id."""
        # Use a hardcoded ID if none is provided (for the guest_session scenario)
        if not user_id:
            user_id = "guest_session"
            
        namespace = user_id
        print(f"Searching persistent memory for user '{user_id}' in namespace '{namespace}'...")
        
        query_vector = self.embedder.encode(query).tolist()
        
        # --- KEY CHANGE: Search only within the user_id namespace ---
        results = self.index.query(
            vector=query_vector, 
            top_k=top_k, 
            include_metadata=True,
            namespace=namespace # Pinecone searches only the user_id namespace
        )

        memories = []
        if results and "matches" in results:
            for match in tqdm(results["matches"], desc=f"Retrieving matches for {user_id}"):
                meta = match.get("metadata", {})
                if meta.get("text"):
                    memories.append((meta["text"], float(match["score"])))

        return memories

# =====================================================
# Run brain.py standalone
# =====================================================
if __name__ == "__main__":
    print("\n=== Running brain.py in standalone mode ===")
    
    # NOTE: user_id is hardcoded for standalone testing
    test_user_id = "standalone_test_user" 
    memory = PersistentMemory(api_key=PINECONE_API_KEY)

    while True:
        user_input = input(f"\nEnter query for user '{test_user_id}' (or 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Exiting memory session.")
            break

        # Store input
        memory.add_memory(user_input, test_user_id)

        # Retrieve relevant memories
        results = memory.search_memory(user_input, test_user_id)
        if results:
            print("\nRecalled from memory:")
            for text, score in results:
                print(f"- {text} (score: {score:.2f})")
        else:
            print("No relevant memory found.")






# import os
# import time
# from tqdm import tqdm
# from sentence_transformers import SentenceTransformer
# from pinecone import Pinecone, ServerlessSpec
# from dotenv import load_dotenv

# load_dotenv()
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


# MODEL_DIMENSION = 384

# class PersistentMemory:
#     def __init__(self, index_name="persistent-memory", api_key=None):
#         print("\nInitializing persistent memory...")

#         self.api_key = api_key or PINECONE_API_KEY
#         if not self.api_key:
#             raise ValueError("Missing Pinecone API key. Please set PINECONE_API_KEY in your .env file.")
#         self.index_name = index_name

#         self.pc = Pinecone(api_key=self.api_key)


#         existing_indexes = [i["name"] for i in self.pc.list_indexes()]

#         if self.index_name not in existing_indexes:
#             print(f"Creating new Pinecone index '{self.index_name}' with {MODEL_DIMENSION} dimensions...")
#             self.pc.create_index(
#                 name=self.index_name,
#                 dimension=MODEL_DIMENSION, 
#                 metric="cosine",            
#                 spec=ServerlessSpec(
#                     cloud="aws",
#                     region="us-east-1"      
#                 )
#             )
#             print("Index creation initiated. Waiting for index to be ready...")
#             time.sleep(10) 
#         else:
#             print(f"Using existing index '{self.index_name}'")
            
#         self.index = self.pc.Index(self.index_name)

#         print("Loading embedding model (local fallback)...")
#         for _ in tqdm(range(3), desc="Loading embeddings"):
#             time.sleep(0.5)
#         self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#         print("Embedding model loaded successfully.\n")

#     def add_memory(self, text, role="user"):
#         """Store a text with embeddings into Pinecone."""
#         if not text.strip():
#             return
#         print(f"Storing new {role} message...")

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


# if __name__ == "__main__":
#     print("\n=== Running brain.py in standalone mode ===")
#     memory = PersistentMemory(api_key=PINECONE_API_KEY)

#     while True:
#         user_input = input("\nEnter query (or 'exit' to quit): ").strip()
#         if user_input.lower() == "exit":
#             print("Exiting memory session.")
#             break

#         memory.add_memory(user_input)

#         results = memory.search_memory(user_input)
#         if results:
#             print("\nRecalled from memory:")
#             for text, score in results:
#                 print(f"- {text} (score: {score:.2f})")
#         else:
#             print("No relevant memory found.")


