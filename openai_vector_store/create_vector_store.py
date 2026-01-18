import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Load your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Please set OPENAI_API_KEY in your .env file")

client = OpenAI(api_key=openai_api_key)

# 1️⃣ Create a new vector store with a friendly name
vector_store = client.vector_stores.create(name="my_rag_docs")
vector_store_id = vector_store.id
print("Vector Store ID:", vector_store_id)

# 2️⃣ Upload each file into the vector store
data_dir = "data"
for filename in os.listdir(data_dir):
    file_path = os.path.join(data_dir, filename)
    if os.path.isfile(file_path) and filename.lower().endswith((".pdf", ".txt", ".md")):
        with open(file_path, "rb") as f:
            # Upload & wait for processing
            uploaded = client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store_id,
                file=f
            )
        print(f"Uploaded {filename} to vector store:", uploaded.id)

print("All files uploaded successfully!")
print("Use this vector_store_id:", vector_store_id)
