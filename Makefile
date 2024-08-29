DOCKER_COMPOSE_PATH = ./docker-compose.yml

run:
	docker-compose -f $(DOCKER_COMPOSE_PATH) up --build --remove-orphans

build:
	docker-compose -f $(DOCKER_COMPOSE_PATH) build

up:
	docker-compose -f $(DOCKER_COMPOSE_PATH) up

stop:
	docker-compose -f $(DOCKER_COMPOSE_PATH) stop

start:
	docker-compose -f $(DOCKER_COMPOSE_PATH) start

down:
	docker-compose -f $(DOCKER_COMPOSE_PATH) down

clean:
	docker-compose -f $(DOCKER_COMPOSE_PATH) down --rmi all --volumes

clean_docker:
	docker system prune -a --volumes -f

re:
	make clean
	make
all:
	make run