SESSION  := sam-dev
NETWORK  := sam-local
ENDPOINT := http://localhost:8000
API      := http://127.0.0.1:3000
ID       ?= user-1
NAME     ?= Ada Lovelace

# Dummy credentials, exported to every command below (used by the aws CLI)
export AWS_ACCESS_KEY_ID     := local
export AWS_SECRET_ACCESS_KEY := local
export AWS_DEFAULT_REGION    := us-east-1

.PHONY: dev up logs wait-table build api post get scan stop clean

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
wait-table:
	@echo "Waiting for the table to be created..."
	@until docker compose logs create-table 2>/dev/null | grep -q 'TABLE CREATED'; do sleep 1; done

build:
	sam build

api: wait-table build
	sam local start-api --env-vars env.json --docker-network $(NETWORK)

## ---- right: client -------------------------------------------------------
post:
	curl -X POST $(API)/profile \
		-H 'Content-Type: application/json' \
		-d '{"id": "$(ID)", "name": "$(NAME)"}'

get:
	curl "$(API)/profile?id=$(ID)"

scan:
	aws dynamodb scan --table-name ProfilesTable --endpoint-url $(ENDPOINT)

## ---- teardown -------------------------------------------------------------
stop:
	docker compose down
	-tmux kill-session -t $(SESSION)

clean: stop
	rm -rf .aws-sam