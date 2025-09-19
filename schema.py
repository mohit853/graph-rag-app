from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel, Field

# Define the nodes (entities) in your graph
class Movie(BaseModel):
    """Movie entity."""
    title: str = Field(..., description="The title of the movie.")
    release_date: Optional[str] = Field(None, description="The release date of the movie.")
    genres: Optional[List[str]] = Field(None, description="The genres of the movie.")

class Person(BaseModel):
    """Person entity (actor, director, etc.)."""
    name: str = Field(..., description="The name of the person.")
    role: Optional[str] = Field(None, description="The role of the person in the movie (e.g., 'Actor', 'Director').")

# Define the relationships between the nodes
class ActedIn(BaseModel):
    """Represents a person acting in a movie."""
    source: Person = Field(..., description="The person who acted.")
    target: Movie = Field(..., description="The movie they acted in.")
    
class Directed(BaseModel):
    """Represents a person directing a movie."""
    source: Person = Field(..., description="The person who directed.")
    target: Movie = Field(..., description="The movie they directed.")