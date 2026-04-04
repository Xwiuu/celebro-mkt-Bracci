import os
import io
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from typing import List, Optional

class KnowledgeService:
    def __init__(self, persist_directory="./chroma_data"):
        # Garante que o diretório de persistência existe
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="celebro_knowledge",
            embedding_function=self.embedding_fn
        )

    def _get_text_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Quebra o texto em pedaços de tamanho fixo."""
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    async def upload_document(self, file_content: bytes, filename: str, category: str):
        """Lê PDF ou TXT e salva no ChromaDB em chunks."""
        text = ""
        if filename.lower().endswith(".pdf"):
            try:
                pdf = PdfReader(io.BytesIO(file_content))
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                raise Exception(f"Erro ao ler PDF {filename}: {str(e)}")
        else:
            try:
                text = file_content.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback para latin-1 se utf-8 falhar
                text = file_content.decode("latin-1")

        if not text.strip():
            return {"status": "error", "message": "Documento vazio ou ilegível."}

        chunks = self._get_text_chunks(text)
        # Gerar IDs únicos baseados no nome do arquivo e índice
        import hashlib
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
        metadatas = [{"category": category, "source": filename} for _ in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        return {"status": "success", "chunks_added": len(chunks), "filename": filename}

    async def search_knowledge(self, query: str, category: Optional[str] = None, n_results: int = 3) -> List[str]:
        """Busca no ChromaDB os trechos mais relevantes."""
        where_filter = {"category": category} if category else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        if results and results["documents"] and len(results["documents"]) > 0:
            return results["documents"][0]
        return []

knowledge_service = KnowledgeService()
