SESSION  := sam-dev
API      := http://127.0.0.1:3000
LAT      ?= -23.55
LON      ?= -46.63
LIMIT    ?= 3
HOST     := host.docker.internal:host-gateway

.PHONY: dev up logs seed build api invoke post stop clean

## ---- tmux layout ---------------------------------------------------------
dev:
	@if tmux has-session -t $(SESSION) 2>/dev/null; then \
		exec tmux attach -t $(SESSION); \
	fi; \
	tmux new-session -d -s $(SESSION) -c "$(CURDIR)"; \
	TOP=$$(tmux display-message -p -t $(SESSION) '#{pane_id}'); \
	RIGHT=$$(tmux split-window -h -t $$TOP -c "$(CURDIR)" -P -F '#{pane_id}'); \
	BOTTOM=$$(tmux split-window -v -t $$TOP -c "$(CURDIR)" -P -F '#{pane_id}'); \
	tmux send-keys -t $$TOP    "make up logs" C-m; \
	tmux send-keys -t $$BOTTOM "make api" C-m; \
	tmux send-keys -t $$RIGHT  "clear" C-m; \
	tmux send-keys -t $$RIGHT  "make post"; \
	tmux select-pane -t $$RIGHT; \
	exec tmux attach -t $(SESSION)

## ---- top left: Docker ----------------------------------------------------
up:
	docker compose down
	docker compose up -d

logs:
	docker compose logs -f

## ---- bottom left: SAM ----------------------------------------------------
seed:
	@until curl -s -o /dev/null http://localhost:8000; do sleep 1; done
	uv run --with boto3 python seed.py

build:
	sam build

api: seed build
	sam local start-api --env-vars env.json --add-host $(HOST)

invoke: build
	sam local invoke LanchonetesProximas --env-vars env.json --add-host $(HOST) -e event.json

## ---- right: client -------------------------------------------------------
post:
	curl -X POST $(API)/lanchonetes-proximas \
		-d '{"latitude": $(LAT), "longitude": $(LON), "limite": $(LIMIT)}'

## ---- cleanup -------------------------------------------------------------
stop:
	-tmux kill-session -t $(SESSION)

clean: stop
	docker compose down
