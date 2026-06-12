# OCR & AI Service — Plan d'Implémentation Complet

**Service :** bank-platform-ai-ocr  
**Port :** 8086  
**Stockage :** MinIO (S3-compatible)  
**Langage :** Python 3.11 / FastAPI  
**Phases plan :** P2.6 → P2.10

---

## Table des Matières

1. [T1 — Initialisation](#t1--initialisation)
2. [T2 — Pipeline OCR](#t2--pipeline-ocr)
3. [T3 — Scoring Crédit](#t3--scoring-crédit)
4. [T4 — Stockage Documents](#t4--stockage-documents)
5. [T5 — Tests + Dockerisation](#t5--tests--dockerisation)
6. [Ordre d'implémentation recommandé](#ordre-dimplémentation-recommandé)

---

## T1 — Initialisation

> P2.6 — Dépendances système et Python

- [ ] Installer les dépendances système (dans le Dockerfile ET localement) :
  ```bash
  apt-get install -y tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng poppler-utils
  ```
- [ ] Installer les dépendances Python :
  ```bash
  pip install fastapi uvicorn[standard] pytesseract easyocr opencv-python-headless \
              pdf2image scikit-learn numpy pillow boto3 pymongo python-dotenv \
              python-multipart pydantic[dotenv] pytest pytest-asyncio httpx \
              prometheus-client opentelemetry-sdk opentelemetry-instrumentation-fastapi \
              python-json-logger
  ```
- [ ] Créer la structure du projet :
  ```
  app/
  ├── __init__.py
  ├── main.py
  ├── routers/
  │   └── ocr_router.py
  ├── services/
  │   ├── ocr_service.py
  │   ├── preprocessing_service.py
  │   ├── parsing_service.py
  │   ├── scoring_service.py
  │   └── storage_service.py
  └── core/
      ├── config.py
      ├── database.py
      └── logging.py
  ```
- [ ] Configurer `app/core/config.py` :
  - `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`
  - `MONGODB_URL`, `MONGODB_DB_NAME`
  - `TESSERACT_CMD` (chemin Tesseract), `OCR_LANGUAGES=fra+eng`
  - `SERVICE_PORT=8086`

---

## T2 — Pipeline OCR

> P2.7 — Extraction de texte en 4 étapes

- [ ] Créer `app/services/preprocessing_service.py` :
  - [ ] Étape 1 — **Conversion** : si PDF → convertir chaque page en image avec `pdf2image.convert_from_bytes()` (nécessite `poppler`)
  - [ ] Étape 2 — **Redressement** (deskewing) : détecter et corriger l'angle d'inclinaison avec `OpenCV`
  - [ ] Étape 3 — **Binarisation** : conversion en niveaux de gris + seuillage adaptatif `cv2.adaptiveThreshold()`
  - [ ] Étape 4 — **Réduction du bruit** : filtre médian `cv2.medianBlur()`

- [ ] Créer `app/services/ocr_service.py` :
  - Méthode principale `extract(file_bytes, filename) -> OcrResult`
  - Appeler le pipeline de prétraitement
  - Tenter extraction avec **Tesseract** (`pytesseract.image_to_string(lang='fra+eng')`)
  - Si confiance Tesseract < 60% → fallback vers **EasyOCR**
  - Retourner le texte brut extrait

- [ ] Créer `app/services/parsing_service.py` :
  - Analyser le texte extrait par regex pour identifier les champs :
    - Nom, prénom (pattern NOM Prénom)
    - Numéro de pièce d'identité (CNI/Passeport)
    - Date de naissance (formats DD/MM/YYYY, DD-MM-YYYY)
    - Montant de revenus (patterns : `salaire`, `net à payer`, montants en XAF/FCFA)
    - Employeur (raison sociale)
  - Retourner un JSON structuré :
    ```json
    {
      "nom": "...", "prenom": "...", "numeroId": "...",
      "dateNaissance": "...", "revenus": 0.0, "employeur": "...",
      "confidence": 0.85
    }
    ```

- [ ] Créer le endpoint **POST `/api/ocr/extract`** dans `app/routers/ocr_router.py` :
  - Accepter `multipart/form-data` avec le fichier (`UploadFile`)
  - Orchestrer : prétraitement → OCR → parsing → stockage → retour JSON
  - Timeout interne : 30s (fichiers lourds)

---

## T3 — Scoring Crédit

> P2.8 — Modèle ML de scoring

- [ ] Créer `app/services/scoring_service.py`
- [ ] Définir les features d'entrée :
  - `revenus_mensuels` (extrait par OCR)
  - `montant_demande` (du loan request)
  - `ratio_endettement` = montant_demande / (revenus * durée)
  - `anciennete_emploi` (si disponible dans le document)
  - `historique_credit` (0 si premier prêt, sinon score précédent)
- [ ] Implémenter avec **règles métier** (version de base, sans modèle ML entraîné) :
  ```python
  def compute_score(features: dict) -> int:
      score = 100
      if features['ratio_endettement'] > 0.40: score -= 30
      if features['revenus_mensuels'] < 50000: score -= 20
      if features['anciennete_emploi_mois'] < 12: score -= 15
      return max(0, score)
  ```
- [ ] Optionnel (si données disponibles) : entraîner un `RandomForestClassifier` ou `LogisticRegression` avec scikit-learn
- [ ] Retourner :
  ```json
  {
    "score": 78,
    "decision": "APPROVE",  // APPROVE si >70, MANUAL_REVIEW si 40-70, REJECT si <40
    "factors": ["ratio_endettement_ok", "revenus_suffisants"]
  }
  ```
- [ ] Créer le endpoint **POST `/api/ocr/score`** :
  - Entrée : données extraites par OCR + paramètres du prêt
  - Sortie : score + décision + facteurs

---

## T4 — Stockage Documents

> P2.9 — MinIO + MongoDB

- [ ] Créer `app/services/storage_service.py` avec `boto3` :
  - Configurer le client MinIO (endpoint S3-compatible)
  - Méthode `upload_file(file_bytes, filename, content_type) -> str` : upload dans le bucket et retourner l'URL
  - Méthode `generate_presigned_url(object_name, expiry=3600) -> str` : URL signée à durée limitée
  - Méthode `delete_file(object_name)` : suppression si nécessaire

- [ ] Créer `app/core/database.py` pour MongoDB (`motor`) :
  - Stocker les métadonnées dans la collection `documents` :
    ```json
    {
      "id": "uuid",
      "filename": "cni_client123.jpg",
      "minio_url": "http://minio:9000/bucket/...",
      "content_type": "image/jpeg",
      "sha256_hash": "abc...",
      "statut_ocr": "COMPLETED",
      "ocr_result": { ... },
      "date_upload": "2025-01-01T10:00:00Z"
    }
    ```

- [ ] Créer le endpoint **GET `/api/ocr/documents/{id}/url`** :
  - Retourner une URL pré-signée valide 1h pour l'accès sécurisé

---

## T5 — Tests + Dockerisation

> P2.10

- [ ] **Tests pytest** :
  - [ ] `test_preprocessing.py` — tester le pipeline sur des images de test (CNI fictives)
  - [ ] `test_ocr_service.py` — tester l'extraction de texte sur des images lisibles
  - [ ] `test_parsing_service.py` — tester les regex sur du texte OCR simulé
  - [ ] `test_scoring_service.py` — tester le calcul de score avec différents profils
  - [ ] `test_storage_service.py` — mock MinIO, tester upload et génération d'URL
  - [ ] `test_api.py` — test du endpoint `/api/ocr/extract` avec un fichier de test

- [ ] Préparer des **fixtures de test** :
  - Créer `tests/fixtures/` avec des images PNG de test (texte simple lisible par Tesseract)
  - Ne pas inclure de vraies CNI

- [ ] **Dockerisation** :
  - [ ] `docker/Dockerfile` (une seule stage, `python:3.11-slim`) :
    ```dockerfile
    FROM python:3.11-slim
    RUN apt-get update && apt-get install -y \
        tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng \
        poppler-utils libgl1 && rm -rf /var/lib/apt/lists/*
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY app/ ./app/
    EXPOSE 8086
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]
    ```
  - [ ] `docker/docker-compose.yml` : ocr-service + MinIO + MongoDB
  - [ ] Tester : `docker compose up` → `GET http://localhost:8086/health`

---

## Ordre d'implémentation recommandé

| # | Tâche | Dépendance | Durée estimée |
|---|-------|------------|---------------|
| 1 | T1 — Initialisation + config | — | 1h |
| 2 | T2 — Prétraitement image | T1 | 2h |
| 3 | T2 — Extraction OCR (Tesseract + EasyOCR) | T2 | 2h |
| 4 | T2 — Parsing regex champs | T2 | 2h |
| 5 | T4 — Stockage MinIO + MongoDB | T1 | 2h |
| 6 | T3 — Scoring crédit | T2 | 2h |
| 7 | T2 — Endpoint `/api/ocr/extract` | T2, T4 | 1h |
| 8 | T5 — Tests + fixtures | T2, T3, T4 | 3h |
| 9 | T5 — Dockerisation | Tout | 1h30 |

**Durée totale estimée : 5–7 jours** (conforme plan P2.6 → P2.10 — le plus complexe)

---

## Critères de validation production

- [ ] Extraction de texte fonctionnelle sur une image PNG lisible
- [ ] Fallback EasyOCR actif si confiance Tesseract < 60%
- [ ] Parsing correct des champs (nom, montant, date) sur un document de test
- [ ] Score calculé et décision retournée correctement
- [ ] Upload MinIO fonctionnel, URL pré-signée accessible
- [ ] Métadonnées stockées dans MongoDB
- [ ] `GET /health` retourne `{"status":"UP"}`
- [ ] `docker compose up` démarre sans erreur (avec Tesseract installé dans le container)
