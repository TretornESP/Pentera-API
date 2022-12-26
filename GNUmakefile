VMNAME := autocracker
TARGET_BRANCH := master
.DEFAULT_GOAL := all

.PHONY: all detached attached stop logs clean build rebuild push pull

all:
	@make detached

detached:
	@docker compose up -d

attached:
	@docker compose up

stop:
	@docker compose down

logs:
	@docker compose logs -f $(VMNAME)

clean:
	@docker compose down -v

build:
	@make clean
	@docker compose build

rebuild:
	@docker compose up -d --build

push:
	@git add .
	@git commit
	@git push origin $(TARGET_BRANCH)

status:
	@docker compose ps

pull:
	@git pull origin $(TARGET_BRANCH)
	@make build