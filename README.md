# KnowFlow – Adaptive Knowledge-Driven Multi-Agent Orchestrator

KnowFlow est une plateforme intelligente qui **analyse automatiquement des connaissances scientifiques** à l’aide d’un **orchestrateur multi-agents** et d’une **mémoire hybride** (Vector Store + Knowledge Graph).

L’objectif principal :

- comparer des approches scientifiques  
- résumer des articles  
- expliquer des concepts  
- extraire des relations et “gaps” de recherche  

…tout en restant **traçable, contrôlé, transparent et explicable**.

---

## ✨ Vue d’ensemble de l’architecture

KnowFlow est composé de plusieurs briques principales :

- 🧠 **Orchestrateur central**  
  Qui choisit et combine dynamiquement les agents nécessaires à une requête.

- 🤖 **Agents spécialisés**  
  - Intent & Decomposition  
  - External API Data Collector  
  - Retriever  
  - Summarizer  
  - Concept & Graph  
  - Insight  
  - Evaluator  

- 🧬 **Mémoire hybride AI**  
  - **Vector Store** pour la recherche sémantique  
  - **Knowledge Graph** pour les concepts et relations

- 🎯 **Couche d’adaptation**  
  Règles + ML léger pour adapter la pipeline (quel agent activer, contexte, modèle, etc.).

- 💻 **Interface Web**  
  Affiche la réponse, les sources, les extraits utilisés, le graphe de connaissances et la timeline des agents.

---

## 🎯 Objectifs du projet

- Automatiser l’analyse de littérature scientifique
- Offrir des résumés ciblés et comparatifs
- Extraire les concepts clés et leurs relations
- Détecter contradictions, limites et pistes futures
- Assurer la traçabilité : *“quelle réponse vient de quels documents et de quels agents ?”*

---

## 🧩 Composants & Technologies

### 🔵 A. Interface Web (User Interaction Layer)

**Technos :**

- Next.js (React) – framework moderne côté front
- React – interface dynamique
- Tailwind CSS – design rapide et propre
- Cytoscape.js – affichage interactif du Knowledge Graph
- Axios / Fetch – communication avec l’API FastAPI

**Rôle :**

- L’utilisateur pose des questions
- L’UI envoie la requête au backend (`/query`)
- L’UI affiche :
  - la réponse textuelle
  - les sources + extraits utilisés
  - la liste des agents activés
  - le Knowledge Graph associé à la réponse

---

### 🔵 B. Orchestrateur (FastAPI + LangGraph/CrewAI)

**Technos :**

- FastAPI – API backend
- LangGraph ou CrewAI – orchestrateur multi-agents
- Python – logique métier et orchestration
- Pydantic – validation des schémas d’entrée/sortie

**Rôle :**

- Comprendre la requête de l’utilisateur
- Appeler l’**Intent & Decomposition Agent**
- Choisir dynamiquement quels agents activer
- Construire le contexte pour chaque agent (passages, concepts…)
- Combiner les sorties des agents
- Produire et renvoyer la réponse finale à l’UI

---

## 🤖 Agents spécialisés

### 🟣 1. Intent & Decomposition Agent

**Technos :**

- LLM local via Ollama (Llama 3, Mistral 7B…)
- HuggingFace Transformers
- (Optionnel) scikit-learn pour classifier les intentions

**Rôle :**

- Identifier le type de tâche :
  - résumé
  - comparaison
  - explication
  - gap analysis
  - analyse conceptuelle
- Décomposer la question en sous-tâches pour l’orchestrateur

---

### 🟡 2. External API Data Collector Agent

**Technos :**

- Requests / httpx
- API arXiv, Semantic Scholar, etc.
- PyPDF2 / pdfminer pour l’extraction de texte
- Tâches asynchrones FastAPI

**Rôle :**

- Télécharger de nouveaux articles
- Extraire le texte et stocker dans le **Document Store**
- Générer les embeddings → **Vector Store**
- (Optionnel) Envoyer des passages au Concept & Graph Agent

> C’est un agent **d’ingestion de données**, pas un agent de raisonnement.

---

### 🟠 3. Retriever Agent

**Technos :**

- Sentence-Transformers – génération d’embeddings
- Qdrant **ou** ChromaDB – Vector Store
- (Optionnel) FAISS – alternative locale

**Rôle :**

- Exécuter la recherche sémantique
- Retourner les passages les plus pertinents
- Alimenter :
  - Summarizer Agent
  - Concept & Graph Agent
  - Insight Agent

---

### 🟢 4. Summarizer Agent

**Technos :**

- LLM (Ollama, modèles instruct)
- Transformers (T5, Llama-3 instruct…)
- Prompt engineering

**Rôle :**

- Produire :
  - résumés ciblés
  - résumés comparatifs
  - résumés explicatifs
- Nettoyer le texte en entrée du Concept & Graph Agent si nécessaire

---

### 🟩 5. Concept & Graph Agent

**Technos :**

- spaCy + Transformers – NER et extraction de relations
- NetworkX – gestion locale du graphe
- (Optionnel) Neo4j – base graphe plus avancée
- LLM pour structurer les relations

**Rôle :**

- Extraire des concepts à partir :
  - des passages du Retriever
  - des résumés du Summarizer
  - des nouveaux papiers collectés par API
- Identifier des relations :
  - `utilise`, `améliore`, `dépend de`, `surpasse`, …
- Mettre à jour le Knowledge Graph
- Gérer les doublons (fusion de concepts synonymes)

---

### 🔵 6. Insight Agent

**Technos :**

- LLM local
- Raisonnement sur graphe
- Pattern mining (analyse de motifs)

**Rôle :**

- Trouver :
  - forces / faiblesses
  - limitations des approches
  - contradictions entre travaux
  - “gaps” de recherche
- Proposer des pistes futures

---

### 🟤 7. Evaluator Agent

**Technos :**

- LLM critique
- Règles heuristiques
- (Optionnel) scikit-learn pour un modèle de scoring
- Métriques maison

**Rôle :**

- Vérifier que la réponse :
  - est cohérente
  - reste fidèle aux sources
  - couvre la question
- Renvoyer un **score de qualité**
- Informer l’orchestrateur si besoin de :
  - relancer Retriever
  - relancer Summarizer
  - changer de modèle ou de stratégie

---

## 🧠 Memory Layer – Hybrid Knowledge & Memory

### 📁 Document Store

- Stockage des PDF + texte pré-extrait + métadonnées

**Technos :**

- Système de fichiers / MinIO / MongoDB GridFS
- pdfminer, PyPDF2

---

### 💠 Vector Store

- Stockage des embeddings
- Recherche sémantique des passages pertinents

**Technos :**

- Qdrant (recommandé) ou ChromaDB
- Sentence-Transformers

---

### 🧠 Knowledge Graph

- **Nodes** = concepts
- **Edges** = relations entre concepts

**Technos :**

- NetworkX (local)
- (Optionnel) Neo4j Community Edition
- spaCy / LLM pour l’extraction

---

## 🎛 Adaptation Layer

**Technos :**

- Règles Python
- scikit-learn (routing simple)
- Noeuds conditionnels LangGraph

**Rôle :**

- Ajuster automatiquement :
  - choix des agents
  - taille du contexte
  - choix du modèle (petit / moyen / grand)
- Déclencher des itérations (ex : relancer Retriever si le score qualité est bas)
- Améliorer la qualité finale de la réponse

---

## 📊 Observability & Evaluation

**Technos :**

- MLflow – suivi d’expériences
- LangFuse – traces LLM
- Logging Python structuré
- (Optionnel) Grafana / Prometheus

**Rôle :**

- Tracer les appels d’agents
- Mesurer coûts, temps de réponse, qualité
- Comparer :
  - LLM seul vs orchestration multi-agents

---

## 🔁 Workflow global

### Étape 1 – Ingestion & Indexation

1. External API Agent télécharge les papiers (arXiv, Semantic Scholar…)
2. Extraction de texte (PDF → texte brut)
3. Embeddings → stockage dans le **Vector Store**
4. Documents bruts + métadonnées → **Document Store**

### Étape 2 – Inference (Analyse d’une requête)

1. L’utilisateur pose une question via l’UI
2. L’UI appelle le backend FastAPI (`/query`)
3. L’orchestrateur consulte l’**Intent Agent**
4. En fonction de l’intent, il choisit une pipeline :
   - Résumé simple → Retriever + Summarizer
   - Comparaison → Retriever + Summarizer + Insight
   - Gap analysis → Retriever + Concept & Graph + Insight
   - Extraction conceptuelle → Retriever + Concept & Graph
5. Retriever renvoie les passages pertinents
6. Les agents (Summarizer, Concept & Graph, Insight…) travaillent dessus
7. Evaluator estime la qualité
8. Adaptation Layer ajuste si nécessaire (nouvelle recherche, autre modèle…)
9. L’orchestrateur compose la réponse finale
10. L’UI affiche réponse + graphe + sources + timeline des agents

---

## 🗂 Structure du projet (simplifiée)

```bash
knowflow/
├── frontend/                # Interface Web (Next.js + React + Tailwind + Cytoscape)
│   ├── app/                 # Pages (dashboard, query, graph, etc.)
│   ├── components/          # Layout, UI, query, sources, agents, graph
│   ├── lib/                 # client API, types, helpers
│   ├── styles/              # Tailwind + styles globaux
│   └── public/              # Assets (logos, icônes…)
├── backend/                 # API + Orchestrateur + Agents
│   ├── app/
│   │   ├── main.py          # Entrée FastAPI
│   │   ├── api/             # Routes (query, graph, health…)
│   │   ├── core/            # Config, logging, sécurité
│   │   ├── schemas/         # Pydantic models
│   │   ├── orchestrator/    # Graph LangGraph/CrewAI, pipelines, routing
│   │   ├── agents/          # Tous les agents spécialisés
│   │   ├── services/        # Logique métier (retrieval, summary, KG…)
│   │   ├── memory/          # Document store, vector store, knowledge graph
│   │   ├── external/        # Clients arXiv, Semantic Scholar, PDF extractor
│   │   ├── adaptation/      # Règles + modèles de routing
│   │   ├── observability/   # Traces, métriques, expériences
│   │   └── tests/           # Tests unitaires
│   └── requirements.txt
├── notebooks/               # Expériences (embeddings, KG, évaluation…)
├── infra/                   # Docker / déploiement
├── docs/                    # Documentation détaillée (architecture, agents, API…)
└── README.md
