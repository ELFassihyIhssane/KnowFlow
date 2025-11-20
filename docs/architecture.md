flowchart LR

    %% ===== UTILISATEUR ET UI =====
    U[👤 Utilisateur<br/>Question scientifique] -->|Envoie la question| UI[💻 Interface Web<br/>Next.js et React]

    UI -->|Transmet la requête| API[🧩 API Backend<br/>FastAPI]

    %% ===== ORCHESTRATEUR ET AGENTS =====
    API -->|Déclenche la pipeline intelligence| ORCH[🧠 Orchestrateur Multi Agents]

    subgraph ORCH_ZONE[🧠 Orchestrateur]
        direction TB
        ORCH
        
        ORCH -->|Analyse la demande| INTENT[🎯 Agent Intent<br/>Analyse d'intention]
        ORCH -->|Recherche les passages| RET[🔎 Agent Retriever<br/>Recherche sémantique]
        ORCH -->|Produit le résumé| SUM[📝 Agent Summarizer<br/>Résumé ciblé]
        ORCH -->|Extrait concepts et liens| CG[🕸️ Agent Graph<br/>Concepts et relations]
        ORCH -->|Fournit analyse avancée| INS[💡 Agent Insight<br/>Analyse profonde]
        ORCH -->|Vérifie la qualité| EVAL[✅ Agent Evaluator<br/>Contrôle qualité]
    end

    %% ===== MEMOIRE HYBRIDE =====
    ORCH -->|Accède et met à jour| MEM[🧠 Memory Layer<br/>Documents, Vecteurs, Knowledge Graph]
    MEM -->|Retourne passages et contexte| ORCH

    %% ===== COLLECTEUR EXTERNE =====
    EXT[🌐 Agent Collecteur<br/>APIs scientifiques] -->|Ajoute nouveaux papiers et embeddings| MEM

    %% ===== ADAPTATION ET OBSERVABILITE =====
    ORCH -->|Ajuste la stratégie| ADAPT[⚙️ Couche Adaptation<br/>Règles et ML léger]
    ORCH -->|Génère traces et métriques| OBS[📊 Observabilité<br/>Logs et mesures]

    %% ===== REPONSE ET AFFICHAGE =====
    ORCH -->|Produit réponse structurée| RESP[📦 Réponse finale<br/>Texte, sources, graphe]

    RESP -->|Affiche le résultat| UI

    UI -->|Affichage complet| VIEW[🖼️ Visualisation<br/>Réponse, sources, graphe]

    %% ===== STYLES =====
    classDef userNode fill:#FFEBEE,stroke:#E53935,stroke-width:1px,rx:18,ry:18;
    classDef frontNode fill:#E8F5E9,stroke:#43A047,stroke-width:1px,rx:18,ry:18;
    classDef coreNode fill:#FFF3E0,stroke:#FB8C00,stroke-width:1px,rx:18,ry:18;
    classDef agentNode fill:#EDE7F6,stroke:#7E57C2,stroke-width:1px,rx:18,ry:18;
    classDef memoryNode fill:#E3F2FD,stroke:#1E88E5,stroke-width:1px,rx:18,ry:18;

    class U userNode;
    class UI,API,VIEW frontNode;
    class ORCH,ADAPT,OBS,RESP coreNode;
    class INTENT,RET,SUM,CG,INS,EVAL agentNode;
    class MEM,EXT memoryNode;
