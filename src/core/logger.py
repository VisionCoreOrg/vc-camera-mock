import logging
import sys

class ColorFormatter(logging.Formatter):
    """
    Formatador de log personalizado com suporte a cores ANSI para ambiente local.
    Mesmo padrão visual do vc-worker-portaria, para logs consistentes no stack.
    """
    RESET = "\033[0m"
    CORES = {
        logging.DEBUG: "\033[90m",     # Cinza
        logging.INFO: "\033[32m",      # Verde
        logging.WARNING: "\033[33m",   # Amarelo
        logging.ERROR: "\033[31m",     # Vermelho
        logging.CRITICAL: "\033[1;31m"  # Vermelho Negrito
    }

    def format(self, record):
        cor = self.CORES.get(record.levelno, self.RESET)
        log_fmt = (
            f"[{cor}%(levelname)s{self.RESET}] "
            f"[%(asctime)s] "
            f"[%(name)s] - "
            f"%(message)s"
        )
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def configurar_logger(nome: str = "CameraMock") -> logging.Logger:
    """Configura e retorna um logger padronizado com cores ANSI."""
    logger = logging.getLogger(nome)

    # Se o logger já possui handlers, não adiciona novos para evitar duplicidade
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(ColorFormatter())

        logger.addHandler(handler)

    return logger
