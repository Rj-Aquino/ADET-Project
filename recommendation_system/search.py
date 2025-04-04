import pinecone
from sentence_transformers import SentenceTransformer
from exa_py import Exa
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# ✅ Automatically load environment variables from .env file
load_dotenv(dotenv_path=".env")  # Explicitly specify the path if needed

# ✅ Check if variables are loaded
EXA_API_KEY = os.getenv("EXA_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = os.getenv("index_name")

if not EXA_API_KEY or not PINECONE_API_KEY or not PINECONE_ENV or not INDEX_NAME:
    raise ValueError("❌ Some Variables are not set. Check your .env file!")

# ✅ Initialize EXA API
exa = Exa(api_key=EXA_API_KEY)

# ✅ Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pc.Index(INDEX_NAME)

# ✅ Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def query_pinecone(query_text, top_n=5):
    """Query Pinecone and return top-N research papers."""
    
    # ✅ Generate query embedding
    query_embedding = model.encode([query_text])[0].tolist()

    # ✅ Query Pinecone index
    results = index.query(
        vector=query_embedding,
        top_k=top_n,
        include_metadata=True
    )

    # ✅ Handle no results case
    if not results.get("matches"):
        print("❌ No relevant research papers found in Pinecone.")
        return []

    return results["matches"]

def query_exa(query_text, top_n=5, research_papers_only=True):
    """Search the web using EXA and return top-N research papers from the last 5 years."""
    
    # ✅ Calculate date 5 years ago from today
    five_years_ago = (datetime.now() - timedelta(days=5 * 365)).isoformat() + "Z"

    # ✅ Define search parameters to be used in the request body
    search_params = {
        "query": query_text,
        "num_results": top_n,
        "category": "research paper" if research_papers_only else None,
        #"startPublishedDate": five_years_ago,
    }

    # ✅ Perform the API request with the correctly structured body
    response = exa.search(**search_params)

    # Check if 'results' exists in the response and is iterable
    if not hasattr(response, 'results') or not isinstance(response.results, list):
        print("❌ No results found from Exa API or unexpected response format.")
        return []

    return response.results

def enhanced_search(query_text, top_n=5):
    """Search both Pinecone and EXA and combine results with enriched information."""
    print("🔍 Searching Pinecone for relevant research papers...")
    pinecone_results = query_pinecone(query_text, top_n)
    
    print("🌐 Searching the web with EXA for additional research papers...")
    exa_results = query_exa(query_text, top_n)
    
    # Create a list to store the combined results
    combined_results = []
    
    # Add Pinecone results to combined_results
    for pinecone_result in pinecone_results:
        title = pinecone_result['metadata'].get('title', None)
        abstract = pinecone_result['metadata'].get('abstract', None)
        authors = pinecone_result['metadata'].get('authors', None)
        year = pinecone_result['metadata'].get('year', None)
        score = pinecone_result.get('score', None)
        
        # Skip results with missing title or score
        if not title or not score:
            continue
        
        # Add Pinecone results directly
        combined_results.append({
            'title': title,
            'score': score,
            'abstract': abstract,
            'authors': authors,
            'year': year,
            'source': "Pinecone"
        })
    
    # Add EXA results to combined_results
    for exa_result in exa_results:
        title = exa_result.title if hasattr(exa_result, 'title') else None
        url = exa_result.url if hasattr(exa_result, 'url') else None
        score = exa_result.score if hasattr(exa_result, 'score') else None
        
        # Skip results with missing title, URL, or score
        if not title or not url or not score:
            continue
        
        # Add EXA results directly
        combined_results.append({
            'title': title,
            'url': url,
            'score': score,
            'source': "EXA"
        })
    
    return combined_results