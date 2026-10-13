# BUG-04 — API : une quantité supérieure au stock est acceptée et le stock devient négatif

| Champ | Valeur |
|---|---|
| **Sévérité** | Critique |
| **Priorité** | P1 |
| **Zone** | API / Stock |
| **Cas de test** | TC-L06 |
| **Statut** | Ouvert — reproduit à chaque exécution de la campagne (base réinitialisée) |
| **Environnement** | QuickOrder V3.1 — Docker Compose (base réinitialisée par `docker compose down -v`), http://127.0.0.1:5000, Chromium (Playwright) 1280×900, Windows 11. |

## Contexte
API REST POST /orders.

## Préconditions
Clé API valide ; Salmon Bowl (id 7) en stock 2.

## Étapes de reproduction
1. GET /api/products/7 → stock 2.
2. POST /api/orders {"items":[{"product_id":7,"quantity":3}],"payment_method":"card"}.
3. GET /api/products/7.

## Résultat attendu
HTTP 409 « stock insuffisant » ; stock inchangé (2).

## Résultat obtenu
HTTP 201, commande #3 confirmed pour 3 Salmon Bowl ; stock après = -1.

## Preuves
- [`TC-L06.json`](../evidence/TC-L06.json)

## Analyse (cause probable dans le code)
`create_order_api()` vérifie `product.available` mais jamais `product.stock >= quantity`.
