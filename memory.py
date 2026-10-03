import json
from pathlib import Path

class Memory:
    def __init__(self, path, max_items=500):
        self.path = Path(path)
        self.max_items = max_items
        self.data = self._load()

    def _load(self):
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self):
        self.path.write_text(
            json.dumps(self.data[-self.max_items:], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add(self, role, content):
        self.data.append({"role": role, "content": content})
        self._save()

    def recent(self, limit=20):
        return self.data[-limit:]

    def relevant(self, query, limit=10):
        words = {w.lower() for w in query.split() if len(w) >= 3}
        scored = []
        for item in self.data:
            text = item.get("content", "").lower()
            score = sum(1 for w in words if w in text)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def clear(self):
        self.data = []
        self._save()
