# Embryon local de l'archiviste

Faire tourner l'archiviste sur la carte graphique d'un seul poste, sans essaim (décisions 0005 et 0006).
Le prototype `travaux/archiviste.py` ne change pas : il parle à une API compatible OpenAI et ne connaît
que le nom du rôle `archiviste-moyen`.

## Sur le poste de Romain

Mesuré le 2026-09-27 (`nvidia-smi`, `docker version`, `docker images`) : NVIDIA GeForce RTX 5070, 12 227 Mio de VRAM
dont ~3 Gio pris par le bureau, pilote 595.84 (CUDA 13.2), 31 Gio de RAM, Docker 29.8 avec le
NVIDIA Container Toolkit 1.20.1, image `localai/localai` v4.9.0 CUDA 12 déjà présente.

LocalAI tourne en conteneur (`compose.yaml`, conteneur `archiviste-localai`), sur le port 8081 car le
8080 est pris par un autre conteneur LocalAI du poste. Le binaire `/usr/local/bin/local-ai` n'est pas utilisé.

```bash
travaux/local/telecharger.sh   # ~5,2 Go dans ~/models, empreinte SHA-256 vérifiée
travaux/local/lancer.sh        # conteneur LocalAI sur 127.0.0.1:8081 ; 1er lancement : moteur llama-cpp CUDA dans un volume
travaux/local/verifier.sh      # liste les modèles, appel minimal, fiche de ce dépôt
docker compose -f travaux/local/compose.yaml down   # arrêt
```

Budget mémoire attendu `[non vérifié]` : ~5 Go de poids + ~2 Go de cache pour 16 k de contexte, soit ~7 Go
sur les ~9 Go libres. Si la carte manque de place, baisser `context_size` à 8192 dans
`modeles/archiviste-moyen.yaml`.

Les chemins et l'adresse se changent par variables d'environnement (`config.sh`) :
`ARCHIVISTE_MODELES`, `ARCHIVISTE_ADRESSE`, `LOCALAI_IMAGE_TAG`, `LOCALAI_API`, `ARCHIVISTE_MODELE`.

## Demain : essaim ou serveur dédié

Rien à changer dans le code de l'archiviste ; seule l'adresse de l'API change.

| Cible | Ce qui change | Ce qui reste |
|---|---|---|
| **Poste seul** (aujourd'hui) | `compose.yaml` via `lancer.sh`, écoute sur `127.0.0.1` | rôle `archiviste-moyen`, API OpenAI |
| **Essaim LocalAI fédéré** (0002) | chaque machine lance le même conteneur en mode fédéré avec le jeton du groupe et le même `archiviste-moyen.yaml` (GGUF adapté à sa carte) ; l'archiviste vise le proxy fédéré | idem |
| **Serveur dédié** | le même `compose.yaml` sur le serveur (`restart: unless-stopped`), derrière une clé d'API (`--cle` / `LOCALAI_API_KEY`) ; un runner auto-hébergé ou une tâche planifiée y lance `archiviste.py` sur les dépôts à chaque poussée | idem |

Le choix entre ces deux suites reste ouvert (`notes/questions-ouvertes.md`, question 1).
