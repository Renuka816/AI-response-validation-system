import chromadb

client = chromadb.PersistentClient(path="../vector_store/chroma_db")

collection = client.get_collection("knowledge_base")

print("Total documents:", collection.count())

print(collection.peek(limit=5))