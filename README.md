# Asistente Pronunciamiento

MVP para búsqueda semántica de pronunciamientos jurídicos a partir de la descripción libre de un caso.

## Arquitectura
- Frontend: React + Vite
- Backend: Python + FastAPI
- Extracción: PyMuPDF / python-docx
- Búsqueda semántica: sentence-transformers
- Índice vectorial: FAISS
- Metadatos: SQLite (MVP), migrable a PostgreSQL
- Storage desacoplado mediante DocumentStorage
- Desarrollo: almacenamiento local
- Objetivo inmediato: Google Drive
- Futuro: SharePoint, FileShare o MinIO

## Flujo
1. Cargar un pronunciamiento PDF/DOCX.
2. Extraer y normalizar texto.
3. Registrar metadatos y ubicación física.
4. Dividir texto en fragmentos e indexarlos.
5. Buscar usando una descripción jurídica en lenguaje natural.
6. Devolver documentos relacionados, coincidencia, fragmento relevante y enlace al original.

## Estructura
```text
frontend/
backend/
  app/
    api/
    documents/
    indexing/
    search/
    storage/
    main.py
  requirements.txt
data/
.env.example
```

El buscador nunca depende directamente de Google Drive: toda interacción con documentos pasa por un adaptador de almacenamiento.
