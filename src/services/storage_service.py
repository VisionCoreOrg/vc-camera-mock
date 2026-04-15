import boto3
from botocore.client import Config
from pathlib import Path
from src.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    BUCKET_NAME,
    MINIO_DATASET_PREFIX,
)


def _get_s3_client():
    """Configura e retorna o cliente Boto3 apontando para o MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",  # ignorado pelo MinIO, mas exigido pelo boto3
    )


def upload_frame(frame_path: Path) -> str | None:
    """
    Faz o upload de um frame local para o MinIO.

    Retorna a chave (path) do objeto no bucket, que será publicada no evento Redis.
    Retorna None em caso de falha.
    """
    client = _get_s3_client()
    key = f"{MINIO_DATASET_PREFIX}/{frame_path.name}"

    try:
        client.upload_file(
            str(frame_path),
            BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )
        print(f"[STORAGE] Frame enviado → {BUCKET_NAME}/{key}")
        return key
    except Exception as e:
        print(f"[STORAGE] Erro ao enviar frame '{frame_path.name}': {e}")
        return None
