import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from dotenv import load_dotenv

# Load API keys from your .env file
load_dotenv()

# --- Your data fetching function here (from previous step) ---
def fetch_movie_and_credits(movie_id):
    # This function should be the one you got working
    # It returns a tuple of movie_details, movie_credits
    ...

# --- Your Pydantic schemas here (from step 1) ---
from schema import Movie, Person, ActedIn, Directed

if __name__ == "__main__":
    # Initialize the LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    llm_transformer = LLMGraphTransformer(llm=llm)

    # Fetch the raw JSON data
    movie_details, movie_credits = fetch_movie_and_credits(27205) # Example: Inception
    
    # Combine the data for the LLM to process
    full_data = {
        "movie_details": movie_details,
        "movie_credits": movie_credits
    }
    
    # Convert the raw data to a LangChain Document
    doc = Document(page_content=json.dumps(full_data))

    # Transform the document into a knowledge graph
    graph_documents = llm_transformer.convert_to_graph_documents([doc])

    # Now, inspect the output
    print("--- Extracted Graph Documents ---")
    for gd in graph_documents:
        print(f"Nodes: {gd.nodes}")
        print(f"Relationships: {gd.relationships}")
        print("-" * 20)

    # You'll get a list of nodes and relationships, like this:
    # Nodes: [Node(id='Inception', type='Movie'), Node(id='Christopher Nolan', type='Person')]
    # Relationships: [Relationship(source=Node(id='Christopher Nolan', type='Person'), target=Node(id='Inception', type='Movie'), type='DIRECTED')]

    # The next step would be to save these to a graph database like Neo4j.