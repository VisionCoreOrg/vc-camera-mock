import random
from pathlib import Path
from src.config import DATASET_PATH, FRAME_MODE

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


class FramePicker:
    """
    Seleciona frames locais para simular o disparo de uma câmera.
    Suporta dois modos:
      - sequential: percorre as imagens em ordem, reiniciando ao atingir o fim
      - random: seleciona uma imagem aleatória a cada disparo
    """

    def __init__(self):
        self._path = Path(DATASET_PATH)
        self._mode = FRAME_MODE
        self._frames = self._load_frames()
        self._index = 0

        if not self._frames:
            raise RuntimeError(
                f"[CAMERA] Nenhuma imagem encontrada em '{DATASET_PATH}'. "
                "Adicione imagens ao diretório dataset/ antes de iniciar."
            )

        print(
            f"[CAMERA] Dataset carregado: {len(self._frames)} imagens "
            f"(modo: {self._mode})"
        )

    def _load_frames(self) -> list[Path]:
        """Carrega e ordena todas as imagens suportadas no DATASET_PATH."""
        if not self._path.exists():
            return []
        return sorted(
            f
            for f in self._path.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def next_frame(self) -> Path:
        """Retorna o próximo frame de acordo com o modo configurado."""
        if self._mode == "random":
            return random.choice(self._frames)

        # sequential — ciclo contínuo
        frame = self._frames[self._index % len(self._frames)]
        self._index += 1
        return frame

    @property
    def total(self) -> int:
        return len(self._frames)
