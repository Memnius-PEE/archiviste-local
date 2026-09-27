#!/usr/bin/env bash
# Démarre LocalAI seul sur ce poste (mode « embryon » : pas de P2P, pas de fédération),
# écoute en local et sert les rôles déclarés dans travaux/local/modeles/.
# Au premier lancement, LocalAI télécharge son moteur llama-cpp (CUDA) dans $MOTEURS.
set -euo pipefail
source "$(dirname "$0")/config.sh"

mkdir -p "$MODELES" "$MOTEURS"
for f in "$ICI"/modeles/*.yaml; do
  ln -sf "$f" "$MODELES/$(basename "$f")"
done
[[ -f "$MODELES/$GGUF" ]] || { echo "poids absents : lancez d'abord $ICI/telecharger.sh" >&2; exit 1; }

exec local-ai run \
  --models-path "$MODELES" \
  --backends-path "$MOTEURS" \
  --address "$ADRESSE" \
  "$@"
