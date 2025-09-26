from datetime import datetime
from typing import Dict
from utils import get_driver, tmdb_get

# Tiny seed set for the POC (you can expand later)
SEED_LIST_IDS = [27205, 157336, 49026, 550, 424, 603]  # Inception, Interstellar, The Dark Knight, Fight Club, Schindler's List, The Matrix

def upsert_movie(tx, m: Dict):
    tx.run(
        """
        MERGE (x:Movie {id: $id})
          ON CREATE SET x.title=$title, x.year=$year, x.fetched_at=$fetched_at, x.source='TMDb'
          ON MATCH  SET x.title=$title, x.year=$year, x.fetched_at=$fetched_at
        """,
        **m
    )

def upsert_person(tx, p: Dict):
    tx.run(
        """
        MERGE (x:Person {id: $id})
          ON CREATE SET x.name=$name, x.fetched_at=$fetched_at, x.source='TMDb'
          ON MATCH  SET x.name=$name, x.fetched_at=$fetched_at
        """,
        **p
    )

def relate_acted_in(tx, pid: int, mid: int, order: int, now_iso: str):
    tx.run(
        """
        MATCH (p:Person {id:$pid}), (m:Movie {id:$mid})
        MERGE (p)-[r:ACTED_IN]->(m)
          ON CREATE SET r.cast_order=$order, r.fetched_at=$now, r.source='TMDb'
          ON MATCH  SET r.cast_order=$order, r.fetched_at=$now
        """,
        pid=pid, mid=mid, order=order, now=now_iso
    )

def relate_directed(tx, pid: int, mid: int, now_iso: str):
    tx.run(
        """
        MATCH (p:Person {id:$pid}), (m:Movie {id:$mid})
        MERGE (p)-[r:DIRECTED]->(m)
          ON CREATE SET r.fetched_at=$now, r.source='TMDb'
          ON MATCH  SET r.fetched_at=$now
        """,
        pid=pid, mid=mid, now=now_iso
    )

def fetch_movie(mid: int) -> Dict:
    m = tmdb_get(f"/movie/{mid}")
    return {
        "id": m["id"],
        "title": m["title"],
        "year": int(m["release_date"][:4]) if m.get("release_date") else None,
        "fetched_at": datetime.utcnow().isoformat()
    }

def fetch_credits(mid: int):
    return tmdb_get(f"/movie/{mid}/credits")

def main():
    driver = get_driver()
    now_iso = datetime.utcnow().isoformat()

    with driver.session() as sess:
        for mid in SEED_LIST_IDS:
            movie = fetch_movie(mid)
            creds = fetch_credits(mid)

            sess.write_transaction(upsert_movie, movie)

            # Directors
            for c in creds.get("crew", []):
             
                if c.get("job") == "Director":
                    person = {"id": c["id"], "name": c["name"], "fetched_at": now_iso}
                    sess.write_transaction(upsert_person, person)
                    sess.write_transaction(relate_directed, person["id"], movie["id"], now_iso)

            # Top 10 cast
            for cast in creds.get("cast", [])[:10]:
                person = {"id": cast["id"], "name": cast["name"], "fetched_at": now_iso}
                sess.write_transaction(upsert_person, person)
                order = cast.get("order", 9999)
                sess.write_transaction(relate_acted_in, person["id"], movie["id"], order, now_iso)

    driver.close()
    print("Ingest complete for Neo4j 4.1.")

if __name__ == "__main__":
    main()
