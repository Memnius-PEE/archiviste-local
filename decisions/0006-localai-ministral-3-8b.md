# 0006 — LocalAI et Ministral 3 8B Instruct pour l'embryon sur RTX 5070

- Date : 2026-09-27
- Origine : [agent] choix d'après le matériel mesuré, soumis à Romain dans la pull request
- Décidé par : @Pwouette, en attente de validation
- Options écartées : Ollama ou llama.cpp seul (il faudrait réécrire la configuration en passant à l'essaim LocalAI) ; Qwen3-8B (mode « réflexion » à désactiver, déjà écarté par le §4 pour les résumés) ; Gemma 4 12B (~7 Go de poids, trop juste avec 16 k de contexte sur ~9 Go libres) ; Qwen3.8-9B (distillation par un tiers)
- Source : `nvidia-smi` et `local-ai --version` du 2026-09-27 ; galerie LocalAI (`gallery/index.yaml`, entrée `mistralai_ministral-3-8b-instruct-2512-multimodal`) ; `travaux/local/README.md`
- Remplace : —

Le serveur d'inférence est LocalAI 4.9, déjà installé sur le poste et visé par la décision 0002 : la même
configuration de rôle servira dans l'essaim. Le rôle `archiviste-moyen` est tenu par Ministral 3 8B
Instruct 2512 en Q4_K_M (5,2 Go, Apache 2.0), modèle de Mistral AI qui écrit bien le français et n'a pas
de mode réflexion. La qualité des fiches reste à juger sur les dépôts de référence `[non vérifié]`.
