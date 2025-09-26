import os, time, requests
from typing import Any, Dict, List
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

TMDB_KEY    = os.getenv("TMDb_API_KEY")
NEO4J_URI   = os.getenv("NEO4J_URI")
NEO4J_USER  = os.getenv("NEO4J_USER")
NEO4J_PASS  = os.getenv("NEO4J_PASS")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL= os.getenv("OLLAMA_MODEL", "llama3.1:8b")

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def tmdb_get(path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    base = "https://api.themoviedb.org/3"
    p = {"api_key": TMDB_KEY}
    if params: p.update(params)
    for attempt in range(3):
        r = requests.get(f"{base}{path}", params=p, timeout=20)
        if r.status_code == 200:
            return r.json()
        time.sleep(1 + attempt)
    r.raise_for_status()

def ollama_generate(prompt: str, temperature: float = 0.1) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "options": {"temperature": temperature},
        "stream": False  # <— important
    }
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    if "error" in data and data["error"]:
        raise RuntimeError(f"Ollama error: {data['error']}")
    return (data.get("response") or "").strip()
