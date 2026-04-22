# Seedance Polza MCP Server

`mcp-name: io.github.ivanantigravity-lgtm/seedance-polza-mcp-server`

MCP сервер для генерации видео через `POST /v1/media` в Polza.ai с фокусом на `bytedance/seedance-2`.

Что умеет:

- запускать text-to-video и image-to-video генерации
- читать статус генерации через `GET /v1/media/{id}`
- ждать завершения polling-ом
- возвращать компактный результат без лишней воды

## Tools

- `seedance_create_video`
- `seedance_get_status`
- `seedance_wait_for_completion`
- `seedance_model_guide`

## Дефолты

- модель по умолчанию: `bytedance/seedance-2`
- polling interval: `8` секунд
- max wait: `900` секунд

## Переменные окружения

```env
POLZA_API_KEY=YOUR_POLZA_API_KEY
POLZA_BASE_URL=https://polza.ai/api/v1
SEEDANCE_MODEL=bytedance/seedance-2
SEEDANCE_POLL_INTERVAL=8
SEEDANCE_MAX_WAIT=900
LOG_LEVEL=INFO
```

## Локальный запуск

```bash
uv run python -m seedance_polza_mcp_server.server
```

## Что возвращает сервер

Сервер не пытается делать лишнюю магию.

Он возвращает:

- ID генерации
- статус
- model
- usage
- url результата, если видео готово
- warnings / error, если они есть

## Что поддерживает по входу

Базовые параметры под видео:

- `prompt`
- `aspect_ratio`
- `resolution`
- `duration`
- `images`
- `videos`
- `seed`
- `async`
- `user`

Для `images` и `videos` поддерживаются объекты вида:

```json
{
  "type": "url",
  "data": "https://example.com/file.png"
}
```

или

```json
{
  "type": "base64",
  "data": "data:image/png;base64,..."
}
```

## Важно

Этот сервер не гоняет live preview и не тратит токены сам по себе.  
Генерация запускается только по явному вызову tool.
