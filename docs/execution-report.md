# Rapport d'exécution et analyse de campagne — QuickOrder V3.1

**Équipe :** quality-audit-team-1 · **Date d'exécution :** 13/10/2026 · **Build :** QuickOrder V3.1 (Docker Compose, base seed réinitialisée avant chaque passage)

## 1. Conditions d'exécution

| Élément | Valeur |
|---|---|
| Application | http://127.0.0.1:5000 (conteneur `quickorder`, Werkzeug 3.1.3 / Python 3.12) |
| Swagger | http://127.0.0.1:5000/docs/ avec la clé `X-API-Key: quickorder-demo-key` |
| Navigateur | Chromium (Playwright), 1280×900, locale fr-FR |
| Outils | Navigateur, Swagger UI, DevTools (exécution JS dans la page, capture réseau et console), client HTTP Python `requests` |
| Comptes | alice@example.com, bob@example.com (clients) ; admin@quickorder.local (admin) ; un compte créé pendant TC-R11 |
| Exécution | `scripts/run_campaign.py` : chaque cas exécute les étapes décrites dans `test-cases.xlsx`, compare le résultat à l'attendu et enregistre les preuves dans `docs/evidence/` |
| Reproductibilité | Campagne complète rejouée 3 fois sur base propre. Comportements de l'application identiques à chaque passage, hors horodatages. Au 1er passage, TC-N05 avait échoué à cause d'un sélecteur erroné dans le script de test, corrigé ensuite ; ce n'était pas un défaut de l'application. |

## 2. Résultats chiffrés

| Type | Total | ✅ Pass | ❌ Fail | ⛔ Blocked | ⏭️ Skipped |
|---|:-:|:-:|:-:|:-:|:-:|
| Nominal | 7 | 6 | 1 | 0 | 0 |
| Limite | 8 | 4 | 4 | 0 | 0 |
| Erreur | 11 | 6 | 4 | 1 | 0 |
| Règle métier | 11 | 2 | 9 | 0 | 0 |
| **Total** | **37** | **18 (49 %)** | **18 (49 %)** | **1 (3 %)** | **0** |

- **Taux d'exécution :** 36 cas sur 37 (97 %).
- **Taux de réussite des cas exécutés :** 18 sur 36 (50 %).
- **Anomalies :** 17 bug reports, dont **1 bloquante, 4 critiques, 7 majeures et 5 mineures**.
- **Règles métier :** 9 sur 11 en échec. Le moteur de règles (stock, minimum, statut du restaurant, paiement) est le point le plus faible.

### Détail par cas

| ID | Titre | Statut | Bug |
|---|---|:-:|---|
| TC-N01 | Connexion client valide | ✅ Pass | |
| TC-N02 | Recherche par nom « Pizza » | ✅ Pass | |
| TC-N03 | Ajout au panier et calcul du total | ✅ Pass | |
| TC-N04 | Commande carte + WELCOME10 | ✅ Pass | |
| TC-N05 | API GET /restaurants via Swagger | ✅ Pass | |
| TC-N06 | Annulation d'une commande confirmed | ✅ Pass | |
| TC-N07 | Suppression d'un produit du panier | ❌ Fail | [BUG-15](bug-reports/BUG-15.md) |
| TC-L01 | Filtre Livraison max ≤ 2,50 € | ❌ Fail | [BUG-12](bug-reports/BUG-12.md) |
| TC-L02 | WELCOME10 à 19,99 / 20,00 € | ✅ Pass | |
| TC-L03 | Plafond de réduction WELCOME10 | ✅ Pass | |
| TC-L04 | API quantité 0 | ✅ Pass | |
| TC-L05 | API quantité 21 | ✅ Pass | |
| TC-L06 | API quantité > stock | ❌ Fail | [BUG-04](bug-reports/BUG-04.md) |
| TC-L07 | UI quantité 500 via DevTools | ❌ Fail | [BUG-05](bug-reports/BUG-05.md) |
| TC-L08 | Ajout d'un produit en stock 0 | ❌ Fail | [BUG-05](bug-reports/BUG-05.md) |
| TC-E01 | Mot de passe incorrect | ✅ Pass | |
| TC-E02 | API sans clé | ✅ Pass | |
| TC-E03 | API clé incorrecte | ✅ Pass | |
| TC-E04 | API produit inexistant (format 404) | ❌ Fail | [BUG-16](bug-reports/BUG-16.md) |
| TC-E05 | API coupon expiré (validation) | ✅ Pass | |
| TC-E06 | API commande avec coupon expiré | ❌ Fail | [BUG-09](bug-reports/BUG-09.md) |
| TC-E07 | Inscription avec email existant | ✅ Pass | |
| TC-E08 | Espèces : montant insuffisant | ❌ Fail | [BUG-02](bug-reports/BUG-02.md) |
| TC-E09 | Accès /admin par un client | ✅ Pass | |
| TC-E10 | Redirection ouverte ?next= | ❌ Fail | [BUG-11](bug-reports/BUG-11.md) |
| TC-E11 | Paiement carte refusé | ⛔ Blocked | voir § 3 |
| TC-R01 | Panier mono-restaurant | ✅ Pass | |
| TC-R02 | Commande dans un restaurant fermé | ❌ Fail | [BUG-03](bug-reports/BUG-03.md) |
| TC-R03 | Minimum de commande | ❌ Fail | [BUG-06](bug-reports/BUG-06.md) |
| TC-R04 | ATLAS15 annoncé à -15 % | ❌ Fail | [BUG-08](bug-reports/BUG-08.md) |
| TC-R05 | PayPal : une seule commande | ❌ Fail | [BUG-01](bug-reports/BUG-01.md) |
| TC-R06 | Admin : delivered → confirmed | ❌ Fail | [BUG-10](bug-reports/BUG-10.md) |
| TC-R07 | Avis sans commande | ❌ Fail | [BUG-13](bug-reports/BUG-13.md) |
| TC-R08 | Annulation d'une commande livrée | ✅ Pass | |
| TC-R09 | Sous-total fourni par le client | ❌ Fail | [BUG-17](bug-reports/BUG-17.md) |
| TC-R10 | Recherche sur la description | ❌ Fail | [BUG-14](bug-reports/BUG-14.md) |
| TC-R11 | Adresse de livraison obligatoire | ❌ Fail | [BUG-07](bug-reports/BUG-07.md) |

Le résultat obtenu détaillé et les preuves de chaque cas sont dans [test-cases.xlsx](test-cases.xlsx), colonnes « Résultat obtenu » et « Preuves ».

## 3. Cas bloqués et non exécutés

- **TC-E11 (Blocked)** : le simulateur de paiement ne propose que « Carte bancaire — succès », « PayPal — succès » et « Espèces ». Il est impossible de provoquer un refus. Dans le code, `payment_ok` vaut toujours `True`, donc le statut `payment_failed`, pourtant prévu dans le filtre « Mes commandes », n'est jamais atteignable. **Ce chemin critique n'est donc pas testé.** Un mode de refus doit être ajouté au simulateur (voir [improvement-plan.md](improvement-plan.md), AM-07).
- **Skipped : aucun.** Les éléments volontairement non couverts (performance, accessibilité, multi-navigateurs) sont déclarés hors périmètre dans la stratégie. Ils ne sont pas comptés comme Skipped.

## 4. Observations DevTools

- **Contraintes uniquement côté client :** la quantité d'un produit n'est limitée que par l'attribut HTML `max=99` sur la fiche et `max=stock` dans le panier. En le retirant dans la console (`evidence/TC-L07_devtools.js`), le serveur accepte 500 unités (BUG-05).
- **Réseau :** la requête de paiement en espèces est un simple `POST /checkout` avec `payment_method=cash&cash_received=1&confirm=1` (`evidence/TC-E08_network.json`). Aucune validation n'a lieu côté serveur.
- **Console :** aucune erreur JavaScript sur les pages de l'application (`evidence/console.log`). Seul avertissement relevé : une dépréciation de Swagger UI sur le format des deep links. Sans impact.
- **HTML invalide :** le panier contient un `<form></form>` vide imbriqué dans un autre formulaire (BUG-15).
- **Dépendance externe :** Swagger UI est chargé depuis `unpkg.com`, avec une version flottante `@5`. La documentation de l'API est indisponible hors ligne.

## 5. Principaux risques

1. **Pertes financières directes** : double commande PayPal (BUG-01), espèces non couvertes (BUG-02), réductions appliquées à tort (BUG-09).
2. **Commandes impossibles à honorer** : restaurant fermé (BUG-03), produits épuisés et stock négatif (BUG-04, BUG-05), adresse vide (BUG-07), minimum non respecté (BUG-06). Elles entraînent annulations, remboursements et perte de confiance des restaurants partenaires.
3. **Risque légal et d'image** : promotion annoncée à -15 % mais appliquée à -10 % (BUG-08, pratique commerciale trompeuse), avis sans achat (BUG-13).
4. **Sécurité** : redirection ouverte exploitable pour de l'hameçonnage (BUG-11). La clé API est unique et partagée ; tous les appels agissent au nom d'Alice.
5. **Fiabilité des opérations** : statuts modifiables à rebours par l'admin (BUG-10) et chemin d'échec de paiement non testable (TC-E11).

## 6. Points positifs

- L'authentification, le contrôle d'accès à `/admin` et l'unicité des comptes sont conformes.
- Le calcul des coupons est juste sur l'endpoint de validation : bornes du minimum, plafond, expiration.
- La validation des quantités de l'API (1 à 20) et l'authentification par clé (401) sont correctes.
- La règle du panier mono-restaurant et le refus d'annuler une commande livrée fonctionnent.

## 7. Recommandation : ❌ NO-GO

**La mise en production est déconseillée en l'état.** Aucun des critères de Go définis dans la stratégie n'est atteint :

| Critère de Go | Constat |
|---|---|
| Aucune anomalie bloquante ou critique ouverte | ❌ 1 bloquante + 4 critiques |
| Aucune anomalie majeure ouverte sur le paiement | ❌ BUG-01, 02, 06, 07 |
| ≥ 95 % de réussite sur les cas P1 (R2, R5, R7) | ❌ 6 sur 17 exécutés (35 %) |

**Conditions pour réévaluer en Go :**
1. Corriger les anomalies P1 : BUG-01 à BUG-07.
2. Ajouter un scénario de refus de paiement et débloquer TC-E11.
3. Rejouer intégralement la campagne avec `scripts/run_campaign.py` : la re-validation des 18 échecs plus la non-régression des 18 succès est automatisée.
4. Traiter les P2 (BUG-08 à BUG-12) avant ou juste après la mise en production, selon une décision du métier (communication sur ATLAS15, sécurité).
