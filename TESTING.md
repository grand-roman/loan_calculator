# Инструкции по тестированию

## Запуск тестов

### Способ 1: Использование скрипта (рекомендуется)

```bash
./run_tests.sh
```

Для запуска с подробным выводом:

```bash
./run_tests.sh -v
```

Для запуска конкретного файла тестов:

```bash
./run_tests.sh test_main.py -v
```

### Способ 2: Прямой вызов pytest

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest
```

Или с опциями:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -v
```

## Решение проблемы RecursionError

Ошибка `RecursionError: maximum recursion depth exceeded` была исправлена путём:

1. **Обновления фикстуры `app` в test_main.py**: Изменён способ патчинга `tk.Tk.__init__` с использованием `patch.object()` вместо `patch()`, что предотвращает бесконечную рекурсию при вызове `super().__init__()`.

2. **Создание pytest.ini**: Добавлена конфигурация для отключения проблемного плагина allure-pytest.

3. **Создание скрипта run_tests.sh**: Автоматическая настройка окружения для запуска тестов.

## Структура тестов

- `test_main.py` - Тесты для основного приложения (GUI и бизнес-логика)
- `test_main_methods.py` - Дополнительные тесты методов приложения
- `test_api.py` - Тесты для API модуля
- `test_db.py` - Тесты для модуля работы с базой данных

## Общее количество тестов

Всего в проекте: **60 тестов**

- test_main.py: 21 тест
- test_main_methods.py: 11 тестов
- test_api.py: 10 тестов
- test_db.py: 18 тестов

