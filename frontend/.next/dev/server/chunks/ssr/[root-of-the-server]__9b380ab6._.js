module.exports = [
"[externals]/util [external] (util, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("util", () => require("util"));

module.exports = mod;
}),
"[externals]/stream [external] (stream, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("stream", () => require("stream"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[externals]/http [external] (http, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http", () => require("http"));

module.exports = mod;
}),
"[externals]/https [external] (https, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("https", () => require("https"));

module.exports = mod;
}),
"[externals]/url [external] (url, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("url", () => require("url"));

module.exports = mod;
}),
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/crypto [external] (crypto, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("crypto", () => require("crypto"));

module.exports = mod;
}),
"[externals]/http2 [external] (http2, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http2", () => require("http2"));

module.exports = mod;
}),
"[externals]/assert [external] (assert, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("assert", () => require("assert"));

module.exports = mod;
}),
"[externals]/zlib [external] (zlib, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("zlib", () => require("zlib"));

module.exports = mod;
}),
"[externals]/events [external] (events, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("events", () => require("events"));

module.exports = mod;
}),
"[project]/lib/api-client.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "fetchGraph",
    ()=>fetchGraph,
    "runQuery",
    ()=>runQuery
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/axios/lib/axios.js [app-ssr] (ecmascript)");
;
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:7000";
async function runQuery(question) {
    const { data } = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post(`${API_BASE}/api/query`, {
        question
    });
    return data;
}
async function fetchGraph() {
    const { data } = await __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get(`${API_BASE}/api/graph/full`);
    return data;
}
}),
"[project]/components/graph/GraphView.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GraphView",
    ()=>GraphView
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$cytoscapejs$2f$dist$2f$react$2d$cytoscape$2e$modern$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react-cytoscapejs/dist/react-cytoscape.modern.js [app-ssr] (ecmascript)");
"use client";
;
;
function GraphView({ graph }) {
    if (!graph) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "h-[600px] overflow-hidden rounded-2xl border border-white/10 bg-slate-950/60 p-6 text-slate-200",
            children: "(no graph loaded)"
        }, void 0, false, {
            fileName: "[project]/components/graph/GraphView.tsx",
            lineNumber: 11,
            columnNumber: 7
        }, this);
    }
    const elements = [
        ...(graph.nodes || []).map((n)=>({
                data: {
                    id: String(n.id),
                    label: String(n.label ?? n.id),
                    type: String(n.type ?? "Concept")
                }
            })),
        ...(graph.edges || []).map((e, i)=>({
                data: {
                    id: String(e.id ?? `e-${i}`),
                    source: String(e.source),
                    target: String(e.target),
                    label: String(e.relation ?? "rel")
                }
            }))
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-2xl border border-white/10 bg-slate-950/40 p-4",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mb-3 flex items-center justify-between",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "text-sm font-semibold text-slate-200",
                            children: "Knowledge Graph"
                        }, void 0, false, {
                            fileName: "[project]/components/graph/GraphView.tsx",
                            lineNumber: 41,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "text-xs text-slate-400",
                            children: "Tip: zoom with trackpad / wheel • drag nodes • hover edges to see relation"
                        }, void 0, false, {
                            fileName: "[project]/components/graph/GraphView.tsx",
                            lineNumber: 42,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/graph/GraphView.tsx",
                    lineNumber: 40,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/graph/GraphView.tsx",
                lineNumber: 39,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "h-[650px] overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-slate-950 to-slate-900",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2d$cytoscapejs$2f$dist$2f$react$2d$cytoscape$2e$modern$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                    elements: elements,
                    style: {
                        width: "100%",
                        height: "100%"
                    },
                    layout: {
                        // Layout “stable” et lisible (force-directed)
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
                        // =========================
                        // Base Node Style (lisible)
                        // =========================
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
                                // ✅ évite les énormes phrases
                                "text-wrap": "wrap",
                                "text-max-width": 140,
                                // ✅ lisibilité (halo autour du texte)
                                "text-background-color": "#213448",
                                "text-background-opacity": 0.7,
                                "text-background-padding": 3,
                                "text-background-shape": "round-rectangle"
                            }
                        },
                        // =========================
                        // Node Types (palette)
                        // =========================
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
                        // =========================
                        // Edge Style (moins de bruit)
                        // =========================
                        {
                            selector: "edge",
                            style: {
                                width: 2,
                                "line-color": "rgba(234,224,207,0.35)",
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                                "target-arrow-color": "rgba(234,224,207,0.45)",
                                // 🚫 pas de label par défaut (sinon illisible)
                                label: "",
                                "font-size": 10,
                                color: "#EAE0CF"
                            }
                        },
                        // ✅ relation visible uniquement au hover
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
                        // =========================
                        // Hover Node (feedback)
                        // =========================
                        {
                            selector: "node:hover",
                            style: {
                                "border-width": 2,
                                "border-color": "#94B4C1"
                            }
                        },
                        // =========================
                        // Selected Node (debug)
                        // =========================
                        {
                            selector: "node:selected",
                            style: {
                                "border-width": 3,
                                "border-color": "#EAE0CF"
                            }
                        }
                    ],
                    cy: (cy)=>{
                        // interactions smooth + defaults
                        cy.minZoom(0.35);
                        cy.maxZoom(2.5);
                        // double click = fit
                        cy.on("dbltap", ()=>{
                            cy.animate({
                                fit: {
                                    eles: cy.elements(),
                                    padding: 60
                                }
                            }, {
                                duration: 250
                            });
                        });
                    }
                }, void 0, false, {
                    fileName: "[project]/components/graph/GraphView.tsx",
                    lineNumber: 49,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/graph/GraphView.tsx",
                lineNumber: 48,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/graph/GraphView.tsx",
        lineNumber: 38,
        columnNumber: 5
    }, this);
}
}),
"[project]/app/graph/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>GraphPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api-client.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$graph$2f$GraphView$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/graph/GraphView.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
function GraphPage() {
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [graph, setGraph] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    async function load() {
        setLoading(true);
        setError(null);
        try {
            const g = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2d$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["fetchGraph"])();
            setGraph(g);
        } catch (e) {
            setError(e?.message || "Graph endpoint not available");
        } finally{
            setLoading(false);
        }
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        className: "mx-auto max-w-6xl p-6",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                className: "text-2xl font-semibold",
                children: "Knowledge Graph"
            }, void 0, false, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 27,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-1 text-zinc-300",
                children: "Cytoscape view of the KG (requires backend /api/graph)."
            }, void 0, false, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 28,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-4 flex items-center gap-3",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: load,
                        className: "rounded-lg bg-zinc-800 px-4 py-2 hover:bg-zinc-700 disabled:opacity-60",
                        disabled: loading,
                        children: loading ? "Loading..." : "Load graph"
                    }, void 0, false, {
                        fileName: "[project]/app/graph/page.tsx",
                        lineNumber: 33,
                        columnNumber: 9
                    }, this),
                    error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "text-red-300",
                        children: error
                    }, void 0, false, {
                        fileName: "[project]/app/graph/page.tsx",
                        lineNumber: 40,
                        columnNumber: 19
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 32,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-6",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$graph$2f$GraphView$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["GraphView"], {
                    graph: graph
                }, void 0, false, {
                    fileName: "[project]/app/graph/page.tsx",
                    lineNumber: 44,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/graph/page.tsx",
                lineNumber: 43,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/graph/page.tsx",
        lineNumber: 26,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__9b380ab6._.js.map