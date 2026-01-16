import json
import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.documents import Document
from app.services.vector_store import VectorStoreService

KB_FILE_PATH = "data/knowledge_base.json"

def load_kb_entries(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def format_entry_to_text(entry, kb_metadata):
    """
    Converts a KB entry into a rich text format for embedding.
    """
    
    # Extract metadata from the root KB object
    source_title = kb_metadata.get("source_document", {}).get("title", "Unknown Source")
    
    # header
    header = (
        f"DOMARIN: REGULATORY_COMPLIANCE\n"
        f"SOURCE_DOC: {source_title}\n"
        f"DOC_TYPE: KnowledgeBase_Entry\n"
        f"CATEGORY: {entry.get('category', 'General')}\n"
        f"TITLE: {entry.get('title', 'Untitled')}\n"
        f"---\n"
    )
    
    # Body components
    components = []
    
    # Question Intents (High signal for retrieval)
    if "question_intents" in entry and entry["question_intents"]:
        intents = "\n".join([f"- {intent}" for intent in entry["question_intents"]])
        components.append(f"QUESTION_INTENTS:\n{intents}")
        
    # Key Points
    if "key_points" in entry and entry["key_points"]:
        kps = "\n".join([f"- {kp}" for kp in entry["key_points"]])
        components.append(f"KEY_POINTS:\n{kps}")
        
    # Content
    if "content" in entry:
        components.append(f"CONTENT:\n{entry['content']}")
        
    # Answer Guidance (Crucial for consistent answers/structured output)
    if "answer_guidance" in entry:
        guidance_json = json.dumps(entry["answer_guidance"], indent=2)
        components.append(f"ANSWER_GUIDANCE:\n{guidance_json}")
        
    return header + "\n\n".join(components)

def run_ingestion():
    print(f"Loading Knowledge Base from {KB_FILE_PATH}...")
    if not os.path.exists(KB_FILE_PATH):
        print(f"Error: File {KB_FILE_PATH} not found.")
        return

    kb_data = load_kb_entries(KB_FILE_PATH)
    entries = kb_data.get("entries", [])
    
    print(f"Found {len(entries)} entries. Preparing documents...")
    
    documents = []
    for entry in entries:
        text_content = format_entry_to_text(entry, kb_data)
        
        # Metadata for the document
        metadata = {
            "id": entry.get("id"),
            "category": entry.get("category"),
            "title": entry.get("title"),
            "source": kb_data.get("source_document", {}).get("title"),
            "type": "kb_entry"
        }
        
        doc = Document(page_content=text_content, metadata=metadata)
        documents.append(doc)
        
    print("Initializing Vector Store...")
    vector_store = VectorStoreService()
    
    print(f"Ingesting {len(documents)} documents into FAISS...")
    vector_store.add_documents(documents)
    
    print("Ingestion Complete!")

if __name__ == "__main__":
    run_ingestion()
