# bank-platform-ai-ocr

Service d'intelligence artificielle et OCR pour la plateforme bancaire distribuée.

## Technologies
- Python 3.11+
- FastAPI
- Tesseract OCR / EasyOCR
- OpenCV
- scikit-learn
- MinIO (stockage documents)
- MongoDB (métadonnées)

## Port
`8086`

## Prérequis système
```bash
apt-get install tesseract-ocr poppler-utils
```

## Structure
- `app/` - Code source
- `models/` - Modèles ML entraînés
- `tests/` - Tests pytest
- `docker/` - Dockerfile
- `docs/` - Documentation

## Démarrage
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8086 --reload
```

## Health Check
```bash
curl http://localhost:8086/health
```
