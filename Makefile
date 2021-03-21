# Try to use podman if available
ifeq ($(shell type podman >/dev/null 2>&1; echo $$?),0)
DOCKER_CMD = podman
COMPOSE_CMD = podman-compose
else
DOCKER_CMD = docker
COMPOSE_CMD = docker-compose
endif

.ONESHELL:
createenv:
	set -auxo pipefail
	python3.6 -m venv ./.venv
	source ./.venv/bin/activate
	pip3.6 install --upgrade pip
	pip3.6 install numpy==1.18.5   # otherwise pandas won't compile
	pip3.6 install apache-airflow[postgres,aws]==1.10.12

.ONESHELL:
start-airflow:
	mkdir -p .pg/data
	$(COMPOSE_CMD) up -d

stop-airflow:
	$(COMPOSE_CMD) down

restart-airflow: stop-airflow start-airflow

clean-airflow: stop-airflow
	$(DOCKER_CMD) run \
		--security-opt label=disable \
		--rm \
		-v $$(pwd)/.pg:/rm \
		busybox \
		/bin/sh -c 'rm -rf /rm/data'
	rm -rf .pg

.ONESHELL:
pep8: createenv
	source ./.venv/bin/activate
	pip3.6 install flake8 pylint
	flake8 dags/*.py
	pylint dags/*.py

.ONESHELL:
test: createenv
	source ./.venv/bin/activate
	python create_tables.py
	python etl.py

clear: clean

clean: clean-airflow
	rm -rf ./.venv

