# BUG-09 — API : un coupon expiré est appliqué lors de la création de commande

| Champ | Valeur |
|---|---|
| **Sévérité** | Majeure |
| **Priorité** | P2 |
| **Zone** | API / Coupons |
| **Cas de test** | TC-E06 |
| **Statut** | Ouvert — reproduit à chaque exécution de la campagne (base réinitialisée) |
| **Environnement** | QuickOrder V3.1 — Docker Compose (base réinitialisée par `docker compose down -v`), http://127.0.0.1:5000, Chromium (Playwright) 1280×900, Windows 11. |

## Contexte
API POST /orders avec un champ coupon.

## Préconditions
Coupon EXPIRED10 expiré (refusé par /coupons/validate, cf. TC-E05).

## Étapes de reproduction
1. POST /api/orders {"items":[{"product_id":20,"quantity":2}],"coupon":"EXPIRED10","payment_method":"card"}.

## Résultat attendu
HTTP 400 « coupon expiré » ou discount = 0.

## Résultat obtenu
HTTP 201, commande #4 avec discount = 3,58 € (10 % appliqué). Incohérence avec /coupons/validate qui refuse ce même coupon.

## Preuves
- [`TC-E06.json`](../evidence/TC-E06.json)
- [`TC-E05.json`](../evidence/TC-E05.json)

## Analyse (cause probable dans le code)
`create_order_api()` filtre sur `active=True` mais ne teste pas `expires_at`.
