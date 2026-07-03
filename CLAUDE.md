# vc-camera-mock

Simulador de câmera para o VisionCore. Seleciona frames de um dataset local, faz upload para o MinIO e publica eventos na fila Redis para consumo pelo `vc-worker-portaria`.

## Stack

- **Linguagem**: Python 3.12
- **Storage**: MinIO via `boto3` (S3-compatible)
- **Mensageria**: Redis (lista como fila — `LPUSH` / `BRPOP`)
- **Container**: Docker + Docker Compose

## Estrutura

```
src/
├── main.py                    # Loop principal: pick → upload → publish
├── config.py                  # Lê variáveis de ambiente
└── services/
    ├── frame_picker.py        # Seleciona o próximo frame (sequential ou random)
    ├── storage_service.py     # Upload para MinIO via boto3
    └── redis_service.py       # Conexão ao Redis e publish de eventos
dataset/                       # Imagens de entrada (.jpg/.jpeg/.png)
```

## Fluxo

```
dataset/ → upload MinIO (dataset/<filename>) → LPUSH camera:portaria:queue
                                                   ↓
                                          vc-worker-portaria (BLMOVE)
```

A cada `INTERVAL_SECONDS`, o loop:
1. Seleciona um frame via `FramePicker` (modo `sequential` ou `random`)
2. Faz upload para `plate-bucket/dataset/<filename>` no MinIO
3. Publica evento JSON na fila Redis:
   ```json
   { "path": "dataset/frame.jpg", "camera_id": "...", "timestamp": "..." }
   ```

## Controle remoto (flag no Redis)

O mock roda sempre, mas só publica frames quando ligado pelo painel
administrativo (o vc-api-core escreve a flag de estado):

| Chave | Valores | Quem escreve | Quem lê |
|-------|---------|--------------|---------|
| `camera:portaria:mock:estado` | `ligado` / `desligado` (ausente = desligado) | vc-api-core | mock |
| `camera:portaria:mock:heartbeat` | timestamp ISO com TTL | mock (a cada iteração) | vc-api-core |

Desligado, o loop dorme 1s entre checagens sem publicar. Não existe mais
arquivo de flag local nem dependência de `docker start/stop`.

## Variáveis de Ambiente (.env)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CAMERA_ID` | `cam_mock_portaria_01` | Identificador da câmera simulada |
| `INTERVAL_SECONDS` | `5` | Intervalo em segundos entre disparos |
| `FRAME_MODE` | `sequential` | Modo de seleção: `sequential` ou `random` |
| `DATASET_PATH` | `./dataset` | Caminho local das imagens |
| `MINIO_ENDPOINT` | `http://visioncore_minio:9000` | Endpoint MinIO (pinado no compose standalone e no raiz) |
| `MINIO_ROOT_USER` | — | Access key MinIO |
| `MINIO_ROOT_PASSWORD` | — | Secret key MinIO |
| `MINIO_BUCKET_NAME` | `plate-bucket` | Bucket de destino |
| `MINIO_DATASET_PREFIX` | `dataset` | Prefixo dentro do bucket |
| `REDIS_HOST` | `parking_redis` | Host Redis (pinado no compose standalone e no raiz) |
| `REDIS_PORT` | `6379` | Porta Redis |
| `REDIS_PASSWORD` | — | Senha Redis |
| `REDIS_QUEUE` | `camera:portaria:queue` | Nome da fila Redis |

Nos composes (raiz e standalone), REDIS_HOST e MINIO_ENDPOINT são pinados via environment — o .env fornece apenas segredos e knobs (CAMERA_ID, INTERVAL_SECONDS, FRAME_MODE).

## Dataset

Coloque imagens `.jpg`, `.jpeg` ou `.png` em `dataset/` antes de iniciar.  
No Docker Compose, a pasta é montada como bind mount: `./vc-camera-mock/dataset:/app/dataset`.

O serviço falhará na inicialização se o dataset estiver vazio.

## Desenvolvimento Local

```bash
pip install -r requirements.txt

# Copiar e preencher variáveis
cp .env.example .env

# Colocar imagens em dataset/
python3 -m src.main
```

## Docker (standalone)

O stack sobe Redis e MinIO próprios; eventos acumulam na fila local (sem worker).

```bash
docker compose up --build
```

## Padrões do Projeto

- Sem servidor HTTP — o sinal de vida é o heartbeat no Redis (chave com TTL)
- Conexão Redis com retry automático (10 tentativas, 3s de intervalo)
- O `requirements.txt` contém apenas dependências reais do projeto (sem `pip freeze` de sistema)
- Logging estruturado via src/core/logger.py (nunca print())
