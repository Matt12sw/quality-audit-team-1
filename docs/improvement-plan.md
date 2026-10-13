# Plan d'amélioration — QuickOrder V3.1

Les améliorations sont priorisées selon **la valeur (risque évité) rapportée à l'effort**.

- **Valeur** de 1 à 5 : gravité et fréquence des anomalies couvertes, impact financier, légal ou d'image.
- **Effort** de 1 à 5 : estimation de développement et de test. 1 correspond à moins d'une demi-journée.
- **Indice = valeur / effort.** À indice égal, le risque le plus grave l'emporte.

| Rang | ID | Amélioration | Bugs / constats couverts | Valeur | Effort | Indice | Priorité |
|:-:|---|---|---|:-:|:-:|:-:|:-:|
| 1 | AM-01 | Supprimer la création de commande en double pour PayPal et rendre la création idempotente | BUG-01 | 5 | 1 | **5,0** | P1 |
| 2 | AM-02 | Centraliser les règles de commande dans un service unique, partagé par l'UI et l'API | BUG-02, 03, 04, 05, 06, 07, 09 | 5 | 3 | **1,7** | P1 |
| 3 | AM-03 | Gestion fiable du stock : contrôle à l'ajout, à la mise à jour et au paiement, décrément atomique, stock ≥ 0 en base | BUG-04, 05 | 5 | 2 | **2,5** | P1 |
| 4 | AM-04 | Adresse complète obligatoire avant paiement | BUG-07 | 4 | 1 | **4,0** | P1 |
| 5 | AM-05 | Aligner promotions et coupons : corriger ATLAS15 et générer le texte promo à partir du coupon | BUG-08, 17 | 4 | 1 | **4,0** | P2 |
| 6 | AM-06 | Durcir la sécurité : redirection `next` limitée aux URL internes, protection CSRF, clés API par client | BUG-11 + constats | 4 | 2 | **2,0** | P2 |
| 7 | AM-07 | Machine à états des statuts de commande et simulateur de paiement en échec | BUG-10, TC-E11 | 3 | 2 | **1,5** | P2 |
| 8 | AM-08 | Corriger la recherche et les filtres (frais ≤, recherche dans la description, restaurants fermés signalés dans l'API) | BUG-12, 14 | 3 | 1 | **3,0** | P2 |
| 9 | AM-12 | Intégrer la campagne en CI : tests automatisés sur chaque PR (pytest + Playwright) | Prévention des régressions | 4 | 2 | **2,0** | P2 |
| 10 | AM-09 | Ergonomie du panier : bouton Supprimer par ligne, produits épuisés non ajoutables, message clair | BUG-15, BUG-05 (UX) | 2 | 1 | **2,0** | P3 |
| 11 | AM-10 | Contrat d'API homogène : erreurs JSON pour 404/405/500, codes HTTP documentés dans l'OpenAPI | BUG-16 | 2 | 1 | **2,0** | P3 |
| 12 | AM-11 | Avis réservés aux clients ayant une commande livrée chez le restaurant | BUG-13 | 2 | 1 | **2,0** | P3 |

L'ordre ne suit pas strictement l'indice. AM-02 et AM-03 passent avant des améliorations à meilleur indice parce qu'elles bloquent la mise en production (critères de Go) et qu'elles conditionnent la correction de 7 anomalies, dont 4 critiques.

---

## Détail et justification

### AM-01 — PayPal : une commande par paiement (P1)
- **Problème :** chaque paiement PayPal crée 2 commandes, avec double débit et double préparation (TC-R05).
- **Proposition :** supprimer le second `build_order` dans `orders.checkout` et `api.create_order_api`. Ajouter une clé d'idempotence par checkout, par exemple un jeton en session ou l'en-tête `Idempotency-Key` côté API, pour résister aussi aux doubles clics.
- **Justification :** c'est l'anomalie la plus grave pour l'effort le plus faible. Elle touche directement l'argent du client.
- **Critère d'acceptation :** TC-R05 passe : +1 commande, stock décrémenté une seule fois.

### AM-02 — Service de validation de commande unique (P1)
- **Problème :** l'UI et l'API dupliquent la logique de commande, et aucune des deux n'applique les règles métier : restaurant ouvert, minimum, stock, espèces suffisantes, coupon non expiré, adresse.
- **Proposition :** créer `OrderService.validate_and_create(cart, user, payment)`, qui lève des erreurs métier explicites. L'UI les affiche en message flash ; l'API les traduit en 400 ou 409 JSON.
- **Justification :** couvre 7 anomalies d'un coup et rend impossible toute divergence future entre UI et API (cf. BUG-09 : coupon refusé par `/coupons/validate` mais appliqué par `/orders`).
- **Critère d'acceptation :** TC-E06, TC-E08, TC-L06, TC-R02, TC-R03 et TC-R11 passent, en UI comme en API.

### AM-03 — Stock fiable (P1)
- **Problème :** produits à stock 0 ajoutables, quantités illimitées, stock négatif (-1, -400).
- **Proposition :** contrôler `quantity ≤ stock` à l'ajout, à la mise à jour et au paiement. Utiliser une décrémentation conditionnelle (`UPDATE … WHERE stock >= :q`) et une contrainte `CHECK (stock >= 0)`. Côté UI, désactiver le bouton « Ajouter » d'un produit épuisé.
- **Justification :** le stock négatif signifie des commandes payées que le restaurant ne pourra pas servir.
- **Critère d'acceptation :** TC-L06, TC-L07 et TC-L08 passent.

### AM-04 — Adresse de livraison obligatoire (P1)
- **Problème :** l'inscription crée une adresse vide, sélectionnée par défaut au checkout (TC-R11).
- **Proposition :** ne plus créer d'adresse vide à l'inscription. Au checkout, exiger ou proposer la saisie d'une adresse complète, avec code postal à 5 chiffres.
- **Justification :** une commande payée sans adresse ne peut pas être livrée. Ce cas touche tous les nouveaux clients dès leur première commande, le moment le plus sensible pour la rétention.

### AM-05 — Cohérence des promotions (P2)
- **Problème :** ATLAS15 est annoncé à -15 % et appliqué à -10 %. Le texte promo est saisi en dur, indépendamment du coupon.
- **Proposition :** corriger la donnée (15 %). Générer le bandeau promo à partir du coupon, avec pourcentage, minimum et plafond. Calculer la remise côté serveur à partir du panier, sans `subtotal` client (BUG-17).
- **Justification :** risque légal (pratique commerciale trompeuse) et perte de confiance. La correction des données est immédiate.

### AM-06 — Sécurité applicative (P2)
- **Problème :** redirection ouverte via `?next=` (TC-E10). Constats annexes : formulaires sans jeton CSRF, déconnexion en `GET`, clé API unique partagée qui agit toujours au nom d'Alice.
- **Proposition :** valider `next` (chemin relatif, même hôte). Activer Flask-WTF CSRF. Passer la déconnexion en `POST`. Émettre une clé API par client ou partenaire.
- **Justification :** l'hameçonnage par lien piégé est trivial à exploiter. Une clé partagée empêche toute traçabilité.

### AM-07 — Statuts et simulateur de paiement (P2)
- **Problème :** l'admin peut faire revenir une commande livrée à « confirmed » (TC-R06). Le refus de paiement est impossible à tester (TC-E11 bloqué).
- **Proposition :** définir une table de transitions autorisées (confirmed → preparing → out_for_delivery → delivered, annulation possible avant out_for_delivery). Journaliser l'historique. Ajouter une option « Carte bancaire — refus » au simulateur.
- **Justification :** rend le suivi fiable et permet de tester le chemin d'échec du paiement, aujourd'hui aveugle.

### AM-08 — Recherche et filtres (P2)
- **Problème :** le filtre de frais de livraison est inversé et la recherche ignore la description.
- **Proposition :** utiliser `delivery_fee <= max`. Rechercher sur `name OR description OR category`. Exposer `is_open` et un paramètre `open=true` dans l'API.
- **Justification :** correction d'une ligne pour un parcours d'entrée très fréquent. Le filtre actuel montre exactement les mauvais restaurants.

### AM-09 à AM-11 — Finitions (P3)
- **AM-09 :** ajouter un bouton « Supprimer » par ligne de panier (la route existe déjà) et corriger le formulaire imbriqué.
- **AM-10 :** déclarer un gestionnaire d'erreurs JSON sur le blueprint API, pour qu'un client API puisse toujours parser la réponse.
- **AM-11 :** exiger une commande livrée pour publier un avis et lier l'avis à `order_id`.

### AM-12 — Automatiser la non-régression (P2)
- **Proposition :** intégrer `scripts/run_campaign.py`, adapté en tests pytest-playwright, au pipeline CI, avec une base réinitialisée à chaque exécution.
- **Justification :** les 37 cas sont déjà automatisés. Les rejouer à chaque modification garantit que les corrections P1 ne réintroduisent pas d'anomalies et accélère la re-validation avant le Go.
