# Addons-Launcher

Простой лаунчер для обновления аддонов WoW из вашего Git-репозитория.

## Быстрый старт

1. Установите Python 3.
2. Сконфигурируйте запуск:

```bash
./launcher.py configure \
  --repo-url https://github.com/you/wow-addons.git \
  --addons-subdir addons \
  --addons-dir "~/World of Warcraft/_retail_/Interface/AddOns"
```

3. Обновляйте аддоны:

```bash
./launcher.py update
```

## Параметры

- `--repo-url` — ссылка на Git-репозиторий с аддонами.
- `--addons-subdir` — подпапка в репозитории, где лежат аддоны (необязательно).
- `--addons-dir` — локальная папка `Interface/AddOns`.
- `--branch` — ветка репозитория (по умолчанию `main`).
- `--no-shallow` — отключить shallow clone.

## Как работает

- Репозиторий клонируется в `.addons_repo/` и обновляется при каждом запуске.
- Аддоны синхронизируются в указанную папку `Interface/AddOns`.
- Локальная конфигурация хранится в `config.json`.
