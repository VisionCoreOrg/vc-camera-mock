import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# Identidade da câmera simulada
# ==========================================
CAMERA_ID = os.getenv("CAMERA_ID", "cam_mock_portaria_01")

# ==========================================
# Comportamento do disparo
# ==========================================
INTERVAL_SECONDS = float(os.getenv("INTERVAL_SECONDS", "5"))
FRAME_MODE = os.getenv("FRAME_MODE", "sequential")  # "sequential" ou "random"
DATASET_PATH = os.getenv("DATASET_PATH", "./dataset")

# ==========================================
# MinIO (Storage)
# ==========================================
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://visioncore_minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "plate-bucket")
MINIO_DATASET_PREFIX = os.getenv("MINIO_DATASET_PREFIX", "dataset")

# ==========================================
# Redis (Event Broker)
# ==========================================
REDIS_HOST = os.getenv("REDIS_HOST", "parking_redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "camera:portaria:queue")
