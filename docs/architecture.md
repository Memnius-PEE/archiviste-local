# L'archiviste de Memnius

Architecture d'un agent d'archivage sur modèles locaux, porté par l'essaim LocalAI du groupe.

*Version 1.1, 26 septembre 2026. Première étape exécutable : [`travaux/archiviste.py`](../travaux/archiviste.py).*

*Versée dans ce sujet depuis l'étude initiale du projet Memnius, puis alignée sur le kit v1 : forge GitHub
(décision 0010 du socle), dépôt `Memnius-PEE/archives` et `etat.json` recopié par le registre. Étude en
phase prospective : rien n'a encore tourné sur l'essaim (décision 0004 de ce sujet).*

---

## 1. Ce que fait l'archiviste

L'archiviste suit chaque dépôt du groupe d'étude et tient à jour, pour chacun, une **fiche d'archive** : ce que contient le dépôt, qui y a contribué, ce qui s'y est passé, et comment reprendre le sujet. Les fiches alimentent le **registre unifié** et, plus tard, un **index de recherche** interrogeable par les humains comme par les agents. Quand un dépôt s'endort, l'archiviste le **scelle** : fiche finale, copie intégrale vérifiable, répliquée sur plusieurs machines de l'essaim.

Trois principes guident tout le reste :

1. **Les faits viennent de Git, pas du modèle.** Dates, auteurs, nombre de commits, empreintes, fichiers : tout est calculé de façon déterministe. Le modèle ne rédige que ce qui demande de la langue (résumés, mots-clés, chronologie commentée), et ces champs sont marqués comme générés.
2. **Rien ne sort de l'essaim.** Aucun appel à un service externe. Mais attention : dans l'essaim, un extrait de dépôt peut être traité sur la machine d'un ami (voir §7).
3. **Tout est rejouable.** Chaque fiche porte le commit archivé, le modèle et la version de consigne utilisés. On peut régénérer une fiche à l'identique des faits, et comparer deux rédactions.

## 2. Vue d'ensemble

```
             dépôts du groupe (GitHub)
                        │  git fetch --mirror (lecture seule)
                        ▼
┌────────────────────── nœud archiviste ──────────────────────┐
│ 1. Collecteur      faits Git, inventaire, README, diff       │  déterministe
│ 2. Filtre          exclusion des secrets, masquage           │  déterministe
│ 3. Découpeur       morceaux par fichier/section + empreinte  │  déterministe
│ 4. Résumeur        fichier → dossier → dépôt (map-reduce)    │──┐
│ 5. Rédacteur       fiche d'archive (JSON validé → Markdown)  │──┤ appels
│ 6. Indexeur        plein texte + vecteurs                    │──┤ LocalAI
│ 7. Publieur        commit dans le dépôt « archives »         │  │
└──────────────────────────────────────────────────────────────┘  │
                        │                                         ▼
                        ▼                              ┌── essaim LocalAI ──┐
             dépôt « archives »                        │ proxy fédéré       │
             ├─ fiches/<id>.md                         │  ├─ machine A      │
             ├─ etat.json ──► recopié par le registre    │  ├─ machine B      │
             ├─ index/          (SQLite FTS5 + vec)    │  └─ machine C …    │
             └─ scellés/<id>/   (bundle + SHA-256)     └────────────────────┘
```

Le **nœud archiviste** n'a pas besoin de GPU : il orchestre et appelle l'API OpenAI-compatible de LocalAI. Ce peut être la machine de l'un d'entre vous, un petit serveur, ou un workflow planifié GitHub Actions sur un runner auto-hébergé du groupe (un runner hébergé par GitHub n'a pas accès à l'essaim).

## 3. L'essaim LocalAI : comment s'en servir

LocalAI propose deux façons de répartir le travail entre machines (les noms exacts des commandes varient selon la version ; vérifiez la documentation « Distributed inference » de votre version) :

| Mode | Principe | Usage pour l'archiviste |
|---|---|---|
| **Fédéré** | Chaque machine charge un modèle entier ; un proxy répartit les *requêtes* entre elles. | **Mode recommandé.** L'archivage est un travail par lots : des centaines de petites requêtes indépendantes (un fichier, un dossier) se répartissent naturellement. Une machine éteinte ralentit le lot sans le casser. |
| **Workers (llama.cpp RPC)** | Un seul modèle est *découpé* entre plusieurs machines. | À réserver au modèle de synthèse le plus gros, et seulement sur réseau local rapide. Sur Internet, la latence rend l'inférence très lente. |

Conséquences pratiques :

- **Un nom de modèle commun par rôle** (`archiviste-petit`, `archiviste-moyen`, `archiviste-embed`…) déclaré dans la config de chaque machine, même si le fichier GGUF derrière diffère selon le matériel. Le code de l'archiviste ne connaît que les rôles.
- **Les tâches doivent être idempotentes et courtes** : si un pair disparaît en cours de route, la requête est relancée ailleurs. Aucun état ne vit sur les pairs.
- **Le jeton de l'essaim est un secret** : quiconque le possède peut rejoindre l'essaim et voir passer des extraits de dépôts.

## 4. Choix des modèles pour du matériel grand public

Les rôles sont stables ; les modèles cités sont des exemples à confirmer dans la galerie LocalAI au moment de l'installation (le paysage bouge vite). Format GGUF, quantification **Q4_K_M** par défaut (bon compromis qualité/mémoire), Q5/Q6 si la mémoire le permet.

| Rôle | Tâche | Matériel visé | Exemples de modèles | Mémoire approx. |
|---|---|---|---|---|
| `archiviste-embed` | vecteurs pour la recherche | toute machine, CPU suffit | bge-m3, Qwen3-Embedding-0.6B, multilingual-e5 (bons en français) | < 2 Go |
| `archiviste-petit` | tri des fichiers, résumé d'un fichier ou d'un lot de commits | portable 16 Go de RAM, sans GPU | Qwen3-4B, Gemma 3 4B | 3–4 Go |
| `archiviste-moyen` | résumé de dossier, rédaction de fiche | GPU 8–12 Go ou 32 Go de RAM | Qwen3-8B, Gemma 3 12B, Llama 3.1 8B | 6–9 Go |
| `archiviste-grand` | synthèse de dépôt volumineux, relecture croisée | GPU 16–24 Go, ou 64 Go de RAM | Qwen3-30B-A3B (MoE, rapide même sur CPU), Mistral Small 24B | 15–20 Go |
| `archiviste-rerank` *(optionnel)* | reclasser les résultats de recherche | CPU | bge-reranker-v2-m3 | ~1 Go |

Points d'attention :

- **Contexte** : fixez `context_size` à 8 k–16 k tokens pour les petits modèles ; au-delà, la mémoire explose et la qualité baisse. Le découpage (§5) est fait pour que chaque requête tienne dans 8 k.
- **Sortie structurée** : demandez du JSON et validez-le côté archiviste (le script le fait, avec une relance). Si votre backend le permet, activez `response_format: json_object` ou une grammaire pour le garantir.
- **Modèles « à raisonnement »** : désactivez la réflexion (mode *no-think*) pour les tâches de résumé ; elle coûte cher pour peu de gain. Le script ignore de toute façon les blocs `<think>`.
- **Français** : Qwen3, Gemma 3 et Mistral écrivent correctement en français ; évitez les modèles entraînés surtout en anglais pour la rédaction.
- **Un seul modèle pour démarrer** : `archiviste-moyen` suffit à l'étape 1. Les autres rôles arrivent avec le map-reduce (étape 2) et l'index (étape 4).

## 5. Flux d'ingestion depuis Git

### 5.1 Déclenchement

- **Planifié** : une passe par nuit (cron ou workflow planifié GitHub Actions) sur tous les dépôts du registre.
- **À la demande** : `archiviste fiche <depot>` pour un dépôt, ou un webhook sur push vers la branche principale (plus tard).

### 5.2 Étapes

1. **Collecte (déterministe).** `git fetch --mirror` dans un cache local, puis lecture de `HEAD` de la branche principale : liste des fichiers, extensions, commits (`git log --no-merges`, identités normalisées par `.mailmap`), README, présence d'instructions pour agents (`AGENTS.md`, `CLAUDE.md`…), licence, tags.
2. **Incrémental.** La fiche mémorise le `commit` archivé. À la passe suivante, seul `git diff <commit>..HEAD` est retraité ; si rien n'a changé, rien n'est appelé.
3. **Filtre de sécurité.** Fichiers exclus d'office (`.env*`, clés, `id_rsa`, `credentials*`…), masquage des motifs de secrets dans tout extrait. À terme, passer `gitleaks` avant tout envoi. Les consignes `archivage` de `memnius.yaml` sont appliquées (dépôt exclu, chemins exclus). Un dépôt en politique `local-seulement` n'est traité que sur le nœud archiviste lui-même (§7).
4. **Découpage.** Un morceau = un fichier texte, ou une section (titre Markdown, fonction, cellule de notebook) si le fichier dépasse ~6 k tokens. Les binaires, données brutes et fichiers générés ne sont décrits que par leurs métadonnées (nom, taille, type). Chaque morceau reçoit l'empreinte SHA-256 de son contenu.
5. **Résumé hiérarchique (map-reduce).** Morceau → résumé court (`archiviste-petit`), puis dossier → synthèse (`archiviste-moyen`), puis dépôt → fiche. Les commits sont regroupés par mois et résumés en une chronologie. **Cache par empreinte** : un morceau inchangé n'est jamais résumé deux fois, ce qui rend les passes nocturnes quasi gratuites.
6. **Rédaction de la fiche.** Le modèle reçoit les faits et les synthèses, répond en JSON, l'archiviste valide (champs, longueurs, types), relance une fois si besoin, sinon produit une fiche factuelle seule plutôt qu'une fiche douteuse.
7. **Indexation.** Résumés et morceaux vont dans une base SQLite : table FTS5 pour le plein texte, extension `sqlite-vec` pour les vecteurs. Un fichier, zéro serveur, copiable partout.
8. **Publication.** Les fiches et `etat.json` sont commités dans le dépôt `Memnius-PEE/archives`. L'historique Git de ce dépôt devient l'historique des fiches.

## 6. La fiche d'archive

Un fichier Markdown par dépôt, `fiches/<id>.md`, lisible par un humain dans GitHub et par une machine grâce à son en-tête. Chaque valeur de l'en-tête est écrite en JSON sur une ligne : c'est du YAML valide, relisible sans dépendance.

```yaml
---
schema: "memnius/fiche-archive/v1"
id: "optique-ondulatoire"             # identifiant stable, = clé du registre
titre: "Optique ondulatoire"
depot: "https://github.com/Memnius-PEE/optique-ondulatoire.git"
commit: "da66421…"                    # commit archivé (point de reprise de l'incrémental)
date_fiche: "2026-09-26T14:54:16+00:00"
statut: "actif"                        # actif | dormant | scellé | vide
periode: ["2025-01-10", "2026-09-26"]
nb_commits: 2
nb_fichiers: 3
contributeurs: [{"nom": "Alice", "commits": 1}, {"nom": "Bob", "commits": 1}]
extensions: {".md": 1, ".py": 1}
instructions_agents: ["AGENTS.md"]
licence: "LICENSE"
resume_court: "…"                      # IA, ≤ 300 caractères
mots_cles: ["interferences", "young"]  # IA
genere_par: {"modele": "archiviste-moyen", "version_prompt": "fiche-v1"}
relu_par: null                         # rempli par un humain à la relecture
---
```

Corps de la fiche : **Résumé** (avec la mention « rédigé par l'archiviste, non relu » tant que `relu_par` est vide), **Chronologie**, **Pour reprendre le sujet**, **Faits**, **Derniers commits**. Les étapes suivantes ajouteront **Décisions notables** (extraites d'un journal de décisions s'il existe) et **Scellé** (empreinte et emplacements des copies).

Règles :

- Les champs factuels ne sont jamais écrits par le modèle.
- Les champs rédigés par le modèle sont identifiables (`genere_par`) et relisibles (`relu_par`).
- Une relecture humaine est **obligatoire** pour passer au statut `scellé`, facultative sinon.
- Le schéma est versionné (`schema`) ; tout changement incompatible crée une `v2`.

## 7. Garde-fous

| Risque | Garde-fou |
|---|---|
| Hallucination présentée comme un fait | Faits calculés par Git ; champs IA marqués ; consigne « n'invente rien » ; validation JSON ; relecture avant scellé. |
| Fuite de secrets vers le modèle | Liste d'exclusion de fichiers, masquage des motifs de secrets (dans le script dès l'étape 1), `gitleaks` avant envoi à l'étape 2. |
| Contenu sensible traité chez un pair | Politique `archivage.politique: local-seulement` dans `memnius.yaml` (à ajouter au schéma, §8) : le nœud archiviste utilise alors son propre LocalAI, jamais l'essaim. Jeton de l'essaim traité comme un secret et changé quand quelqu'un quitte le groupe. |
| L'archiviste modifie un dépôt de travail | Accès **en lecture seule** aux dépôts (GitHub App `memnius-archiviste`, Contents et Metadata en lecture). L'archiviste n'écrit que dans le dépôt `Memnius-PEE/archives`, par une clé de déploiement. |
| Injection de consignes cachées dans un README | Le contenu des dépôts est placé dans le message utilisateur, jamais dans la consigne système ; l'archiviste n'exécute aucune action décidée par le modèle, il ne fait que remplir des champs validés. |
| Dérive silencieuse quand on change de modèle | `genere_par` + `version_prompt` dans chaque fiche ; un changement de modèle se teste sur 3 dépôts de référence avant d'être généralisé. |
| Perte d'archives | Scellés répliqués sur au moins 2 machines de l'essaim + GitHub, vérification périodique des empreintes. |

## 8. Lien avec le registre unifié

Le registre est tenu par le dépôt `Memnius-PEE/registre` (schéma `schema/registre.schema.json`). Il est
**reconstruit chaque nuit** par `memnius.py construire` à partir du `memnius.yaml` de chaque sujet et des
faits Git et GitHub, jamais édité à la main. Registre et fiche d'archive partagent la même clé : **`id`**.

- **Le sujet déclare** dans `memnius.yaml` : titre, résumé, statut humain, mainteneurs, visibilité, et le bloc
  `archivage` (`politique: standard | prioritaire | exclure | local-seulement`, motifs `exclure`). L'archiviste
  respecte ces consignes : `exclure` saute le sujet, les motifs retirent des chemins de la collecte,
  `prioritaire` passe en tête de la passe nocturne, `local-seulement` n'est traité que sur le nœud
  archiviste (§7). La politique `local-seulement` est déjà dans le schéma v1.
- **L'archiviste lit** dans `registre.json` la liste des sujets et `depot.dernier_commit`. Il réarchive un
  sujet seulement si ce commit diffère de `archiviste.commit_archive`.
- **L'archiviste n'écrit jamais dans le registre.** Il publie `etat.json` dans `Memnius-PEE/archives`
  (`derniere_fiche`, `commit_archive`, `archive_le` par sujet) ; le registre le recopie dans le bloc réservé
  `archiviste` de chaque entrée (`memnius.py construire --archiviste etat.json`). Voir le README du dépôt
  `archives` et la décision 0009 du socle.
- Les champs rédigés par le modèle (résumé court, mots-clés) restent dans la fiche d'archive et ne remplacent
  jamais le `resume` déclaré par les humains dans `memnius.yaml`.
- La commande `archiviste.py registre fiches/` de l'étape 1 produit un petit registre provisoire à partir des
  fiches. Elle sert à tester seule et sera remplacée, à l'étape 3, par la production d'`etat.json`.

## 9. Cycle de vie et scellé

```
actif ──(aucun commit depuis 6 mois)──► dormant ──(décision humaine)──► scellé
  ▲                                        │
  └──────────(nouveau commit)──────────────┘
```

Sceller un dépôt :

1. Fiche finale régénérée et **relue** (`relu_par` rempli).
2. `git bundle create <id>-<date>.bundle --all` : le dépôt complet, historique compris, en un fichier.
3. Empreinte SHA-256 du bundle, tag `archive/<date>` sur le dépôt d'origine.
4. Copie du bundle dans `scellés/<id>/` (Git LFS ou stockage à part selon la taille) et sur au moins deux machines de l'essaim.
5. Dépôt d'origine passé en lecture seule (« Archive this repository » dans GitHub).

Restaurer : `git clone <id>-<date>.bundle` suffit, sans GitHub ni archiviste.

## 10. Feuille de route

| Étape | Contenu | Critère de réussite |
|---|---|---|
| **1 — Fiche unique** *(prototype écrit)* | `archiviste.py` : collecte Git, masquage, appel LocalAI, fiche validée, mode sans IA, registre JSON. | Une fiche correcte sur un vrai dépôt du groupe, générée via l'essaim. |
| 2 — Incrémental et map-reduce | Cache par empreinte, résumés fichier → dossier → dépôt, diff depuis le dernier commit archivé, gitleaks. | Deuxième passe sur un dépôt inchangé : zéro appel au modèle. |
| 3 — Dépôt `archives` et passe nocturne | Workflow planifié, fiches commitées dans `Memnius-PEE/archives`, `etat.json` publié et recopié par le registre, réarchivage seulement si `dernier_commit` a changé. | Tous les dépôts ont une fiche à jour chaque matin. |
| 4 — Index et questions | SQLite FTS5 + vecteurs, commande `archiviste demander "…"` (recherche + réponse sourcée), exposable aux agents via MCP. | « Qui a travaillé sur l'ajustement des pics ? » renvoie la bonne fiche et le bon commit. |
| 5 — Scellés | Détection des dormants, procédure de scellé, réplication et vérification des empreintes. | Un dépôt scellé se restaure depuis une machine de l'essaim, GitHub injoignable. |

## 11. Tester l'étape 1

Prérequis : Python 3.9+, git, et un point d'accès LocalAI (celui de l'essaim ou une instance locale).

```bash
# 1. Sans modèle : vérifie la collecte et le format
python3 travaux/archiviste.py fiche ~/depots/optique-ondulatoire --sans-ia -o fiches/

# 2. Avec l'essaim (adresse du proxy fédéré, nom du modèle déclaré dans LocalAI)
export LOCALAI_API=http://<proxy-essaim>:8080/v1
python3 travaux/archiviste.py fiche ~/depots/optique-ondulatoire -o fiches/ --modele archiviste-moyen

# 3. Registre à partir des fiches
python3 travaux/archiviste.py registre fiches/ -o registre.json
```

Ce qu'il faut regarder : le résumé dit-il vrai ? la chronologie colle-t-elle aux commits ? combien de temps a pris l'appel, et sur quelle machine ? Si le modèle échoue, le script le signale et écrit quand même la fiche factuelle.

Vérifié ici, avec un faux serveur OpenAI-compatible à la place de LocalAI : génération de la fiche, relance après une première réponse non-JSON, suppression des blocs `<think>`, masquage d'une clé présente dans le README (absente de la requête envoyée), repli en fiche factuelle quand le serveur est injoignable, en-tête relu par PyYAML, registre produit. **Pas encore testé contre un vrai modèle** : c'est le premier test à faire sur l'essaim, quand la phase prospective sera levée.
