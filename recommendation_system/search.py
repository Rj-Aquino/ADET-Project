# import os
# from datetime import datetime, timedelta
# from dotenv import load_dotenv

# #sample

# # ✅ Automatically load environment variables from .env file
# load_dotenv(dotenv_path=".env")

# # ✅ Check if variables are loaded
# EXA_API_KEY = os.getenv("EXA_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_ENV = os.getenv("PINECONE_ENV")
# INDEX_NAME = os.getenv("index_name")

# if not EXA_API_KEY or not PINECONE_API_KEY or not PINECONE_ENV or not INDEX_NAME:
#     raise ValueError("❌ Some Variables are not set. Check your .env file!")

# # ✅ Lazy initialization containers
# _exa = None
# _index = None
# _model = None

# def get_exa():
#     global _exa
#     if _exa is None:
#         from exa_py import Exa
#         _exa = Exa(api_key=EXA_API_KEY)
#     return _exa

# def get_index():
#     global _index
#     if _index is None:
#         import pinecone
#         pc = pinecone.Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
#         _index = pc.Index(INDEX_NAME)
#     return _index

# def get_model():
#     global _model
#     if _model is None:
#         from sentence_transformers import SentenceTransformer
#         _model = SentenceTransformer('all-MiniLM-L6-v2')
#     return _model

# def query_pinecone(query_text, top_n=5):
#     """Query Pinecone and return top-N research papers."""
#     model = get_model()
#     index = get_index()

#     # ✅ Generate query embedding
#     query_embedding = model.encode([query_text])[0].tolist()

#     # ✅ Query Pinecone index
#     results = index.query(
#         vector=query_embedding,
#         top_k=top_n,
#         include_metadata=True
#     )

#     if not results.get("matches"):
#         print("❌ No relevant research papers found in Pinecone.")
#         return []

#     return results["matches"]

# def query_exa(query_text, top_n=5, research_papers_only=True):
#     """Search the web using EXA and return top-N research papers from the last 5 years."""
#     exa = get_exa()

#     five_years_ago = (datetime.now() - timedelta(days=5 * 365)).isoformat() + "Z"

#     search_params = {
#         "query": query_text,
#         "num_results": top_n,
#         "category": "research paper" if research_papers_only else None,
#         # "startPublishedDate": five_years_ago,
#     }

#     response = exa.search(**search_params)

#     if not hasattr(response, 'results') or not isinstance(response.results, list):
#         print("❌ No results found from Exa API or unexpected response format.")
#         return []

#     return response.results

# def enhanced_search(query_text, top_n=5):
#     """Search both Pinecone and EXA and combine results with enriched information."""
#     print("🔍 Searching Pinecone for relevant research papers...")
#     pinecone_results = query_pinecone(query_text, top_n)

#     print("🌐 Searching the web with EXA for additional research papers...")
#     exa_results = query_exa(query_text, top_n)

#     combined_results = []

#     for pinecone_result in pinecone_results:
#         title = pinecone_result['metadata'].get('title')
#         abstract = pinecone_result['metadata'].get('abstract')
#         authors = pinecone_result['metadata'].get('authors')
#         year = pinecone_result['metadata'].get('year')
#         score = pinecone_result.get('score')

#         if not title or not score:
#             continue

#         combined_results.append({
#             'title': title,
#             'score': score,
#             'abstract': abstract,
#             'authors': authors,
#             'year': year,
#             'source': "Pinecone"
#         })

#     for exa_result in exa_results:
#         title = getattr(exa_result, 'title', None)
#         url = getattr(exa_result, 'url', None)
#         score = getattr(exa_result, 'score', None)

#         if not title or not url or not score:
#             continue

#         combined_results.append({
#             'title': title,
#             'url': url,
#             'score': score,
#             'source': "EXA"
#         })

#     return combined_results
