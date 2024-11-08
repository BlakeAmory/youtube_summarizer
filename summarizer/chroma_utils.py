import chromadb
from django.conf import settings
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEmbeddings()

# Initialize Chroma collection
collection = chroma_client.get_or_create_collection("video_summaries")


def store_video_data(video_summary):
    collection.add(
        documents=[video_summary.summary],
        metadatas=[
            {"video_url": video_summary.video_url, "title": video_summary.video_title}
        ],
        ids=[str(video_summary.id)],
    )


def search_similar_videos(query, n_results=5):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results
