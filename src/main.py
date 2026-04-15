import time
from datetime import datetime, timezone

from src.config import CAMERA_ID, INTERVAL_SECONDS
from src.services.frame_picker import FramePicker
from src.services.storage_service import upload_frame
from src.services.redis_service import connect_with_retry, publish_frame_event


def run() -> None:
    """Loop principal do mock de câmera."""
    print("🚀 VisionCore Camera Mock — Iniciado!")
    print(f"📷 Câmera ID : {CAMERA_ID}")
    print(f"⏱  Intervalo : {INTERVAL_SECONDS}s entre frames")

    picker = FramePicker()
    redis_client = connect_with_retry()

    print(f"\n🎬 Simulação iniciada com {picker.total} imagens no dataset.\n")

    while True:
        frame_path = picker.next_frame()
        print(f"\n📸 Disparando frame: {frame_path.name}")

        key = upload_frame(frame_path)
        if key:
            timestamp = datetime.now(timezone.utc).isoformat()
            publish_frame_event(redis_client, key, CAMERA_ID, timestamp)
        else:
            print("[CAMERA] ⚠️  Frame ignorado por falha no upload.")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
