# Паттерны кода — Лимиты

- **Секреты:** только переменные окружения (env_vars.txt / .env), не коммитить.
- **API:** все вызовы T-Invest через `requests`, один базовый URL и заголовки из `_get_api_url()` / `_get_headers()`.
- **Цены:** конвертация через `_quotation_to_float` и `_float_to_quotation`.
- **Кэш:** простой in-memory с TTL через `_cache_get` / `_cache_set`.
- **Логирование:** `logger.info` / `logger.warning` для важных операций и ошибок.
