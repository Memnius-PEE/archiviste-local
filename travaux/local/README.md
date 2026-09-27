# Embryon local de l'archiviste

Faire tourner l'archiviste sur la carte graphique d'un seul poste, sans essaim (décisions 0005 et 0006).
Le prototype `travaux/archiviste.py` ne change pas : il parle à une API compatible OpenAI et ne connaît
que le nom du rôle `archiviste-moyen`.

## Sur le poste de Romain

Mesuré le 2026-09-27 (`nvidia-smi`, `local-ai --version`) : NVIDIA GeForce RTX 5070, 12 227 Mio de VRAM
dont ~3 Gio pris par le bureau, pilote 595.84 (CUDA 13.2), 31 Gio de RAM, LocalAI v4.9.0 déjà installé
dans `/usr/local/bin`.

```bash
travaux/local/telecharger.sh   # ~5,2 Go dans ~/models, empreinte SHA-256 vérifiée
travaux/local/lancer.sh        # LocalAI sur 127.0.0.1:8080 ; 1er lancement : moteur llama-cpp CUDA dans ~/backends
travaux/local/verifier.sh      # dans un autre terminal : liste les modèles, appel minimal, fiche de ce dépôt
```

Budget mémoire attendu `[non vérifié]` : ~5 Go de poids + ~2 Go de cache pour 16 k de contexte, soit ~7 Go
sur les ~9 Go libres. Si la carte manque de place, baisser `context_size` à 8192 dans
`modeles/archiviste-moyen.yaml`.

Les chemins et l'adresse se changent par variables d'environnement (`config.sh`) :
`ARCHIVISTE_MODELES`, `ARCHIVISTE_MOTEURS`, `ARCHIVISTE_ADRESSE`, `LOCALAI_API`, `ARCHIVISTE_MODELE`.

## Demain : essaim ou serveur dédié

Rien à changer dans le code de l'archiviste ; seule l'adresse de l'API change.

| Cible | Ce qui change | Ce qui reste |
|---|---|---|
| **Poste seul** (aujourd'hui) | `lancer.sh`, écoute sur `127.0.0.1` | rôle `archiviste-moyen`, API OpenAI |
| **Essaim LocalAI fédéré** (0002) | chaque machine lance `local-ai run` en mode fédéré avec le jeton du groupe et le même `archiviste-moyen.yaml` (GGUF adapté à sa carte) ; l'archiviste vise le proxy fédéré | idem |
| **Serveur dédié** | le même `lancer.sh` en service système sur le serveur, derrière une clé d'API (`--cle` / `LOCALAI_API_KEY`) ; un runner auto-hébergé ou une tâche planifiée y lance `archiviste.py` sur les dépôts à chaque poussée | idem |

Le choix entre ces deux suites reste ouvert (`notes/questions-ouvertes.md`, question 1).
