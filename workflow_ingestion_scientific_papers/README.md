# n8n workflow — arXiv_API (KnowFlow ingestion)

This folder contains a single **n8n workflow** that fetches papers from the **arXiv API**, converts the XML feed to JSON, maps each entry to the `Document` payload, then **POSTs** it to the KnowFlow ingestion endpoint.

## Files
- `arXiv_API.json` — exported n8n workflow
- `README.md` — this file

## What the workflow does
Nodes order:
1) **HTTP Request** → calls arXiv API (query + pagination)
2) **XML** → converts XML to JSON
3) **Split Entries (Code)** → splits the `feed.entry[]` into one item per paper
4) **Map To Document (Code)** → builds the payload:
   - `source: "arxiv"`
   - `content_type: "pdf" | "web_page"`
   - `title`, `abstract`, `url`, `pdf_url`, `authors`, `year`, `created_at`
5) **POST Document** → sends each document to:
   - `http://host.docker.internal:7000/api/collector/ingest`

## Run n8n container (standalone)
```bash
docker pull n8nio/n8n

docker run --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_HOST=localhost \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  -e WEBHOOK_URL=http://localhost:5678/ \
  n8nio/n8n
