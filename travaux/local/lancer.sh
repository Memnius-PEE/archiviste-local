#!/usr/bin/env bash
# Démarre LocalAI en conteneur sur ce poste (mode « embryon » : pas de P2P, pas de fédération).
# Arrêt : docker compose -f travaux/local/compose.yaml down
set -euo pipefail
source "$(dirname "$0")/config.sh"

[[ -f "$ARCHIVISTE_MODELES/$GGUF" ]] || { echo "poids absents : lancez d'abord $ICI/telecharger.sh" >&2; exit 1; }
docker compose -f "$ICI/compose.yaml" up -d "$@"
echo "LocalAI démarre sur $API ; journal : docker logs -f archiviste-localai"
