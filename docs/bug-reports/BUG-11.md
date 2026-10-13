# BUG-11 — Redirection ouverte après connexion via le paramètre ?next=

| Champ | Valeur |
|---|---|
| **Sévérité** | Majeure |
| **Priorité** | P2 |
| **Zone** | Sécurité / Authentification |
| **Cas de test** | TC-E10 |
| **Statut** | Ouvert — reproduit à chaque exécution de la campagne (base réinitialisée) |
| **Environnement** | QuickOrder V3.1 — Docker Compose (base réinitialisée par `docker compose down -v`), http://127.0.0.1:5000, Chromium (Playwright) 1280×900, Windows 11. |

## Contexte
Formulaire de connexion /login.

## Préconditions
Aucun.

## Étapes de reproduction
1. Envoyer POST /login?next=https://evil.example.com/phishing avec des identifiants valides.
2. Lire l'en-tête Location de la réponse.

## Résultat attendu
Redirection vers une URL interne uniquement (next externe ignoré → /).

## Résultat obtenu
HTTP 302, Location: https://evil.example.com/phishing. Un lien piégé peut renvoyer un utilisateur fraîchement connecté vers un site d'hameçonnage.

## Preuves
- [`TC-E10.json`](../evidence/TC-E10.json)

## Analyse (cause probable dans le code)
`auth.login` : `redirect(request.args.get("next") or ...)` sans validation du domaine.
