#!/usr/bin/env python3
"""Archiviste Memnius, étape 1 : une fiche d'archive par dépôt Git.

Python 3.9+ et git suffisent (bibliothèque standard uniquement).

    # fiche factuelle seule, sans appel à un modèle
    python3 archiviste.py fiche chemin/vers/depot --sans-ia -o fiches/

    # fiche complète via l'API OpenAI-compatible de LocalAI
    python3 archiviste.py fiche chemin/vers/depot -o fiches/ \
        --api http://localhost:8080/v1 --modele qwen3-8b

    # agrège les en-têtes des fiches en un registre JSON
    python3 archiviste.py registre fiches/ -o registre.json

Principe : les faits (commits, dates, auteurs, fichiers) sont calculés par Git,
jamais par le modèle. Le modèle ne rédige que les champs marqués « ia ».
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCHEMA = "memnius/fiche-archive/v1"
VERSION_PROMPT = "fiche-v1"

# Fichiers jamais lus ni envoyés au modèle.
FICHIERS_EXCLUS = re.compile(
    r"(^|/)(\.env[^/]*|.*\.(pem|key|p12|pfx|kdbx)|id_(rsa|ed25519|ecdsa)[^/]*|\.netrc|credentials[^/]*)$",
    re.I,
)
# Motifs de secrets masqués dans tout extrait envoyé au modèle.
SECRETS = re.compile(
    r"(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|glpat-[A-Za-z0-9_\-]{20,}"
    r"|sk-[A-Za-z0-9_\-]{20,}|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S{6,}))"
)
LIMITE_README = 4000
LIMITE_COMMITS = 40


def git(depot: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(depot), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} : {r.stderr.strip()}")
    return r.stdout


def masquer(texte: str) -> str:
    return SECRETS.sub("[MASQUÉ]", texte)


def slug(nom: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", nom.lower()).strip("-")
    return s or "depot"


# --- Collecte des faits (déterministe) --------------------------------------

def collecter(depot: Path) -> dict:
    depot = depot.resolve()
    head = git(depot, "rev-parse", "HEAD").strip()
    try:
        origine = git(depot, "remote", "get-url", "origin").strip()
    except RuntimeError:
        origine = None

    commits = []
    for ligne in git(depot, "log", "--no-merges", "--format=%H%x1f%aN%x1f%aI%x1f%s").splitlines():
        h, auteur, date, sujet = ligne.split("\x1f", 3)
        commits.append({"sha": h, "auteur": auteur, "date": date, "sujet": sujet})

    par_auteur = collections.Counter(c["auteur"] for c in commits)
    fichiers = [f for f in git(depot, "ls-files").splitlines() if f]
    extensions = collections.Counter(
        (Path(f).suffix.lower() or "(sans)") for f in fichiers if not FICHIERS_EXCLUS.search(f)
    )
    dossiers = collections.Counter(f.split("/")[0] if "/" in f else "." for f in fichiers)

    def present(*noms: str) -> str | None:
        bas = {f.lower(): f for f in fichiers}
        for n in noms:
            if n.lower() in bas:
                return bas[n.lower()]
        return None

    readme = present("README.md", "README.rst", "README.txt", "README", "LISEZMOI.md")
    texte_readme = ""
    if readme:
        texte_readme = masquer(git(depot, "show", f"HEAD:{readme}")[:LIMITE_README])

    dates = sorted(c["date"] for c in commits)
    return {
        "nom": depot.name,
        "chemin": str(depot),
        "origine": origine,
        "commit": head,
        "nb_commits": len(commits),
        "premier_commit": dates[0] if dates else None,
        "dernier_commit": dates[-1] if dates else None,
        "contributeurs": [{"nom": n, "commits": k} for n, k in par_auteur.most_common()],
        "nb_fichiers": len(fichiers),
        "extensions": dict(extensions.most_common(12)),
        "dossiers": dict(dossiers.most_common(15)),
        "readme": readme,
        "texte_readme": texte_readme,
        "instructions_agents": [f for f in ("AGENTS.md", "CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md") if present(f)],
        "licence": present("LICENSE", "LICENSE.md", "LICENCE", "COPYING"),
        "derniers_commits": [
            {"date": c["date"][:10], "auteur": c["auteur"], "sujet": masquer(c["sujet"])}
            for c in commits[:LIMITE_COMMITS]
        ],
    }


def statut(faits: dict, mois_dormance: int = 6) -> str:
    if not faits["dernier_commit"]:
        return "vide"
    dernier = dt.datetime.fromisoformat(faits["dernier_commit"])
    age = dt.datetime.now(dernier.tzinfo) - dernier
    return "dormant" if age.days > 30 * mois_dormance else "actif"


# --- Rédaction par le modèle local ------------------------------------------

CONSIGNE = """Tu es l'archiviste d'un groupe d'étude. On te donne les faits bruts d'un dépôt Git.
Réponds UNIQUEMENT par un objet JSON, en français, avec exactement ces clés :
- "resume_court" : une phrase de 300 caractères au plus, qui dit de quoi traite le dépôt.
- "resume" : 3 à 6 phrases : sujet, approche, état d'avancement.
- "mots_cles" : liste de 3 à 8 mots-clés en minuscules.
- "chronologie" : liste de 2 à 6 étapes {"periode": "AAAA-MM", "fait": "..."} déduites des commits.
- "pour_reprendre" : 1 à 3 phrases pour quelqu'un qui reprendrait le sujet.
N'invente rien qui ne figure pas dans les faits. Si une information manque, dis-le."""


def prompt_faits(f: dict) -> str:
    lignes = [
        f"Dépôt : {f['nom']}",
        f"Commits : {f['nb_commits']} du {(f['premier_commit'] or '?')[:10]} au {(f['dernier_commit'] or '?')[:10]}",
        f"Contributeurs : {', '.join(c['nom'] + ' (' + str(c['commits']) + ')' for c in f['contributeurs'][:10])}",
        f"Fichiers : {f['nb_fichiers']} ; extensions : {json.dumps(f['extensions'], ensure_ascii=False)}",
        f"Dossiers principaux : {json.dumps(f['dossiers'], ensure_ascii=False)}",
        "",
        "Derniers commits (du plus récent au plus ancien) :",
        *(f"- {c['date']} {c['auteur']} : {c['sujet']}" for c in f["derniers_commits"]),
        "",
        f"README ({f['readme'] or 'absent'}) :",
        f["texte_readme"] or "(aucun)",
    ]
    return "\n".join(lignes)


def extraire_json(texte: str) -> dict:
    texte = re.sub(r"<think>.*?</think>", "", texte, flags=re.S)  # modèles « à raisonnement »
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut < 0 or fin < 0:
        raise ValueError("pas de JSON dans la réponse")
    return json.loads(texte[debut : fin + 1])


def valider(r: dict) -> dict:
    erreurs = []
    if not isinstance(r.get("resume_court"), str) or not r["resume_court"].strip():
        erreurs.append("resume_court manquant")
    elif len(r["resume_court"]) > 300:
        r["resume_court"] = r["resume_court"][:297].rstrip() + "…"
    for cle in ("resume", "pour_reprendre"):
        if not isinstance(r.get(cle), str) or not r[cle].strip():
            erreurs.append(f"{cle} manquant")
    if not isinstance(r.get("mots_cles"), list) or not all(isinstance(m, str) for m in r["mots_cles"]):
        erreurs.append("mots_cles invalide")
    else:
        r["mots_cles"] = [m.strip().lower() for m in r["mots_cles"] if m.strip()][:8]
    chrono = r.get("chronologie", [])
    if not isinstance(chrono, list) or not all(isinstance(e, dict) and "fait" in e for e in chrono):
        erreurs.append("chronologie invalide")
    if erreurs:
        raise ValueError("; ".join(erreurs))
    return r


def rediger(faits: dict, api: str, modele: str, cle: str | None, delai: int) -> dict:
    corps = {
        "model": modele,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": CONSIGNE},
            {"role": "user", "content": prompt_faits(faits)},
        ],
    }
    derniere_erreur = None
    for _ in range(2):  # un essai, puis une relance si le JSON est invalide
        req = urllib.request.Request(
            api.rstrip("/") + "/chat/completions",
            data=json.dumps(corps).encode(),
            headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {cle}"} if cle else {})},
        )
        with urllib.request.urlopen(req, timeout=delai) as rep:
            donnees = json.load(rep)
        texte = donnees["choices"][0]["message"]["content"]
        try:
            return valider(extraire_json(texte))
        except (ValueError, json.JSONDecodeError) as e:
            derniere_erreur = e
            corps["messages"] += [
                {"role": "assistant", "content": texte},
                {"role": "user", "content": f"Réponse invalide ({e}). Renvoie seulement l'objet JSON demandé."},
            ]
    raise ValueError(f"le modèle n'a pas produit de JSON valide : {derniere_erreur}")


# --- Écriture de la fiche ----------------------------------------------------

def entete(champs: dict) -> str:
    # Chaque valeur est écrite en JSON sur une ligne : c'est du YAML valide,
    # et le registre peut le relire sans dépendance.
    return "---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in champs.items()) + "---\n"


def ecrire_fiche(faits: dict, ia: dict | None, modele: str | None) -> tuple[str, str]:
    ident = slug(faits["nom"])
    maintenant = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    champs = {
        "schema": SCHEMA,
        "id": ident,
        "titre": faits["nom"],
        "depot": faits["origine"],
        "commit": faits["commit"],
        "date_fiche": maintenant,
        "statut": statut(faits),
        "periode": [(faits["premier_commit"] or "")[:10], (faits["dernier_commit"] or "")[:10]],
        "nb_commits": faits["nb_commits"],
        "nb_fichiers": faits["nb_fichiers"],
        "contributeurs": faits["contributeurs"],
        "extensions": faits["extensions"],
        "instructions_agents": faits["instructions_agents"],
        "licence": faits["licence"],
        "resume_court": ia["resume_court"] if ia else None,
        "mots_cles": ia["mots_cles"] if ia else [],
        "genere_par": {"modele": modele, "version_prompt": VERSION_PROMPT} if ia else None,
        "relu_par": None,
    }
    corps = [entete(champs), f"# {faits['nom']}\n"]
    if ia:
        corps += [
            "## Résumé\n", "> Rédigé par l'archiviste (modèle local), non relu.\n",
            ia["resume"].strip() + "\n",
            "## Chronologie\n",
            *(f"- **{e.get('periode', '?')}** : {e['fait']}" for e in ia.get("chronologie", [])),
            "", "## Pour reprendre le sujet\n", ia["pour_reprendre"].strip() + "\n",
        ]
    else:
        corps += ["## Résumé\n", "_Fiche factuelle : aucun résumé généré (mode --sans-ia)._\n"]
    corps += [
        "## Faits\n",
        f"- Commits : {faits['nb_commits']} ({champs['periode'][0]} → {champs['periode'][1]})",
        f"- Contributeurs : {', '.join(c['nom'] + ' (' + str(c['commits']) + ')' for c in faits['contributeurs'])}",
        f"- Fichiers suivis : {faits['nb_fichiers']}",
        f"- Instructions pour agents : {', '.join(faits['instructions_agents']) or 'aucune'}",
        f"- Licence : {faits['licence'] or 'aucune'}",
        "", "## Derniers commits\n",
        *(f"- {c['date']} · {c['auteur']} · {c['sujet']}" for c in faits["derniers_commits"][:10]),
        "",
    ]
    return ident, "\n".join(corps)


def lire_entete(chemin: Path) -> dict:
    texte = chemin.read_text(encoding="utf-8")
    if not texte.startswith("---\n"):
        return {}
    bloc = texte[4 : texte.index("\n---", 4)]
    champs = {}
    for ligne in bloc.splitlines():
        cle, _, valeur = ligne.partition(": ")
        champs[cle] = json.loads(valeur)
    return champs


# --- Commandes ---------------------------------------------------------------

def cmd_fiche(a: argparse.Namespace) -> int:
    faits = collecter(Path(a.depot))
    ia = None
    if not a.sans_ia:
        try:
            ia = rediger(faits, a.api, a.modele, a.cle or os.environ.get("LOCALAI_API_KEY"), a.delai)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as e:
            print(f"avertissement : rédaction IA impossible ({e}) ; fiche factuelle seule.", file=sys.stderr)
    ident, texte = ecrire_fiche(faits, ia, a.modele if ia else None)
    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    chemin = sortie / f"{ident}.md"
    chemin.write_text(texte, encoding="utf-8")
    print(chemin)
    return 0


def cmd_registre(a: argparse.Namespace) -> int:
    entrees = []
    for p in sorted(Path(a.dossier).glob("*.md")):
        e = lire_entete(p)
        if e.get("schema") == SCHEMA:
            entrees.append({k: e.get(k) for k in (
                "id", "titre", "depot", "statut", "periode", "resume_court",
                "mots_cles", "nb_commits", "commit", "date_fiche", "relu_par")} | {"fiche": p.name})
    registre = {"schema": "memnius/registre/v0", "genere_le": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "depots": entrees}
    Path(a.sortie).write_text(json.dumps(registre, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{a.sortie} : {len(entrees)} dépôt(s)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Archiviste Memnius, étape 1")
    sp = p.add_subparsers(dest="cmd", required=True)
    f = sp.add_parser("fiche", help="produit la fiche d'archive d'un dépôt")
    f.add_argument("depot")
    f.add_argument("-o", "--sortie", default="fiches")
    f.add_argument("--api", default=os.environ.get("LOCALAI_API", "http://localhost:8080/v1"))
    f.add_argument("--modele", default=os.environ.get("ARCHIVISTE_MODELE", "qwen3-8b"))
    f.add_argument("--cle", help="clé d'API LocalAI si l'instance en exige une")
    f.add_argument("--delai", type=int, default=600, help="secondes avant abandon de l'appel au modèle")
    f.add_argument("--sans-ia", action="store_true", help="n'appelle pas le modèle")
    f.set_defaults(func=cmd_fiche)
    r = sp.add_parser("registre", help="agrège les fiches en registre JSON")
    r.add_argument("dossier")
    r.add_argument("-o", "--sortie", default="registre.json")
    r.set_defaults(func=cmd_registre)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
