from typing import Dict, List, Tuple
from rapidfuzz import fuzz, process
from utils import get_driver

def resolve_movie(tx, title: str) -> List[Dict]:
    # Exact first, then fuzzy
    exact = tx.run("MATCH (m:Movie) WHERE toLower(m.title)=toLower($t) RETURN m.id AS id, m.title AS title, m.year AS year", t=title).data()
    if exact: return exact
    candidates = tx.run("MATCH (m:Movie) RETURN m.id AS id, m.title AS title, m.year AS year").data()
    choices = [(c["title"], c) for c in candidates]
    best = process.extract(title, [c[0] for c in choices], scorer=fuzz.WRatio, limit=3)
    out=[]
    for name, score, idx in best:
        c = choices[idx][1]
        if score >= 80:
            out.append(c)
    return out
# Fuzzy matching for people is trickier due to name collisions, so we return multiple candidates
def resolve_person(tx, name: str) -> List[Dict]:
    exact = tx.run("MATCH (p:Person) WHERE toLower(p.name)=toLower($n) RETURN p.id AS id, p.name AS name", n=name).data()
    if exact: return exact
    candidates = tx.run("MATCH (p:Person) RETURN p.id AS id, p.name AS name").data()
    choices = [(c["name"], c) for c in candidates]
    best = process.extract(name, [c[0] for c in choices], scorer=fuzz.WRatio, limit=3)
    out=[]
    for nm, score, idx in best:
        c = choices[idx][1]
        if score >= 80:
            out.append(c)
    return out
# Gather one-hop facts for a given node (movie or person) we find only 2 types of relations for simplicity like directed/acted_in we limit that to top 20 results
def one_hop_facts(tx, node_id: int, node_label: str, cap: int = 20) -> List[Dict]:
    if node_label == "Movie":
        q = (
            "MATCH (p:Person)-[r:ACTED_IN]->(m:Movie {id:$id}) "
            "RETURN 'fact' AS kind, p.name AS subj, 'ACTED_IN' AS rel, m.title AS obj, r.fetched_at AS fetched_at, 'p->m' AS dir "
            "UNION ALL "
            "MATCH (p:Person)-[r:DIRECTED]->(m:Movie {id:$id}) "
            "RETURN 'fact' AS kind, p.name AS subj, 'DIRECTED' AS rel, m.title AS obj, r.fetched_at AS fetched_at, 'p->m' AS dir "
            "LIMIT $cap"
        )
    else:  # Person
        q = (
            "MATCH (p:Person {id:$id})-[r:ACTED_IN]->(m:Movie) "
            "RETURN 'fact' AS kind, p.name AS subj, 'ACTED_IN' AS rel, m.title AS obj, r.fetched_at AS fetched_at, 'p->m' AS dir "
            "UNION ALL "
            "MATCH (p:Person {id:$id})-[r:DIRECTED]->(m:Movie) "
            "RETURN 'fact' AS kind, p.name AS subj, 'DIRECTED' AS rel, m.title AS obj, r.fetched_at AS fetched_at, 'p->m' AS dir "
            "LIMIT $cap"
        )
    return tx.run(q, id=node_id, cap=cap).data()



def two_hop_connection(tx, a_id: int, b_id: int, cap_paths: int = 3) -> List[Dict]:
    q = """
    MATCH (a {id:$a_id}), (b {id:$b_id}),
          p = shortestPath((a)-[*..2]-(b))
    RETURN p LIMIT $cap
    """
    rows = tx.run(q, a_id=a_id, b_id=b_id, cap=cap_paths)
    facts=[]
    for r in rows:
        path = r["p"]
        # Flatten into facts like subj -[type]-> obj
        for rel in path.relationships:
            start = path.nodes[rel.start_node.id]["name"] if "name" in path.nodes[rel.start_node.id] else path.nodes[rel.start_node.id].get("title")
            end   = path.nodes[rel.end_node.id]["name"]   if "name" in path.nodes[rel.end_node.id] else path.nodes[rel.end_node.id].get("title")
            facts.append({"kind":"fact","subj":start,"rel":type(rel).__name__.upper(),"obj":end,"fetched_at":rel.get("fetched_at"),"dir":"?"})
    return facts
