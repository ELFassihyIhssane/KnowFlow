# KnowFlow — Orchestrateur multi-agents adaptatif guidé par la connaissance

## Présentation générale

KnowFlow est un système de question-réponse scientifique fondé sur une orchestration multi-agents, conçu pour produire des réponses traçables, évaluées et contrôlables par l’utilisateur.  
Contrairement aux systèmes RAG classiques, KnowFlow rend explicites le raisonnement suivi, les agents activés, les passages documentaires utilisés et les métriques de qualité associées à chaque réponse.

Le projet vise à répondre aux limites des modèles de langage appliqués à l’analyse scientifique, notamment le manque de transparence, l’absence d’évaluation structurée et l’impossibilité de contrôler ou d’adapter le pipeline de génération.

---

## Architecture globale

KnowFlow repose sur une architecture modulaire orchestrée autour d’un état partagé.  
Chaque requête utilisateur est traitée par un pipeline structuré composé d’agents spécialisés, coordonnés par un orchestrateur basé sur un graphe d’exécution.

Pipeline principal :
- Analyse de l’intention et décomposition en sous-tâches
- Récupération documentaire sémantique
- Génération de réponse (résumé, comparaison ou analyse)
- Extraction de concepts et relations
- Analyse critique approfondie
- Évaluation de la qualité
- Proposition d’adaptation contrôlée

L’orchestration est implémentée avec LangGraph et repose sur un état typé et traçable.

---

## Orchestrateur et état partagé

Le cœur du système est l’orchestrateur multi-agents, qui manipule un état global (`OrchestratorState`).  
Cet état contient notamment :
- la question utilisateur
- l’intention détectée et les sous-tâches
- les passages récupérés
- les résultats intermédiaires (résumé, concepts, analyses)
- les métriques d’évaluation
- les paramètres de configuration du pipeline
- les actions d’adaptation proposées

L’orchestrateur définit explicitement les transitions entre agents, ainsi que les conditions de routage selon l’intention et les résultats intermédiaires.

---

## Agents spécialisés

Chaque agent est implémenté comme un module indépendant, contribuant à l’état global.

- **Intent Agent**  
  Identifie l’intention principale de la requête (`summary`, `comparison`, `gap`, `deep_analysis`, etc.) et génère une liste de sous-tâches atomiques.

- **Retriever Agent**  
  Effectue une recherche sémantique à partir d’embeddings et récupère les passages les plus pertinents depuis la base vectorielle Qdrant.

- **Summarizer Agent**  
  Génère une réponse structurée et fondée sur les passages récupérés.  
  En l’absence de passages, un mode de repli explicite est utilisé, signalant l’absence de citations.

- **Concept Graph Agent**  
  Extrait les concepts et relations à partir des passages via une approche hybride combinant LLM et heuristiques NLP.  
  Les concepts sont normalisés, dédupliqués et stockés dans un graphe de connaissances.

- **Insight Agent**  
  Produit des analyses critiques basées sur :
  - des heuristiques de détection de lacunes
  - des statistiques descriptives
  - le raisonnement sur le graphe de connaissances
  - une synthèse finale par LLM strictement ancrée dans les passages

- **Evaluator Agent**  
  Évalue la qualité de la réponse via plusieurs métriques :
  - fidélité aux passages
  - couverture de la question et des sous-tâches
  - cohérence du raisonnement
  - profondeur analytique  
  Une critique optionnelle par LLM peut être activée pour formuler des recommandations.

---

## Mémoire hybride et récupération d’information

KnowFlow repose sur une mémoire hybride combinant trois composantes :

### Stockage documentaire

Les documents scientifiques sont stockés dans une base PostgreSQL via SQLAlchemy.  
Chaque document contient les métadonnées, le texte brut extrait des PDF et une version nettoyée destinée à la vectorisation.

L’extraction PDF est réalisée avec pdfminer, suivie d’une phase de nettoyage du texte.

### Recherche vectorielle

Les documents sont découpés en passages et vectorisés avec Sentence-Transformers (`all-MiniLM-L6-v2`).  
Les embeddings sont indexés dans Qdrant, exécuté via Docker, et interrogés pour la recherche sémantique.

Chaque document génère plusieurs vecteurs (titre, résumé, corps) afin d’améliorer la couverture.

### Graphe de connaissances

Les concepts et relations extraits sont stockés dans un graphe de connaissances implémenté avec NetworkX.  
Le graphe est persisté localement au format JSON et exploité pour l’analyse conceptuelle et critique.

---

## Couche d’adaptation contrôlée

Après l’évaluation, une couche d’adaptation basée sur des règles interprétables propose des ajustements du pipeline, par exemple :
- augmentation du nombre de passages récupérés
- réduction de la température du modèle
- activation ou désactivation de la critique LLM

Ces ajustements ne sont jamais appliqués automatiquement.  
Ils sont exposés à l’utilisateur, qui décide explicitement de relancer le pipeline avec les nouveaux paramètres.

---

## API Backend

Le backend est implémenté avec FastAPI et expose notamment :
- un endpoint `/query` pour l’exécution standard
- un endpoint `/query/retry` pour la relance manuelle avec adaptation

Les réponses de l’API incluent :
- la réponse finale
- les passages utilisés
- les métriques d’évaluation
- les analyses critiques
- les actions d’adaptation proposées
- l’état des paramètres du pipeline

---

## Observabilité et traçabilité

KnowFlow intègre une couche complète d’observabilité :
- journalisation structurée avec structlog
- métriques de performance avec Prometheus
- suivi expérimental optionnel avec MLflow
- traçage LLM optionnel avec Langfuse

Chaque requête, appel d’agent et décision d’adaptation est traçable.

---

## Interface Web

L’interface utilisateur est développée avec Next.js, React et Tailwind CSS.  
Elle permet de :
- poser des questions scientifiques
- visualiser les réponses et leurs sources
- inspecter les agents activés
- analyser les métriques de qualité
- explorer le graphe de connaissances
- déclencher manuellement une relance adaptée

---

## Collecte automatisée des données

La collecte documentaire est automatisée via n8n, notamment depuis arXiv.  
Les métadonnées et documents sont stockés automatiquement dans la base PostgreSQL, puis traités, nettoyés et indexés sans intervention manuelle.

---

## Technologies utilisées

- Python, FastAPI, Pydantic
- LangGraph (orchestration multi-agents)
- PostgreSQL, SQLAlchemy
- Sentence-Transformers
- Qdrant (Docker)
- NetworkX
- Prometheus, structlog
- MLflow (optionnel)
- Langfuse (optionnel)
- Next.js, React, Tailwind CSS
- n8n, Docker

---

## Objectif du projet

KnowFlow constitue un MVP robuste et extensible pour l’assistance à l’analyse scientifique, orienté transparence, contrôle humain et inspection du raisonnement.  
Il pose les bases d’un système fiable, interprétable et évolutif pour la recherche scientifique assistée par intelligence artificielle.
