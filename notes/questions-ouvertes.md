# Questions ouvertes

Points à trancher avant de sortir de la phase prospective. Chaque réponse retenue devient une entrée de `decisions/`.

1. **Nœud archiviste** : sur quelle machine tourne l'orchestration ? Un poste de membre, un petit serveur,
   ou un runner GitHub Actions auto-hébergé (un runner hébergé par GitHub n'atteint pas l'essaim) ?
2. **Modèles par rôle** : quels fichiers GGUF retenir pour `archiviste-petit` et `archiviste-moyen` sur le
   matériel réel des membres ? Les exemples de `docs/architecture.md` §4 sont `[non vérifié]` sur ce matériel.
3. **Dépôts de référence** : quels trois sujets servent à comparer deux modèles ou deux versions de consigne ?
   `optique-ondulatoire` est un candidat ; ce sujet-ci en est un autre.
4. **Relecture** : qui remplit `relu_par`, et faut-il une relecture pour chaque fiche ou seulement avant un scellé ?
5. **Essaim et confiance** : comment distribuer et renouveler le jeton de l'essaim quand quelqu'un quitte le groupe ?
6. **Sujets privés** : un sujet `visibilite: prive` doit-il passer d'office en `local-seulement` ?
