from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL = "intfloat/multilingual-e5-small"

class SearchEngine:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.model = SentenceTransformer(MODEL)
        self.records_path = root / "records.json"
        self.records = json.loads(self.records_path.read_text(encoding="utf-8")) if self.records_path.exists() else []

    @property
    def document_count(self):
        return len({r["metadata"]["storage_id"] for r in self.records})

    def _chunks(self, text: str, size=900, overlap=150):
        clean = " ".join(text.split())
        step = size - overlap
        return [clean[i:i+size] for i in range(0, len(clean), step) if clean[i:i+size].strip()]

    def _embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def add_document(self, text, metadata):
        chunks = self._chunks(text)
        embeddings = self._embed(["passage: " + c for c in chunks])
        for chunk, vector in zip(chunks, embeddings):
            self.records.append({"chunk": chunk, "vector": vector, "metadata": metadata})
        self.records_path.write_text(json.dumps(self.records, ensure_ascii=False), encoding="utf-8")
        return metadata

    def search(self, query: str, limit=10):
        if not self.records:
            return []
        q = np.array(self._embed(["query: " + query])[0], dtype=np.float32)
        best = {}
        for record in self.records:
            score = float(np.dot(q, np.array(record["vector"], dtype=np.float32)))
            sid = record["metadata"]["storage_id"]
            if sid not in best or score > best[sid][0]:
                best[sid] = (score, record)
        ranked = sorted(best.values(), key=lambda x: x[0], reverse=True)[:limit]
        return [{
            "score": round(max(0, score) * 100, 1),
            "fragment": record["chunk"],
            "metadata": record["metadata"],
            "download_url": f"/api/documents/{record['metadata']['storage_id']}"
        } for score, record in ranked]
