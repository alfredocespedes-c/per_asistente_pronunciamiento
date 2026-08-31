from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .storage.local import LocalStorage
from .documents.extractor import extract_text
from .search.engine import SearchEngine

app = FastAPI(title="Asistente Pronunciamiento API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

storage = LocalStorage(Path("data/documents"))
engine = SearchEngine(Path("data/index"))

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

@app.get("/health")
def health():
    return {"status": "ok", "documents": engine.document_count}

@app.post("/api/search")
def search(payload: SearchRequest):
    if not payload.query.strip():
        raise HTTPException(400, "Debe ingresar una descripción del caso")
    return {"query": payload.query, "results": engine.search(payload.query, payload.limit)}

@app.post("/api/pronunciamientos")
async def upload(
    file: UploadFile = File(...),
    numero: str = Form(""),
    fecha: str = Form(""),
    materia: str = Form(""),
    organismo: str = Form(""),
    tags: str = Form("")
):
    raw = await file.read()
    stored = storage.upload(file.filename or "documento", raw)
    text = extract_text(stored.path)
    if not text.strip():
        storage.delete(stored.id)
        raise HTTPException(422, "No fue posible extraer texto del documento")
    metadata = {"numero": numero, "fecha": fecha, "materia": materia, "organismo": organismo, "tags": tags, "filename": stored.name, "storage_id": stored.id}
    document = engine.add_document(text, metadata)
    return {"status": "indexed", "document": document}

@app.get("/api/documents/{storage_id}")
def download(storage_id: str):
    item = storage.get(storage_id)
    if not item:
        raise HTTPException(404, "Documento no encontrado")
    return FileResponse(item.path, filename=item.name)
