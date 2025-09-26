# GraphRAG with Neo4j, TMDB API, and Ollama

This project demonstrates how to build a **Graph-based Retrieval-Augmented Generation (GraphRAG)** pipeline using **Neo4j**, data from the **TMDB API**, and an **on-premise LLM** for query answering.

## 🚀 Steps Implemented

1. **Data Ingestion**
   - Movie and cast data was pulled using the TMDB API.
   - Movies and their associated metadata (directors, actors) were ingested.

2. **Graph Construction in Neo4j**
   - Movies, actors, and directors were represented as nodes.
   - Relationships like `ACTED_IN` and `DIRECTED` were created to model connections.

3. **Query Processing with Similarity Search**
   - Natural language queries are resolved by first attempting exact matches.
   - If no exact match is found, **fuzzy string matching** (`fuzz.WRatio`) is used to identify the closest titles or names.

4. **Neighborhood Search for Answers**
   - Once the entity is matched, its 1-hop or 2-hop neighborhood is traversed in Neo4j.
   - Relevant facts are gathered and returned as structured answers.

5. **Citation Generation**
   - Each retrieved fact is assigned an **ID (F#)** for traceability.
   - Answers explicitly cite these facts, ensuring transparency and verifiability.

6. **On-Premise LLM with Ollama**
   - Used **Ollama with Llama 3.1.  
   - Ensures **data privacy** and **on-premise constraint compliance** by avoiding external API calls.



## 🛠️ Tech Stack

- **TMDB API** (data source)  
- **Neo4j** (graph database)  
- **Python** (data ingestion, query resolution, NLP similarity search)  
- **fuzzywuzzy (fuzz.WRatio)** (string similarity for query handling)  
- **Ollama with Llama 3.1 (8B)** (on-premise LLM for RAG answers)  

---

## 📑 Citations

- All answers reference supporting facts as **F#**, ensuring explainable outputs.

Outputs :
<img width="1441" height="610" alt="image" src="https://github.com/user-attachments/assets/5bd3341d-9f12-4db5-9d8b-b22054b5215d" />
<img width="1475" height="716" alt="image" src="https://github.com/user-attachments/assets/826185a1-6af6-453a-a822-5311fe69ad69" />



