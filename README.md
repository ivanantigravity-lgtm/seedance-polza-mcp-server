# Seedance Polza MCP Server

`mcp-name: io.github.ivanantigravity-lgtm/seedance-polza-mcp-server`

MCP сервер для генерации видео через `bytedance/seedance-2` (и другие Seedance-модели) на Polza.ai.

## Что умеет

- text-to-video и image-to-video генерация
- чтение статуса генерации
- polling до готовности видео
- возвращает компактный результат (id, статус, url, usage, warnings)

## Что нужно для установки

- `Claude Desktop` или `Claude Code`
- [`uv`](https://docs.astral.sh/uv/)
- Python 3.11+
- `POLZA_AI_API_KEY` — ключ берётся на [polza.ai/dashboard/api-keys](https://polza.ai/dashboard/api-keys)

Поставить `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Установка за 2 минуты (через PyPI + uvx)

### Claude Code / VS Code

Создай `.mcp.json` в корне проекта:

```json
{
  "mcpServers": {
    "seedance-polza": {
      "command": "uvx",
      "args": ["seedance-polza-mcp-server@latest"],
      "env": {
        "POLZA_AI_API_KEY": "your-polza-api-key-here"
      }
    }
  }
}
```

Перезапусти Claude Code.

### Claude Desktop (macOS)

Файл `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seedance-polza": {
      "command": "uvx",
      "args": ["seedance-polza-mcp-server@latest"],
      "env": {
        "POLZA_AI_API_KEY": "your-polza-api-key-here"
      }
    }
  }
}
```

### Claude Desktop (Windows)

Файл: `%APPDATA%\Claude\claude_desktop_config.json`. Содержимое идентичное.

## Как проверить, что работает

После перезапуска Claude попроси:

> Сделай через seedance короткое видео: закат над океаном, 16:9, 5 секунд

Claude должен вызвать `seedance_create_video` и дождаться готовности через `seedance_wait_for_completion`.

## Tools

- `seedance_create_video` — запустить генерацию
- `seedance_get_status` — проверить статус по `id`
- `seedance_wait_for_completion` — ждать polling-ом до готовности
- `seedance_model_guide` — краткая памятка по параметрам

## Дефолты

- модель: `bytedance/seedance-2`
- polling interval: `8` секунд
- max wait: `900` секунд

## Переменные окружения

| Переменная | Обязательная | По умолчанию |
| --- | --- | --- |
| `POLZA_AI_API_KEY` | да | — |
| `POLZA_BASE_URL` | нет | `https://polza.ai/api/v1` |
| `SEEDANCE_MODEL` | нет | `bytedance/seedance-2` |
| `SEEDANCE_POLL_INTERVAL` | нет | `8` |
| `SEEDANCE_MAX_WAIT` | нет | `900` |
| `LOG_LEVEL` | нет | `INFO` |

## Поддерживаемые входные параметры

Базовые параметры под видео:

- `prompt`
- `aspect_ratio` (`16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9` и т.д.)
- `resolution` (`480p`, `720p`, `1080p`)
- `duration` (`5s`, `10s`, `15s` — зависит от модели)
- `images` — референсы для image-to-video
- `videos` — референсы для video-to-video
- `seed`
- `async`
- `user`

Формат `images` / `videos`:

```json
{ "type": "url", "data": "https://example.com/file.png" }
```

или

```json
{ "type": "base64", "data": "data:image/png;base64,..." }
```

## Что возвращает сервер

Сервер не делает лишней магии. Он возвращает:

- `id` генерации
- `status`
- `model`
- `usage` (в том числе `cost_rub`)
- `url` результата, если видео готово
- `warnings` / `error` при проблемах

## Локальная разработка

```bash
git clone https://github.com/ivanantigravity-lgtm/seedance-polza-mcp-server.git
cd seedance-polza-mcp-server
uv sync
POLZA_AI_API_KEY=your_key uv run python -m seedance_polza_mcp_server.server
```

## Важно

Этот сервер не гоняет live preview и не тратит токены сам по себе.  
Генерация запускается только по явному вызову tool.

## Лицензия

MIT.
