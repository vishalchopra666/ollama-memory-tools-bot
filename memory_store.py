# memory_store.py
import os
import json
import uuid
import sqlite3
import numpy as np
import faiss

class MemoryStore:
    def __init__(self, db_path="data/memory.db", dim=768):
        self.db_path = db_path
        self.dim = dim
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._setup_db()
        self.index = faiss.IndexFlatL2(self.dim)
        self._load_embeddings()

    def _setup_db(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id TEXT PRIMARY KEY,
                    note TEXT,
                    tags TEXT,
                    embedding TEXT
                )
            ''')

    def _load_embeddings(self):
        self.id_map = []
        rows = self.conn.execute("SELECT id, embedding FROM memory").fetchall()
        if rows:
            vectors = []
            for row in rows:
                self.id_map.append(row[0])
                vectors.append(json.loads(row[1]))
            self.index.add(np.array(vectors).astype('float32'))

    def save_memory(self, note, tags, embedding):
        if len(embedding) != self.dim:
            raise ValueError("Embedding dim mismatch")

        eid = str(uuid.uuid4())
        with self.conn:
            self.conn.execute(
                "INSERT INTO memory (id, note, tags, embedding) VALUES (?, ?, ?, ?)",
                (eid, note, json.dumps(tags), json.dumps(embedding))
            )
        self.id_map.append(eid)
        self.index.add(np.array([embedding]).astype('float32'))

    def search(self, query_embedding, top_k=3):
        if self.index.ntotal == 0:
            return []

        D, I = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        ids = [self.id_map[i] for i in I[0] if i != -1]
        notes = self.conn.execute(
            "SELECT note FROM memory WHERE id IN ({seq})".format(
                seq=','.join(['?'] * len(ids))
            ), ids
        ).fetchall()
        return [n[0] for n in notes]


    def search_with_tag(self, query_embedding, tags=None, top_k=5):
        results = self.search(query_embedding, top_k=top_k * 2)  # get more results

        if not tags:
            return results

        filtered = []
        for note in results:
            for tag in tags:
                if tag in note.lower():
                    filtered.append(note)
                    break
        return filtered[:top_k]



#if __name__ == '__main__':
#    from embedding_utils import embed_text
#    t = MemoryStore()
#    t.save_memory("""These functions are available to me such as
#            \n 1. !save - To save the last assistant reply to disk.
#            \n 2. !remember - To save the anything that you will pass to permanent memory - Sqlite3
#            \n 3. !recall - To recall the chat from sqlite3.
#    """, tags=[], embedding=embed_text("""These functions are available to me such as
#            \n 1. !save - To save the last assistant reply to disk.
#            \n 2. !remember - To save the anything that you will pass to permanent memory - Sqlite3
#            \n 3. !recall - To recall the chat from sqlite3.
#    """))

