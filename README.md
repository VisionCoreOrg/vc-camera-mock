# vc-camera-mock

Serviço que simula o comportamento de uma câmera de portaria no ecossistema VisionCore.

A cada intervalo configurável, seleciona uma imagem do dataset local, faz o upload para o MinIO e publica um evento na fila Redis para que o `vc-worker-portaria` processe o frame.

## Fluxo

```
[Timer: Xs] → frame_picker (local dataset/)
            → storage_service → upload MinIO (dataset/)
            → redis_service  → LPUSH camera:portaria:queue
                                        ↓
                               vc-worker-portaria consome e processa
```

## Pré-requisitos

Os seguintes serviços devem estar online antes de iniciar o mock:

- **parking-infra**: Redis (`parking_redis`) e rede `parking_global_net`
- **vc-worker-portaria** (ou qualquer outro consumidor da fila): MinIO (`visioncore_minio`)

## Configuração

Copie o arquivo de exemplo e ajuste as variáveis:

```bash
cp .env.example .env
```

| Variável | Descrição | Padrão |
|---|---|---|
| `CAMERA_ID` | Identificador da câmera simulada | `cam_mock_portaria_01` |
| `INTERVAL_SECONDS` | Segundos entre disparos de frame | `5` |
| `FRAME_MODE` | Modo de seleção: `sequential` ou `random` | `sequential` |
| `DATASET_PATH` | Caminho local das imagens | `./dataset` |
| `MINIO_ENDPOINT` | Endpoint do MinIO | `http://visioncore_minio:9000` |
| `MINIO_BUCKET_NAME` | Bucket do MinIO | `plate-bucket` |
| `MINIO_DATASET_PREFIX` | Prefixo (pasta) no bucket | `dataset` |
| `REDIS_HOST` | Host do Redis | `parking_redis` |
| `REDIS_QUEUE` | Fila de eventos | `camera:portaria:queue` |

## Dataset

Adicione imagens de placas veiculares na pasta `dataset/`:

```
dataset/
├── placa_001.jpg
├── placa_002.jpg
└── ...
```

> Os arquivos de imagem são ignorados pelo `.gitignore`. Apenas a pasta é versionada.

## Executando com Docker

```bash
# Certifique-se de que a parking_global_net existe
docker network create parking_global_net 2>/dev/null || true

docker compose up --build
```

## Executando localmente (desenvolvimento)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m src.main
```
