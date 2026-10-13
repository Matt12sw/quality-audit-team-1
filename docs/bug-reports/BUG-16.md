# BUG-16 — API : les erreurs 404 sont renvoyées en HTML au lieu de JSON

| Champ | Valeur |
|---|---|
| **Sévérité** | Mineure |
| **Priorité** | P3 |
| **Zone** | API |
| **Cas de test** | TC-E04 |
| **Statut** | Ouvert — reproduit à chaque exécution de la campagne (base réinitialisée) |
| **Environnement** | QuickOrder V3.1 — Docker Compose (base réinitialisée par `docker compose down -v`), http://127.0.0.1:5000, Chromium (Playwright) 1280×900, Windows 11. |

## Contexte
API REST, ressource inexistante.

## Préconditions
Clé API valide.

## Étapes de reproduction
1. GET /api/products/9999 avec X-API-Key.

## Résultat attendu
HTTP 404, Content-Type application/json, corps {"error": "product not found"}.

## Résultat obtenu
HTTP 404, Content-Type text/html, page Werkzeug « Not Found ». Les clients API ne peuvent pas parser l'erreur.

## Preuves
- [`TC-E04.json`](../evidence/TC-E04.json)

## Analyse (cause probable dans le code)
`get_or_404` sans gestionnaire d'erreur JSON sur le blueprint API.
