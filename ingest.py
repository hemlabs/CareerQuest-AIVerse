import os
import re 
from datasets import load_dataset
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURATION ---
# We REMOVED the broken resume dataset. 
# These 2 datasets are all you need for a "Smart" Career AI.
DATASETS_CONFIG = [
    # 1. Teaches the AI about real Job Requirements & Skills
    {"id": "jacob-hugging-face/job-descriptions", "split": "train[:600]", "source_tag": "job_market"},
    
    # 2. Teaches the AI how to interview users (Boss Battle)
    {"id": "glaiveai/glaive-code-assistant-v2",   "split": "train[:200]", "source_tag": "coding_interview"}
]

CHROMA_PATH = "./chroma_db" 

# 🛡️ STRICT BOUNCER: Only allow engineering content
TECH_KEYWORDS = [
    "software", "developer", "engineer", "data scientist", "cyber", "security", 
    "python", "java", "react", "node", "cloud", "aws", "docker", "kubernetes", 
    "frontend", "front-end", "backend", "back-end", "full stack", "full-stack",
    "machine learning", "ai", "artificial intelligence"
]

def ingest_data():
    all_docs = []
    print("🚀 Starting Clean Ingestion (Jobs & Interviews)...")

    # OPTIONAL: Clean old database to remove broken files
    import shutil
    if os.path.exists(CHROMA_PATH):
        print("   🧹 Cleaning up old database...")
        shutil.rmtree(CHROMA_PATH)

    for ds_info in DATASETS_CONFIG:
        ds_id = ds_info["id"]
        print(f"\n📥 Downloading: {ds_id}...")
        
        try:
            dataset = load_dataset(ds_id, split=ds_info["split"])
        except Exception as e:
            print(f"   ❌ Error loading {ds_id}: {e}")
            continue

        print(f"   🔍 Filtering...")
        
        count = 0
        for row in dataset:
            content = ""
            # Handle Glaive (Interview) vs Jacob (Jobs)
            if 'question' in row and 'answer' in row: 
                content = f"Q: {row['question']}\nA: {row['answer']}"
            else:
                content = (row.get('job_description') or row.get('text') or str(row))
            
            is_relevant = False
            
            # Logic: Keep ALL interviews, filter Jobs for tech words
            if ds_info["source_tag"] == "coding_interview":
                is_relevant = True 
            else:
                content_lower = str(content).lower()
                for keyword in TECH_KEYWORDS:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', content_lower):
                        is_relevant = True
                        break
            
            if content and is_relevant:
                all_docs.append(Document(
                    page_content=str(content), 
                    metadata={"source": ds_id, "category": ds_info["source_tag"]}
                ))
                count += 1
        
        print(f"   ✅ Kept {count} items.")

    print(f"\n✂️ Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    print(f"🧠 Embedding into Local Brain (GPU)...")
    embedding_fn = OllamaEmbeddings(model="llama3")
    
    Chroma.from_documents(
        documents=splits,
        embedding=embedding_fn,
        persist_directory=CHROMA_PATH
    )
    
    print(f"\n✅ SUCCESS! Database is ready for the Grand Finale.")

if __name__ == "__main__":
    ingest_data()