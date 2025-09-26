# ask.py (Neo4j 4.1-compatible)
import re
from typing import Dict
from utils import get_driver, ollama_generate
from retrive import resolve_movie, resolve_person, one_hop_facts, two_hop_connection
from prompt_utils import pack_context   # <-- renamed from prompt.py to avoid package clash

def classify(q: str) -> str:
    ql = q.lower()
    if "how" in ql and ("connected" in ql or "relation" in ql or "path" in ql):
        return "connection"
    if any(w in ql for w in ["who", "cast", "director", "acted", "stars", "list"]):
        return "entity"
    return "entity"

def ask(question: str) -> Dict:
    driver = get_driver()
    plan_debug = {}
    try:
        with driver.session() as sess:
            mode = classify(question)
            plan_debug["mode"] = mode

            # pull quoted names/titles as candidates
            names = re.findall(r'"([^"]+)"', question)
            entities = []
            facts = []

            # resolve tokens to movies/people and gather one-hop facts
            for token in names[:2]:
                ms = sess.read_transaction(resolve_movie, token)
                if ms:
                    for m in ms[:1]:
                        entities.append(m)
                        facts += sess.read_transaction(one_hop_facts, m["id"], "Movie", 20)
                    continue
                ps = sess.read_transaction(resolve_person, token)
                if ps:
                    for p in ps[:1]:
                        entities.append(p)
                        facts += sess.read_transaction(one_hop_facts, p["id"], "Person", 20)

            # if it's a connection query and we have two resolved entities, compute 2-hop path facts
            # if mode == "connection" and len(entities) >= 2:
            #     a_id = entities[0]["id"]; b_id = entities[1]["id"]
            #     facts = sess.read_transaction(two_hop_connection, a_id, b_id, 1)

            # fallback: show a few movies if nothing resolved
            if not entities and not facts:
                popular = sess.run(
                    "MATCH (m:Movie) RETURN m.id AS id, m.title AS title, m.year AS year LIMIT 5"
                ).data()
                entities.extend(popular)
    finally:
        driver.close()

    if not facts and not entities:
        return {"answer": "Not enough data in the graph.", "citations": [], "plan_debug": plan_debug}

    ctx = pack_context(question, entities, facts)
    reply = ollama_generate(ctx, temperature=0.1)
    used = re.findall(r"\[F(\d+)\]", reply)
    return {"answer": reply, "citations": sorted(set(used)), "plan_debug": plan_debug}

if __name__ == "__main__":
    for q in [
        # 'Who directed "Interstellar"?'
        # ,
        # 'List main cast of "Inception".',
        # 'How is "Leonardo DiCaprio" connected to "Christopher Nolan"?',
        # 'Who directed "Kuch Kuch Hota Hai"?',
        'Chris Nolenan directed which movies?'
    ]:
        r = ask(q)
        print("\nQ:", q,
              "\nA:", r["answer"],
              "\nCitations:", r["citations"],
              "\nPlan:", r["plan_debug"])
