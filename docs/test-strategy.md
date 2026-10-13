# Stratégie de test — QuickOrder V3.1

**Équipe :** quality-audit-team-1 · **Date :** 13/10/2026 · **Version testée :** QuickOrder V3.1 (Docker Compose)

## 1. Contexte et objectif

QuickOrder est une plateforme de commande de repas (Flask, SQLAlchemy, SQLite) : catalogue de restaurants, panier mono-restaurant, coupons, checkout avec paiement simulé (carte, PayPal, espèces), suivi et annulation de commande, avis, espace profil, back-office administrateur et API REST documentée sous Swagger.

L'équipe QA intervient **avant la mise en production**. Elle ne reconstruit pas l'application : elle évalue sa qualité, prouve les anomalies et émet une recommandation **Go / No-Go**. Le code source n'est pas modifié pendant la campagne.

## 2. Périmètre

| Domaine | Fonctionnalités couvertes | Canal |
|---|---|---|
| Comptes | Inscription, connexion, déconnexion, rôles client et admin | UI, HTTP |
| Catalogue | Liste des restaurants, recherche, filtres (catégorie, frais de livraison, végétarien), tri, fiche restaurant, statut ouvert/fermé | UI, API |
| Panier | Ajout, règle mono-restaurant, mise à jour des quantités, suppression, stock | UI, DevTools |
| Coupons | Validation, minimum de commande, expiration, plafond de réduction, promotions annoncées | UI, API |
| Checkout et paiement | Adresse, minimum de commande, restaurant fermé, paiement carte, PayPal et espèces, création de commande | UI, API, réseau |
| Commandes | Liste, détail, annulation, cycle de vie des statuts | UI, API |
| Avis | Dépôt d'avis et de notes | UI |
| Administration | Contrôle d'accès, changement de statut | UI |
| API REST | Clé API, codes HTTP, format JSON, validations (quantité, stock, coupon, paiement) | Swagger, requêtes HTTP |
| Sécurité applicative (premier niveau) | Contrôle d'accès, redirection après connexion, confiance accordée aux données client | HTTP |

## 3. Hors périmètre

- Tests de performance, de charge et d'endurance (application pédagogique, SQLite mono-fichier).
- Sécurité approfondie : pentest complet, CSRF systématique, force brute, en-têtes HTTP. Seuls les constats évidents rencontrés en route sont signalés.
- Accessibilité RGAA complète et compatibilité multi-navigateurs ou mobile. La campagne est exécutée sur Chromium desktop 1280×900.
- Vrais prestataires de paiement : le paiement est simulé.
- Favoris, profil et adresses multiples : tests exploratoires seulement, sans cas formalisés.
- Les tests unitaires existants (`pytest`) ne sont ni réécrits ni étendus.

## 4. Parcours critiques

Ordre décroissant de criticité métier :

1. **Commander et payer** : panier → checkout → paiement → commande confirmée. C'est là que se jouent le chiffre d'affaires et la confiance client.
2. **Cohérence des montants** : sous-total, frais de livraison, coupon, plafond, minimum de commande, rendu de monnaie.
3. **Disponibilité** : restaurant ouvert, produit en stock, quantité ≤ stock.
4. **Suivi de commande** : statuts, annulation, actions de l'administrateur.
5. **Se connecter** et accéder à son propre espace uniquement.
6. **Trouver un restaurant** : recherche, filtres, tri.
7. **API partenaires** : authentification, contrats JSON, mêmes règles métier que l'interface.

## 5. Risques identifiés

| ID | Risque | Conséquence en production |
|---|---|---|
| R1 | Authentification et gestion des comptes défaillantes | Accès impossible ou usurpation de compte |
| R2 | Commande ou paiement incorrect (double débit, montant non couvert, commande invalide) | Perte financière, litiges, remboursements |
| R3 | Panier incohérent (multi-restaurant, suppression impossible) | Commandes erronées, abandon de panier |
| R4 | Cycle de vie de commande incohérent (annulation, statuts) | Livraisons fantômes, litiges |
| R5 | Réductions mal calculées ou promotions trompeuses | Perte de marge, publicité mensongère |
| R6 | Recherche et filtres erronés | Mauvaise expérience, baisse de conversion |
| R7 | Stock non maîtrisé | Ventes de produits indisponibles, annulations côté restaurant |
| R8 | API non conforme (authentification, format d'erreur, validations) | Intégrations partenaires cassées |
| R9 | Failles de contrôle d'accès ou de redirection | Fuite de données, hameçonnage |
| R10 | Avis non fiables | Atteinte à la réputation des restaurants |

La cotation probabilité × impact se trouve dans [risk-matrix.md](risk-matrix.md).

## 6. Types de tests

| Type | Application dans la campagne | Outils |
|---|---|---|
| Tests fonctionnels boîte noire (UI) | Parcours nominaux, limites, erreurs, règles métier | Chromium piloté par Playwright, captures pleine page |
| Tests aux limites | Bornes des coupons (19,99 / 20,00), quantités (0, 21), stock (stock+1, stock 0), filtres | Swagger, requêtes HTTP, UI |
| Tests d'erreur et négatifs | Identifiants faux, clé API absente ou fausse, ID inexistant, coupon expiré, espèces insuffisantes | UI, API |
| Tests de règles métier | Mono-restaurant, restaurant fermé, minimum, promotions, PayPal, statuts, avis, adresse | UI, API |
| Tests API REST | Codes HTTP, contenu JSON, cohérence avec l'interface | Swagger UI, `requests` (Python), collection Postman fournie |
| Tests DevTools | Contournement des contraintes HTML (`max`), inspection des requêtes réseau, console | Évaluation JS dans la page, journalisation réseau et console |
| Revue statique ciblée | Lecture du code pour expliquer la cause probable d'un échec, sans modification | Lecture du dépôt |
| Tests utilisateurs | 3 scénarios joués par 2 personnes, observation et verbatims | Protocole dans [user-feedback.md](user-feedback.md) |
| Re-test et non-régression | Le script `scripts/run_campaign.py` rejoue l'intégralité de la campagne | Playwright + Python |

## 7. Priorisation risque × impact

- **Probabilité** (1 faible · 2 moyenne · 3 forte) : fréquence d'usage du parcours et complexité des règles.
- **Impact** (1 mineur · 2 significatif · 3 majeur · 4 critique) : conséquence financière, légale ou d'image.
- **Score = P × I.** De 9 à 12 : priorité 1, testée en premier et en profondeur (cas limites et erreurs). De 5 à 8 : priorité 2, cas nominaux et principales limites. De 1 à 4 : priorité 3, cas nominal ou exploratoire.

L'effort de test suit cette priorisation : **18 cas sur 37 couvrent R2, R5 et R7**, les trois risques les mieux cotés.

## 8. Organisation de la campagne

| Étape | Livrable |
|---|---|
| Analyse produit et code, identification des parcours | Cette stratégie, [risk-matrix.md](risk-matrix.md) |
| Conception de 37 cas (7 nominaux, 8 limites, 11 erreurs, 11 règles métier) | [test-cases.xlsx](test-cases.xlsx) |
| Exécution sur base propre (`docker compose down -v && docker compose up --build`) | [evidence/](evidence/), [execution-report.md](execution-report.md) |
| Rédaction des anomalies | [bug-reports/](bug-reports/README.md) |
| Tests utilisateurs | [user-feedback.md](user-feedback.md) |
| Recommandations | [improvement-plan.md](improvement-plan.md) |

**Critères d'entrée :** application démarrée, `GET /api/health` = 200, base issue du seed.

**Critères de sortie :** tous les cas exécutés ou justifiés (Blocked ou Skipped), chaque échec rattaché à un bug reproductible et prouvé.

**Critères de Go :** aucune anomalie bloquante ou critique ouverte, aucune anomalie majeure ouverte sur le parcours de paiement, taux de réussite des cas P1 ≥ 95 %.

**Environnement :** Windows 11, Docker 29.5, image `python:3.12` (Werkzeug 3.1.3), Chromium (Playwright), données du `seed.py` (alice, bob, admin, 6 restaurants, 6 coupons).
