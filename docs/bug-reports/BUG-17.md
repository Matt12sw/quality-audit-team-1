# BUG-17 — API /coupons/validate fait confiance au sous-total envoyé par le client

| Champ | Valeur |
|---|---|
| **Sévérité** | Mineure |
| **Priorité** | P3 |
| **Zone** | API / Coupons |
| **Cas de test** | TC-R09 |
| **Statut** | Ouvert — reproduit à chaque exécution de la campagne (base réinitialisée) |
| **Environnement** | QuickOrder V3.1 — Docker Compose (base réinitialisée par `docker compose down -v`), http://127.0.0.1:5000, Chromium (Playwright) 1280×900, Windows 11. |

## Contexte
API POST /coupons/validate.

## Préconditions
Clé API valide ; panier d'Alice vide.

## Étapes de reproduction
1. POST /api/coupons/validate {"code":"SAVE20","subtotal":9999}.

## Résultat attendu
Le serveur calcule le sous-total à partir du panier réel (ou refuse).

## Résultat obtenu
HTTP 200 {valid: true, discount: 12.0} pour un sous-total fictif. Le front peut afficher une réduction qui ne sera pas appliquée ; surface d'abus si la réponse est réutilisée.

## Preuves
- [`TC-R09.json`](../evidence/TC-R09.json)

## Analyse (cause probable dans le code)
`validate_coupon()` lit `payload["subtotal"]`.
