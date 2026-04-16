#!/usr/bin/env bash
set -e

echo "Khoi dong Fuseki..."
docker compose up -d
sleep 5

echo "Load data vao dataset 'vndbpedia'..."
curl -u admin:admin \
  -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @data/final/vn_dbpedia.ttl \
  "http://localhost:3030/vndbpedia/data?default"

echo ""
echo "Done. Truy cap:"
echo "  Web UI:          http://localhost:3030"
echo "  SPARQL endpoint: http://localhost:3030/vndbpedia/sparql"
