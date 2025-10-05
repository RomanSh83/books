.PHONY: install lint run
.DEFAULT_GOAL := list

list: ## Показать список всех команд
	@echo "Доступные команды:"
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

install: ## Установка зависимостей
	uv sync

lint: ## Запуск автоматического форматирование кода
	pre-commit run --all-files

run: ## Запуск приложения
	uv run app

run_all:
	docker compose -f docker-compose.dev.yaml up -d
	$(MAKE) run

create_migration:
	@read -p "Введите описание ревизии: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

migrate:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1