.PHONY: help up down logs prod status health

help:
	@echo "AI Trading Coach (Gemini)"
	@echo "  make up     Docker 실행"
	@echo "  make prod   nginx 포함"
	@echo "  make down   중지"
	@echo "  make logs   로그"

up:
	docker compose up -d --build

prod:
	docker compose --profile production up -d --build

down:
	docker compose --profile production down

logs:
	docker compose logs -f app

status:
	docker compose ps

health:
	@curl -sf http://localhost:8501/_stcore/health && echo " OK" || echo " FAIL"
