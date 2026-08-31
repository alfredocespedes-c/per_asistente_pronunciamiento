from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import json

@dataclass
class StoredDocument:
    id: str
    name: str
    path: Path

class LocalStorage:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def upload(self, filename: str, content: bytes) -> StoredDocument:
        doc_id = uuid4().hex
        safe_name = Path(filename).name
        folder = self.root / doc_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / safe_name
        path.write_bytes(content)
        (folder / "meta.json").write_text(json.dumps({"name": safe_name}, ensure_ascii=False), encoding="utf-8")
        return StoredDocument(doc_id, safe_name, path)

    def get(self, doc_id: str):
        folder = self.root / doc_id
        meta = folder / "meta.json"
        if not meta.exists():
            return None
        name = json.loads(meta.read_text(encoding="utf-8"))["name"]
        path = folder / name
        return StoredDocument(doc_id, name, path) if path.exists() else None

    def delete(self, doc_id: str):
        item = self.get(doc_id)
        if item:
            item.path.unlink(missing_ok=True)
            (item.path.parent / "meta.json").unlink(missing_ok=True)
            item.path.parent.rmdir()
