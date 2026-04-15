import json
import time
import redis
from src.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_QUEUE


def _create_client() -> redis.Redis:
    """Cria e retorna um cliente Redis autenticado."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )


def connect_with_retry(retries: int = 10, wait: int = 3) -> redis.Redis:
    """
    Tenta conectar ao Redis com retry.
    Útil para aguardar o broker subir antes do mock iniciar.
    """
    for i in range(1, retries + 1):
        try:
            client = _create_client()
            client.ping()
            print(f"[REDIS] Conectado em {REDIS_HOST}:{REDIS_PORT}")
            return client
        except redis.exceptions.ConnectionError as e:
            print(f"[REDIS] Tentativa {i}/{retries} — indisponível: {e}")
            if i < retries:
                time.sleep(wait)
    raise RuntimeError(f"[REDIS] Não foi possível conectar após {retries} tentativas.")


def publish_frame_event(
    client: redis.Redis,
    path: str,
    camera_id: str,
    timestamp: str,
) -> None:
    """
    Publica um evento de frame disponível na fila Redis.

    O payload segue o contrato esperado pelo vc-worker-portaria:
      { "path": "dataset/img.jpg", "camera_id": "...", "timestamp": "..." }
    """
    payload = json.dumps(
        {
            "path": path,
            "camera_id": camera_id,
            "timestamp": timestamp,
        }
    )
    client.lpush(REDIS_QUEUE, payload)
    print(f"[REDIS] Evento publicado → {REDIS_QUEUE} | path={path}")
