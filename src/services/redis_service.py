import json
import time
from datetime import datetime, timezone
import redis
from src.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_QUEUE
from src.core.logger import configurar_logger

logger = configurar_logger("RedisService")


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
            logger.info(f"Conectado em {REDIS_HOST}:{REDIS_PORT}")
            return client
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Tentativa {i}/{retries} — Redis indisponível: {e}")
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
    logger.info(f"Evento publicado → {REDIS_QUEUE} | path={path}")


# ── Controle remoto do mock ───────────────────────────────────────────
# Contrato compartilhado com o vc-api-core (spec da Rodada 3): a API
# escreve a flag de estado; o mock publica o heartbeat.
CHAVE_MOCK_ESTADO = "camera:portaria:mock:estado"
CHAVE_MOCK_HEARTBEAT = "camera:portaria:mock:heartbeat"
VALOR_LIGADO = "ligado"


def mock_ligado(client: redis.Redis) -> bool:
    """True se o painel administrativo ligou a câmera simulada."""
    return client.get(CHAVE_MOCK_ESTADO) == VALOR_LIGADO


def publicar_heartbeat(client: redis.Redis, ttl_segundos: int) -> None:
    """Sinal de vida do mock: chave com TTL lida pelo status da API."""
    client.set(
        CHAVE_MOCK_HEARTBEAT,
        datetime.now(timezone.utc).isoformat(),
        ex=ttl_segundos,
    )
