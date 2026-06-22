# Admin & Reports Service — Plan d'Implémentation Complet

**Service :** bank-platform-admin-reports  
**Port :** 8088  
**Langage :** Node.js 20 LTS / Express  
**Phases plan :** P2.21 → P2.24

---

## Table des Matières

1. [T1 — Initialisation](#t1--initialisation)
2. [T2 — Dashboard Admin (CRUD)](#t2--dashboard-admin-crud)
3. [T3 — Génération de Rapports](#t3--génération-de-rapports)
4. [T4 — Tests + Dockerisation](#t4--tests--dockerisation)
5. [Ordre d'implémentation recommandé](#ordre-dimplémentation-recommandé)

---

## T1 — Initialisation

> Projet Node.js avec Express

- [ ] Initialiser le projet :
  ```bash
  npm init -y
  npm install express pg sequelize dotenv helmet cors joi \
              puppeteer exceljs prom-client \
              @opentelemetry/sdk-node @opentelemetry/exporter-otlp-http \
              jsonwebtoken axios
  npm install --save-dev jest supertest nodemon eslint
  ```
- [ ] Créer la structure du projet :
  ```
  src/
  ├── app.js
  ├── server.js
  ├── models/
  │   ├── operator.model.js
  │   └── admin.model.js
  ├── routes/
  │   ├── operators.routes.js
  │   ├── admins.routes.js
  │   ├── rules.routes.js
  │   └── reports.routes.js
  ├── controllers/
  │   ├── operators.controller.js
  │   ├── admins.controller.js
  │   ├── rules.controller.js
  │   └── reports.controller.js
  ├── services/
  │   ├── operator.service.js
  │   ├── report.service.js
  │   └── pdf.service.js
  └── config/
      ├── index.js
      └── database.js
  ```
- [ ] Configurer `.env` :
  - `PORT=8088`
  - `DATABASE_URL` (PostgreSQL pour les données admin)
  - `TRANSACTION_SERVICE_URL`, `LOAN_SERVICE_URL`, `CLIENT_SERVICE_URL`
  - `JWT_SECRET` (partagé avec auth-service pour valider les tokens)
- [ ] Vérifier le démarrage : `GET http://localhost:8088/health` → `{"status":"UP"}`

---

## T2 — Dashboard Admin (CRUD)

> P2.21 → P2.22 — Gestion des opérateurs, admins et règles métier

- [ ] **Modèle `Operator`** (table PostgreSQL) :

  | Champ | Type | Description |
  |-------|------|-------------|
  | `id` | UUID | PK |
  | `nom` | String | Nom de l'opérateur |
  | `code` | String | Code unique (ex: WAVE, ORANGE) |
  | `isActive` | Boolean | Actif / Désactivé |
  | `commissionRate` | Decimal | Taux de commission |
  | `plafondDepot` | Decimal | Plafond de dépôt |
  | `plafondRetrait` | Decimal | Plafond de retrait |
  | `plafondSolde` | Decimal | Solde maximum |
  | `createdAt` | Date | auto |

- [ ] **CRUD Opérateurs** :

  | Méthode | Endpoint | Auth | Description |
  |---------|----------|------|-------------|
  | POST | `/api/operators` | ADMIN | Créer un opérateur |
  | GET | `/api/operators` | ADMIN | Lister tous les opérateurs |
  | GET | `/api/operators/{id}` | ADMIN | Détail d'un opérateur |
  | PUT | `/api/operators/{id}` | ADMIN | Modifier un opérateur |
  | PUT | `/api/operators/{id}/deactivate` | SUPER_ADMIN | Désactiver |

- [ ] **Modèle `AdminUser`** (table PostgreSQL) :

  | Champ | Type | Description |
  |-------|------|-------------|
  | `id` | UUID | PK |
  | `email` | String | UNIQUE |
  | `nom` | String | — |
  | `role` | Enum | ADMIN / SUPER_ADMIN |
  | `isActive` | Boolean | — |
  | `createdBy` | UUID | FK → AdminUser |

- [ ] **CRUD Administrateurs** :

  | Méthode | Endpoint | Auth | Description |
  |---------|----------|------|-------------|
  | POST | `/api/admins` | SUPER_ADMIN | Créer un admin |
  | GET | `/api/admins` | SUPER_ADMIN | Lister les admins |
  | PUT | `/api/admins/{id}` | SUPER_ADMIN | Modifier un admin |
  | DELETE | `/api/admins/{id}` | SUPER_ADMIN | Désactiver un admin |

- [ ] **Paramétrage des règles métier** :
  - [ ] `GET /api/rules` — lire les règles actuelles (taux commissions, plafonds par opérateur)
  - [ ] `PUT /api/rules/{operatorId}` — mettre à jour les règles d'un opérateur
  - [ ] Stocker en base PostgreSQL, lues dynamiquement par les autres services via REST
  - [ ] Endpoint public (sans auth) `GET /api/rules/{operatorId}` pour que les autres services puissent consulter

---

## T3 — Génération de Rapports

> P2.23 — PDF et Excel

- [ ] **Rapport Transactions** :
  - [ ] Endpoint : `GET /api/reports/transactions?from=&to=&format=pdf|xlsx&operatorId=`
  - [ ] Appeler transaction-service pour récupérer les données (via `axios`)
  - [ ] Calculer les agrégats : volume total, nombre de transactions, commissions totales, par type

- [ ] **Rapport Prêts** :
  - [ ] Endpoint : `GET /api/reports/loans?from=&to=&format=pdf|xlsx&status=`
  - [ ] Appeler loan-service pour récupérer les données
  - [ ] Calculer : total prêts accordés, taux d'approbation, montant total décaissé

- [ ] **Service PDF** (`src/services/pdf.service.js`) avec `puppeteer` :
  - [ ] Créer un template HTML pour chaque rapport (avec styles CSS intégrés)
  - [ ] Méthode `generatePdf(html) -> Buffer` :
    ```javascript
    const browser = await puppeteer.launch({args: ['--no-sandbox']});
    const page = await browser.newPage();
    await page.setContent(html);
    const pdf = await page.pdf({format: 'A4'});
    await browser.close();
    return pdf;
    ```
  - [ ] Retourner le PDF avec header `Content-Type: application/pdf`

- [ ] **Service Excel** avec `exceljs` :
  - [ ] Méthode `generateXlsx(data, columns) -> Buffer` :
    - Créer un workbook avec une feuille par rapport
    - Ajouter les en-têtes et les données
    - Formatter les colonnes (dates, montants)
  - [ ] Retourner le fichier avec header `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

- [ ] **KPIs Dashboard** :
  - [ ] Endpoint : `GET /api/dashboard/kpis` — agrégats globaux pour le frontend Admin :
    - Nombre total de clients actifs
    - Volume de transactions (jour/semaine/mois)
    - Total des prêts en cours
    - Taux d'erreur des transactions (dernier 24h)

---

## T4 — Tests + Dockerisation

> P2.24

- [ ] **Tests Jest** :
  - [ ] `operators.test.js` — CRUD opérateurs (mock PostgreSQL)
  - [ ] `rules.test.js` — lecture et mise à jour des règles
  - [ ] `pdf.service.test.js` — vérifier la génération PDF (mock Puppeteer, vérifier que le buffer n'est pas vide)
  - [ ] `excel.service.test.js` — vérifier la génération Excel avec des données de test
  - [ ] `reports.controller.test.js` — mock des appels aux autres services

- [ ] **Dockerisation** :
  - [ ] `docker/Dockerfile` :
    ```dockerfile
    FROM node:20-slim
    # Puppeteer nécessite Chromium
    RUN apt-get update && apt-get install -y \
        chromium fonts-liberation libappindicator3-1 \
        libasound2 libatk-bridge2.0-0 libgtk-3-0 \
        && rm -rf /var/lib/apt/lists/*
    ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
        PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci --only=production
    COPY src/ ./src/
    EXPOSE 8088
    CMD ["node", "src/server.js"]
    ```
  - [ ] `docker/docker-compose.yml` : admin-service + postgres-admin
  - [ ] Tester : `docker compose up` → `GET http://localhost:8088/health`

---

## Ordre d'implémentation recommandé

| # | Tâche | Dépendance | Durée estimée |
|---|-------|------------|---------------|
| 1 | T1 — Initialisation + config | — | 1h |
| 2 | T2 — Modèles DB (Operator, Admin) | T1 | 1h30 |
| 3 | T2 — CRUD Opérateurs | T2 | 2h |
| 4 | T2 — CRUD Admins | T2 | 1h30 |
| 5 | T2 — Paramétrage règles métier | T2 | 1h |
| 6 | T3 — Service PDF (Puppeteer) | T1 | 2h |
| 7 | T3 — Service Excel (exceljs) | T1 | 1h30 |
| 8 | T3 — Endpoints rapports | T3, T6, T7 | 1h30 |
| 9 | T4 — Tests | Tout | 2h |
| 10 | T4 — Dockerisation | Tout | 1h |

**Durée totale estimée : 4–5 jours** (conforme plan P2.21 → P2.24)

---

## Critères de validation production

- [ ] CRUD opérateurs fonctionnel avec validation Joi
- [ ] Règles métier lisibles par les autres services sans authentification
- [ ] Rapport PDF généré correctement (non vide, format A4)
- [ ] Rapport Excel généré avec colonnes formatées
- [ ] KPIs retournés par `/api/dashboard/kpis`
- [ ] Endpoints protégés par rôle (ADMIN/SUPER_ADMIN)
- [ ] `GET /health` retourne `{"status":"UP"}`
- [ ] `docker compose up` démarre sans erreur (Chromium inclus dans l'image)
