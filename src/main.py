import time
from datetime import datetime, timezone

from src.config import CAMERA_ID, INTERVAL_SECONDS
from src.core.logger import configurar_logger
from src.services.frame_picker import FramePicker
from src.services.storage_service import upload_frame
from src.services.redis_service import (
    connect_with_retry,
    mock_ligado,
    publicar_heartbeat,
    publish_frame_event,
)

logger = configurar_logger("CameraMock")

# O heartbeat precisa sobreviver ao sono entre frames — TTL maior que o intervalo.
TTL_HEARTBEAT_SEGUNDOS = max(15, int(INTERVAL_SECONDS) + 10)


def run() -> None:
    """Loop principal do mock de câmera, pausável via flag no Redis."""
    logger.info("VisionCore Camera Mock iniciado.")
    logger.info(f"Câmera ID: {CAMERA_ID} | Intervalo: {INTERVAL_SECONDS}s entre frames")

    picker = FramePicker()
    redis_client = connect_with_retry()

    logger.info(
        f"Dataset com {picker.total} imagens. "
        "Aguardando comando de início do painel administrativo (flag no Redis)."
    )

    publicando = False
    while True:
        publicar_heartbeat(redis_client, TTL_HEARTBEAT_SEGUNDOS)

        if not mock_ligado(redis_client):
            if publicando:
                logger.info("Simulação pausada pelo painel administrativo.")
                publicando = False
            time.sleep(1.0)
            continue

        if not publicando:
            logger.info("Simulação iniciada pelo painel administrativo.")
            publicando = True

        frame_path = picker.next_frame()
        logger.info(f"Disparando frame: {frame_path.name}")

        key = upload_frame(frame_path)
        if key:
            timestamp = datetime.now(timezone.utc).isoformat()
            publish_frame_event(redis_client, key, CAMERA_ID, timestamp)
        else:
            logger.warning("Frame ignorado por falha no upload.")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
