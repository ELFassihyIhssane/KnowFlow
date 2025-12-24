(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/lib/api-client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "fetchGraph",
    ()=>fetchGraph,
    "retryQuery",
    ()=>retryQuery,
    "runQuery",
    ()=>runQuery
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/axios/lib/axios.js [app-client] (ecmascript)");
;
const API_BASE = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:7000";
async function runQuery(question) {
    const { data } = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].post(`${API_BASE}/api/query`, {
        question
    });
    return data;
}
async function retryQuery(question, retry_count, adaptation_actions) {
    const { data } = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].post(`${API_BASE}/api/query/retry`, {
        question,
        retry_count,
        adaptation_actions
    });
    return data;
}
async function fetchGraph() {
    const { data } = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].get(`${API_BASE}/api/graph/full`);
    return data;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/graph/GraphView.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GraphView",
    ()=>GraphView
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$cytoscapejs$2f$dist$2f$react$2d$cytoscape$2e$modern$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react-cytoscapejs/dist/react-cytoscape.modern.js [app-client] (ecmascript)");
"use client";
;
;
function GraphView({ graph }) {
    if (!graph) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "h-[600px] overflow-hidden rounded-2xl border border-white/10 bg-slate-950/60 p-6 text-slate-200",
            children: "(no graph loaded)"
        }, void 0, false, {
            fileName: "[project]/components/graph/GraphView.tsx",
            lineNumber: 11,
            columnNumber: 7
        }, this);
    }
    const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
    const edges = Array.isArray(graph.edges) ? graph.edges : [];
    // ✅ Build a set of valid node ids
    const nodeIds = new Set(nodes.map((n)=>String(n?.id)));
    // ✅ Filter out invalid edges (null endpoints or endpoints not in nodes)
    const safeEdges = edges.filter((e)=>{
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
        ...nodes.map((n)=>({
                data: {
                    id: String(n.id),
                    label: String(n.label ?? n.id),
                    type: String(n.type ?? "Concept")
                }
            })),
        ...safeEdges.map((e, i)=>({
                data: {
                    id: String(e.id ?? `e-${i}`),
                    source: String(e.source),
                    target: String(e.target),
                    label: String(e.relation ?? "rel")
                }
            }))
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-2xl border border-white/10 bg-slate-950/40 p-4",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mb-3 flex items-center justify-between gap-4",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "text-sm font-semibold text-slate-200",
                            children: "Knowledge Graph"
                        }, void 0, false, {
                            fileName: "[project]/components/graph/GraphView.tsx",
                            lineNumber: 62,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "text-xs text-slate-400",
                            children: "Tip: zoom with trackpad / wheel • drag nodes • hover edges to see relation"
                        }, void 0, false, {
                            fileName: "[project]/components/graph/GraphView.tsx",
                            lineNumber: 63,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "mt-1 text-[11px] text-slate-500",
                            children: [
                                nodes.length,
                                " nodes • ",
                                safeEdges.length,
                                " edges",
                                droppedEdges > 0 ? ` • ${droppedEdges} invalid edges removed` : ""
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/graph/GraphView.tsx",
                            lineNumber: 66,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/graph/GraphView.tsx",
                    lineNumber: 61,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/graph/GraphView.tsx",
                lineNumber: 60,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "h-[650px] overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-slate-950 to-slate-900",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$cytoscapejs$2f$dist$2f$react$2d$cytoscape$2e$modern$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                    elements: elements,
                    style: {
                        width: "100%",
                        height: "100%"
                    },
                    layout: {
                        name: "cose",
                        animate: true,
                        randomize: false,
                        fit: true,
                        padding: 40,
                        nodeRepulsion: 9000,
                        idealEdgeLength: 140,
                        edgeElasticity: 0.2,
                        gravity: 0.25
                    },
                    stylesheet: [
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
                                "text-background-shape": "round-rectangle"
                            }
                        },
                        {
                            selector: 'node[type = "Paper"]',
                            style: {
                                "background-color": "#547792",
                                shape: "round-rectangle",
                                width: 56,
                                height: 40
                            }
                        },
                        {
                            selector: 'node[type = "Method"]',
                            style: {
                                "background-color": "#94B4C1",
                                shape: "ellipse"
                            }
                        },
                        {
                            selector: 'node[type = "Problem"]',
                            style: {
                                "background-color": "#213448",
                                shape: "diamond"
                            }
                        },
                        {
                            selector: 'node[type = "Experiment"]',
                            style: {
                                "background-color": "#EAE0CF",
                                color: "#213448",
                                shape: "hexagon"
                            }
                        },
                        {
                            selector: 'node[type = "Concept"]',
                            style: {
                                "background-color": "#6E8EA0",
                                shape: "round-triangle"
                            }
                        },
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
                                color: "#EAE0CF"
                            }
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
                                "text-background-shape": "round-rectangle"
                            }
                        },
                        {
                            selector: "node:hover",
                            style: {
                                "border-width": 2,
                                "border-color": "#94B4C1"
                            }
                        },
                        {
                            selector: "node:selected",
                            style: {
                                "border-width": 3,
                                "border-color": "#EAE0CF"
                            }
                        }
                    ],
                    cy: (cy)=>{
                        cy.minZoom(0.35);
                        cy.maxZoom(2.5);
                        // ✅ Avoid duplicate handlers in dev / strict mode
                        cy.removeAllListeners();
                        // Prefer dblclick (always available). Keep dbltap if present.
                        const fitAll = ()=>{
                            cy.animate({
                                fit: {
                                    eles: cy.elements(),
                                    padding: 60
                                }
                            }, {
                                duration: 250
                            });
                        };
                        // @ts-ignore
                        const hasDblTap = typeof cy.on === "function";
                        if (hasDblTap) {
                            // some builds support dbltap
                            try {
                                // @ts-ignore
                                cy.on("dbltap", fitAll);
                            } catch  {
                                cy.on("dblclick", fitAll);
                            }
                        } else {
                            cy.on("dblclick", fitAll);
                        }
                    }
                }, void 0, false, {
                    fileName: "[project]/components/graph/GraphView.tsx",
                    lineNumber: 74,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/graph/GraphView.tsx",
                lineNumber: 73,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/graph/GraphView.tsx",
        lineNumber: 59,
        columnNumber: 5
    }, this);
}
_c = GraphView;
var _c;
__turbopack_context__.k.register(_c, "GraphView");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/graph/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>GraphPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api-client.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$graph$2f$GraphView$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/graph/GraphView.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function GraphPage() {
    _s();
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [graph, setGraph] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    // 🔼 Scroll button state
    const [showScrollTop, setShowScrollTop] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [scrollProgress, setScrollProgress] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    async function load() {
        setLoading(true);
        setError(null);
        try {
            const g = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["fetchGraph"])();
            setGraph(g);
        } catch (e) {
            setError(e?.message || "Graph endpoint not available");
        } finally{
            setLoading(false);
        }
    }
    // 👇 Detect scroll + progress
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "GraphPage.useEffect": ()=>{
            function onScroll() {
                const y = window.scrollY || 0;
                const doc = document.documentElement;
                const max = Math.max(1, doc.scrollHeight - doc.clientHeight);
                const p = Math.min(1, Math.max(0, y / max));
                setScrollProgress(p);
                setShowScrollTop(y > 300);
            }
            onScroll();
            window.addEventListener("scroll", onScroll, {
                passive: true
            });
            return ({
                "GraphPage.useEffect": ()=>window.removeEventListener("scroll", onScroll)
            })["GraphPage.useEffect"];
        }
    }["GraphPage.useEffect"], []);
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
    // Progress ring math
    const ring = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "GraphPage.useMemo[ring]": ()=>{
            const size = 48;
            const stroke = 3;
            const r = (size - stroke) / 2;
            const c = 2 * Math.PI * r;
            const dash = c * (1 - scrollProgress);
            return {
                size,
                stroke,
                r,
                c,
                dash
            };
        }
    }["GraphPage.useMemo[ring]"], [
        scrollProgress
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        className: "relative mx-auto max-w-6xl p-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                className: "text-2xl font-semibold",
                children: "Knowledge Graph"
            }, void 0, false, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 62,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-4 flex items-center gap-3",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: load,
                        className: "rounded-lg bg-zinc-800 px-4 py-2 hover:bg-zinc-700 disabled:opacity-60",
                        disabled: loading,
                        children: loading ? "Loading..." : "Load graph"
                    }, void 0, false, {
                        fileName: "[project]/app/graph/page.tsx",
                        lineNumber: 65,
                        columnNumber: 9
                    }, this),
                    error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-red-300",
                        children: error
                    }, void 0, false, {
                        fileName: "[project]/app/graph/page.tsx",
                        lineNumber: 72,
                        columnNumber: 19
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 64,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-6",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$graph$2f$GraphView$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["GraphView"], {
                    graph: graph
                }, void 0, false, {
                    fileName: "[project]/app/graph/page.tsx",
                    lineNumber: 76,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 75,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: [
                    "fixed bottom-6 right-6 z-50",
                    "transition-all duration-300",
                    showScrollTop ? "opacity-100 translate-y-0" : "pointer-events-none opacity-0 translate-y-3"
                ].join(" "),
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    onClick: scrollToTop,
                    "aria-label": "Scroll to top",
                    className: [
                        "group relative grid h-12 w-12 place-items-center rounded-full",
                        "border border-white/15 bg-white/10 backdrop-blur-xl",
                        "shadow-[0_10px_30px_-12px_rgba(0,0,0,0.6)]",
                        "transition-transform duration-300 hover:scale-110 active:scale-95",
                        "focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-beige/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40"
                    ].join(" "),
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            className: [
                                "absolute -inset-2 rounded-full opacity-0 blur-xl transition-opacity duration-300",
                                "bg-brand-beige/30",
                                "group-hover:opacity-100"
                            ].join(" ")
                        }, void 0, false, {
                            fileName: "[project]/app/graph/page.tsx",
                            lineNumber: 101,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                            width: ring.size,
                            height: ring.size,
                            viewBox: `0 0 ${ring.size} ${ring.size}`,
                            className: "absolute inset-0",
                            "aria-hidden": "true",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("circle", {
                                    cx: ring.size / 2,
                                    cy: ring.size / 2,
                                    r: ring.r,
                                    fill: "none",
                                    stroke: "rgba(255,255,255,0.14)",
                                    strokeWidth: ring.stroke
                                }, void 0, false, {
                                    fileName: "[project]/app/graph/page.tsx",
                                    lineNumber: 117,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("circle", {
                                    cx: ring.size / 2,
                                    cy: ring.size / 2,
                                    r: ring.r,
                                    fill: "none",
                                    stroke: "currentColor",
                                    className: "text-brand-beige",
                                    strokeWidth: ring.stroke,
                                    strokeLinecap: "round",
                                    strokeDasharray: ring.c,
                                    strokeDashoffset: ring.dash,
                                    transform: `rotate(-90 ${ring.size / 2} ${ring.size / 2})`
                                }, void 0, false, {
                                    fileName: "[project]/app/graph/page.tsx",
                                    lineNumber: 125,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/graph/page.tsx",
                            lineNumber: 110,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                            width: "20",
                            height: "20",
                            viewBox: "0 0 24 24",
                            fill: "none",
                            className: "relative text-brand-beige transition-transform duration-300 group-hover:-translate-y-0.5",
                            "aria-hidden": "true",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("path", {
                                d: "M12 5l-7 7m7-7l7 7M12 5v14",
                                stroke: "currentColor",
                                strokeWidth: "2",
                                strokeLinecap: "round",
                                strokeLinejoin: "round"
                            }, void 0, false, {
                                fileName: "[project]/app/graph/page.tsx",
                                lineNumber: 149,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/app/graph/page.tsx",
                            lineNumber: 141,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/graph/page.tsx",
                    lineNumber: 89,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 80,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/graph/page.tsx",
        lineNumber: 61,
        columnNumber: 5
    }, this);
}
_s(GraphPage, "PJnyxbZzCjHFrhvu74sVUrMaC4k=");
_c = GraphPage;
var _c;
__turbopack_context__.k.register(_c, "GraphPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_7ccf998d._.js.map