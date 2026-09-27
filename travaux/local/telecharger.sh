#!/usr/bin/env bash
# Télécharge les poids du rôle archiviste-moyen (~5,2 Go) hors du dépôt et vérifie leur empreinte.
set -euo pipefail
source "$(dirname "$0")/config.sh"

mkdir -p "$ARCHIVISTE_MODELES"
cible="$ARCHIVISTE_MODELES/$GGUF"
if [[ ! -f "$cible" ]]; then
  curl -L --fail --continue-at - -o "$cible.partiel" "$GGUF_URL"
  mv "$cible.partiel" "$cible"
fi
echo "$GGUF_SHA256  $cible" | sha256sum --check
