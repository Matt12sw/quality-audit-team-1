# Audit qualité de QuickOrder — Team 1

Audit QA de **QuickOrder V3.1**, une plateforme pédagogique de livraison de repas (Flask, SQLite), réalisé avant sa mise en production.
Application auditée : [amine-el-amrani/quickorder-qa-project](https://github.com/amine-el-amrani/quickorder-qa-project), fork : [Matt12sw/quickorder-qa-project](https://github.com/Matt12sw/quickorder-qa-project). Le code source n'a pas été modifié.

## Verdict : ❌ NO-GO

| Cas de test | Pass | Fail | Blocked | Skipped | Bugs |
|:-:|:-:|:-:|:-:|:-:|:-:|
| **37** | 18 | 18 | 1 | 0 | **17** : 1 bloquante, 4 critiques, 7 majeures, 5 mineures |

Le parcours de commande et de paiement n'est pas fiable :
- un paiement PayPal crée **deux commandes** ;
- un paiement en espèces de 1 € est accepté pour 26,79 € ;
- on peut commander dans un **restaurant fermé**, sans atteindre le minimum, sans adresse, et au-delà du stock (stock **-400**).

Détail dans le [rapport d'exécution](docs/execution-report.md).

## Livrables

| Livrable | Fichier |
|---|---|
| Stratégie de test (périmètre, parcours critiques, risques, types de tests) | [docs/test-strategy.md](docs/test-strategy.md) |
| Matrice des risques (probabilité × impact) | [docs/risk-matrix.md](docs/risk-matrix.md) |
| 37 cas de test avec résultats et preuves (7 nominaux, 8 limites, 11 erreurs, 11 règles métier) | [docs/test-cases.xlsx](docs/test-cases.xlsx) |
| Rapport d'exécution, analyse et recommandation Go / No-Go | [docs/execution-report.md](docs/execution-report.md) |
| 17 bug reports reproductibles | [docs/bug-reports/](docs/bug-reports/README.md) |
| Tests utilisateurs (3 scénarios, 2 participants) | [docs/user-feedback.md](docs/user-feedback.md) |
| Plan d'amélioration (12 actions priorisées) | [docs/improvement-plan.md](docs/improvement-plan.md) |
| Preuves : captures, requêtes et réponses API, réseau, console | [docs/evidence/](docs/evidence/) |

## Rejouer la campagne

La campagne est entièrement automatisée. Le même script sert à la **re-validation** une fois les corrections livrées.

```bash
# 1. Dans le dépôt QuickOrder : base propre
docker compose down -v
docker compose up --build -d

# 2. Dans ce dépôt
python -m venv .venv
.venv/Scripts/activate            # Windows (macOS/Linux : source .venv/bin/activate)
pip install -r scripts/requirements.txt
playwright install chromium
python scripts/run_campaign.py     # exécute les 37 cas → docs/evidence/ + scripts/results.json
python scripts/build_docs.py       # régénère test-cases.xlsx et bug-reports/
```

| Script | Rôle |
|---|---|
| `scripts/testcases.py` | Référentiel des cas : objectif, préconditions, données, étapes, résultat attendu |
| `scripts/run_campaign.py` | Exécution UI (Playwright), API (requests), Swagger et DevTools ; calcule le statut à partir du résultat observé |
| `scripts/bugs.py` | Contenu des bug reports |
| `scripts/build_docs.py` | Génère `test-cases.xlsx` et `docs/bug-reports/*.md` |

## Environnement de test

Windows 11, Docker 29.5, QuickOrder V3.1 sous Docker Compose (Python 3.12, Werkzeug 3.1.3), Chromium (Playwright).
Comptes du seed : `alice@example.com` et `bob@example.com` (`Password123!`), `admin@quickorder.local` (`Admin123!`). Clé API : `quickorder-demo-key`.
