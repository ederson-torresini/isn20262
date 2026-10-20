SESSION := docker-dev
URL     := http://localhost:8080

.PHONY: dev up client root api stop clean

## ---- tmux layout ---------------------------------------------------------
dev:
	@if tmux has-session -t $(SESSION) 2>/dev/null; then \
		exec tmux attach -t $(SESSION); \
	fi; \
	tmux new-session -d -s $(SESSION) -c "$(CURDIR)"; \
	TOP=$$(tmux display-message -p -t $(SESSION) '#{pane_id}'); \
	RIGHT=$$(tmux split-window -h -t $$TOP -c "$(CURDIR)" -P -F '#{pane_id}'); \
	tmux send-keys -t $$TOP    "make up" C-m; \
	tmux send-keys -t $$RIGHT  "clear" C-m; \
	tmux send-keys -t $$RIGHT  "make client"; \
	tmux select-pane -t $$RIGHT; \
	exec tmux attach -t $(SESSION)

## ---- top left: Docker ----------------------------------------------------
up:
	cd rest-api && npm install
	docker compose up

## ---- right: HTTP client --------------------------------------------------
client: root api

root:
	curl -i $(URL)/

api:
	curl -i $(URL)/api

## ---- teardown -------------------------------------------------------------
stop:
	docker compose down
	-tmux kill-session -t $(SESSION)

clean: stop
