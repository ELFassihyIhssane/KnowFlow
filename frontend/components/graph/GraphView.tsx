"use client";

import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";

type GraphPayload = { nodes: any[]; edges: any[] } | null;

export function GraphView({ graph }: { graph: GraphPayload }) {
  if (!graph) {
    return (
      <div className="h-[600px] overflow-hidden rounded-2xl border border-white/10 bg-slate-950/60 p-6 text-slate-200">
        (no graph loaded)
      </div>
    );
  }

  const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph.edges) ? graph.edges : [];

  // ✅ Build a set of valid node ids
  const nodeIds = new Set(nodes.map((n: any) => String(n?.id)));

  // ✅ Filter out invalid edges (null endpoints or endpoints not in nodes)
  const safeEdges = edges.filter((e: any) => {
    const s = e?.source;
    const t = e?.target;
    if (s == null || t == null) return false;

    const ss = String(s);
    const tt = String(t);

    // reject "null"/"undefined" strings too
    if (ss === "null" || ss === "undefined" || tt === "null" || tt === "undefined") return false;

    return nodeIds.has(ss) && nodeIds.has(tt);
  });

  const droppedEdges = edges.length - safeEdges.length;

  const elements = [
    ...nodes.map((n: any) => ({
      data: {
        id: String(n.id),
        label: String(n.label ?? n.id),
        type: String(n.type ?? "Concept"),
      },
    })),
    ...safeEdges.map((e: any, i: number) => ({
      data: {
        id: String(e.id ?? `e-${i}`),
        source: String(e.source),
        target: String(e.target),
        label: String(e.relation ?? "rel"),
      },
    })),
  ];

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
      <div className="mb-3 flex items-center justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-slate-200">Knowledge Graph</div>
          <div className="text-xs text-slate-400">
            Tip: zoom with trackpad / wheel • drag nodes • hover edges to see relation
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            {nodes.length} nodes • {safeEdges.length} edges
            {droppedEdges > 0 ? ` • ${droppedEdges} invalid edges removed` : ""}
          </div>
        </div>
      </div>

      <div className="h-[650px] overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-slate-950 to-slate-900">
        <CytoscapeComponent
          elements={elements}
          style={{ width: "100%", height: "100%" }}
          layout={{
            name: "cose",
            animate: true,
            randomize: false,
            fit: true,
            padding: 40,
            nodeRepulsion: 9000,
            idealEdgeLength: 140,
            edgeElasticity: 0.2,
            gravity: 0.25,
          }}
          stylesheet={[
            {
              selector: "node",
              style: {
                "background-color": "#94B4C1",
                "border-color": "#EAE0CF",
                "border-width": 1,
                width: 38,
                height: 38,

                label: "data(label)",
                color: "#EAE0CF",
                "font-size": 12,
                "font-weight": 600,

                "text-valign": "center",
                "text-halign": "center",

                "text-wrap": "wrap",
                "text-max-width": 140,

                "text-background-color": "#213448",
                "text-background-opacity": 0.7,
                "text-background-padding": 3,
                "text-background-shape": "round-rectangle",
              },
            },

            {
              selector: 'node[type = "Paper"]',
              style: {
                "background-color": "#547792",
                shape: "round-rectangle",
                width: 56,
                height: 40,
              },
            },
            { selector: 'node[type = "Method"]', style: { "background-color": "#94B4C1", shape: "ellipse" } },
            { selector: 'node[type = "Problem"]', style: { "background-color": "#213448", shape: "diamond" } },
            { selector: 'node[type = "Experiment"]', style: { "background-color": "#EAE0CF", color: "#213448", shape: "hexagon" } },
            { selector: 'node[type = "Concept"]', style: { "background-color": "#6E8EA0", shape: "round-triangle" } },

            {
              selector: "edge",
              style: {
                width: 2,
                "line-color": "rgba(234,224,207,0.35)",
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "target-arrow-color": "rgba(234,224,207,0.45)",
                label: "",
                "font-size": 10,
                color: "#EAE0CF",
              },
            },

            {
              selector: "edge:hover",
              style: {
                label: "data(label)",
                width: 3,
                "line-color": "rgba(148,180,193,0.9)",
                "target-arrow-color": "rgba(148,180,193,0.9)",
                "text-background-color": "#213448",
                "text-background-opacity": 0.8,
                "text-background-padding": 3,
                "text-background-shape": "round-rectangle",
              },
            },

            { selector: "node:hover", style: { "border-width": 2, "border-color": "#94B4C1" } },
            { selector: "node:selected", style: { "border-width": 3, "border-color": "#EAE0CF" } },
          ]}
          cy={(cy: cytoscape.Core) => {
            cy.minZoom(0.35);
            cy.maxZoom(2.5);

            // ✅ Avoid duplicate handlers in dev / strict mode
            cy.removeAllListeners();

            // Prefer dblclick (always available). Keep dbltap if present.
            const fitAll = () => {
              cy.animate({ fit: { eles: cy.elements(), padding: 60 } }, { duration: 250 });
            };

            // @ts-ignore
            const hasDblTap = typeof (cy as any).on === "function";
            if (hasDblTap) {
              // some builds support dbltap
              try {
                // @ts-ignore
                cy.on("dbltap", fitAll);
              } catch {
                cy.on("dblclick", fitAll);
              }
            } else {
              cy.on("dblclick", fitAll);
            }
          }}
        />
      </div>
    </div>
  );
}
