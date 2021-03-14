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
	mkdir -p .airflow
	source ./env.vars
	podman \
		run -itd \
    	-v ./.airflow:/root/airflow \
		--security-opt label=disable \
		-v ./dags:/root/airflow/dags \
		-v ./plugins:/root/airflow/plugins \
		--name airflow \
		-v ./scripts:/scripts \
		--entrypoint /scripts/entrypoint.sh \
		-p 3000:3000 \
		-e AIRFLOW__CORE__LOAD_EXAMPLES=False \
		-e REDSHIFT_S3_RO_ROLE \
		-e DB_LOGIN \
		-e DB_PASSWORD \
		-e DB_HOST \
		-e DB_PORT \
		-e DB_NAME \
		apache/airflow:v1-10-stable-python3.6-build

stop-airflow:
	podman rm -f airflow
	rm -f .airflow/*.pid

restart-airflow: stop-airflow start-airflow

clean-airflow: stop-airflow
	rm -rf .airflow

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

