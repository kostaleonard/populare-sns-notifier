VERSION=$(shell python -c "from populare_db_proxy import __version__; print(__version__)")

all: help

help:
	@echo "To install required packages, run 'make install' from a clean 'python:3.9' (or higher) conda environment."

install:
	pip install -r requirements.txt

lint:
	pylint populare_sns_notifier
	pylint tests

test:
	pytest --cov=populare_sns_notifier tests
	coverage xml

run:
	PYTHONPATH=. python populare_sns_notifier/notifier.py

docker_build:
	@echo Building $(VERSION) and latest
	docker build -t kostaleonard/populare_sns_notifier:latest -t kostaleonard/populare_sns_notifier:$(VERSION) .

docker_run:
	@echo Running $(VERSION)
	docker run kostaleonard/populare_sns_notifier:$(VERSION)

docker_push:
	@echo Pushing $(VERSION) and latest
	docker push kostaleonard/populare_sns_notifier:latest
	docker push kostaleonard/populare_sns_notifier:$(VERSION)
