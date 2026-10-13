# Bug reports — campagne initiale QuickOrder V3.1

17 anomalies reproduites le 13/10/2026. Échelles : sévérité Bloquante > Critique > Majeure > Mineure ; priorité P1 (à corriger avant mise en production), P2 (avant MEP ou correctif immédiat), P3 (backlog).

| ID | Titre | Sévérité | Priorité | Cas de test |
|---|---|---|---|---|
| [BUG-01](BUG-01.md) | Un paiement PayPal crée deux commandes identiques et débite le stock deux fois | Bloquante | P1 | TC-R05 |
| [BUG-02](BUG-02.md) | Paiement en espèces accepté avec un montant inférieur au total (rendu de monnaie négatif) | Critique | P1 | TC-E08 |
| [BUG-03](BUG-03.md) | Commande possible dans un restaurant fermé (Night Sushi) | Critique | P1 | TC-R02 |
| [BUG-04](BUG-04.md) | API : une quantité supérieure au stock est acceptée et le stock devient négatif | Critique | P1 | TC-L06 |
| [BUG-05](BUG-05.md) | UI : produit « HORS STOCK » ajoutable au panier et quantité illimitée côté serveur (stock -400) | Critique | P1 | TC-L08, TC-L07 |
| [BUG-06](BUG-06.md) | Le minimum de commande affiché n'est jamais appliqué | Majeure | P1 | TC-R03 |
| [BUG-07](BUG-07.md) | Un nouveau compte peut commander avec une adresse de livraison vide | Majeure | P1 | TC-R11 |
| [BUG-08](BUG-08.md) | Le code ATLAS15 annoncé à -15 % n'applique que -10 % | Majeure | P2 | TC-R04 |
| [BUG-09](BUG-09.md) | API : un coupon expiré est appliqué lors de la création de commande | Majeure | P2 | TC-E06 |
| [BUG-10](BUG-10.md) | Admin : une commande livrée peut revenir au statut « confirmed » | Majeure | P2 | TC-R06 |
| [BUG-11](BUG-11.md) | Redirection ouverte après connexion via le paramètre ?next= | Majeure | P2 | TC-E10 |
| [BUG-12](BUG-12.md) | Le filtre « Livraison max » est inversé | Majeure | P2 | TC-L01 |
| [BUG-13](BUG-13.md) | Un utilisateur peut publier un avis sur un restaurant où il n'a jamais commandé | Mineure | P3 | TC-R07 |
| [BUG-14](BUG-14.md) | La recherche ignore la description des restaurants (UI et API) | Mineure | P3 | TC-R10 |
| [BUG-15](BUG-15.md) | Aucun bouton pour supprimer un produit du panier | Mineure | P3 | TC-N07 |
| [BUG-16](BUG-16.md) | API : les erreurs 404 sont renvoyées en HTML au lieu de JSON | Mineure | P3 | TC-E04 |
| [BUG-17](BUG-17.md) | API /coupons/validate fait confiance au sous-total envoyé par le client | Mineure | P3 | TC-R09 |
