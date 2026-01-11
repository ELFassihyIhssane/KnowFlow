from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

from app.memory.knowledge_graph import get_knowledge_graph
from app.schemas.graph import GraphNode, GraphEdge, GraphView
from app.services.concept.concept_graph_service import normalize_label
from app.agents.concept_graph_agent import ConceptGraphAgent

agent = ConceptGraphAgent()

class UpdateRequest(BaseModel):
    text: str
    question: str = ""

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/full", response_model=GraphView)
def get_full_graph():
    kg = get_knowledge_graph()

    nodes = []
    for nid, attrs in kg.graph.nodes(data=True):
        nodes.append(
            GraphNode(
                id=nid,
                label=attrs.get("label", nid),
                type=attrs.get("type", "concept"),
                properties={k: v for k, v in attrs.items() if k not in {"label", "type"}}
            )
        )

    edges = []
    for u, v, k, attrs in kg.graph.edges(keys=True, data=True):
        props = dict(attrs)
        rel = props.pop("relation", "related_to")
        w = float(props.pop("weight", 1.0))

        edges.append(
            GraphEdge(
                source=u,
                target=v,
                relation=rel,
                weight=w,
                properties=props,  
            )
        )

    return GraphView(nodes=nodes, edges=edges)


@router.post("/subgraph", response_model=GraphView)
def get_subgraph(seeds: List[str], hops: int = 1):
    kg = get_knowledge_graph()
    seed_ids = [normalize_label(s) for s in seeds if s]
    sub = kg.neighbors_subgraph(seed_ids, hops=hops)

    nodes = []
    for nid, attrs in sub.nodes(data=True):
        nodes.append(
            GraphNode(
                id=nid,
                label=attrs.get("label", nid),
                type=attrs.get("type", "concept"),
                properties={k: v for k, v in attrs.items() if k not in {"label", "type"}}
            )
        )

    edges = []
    for u, v, k, attrs in sub.edges(keys=True, data=True):
        props = dict(attrs)
        rel = props.pop("relation", "related_to")
        w = float(props.pop("weight", 1.0))

        edges.append(
            GraphEdge(
                source=u,
                target=v,
                relation=rel,
                weight=w,
                properties=props,
            )
        )

    return GraphView(nodes=nodes, edges=edges)


@router.post("/update")
def update_graph(body: UpdateRequest):
    return agent.update_from_passages(
        passages_text=body.text,
        question=body.question,
        section_only=False,
        core_only=False,
    )
