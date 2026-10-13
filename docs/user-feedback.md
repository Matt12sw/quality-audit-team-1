# Tests utilisateurs — QuickOrder V3.1

> ⚠️ **Statut : protocole prêt, sessions à réaliser.** Les sections « Participants » et « Résultats » se remplissent avec les observations réelles des sessions. Aucun verbatim ne doit être inventé.

## 1. Objectif

Observer de vrais utilisateurs sur les parcours critiques afin de repérer les problèmes d'**utilisabilité** et de **compréhension**, que les tests fonctionnels ne révèlent pas, et de confirmer ou d'infirmer l'impact perçu des anomalies déjà trouvées.

## 2. Protocole

- **Participants :** au moins 2 personnes, idéalement de profils différents (une personne à l'aise avec les applications de livraison, une personne peu technophile). Ni l'une ni l'autre ne doit connaître QuickOrder.
- **Matériel :** ordinateur avec QuickOrder lancé sur une base propre (`docker compose down -v && docker compose up --build`), compte `bob@example.com` / `Password123!`.
- **Durée :** 15 à 20 minutes par personne.
- **Méthode :** « penser à voix haute ». L'observateur lit la consigne, n'aide pas, chronomètre et note les hésitations, erreurs et citations exactes.
- **Après chaque scénario :** note de facilité de 1 (très difficile) à 5 (très facile) et une question ouverte : « Qu'est-ce qui vous a gêné ? ».

## 3. Scénarios

| # | Consigne lue au participant | Ce que l'on observe | Critère de réussite |
|---|---|---|---|
| **S1** | « Vous voulez un repas végétarien livré pour moins de 2,50 € de frais de livraison. Trouvez un restaurant et ajoutez un plat à votre panier. » | Usage des filtres Végétarien et Livraison max (BUG-12), compréhension du badge HORS STOCK (BUG-05) | Un plat végétarien en stock d'un restaurant à ≤ 2,50 € est dans le panier en moins de 3 min |
| **S2** | « Chez Couscous Atlas, commandez de quoi manger pour 2 personnes en utilisant la réduction proposée par le restaurant, puis payez par carte. » | Lecture de la promotion ATLAS15, perception de la réduction réellement appliquée (BUG-08), du minimum de commande et du récapitulatif | Commande confirmée ; le participant sait dire combien il a économisé |
| **S3** | « Vous vous êtes trompé : retirez un des produits de votre panier, puis passez commande en payant en espèces avec un billet de 20 €. » | Découvrabilité de la suppression (BUG-15), compréhension du champ espèces et du rendu de monnaie (BUG-02 si total > 20 €) | Produit retiré et commande passée avec un rendu de monnaie correct ou un refus explicite |

## 4. Grille de restitution (à remplir par observation)

| Champ | Description |
|---|---|
| **Profil** | Âge approximatif, aisance numérique (1 à 5), usage des applications de livraison |
| **Contexte** | Scénario, appareil, durée, succès ou échec, note de facilité |
| **Problème** | Ce qui a bloqué ou fait hésiter (observé, pas supposé) |
| **Fréquence** | Nombre de participants concernés (ex. 2/2) |
| **Impact** | Bloquant / gênant / cosmétique |
| **Verbatim** | Citation exacte entre guillemets |
| **Hypothèse d'amélioration** | Changement proposé pour lever le problème |
| **Priorité** | Haute / moyenne / basse |

## 5. Participants

| ID | Profil | Aisance numérique | Utilise des applis de livraison | Date |
|---|---|:-:|---|---|
| P1 | _à compléter_ | | | |
| P2 | _à compléter_ | | | |

## 6. Résultats par scénario

| Scénario | P1 : réussite / durée / note | P2 : réussite / durée / note |
|---|---|---|
| S1 | | |
| S2 | | |
| S3 | | |

## 7. Problèmes observés

| # | Scénario | Problème | Fréquence | Impact | Verbatim | Hypothèse d'amélioration | Priorité |
|---|---|---|---|---|---|---|---|
| UX-01 | | | | | | | |
| UX-02 | | | | | | | |
| UX-03 | | | | | | | |

## 8. Synthèse

_À rédiger après les sessions : problèmes partagés par les deux participants, écarts avec les anomalies fonctionnelles, éléments à intégrer au plan d'amélioration._
