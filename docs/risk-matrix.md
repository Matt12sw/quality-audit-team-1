# Matrice des risques — QuickOrder V3.1

**Probabilité (P)** : 1 faible · 2 moyenne · 3 forte. **Impact (I)** : 1 mineur · 2 significatif · 3 majeur · 4 critique. **Score = P × I.**

Priorité de test : **P1** pour un score de 9 à 12, **P2** de 5 à 8, **P3** de 1 à 4.

## 1. Cotation avant campagne et résultat observé

| ID | Risque | P | I | Score | Priorité | Cas | Résultat de la campagne | Bugs | Risque résiduel |
|---|---|:-:|:-:|:-:|:-:|:-:|---|---|---|
| R2 | Commande ou paiement incorrect | 3 | 4 | **12** | P1 | 7 | 1 Pass, 5 Fail, 1 Blocked | BUG-01, 02, 03, 06, 07 | 🔴 **Avéré, critique** |
| R7 | Stock non maîtrisé | 3 | 3 | **9** | P1 | 5 | 2 Pass, 3 Fail | BUG-04, 05 | 🔴 **Avéré, critique** |
| R5 | Réductions et promotions mal calculées | 3 | 3 | **9** | P1 | 6 | 3 Pass, 3 Fail | BUG-08, 09, 17 | 🟠 Avéré, majeur |
| R9 | Contrôle d'accès et redirection | 2 | 4 | **8** | P2 | 2 | 1 Pass, 1 Fail | BUG-11 | 🟠 Avéré, majeur |
| R4 | Cycle de vie de commande incohérent | 2 | 3 | **6** | P2 | 3 | 2 Pass, 1 Fail | BUG-10 | 🟠 Avéré, majeur |
| R1 | Authentification et comptes | 2 | 3 | **6** | P2 | 3 | 3 Pass | — (BUG-07 naît à l'inscription) | 🟢 Faible |
| R8 | API non conforme | 2 | 3 | **6** | P2 | 4 | 3 Pass, 1 Fail | BUG-16 (+ BUG-01, 04, 09 côté API) | 🟠 Moyen |
| R6 | Recherche et filtres erronés | 3 | 2 | **6** | P2 | 3 | 1 Pass, 2 Fail | BUG-12, 14 | 🟡 Moyen |
| R3 | Panier incohérent | 2 | 2 | **4** | P3 | 3 | 2 Pass, 1 Fail | BUG-15 | 🟡 Faible à moyen |
| R10 | Avis non fiables | 2 | 2 | **4** | P3 | 1 | 1 Fail | BUG-13 | 🟡 Moyen |

## 2. Carte de chaleur avant campagne

| Probabilité ↓ / Impact → | 1 mineur | 2 significatif | 3 majeur | 4 critique |
|---|---|---|---|---|
| **3 forte** | | R6 | R5, R7 | **R2** |
| **2 moyenne** | | R3, R10 | R1, R4, R8 | R9 |
| **1 faible** | | | | |

## 3. Réévaluation après campagne

La campagne confirme la cotation : **les trois risques P1 sont tous avérés**. Le parcours de paiement, cœur du produit, cumule à lui seul 1 anomalie bloquante, 4 critiques ou majeures et 1 cas non testable (refus de paiement impossible à simuler).

Après campagne, la probabilité de **R9** passe de 2 à 3 : la redirection ouverte est exploitable sans authentification préalable, avec un simple lien piégé. Son score monte à 12.

Les risques R1 (authentification) et R3 (panier) restent les mieux maîtrisés. Leurs comportements nominaux et d'erreur sont conformes.
