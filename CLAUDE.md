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
                                          vc-worker-portaria (BRPOP)
```

A cada `INTERVAL_SECONDS`, o loop:
1. Seleciona um frame via `FramePicker` (modo `sequential` ou `random`)
2. Faz upload para `plate-bucket/dataset/<filename>` no MinIO
3. Publica evento JSON na fila Redis:
   ```json
   { "path": "dataset/frame.jpg", "camera_id": "...", "timestamp": "..." }
   ```

## Variáveis de Ambiente (.env)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CAMERA_ID` | `cam_mock_portaria_01` | Identificador da câmera simulada |
| `INTERVAL_SECONDS` | `5` | Intervalo em segundos entre disparos |
| `FRAME_MODE` | `sequential` | Modo de seleção: `sequential` ou `random` |
| `DATASET_PATH` | `./dataset` | Caminho local das imagens |
| `MINIO_ENDPOINT` | `http://visioncore_minio:9000` | Endpoint MinIO |
| `MINIO_ROOT_USER` | — | Access key MinIO |
| `MINIO_ROOT_PASSWORD` | — | Secret key MinIO |
| `MINIO_BUCKET_NAME` | `plate-bucket` | Bucket de destino |
| `MINIO_DATASET_PREFIX` | `dataset` | Prefixo dentro do bucket |
| `REDIS_HOST` | `parking_redis` | Host Redis |
| `REDIS_PORT` | `6379` | Porta Redis |
| `REDIS_PASSWORD` | — | Senha Redis |
| `REDIS_QUEUE` | `camera:portaria:queue` | Nome da fila Redis |

No Docker Compose raiz, `REDIS_HOST` e `MINIO_ENDPOINT` são sobrescritos pelos nomes de serviço Docker.

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

```bash
docker compose up --build
```

## Padrões do Projeto

- Sem servidor HTTP — não tem healthcheck
- Conexão Redis com retry automático (10 tentativas, 3s de intervalo)
- O `requirements.txt` contém apenas dependências reais do projeto (sem `pip freeze` de sistema)
