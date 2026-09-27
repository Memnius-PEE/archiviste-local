#!/usr/bin/env bash
# Vérifie qu'une API OpenAI-compatible sert le rôle attendu, puis produit une fiche de ce dépôt.
# Marche à l'identique contre le poste local, le proxy de l'essaim ou un serveur dédié :
#   LOCALAI_API=http://serveur:8080/v1 travaux/local/verifier.sh
set -euo pipefail
source "$(dirname "$0")/config.sh"
depot="$(git -C "$ICI" rev-parse --show-toplevel)"
sortie="${1:-$(mktemp -d)}"

echo "== modèles servis par $API"
curl -sf "$API/models" | python3 -c 'import json,sys; print("\n".join(m["id"] for m in json.load(sys.stdin)["data"]))'

echo "== appel minimal au rôle $ROLE"
debut=$(date +%s)
curl -sf "$API/chat/completions" -H 'Content-Type: application/json' \
  -d "{\"model\":\"$ROLE\",\"messages\":[{\"role\":\"user\",\"content\":\"Réponds seulement : prêt.\"}],\"max_tokens\":16}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["choices"][0]["message"]["content"].strip())'
echo "($(( $(date +%s) - debut )) s, chargement du modèle compris)"

echo "== fiche de ce dépôt dans $sortie"
time python3 "$depot/travaux/archiviste.py" fiche "$depot" -o "$sortie" --api "$API" --modele "$ROLE"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv 2>/dev/null || true
