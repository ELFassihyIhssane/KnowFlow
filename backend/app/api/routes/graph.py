from fastapi import APIRouter
from typing import List

from app.memory.knowledge_graph import get_knowledge_graph
from app.schemas.graph import GraphNode, GraphEdge, GraphView
from app.services.concept.concept_graph_service import normalize_label
from app.agents.concept_graph_agent import ConceptGraphAgent
from pydantic import BaseModel

agent = ConceptGraphAgent()

class UpdateRequest(BaseModel):
    text: str

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/full", response_model=GraphView)
def get_full_graph():
    kg = get_knowledge_graph()

    nodes = []
    for nid, attrs in kg.graph.nodes(data=True):
        nodes.append(GraphNode(id=nid, label=attrs.get("label", nid), type=attrs.get("type", "concept"), properties={}))

    edges = []
    for u, v, attrs in kg.graph.edges(data=True):
        edges.append(GraphEdge(source=u, target=v, relation=attrs.get("relation", "related_to"), weight=float(attrs.get("weight", 1.0)), properties={}))

    return GraphView(nodes=nodes, edges=edges)


@router.post("/subgraph", response_model=GraphView)
def get_subgraph(seeds: List[str], hops: int = 1):
    kg = get_knowledge_graph()
    seed_ids = [normalize_label(s) for s in seeds if s]
    sub = kg.neighbors_subgraph(seed_ids, hops=hops)

    nodes = []
    for nid, attrs in sub.nodes(data=True):
        nodes.append(GraphNode(id=nid, label=attrs.get("label", nid), type=attrs.get("type", "concept"), properties={}))

    edges = []
    for u, v, attrs in sub.edges(data=True):
        edges.append(GraphEdge(source=u, target=v, relation=attrs.get("relation", "related_to"), weight=float(attrs.get("weight", 1.0)), properties={}))

    return GraphView(nodes=nodes, edges=edges)

@router.post("/update")
def update_graph(body: UpdateRequest):
    return agent.update_from_passages(body.text)