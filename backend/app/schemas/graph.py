# app/schemas/graph.py
from typing import Dict, List
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    label: str
    type: str = "concept"
    properties: Dict[str, object] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: Dict[str, object] = Field(default_factory=dict)


class GraphUpdateResult(BaseModel):
    nodes_added: int = 0
    edges_added: int = 0
    merged_nodes: int = 0
    extracted_concepts: List[str] = Field(default_factory=list)
    extracted_edges: List[GraphEdge] = Field(default_factory=list)


class GraphView(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
