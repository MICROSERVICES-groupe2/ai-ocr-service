from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ai-ocr-service"
    PORT: int = 8086
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "bank-documents"
    MONGODB_URL: str = "mongodb://root:root@localhost:27017/?authSource=admin"
    MONGODB_DB_NAME: str = "ocr_db"
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    OCR_LANGUAGES: str = "fra+eng"

    class Config:
        env_file = ".env"

settings = Settings()
