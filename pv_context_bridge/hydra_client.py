import os
import requests
import json
import uuid
from typing import Any

from pv_memory.memory_integrity_store import (
    memory_integrity_store,
    MemoryIntegrityViolation,
    MemoryIntegrityRecord,
)

HYDRA_API_KEY = os.getenv("HYDRADB_API_KEY")
BASE_URL = "https://api.hydradb.com"


class ContextContaminationError(Exception):
    """Raised when memory integrity or contamination scan fails on RAG context."""
    pass

class HydraClient:
    def __init__(self, tenant_id="privatevault-demo", sub_tenant_id="demo"):
        self.tenant_id = tenant_id
        self.sub_tenant_id = sub_tenant_id

    def ingest_policy(self, content_text):
        # === MEMORY INTEGRITY WIRE (Module 2): write on ingest ===
        memory_key = f"policy:{hash(content_text)}"
        memory_integrity_store.write(
            memory_key=memory_key,
            content=content_text,
            agent_id="hydra-ingest",
            tenant_id=self.tenant_id,
            write_source="hydra_client.ingest_policy"
        )
        # ========================================================

        headers = {
            "Authorization": f"Bearer {HYDRA_API_KEY}"
        }

        # 🔥 FULL STRUCTURE REQUIRED BY HYDRA
        app_knowledge = json.dumps([
            {
                "id": str(uuid.uuid4()),
                "tenant_id": self.tenant_id,
                "sub_tenant_id": self.sub_tenant_id,
                "content": {
                    "text": content_text
                },
                "metadata": {
                    "type": "policy",
                    "risk": "high"
                }
            }
        ])

        data = {
            "tenant_id": self.tenant_id,
            "sub_tenant_id": self.sub_tenant_id,
            "app_knowledge": app_knowledge
        }

        response = requests.post(
            f"{BASE_URL}/ingestion/upload_knowledge",
            headers=headers,
            data=data
        )

        return response.text

    def query(self, question):
        headers = {
            "Authorization": f"Bearer {HYDRA_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "question": question,
            "session_id": "pv-demo",
            "tenant_id": self.tenant_id,
            "sub_tenant_id": self.sub_tenant_id
        }

        response = requests.post(
            f"{BASE_URL}/search/qna",
            headers=headers,
            json=payload
        )

        result = response.json()

        # === MEMORY INTEGRITY WIRE (Module 2): read on query (real RAG path) ===
        memory_key = f"query:{hash(question)}"
        try:
            memory_integrity_store.read(
                memory_key=memory_key,
                agent_id="hydra-query",
                tenant_id=self.tenant_id,
                expected_content=result  # verify returned context
            )
        except MemoryIntegrityViolation as e:
            raise ContextContaminationError(f"Context poisoned: {str(e)}") from e
        # ===============================================================

        return result


if __name__ == "__main__":
    client = HydraClient()

    print(">> Uploading policy...")
    upload_res = client.ingest_policy(
        "Maximum transaction limit is 250000 INR. Any transaction above this must be blocked."
    )
    print(upload_res)

    print("\n>> Querying context...")
    query_res = client.query("What is the transaction limit?")
    print(query_res)
