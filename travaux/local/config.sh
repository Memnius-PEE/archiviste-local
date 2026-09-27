# Réglages communs aux scripts de travaux/local/, surchargeables par l'environnement.
# Les poids et les moteurs de LocalAI vivent hors du dépôt (règle des 10 Mo).
MODELES="${ARCHIVISTE_MODELES:-$HOME/models}"
MOTEURS="${ARCHIVISTE_MOTEURS:-$HOME/backends}"
ADRESSE="${ARCHIVISTE_ADRESSE:-127.0.0.1:8080}"   # locale seulement : pas d'essaim, pas d'accès réseau
API="${LOCALAI_API:-http://$ADRESSE/v1}"
ROLE="${ARCHIVISTE_MODELE:-archiviste-moyen}"

GGUF="Ministral-3-8B-Instruct-2512-Q4_K_M.gguf"
GGUF_URL="https://huggingface.co/unsloth/Ministral-3-8B-Instruct-2512-GGUF/resolve/main/$GGUF"
GGUF_SHA256="5dbc3647eb563b9f8d3c70ec3d906cce84b86bb35c5e0b8a36e7df3937ab7174"

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
