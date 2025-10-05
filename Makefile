V = 0
Q = $(if $(filter 1,$V),,@)
M = $(shell printf "\033[34;1mepr-mcp-python ▶\033[0m")

.PHONY: install
install: ;$(info $(M) installing mcp...) @ ## Installs epr-mcp-python into a virtualenv called epr-mcp
	$Q python3 -m venv $(DESTDIR).virtualenvs/epr-mcp-python && \
	$Q $(DESTDIR).virtualenvs/epr-mcp-python/bin/python3 -m pip install \
				-e .

.PHONY: lint
lint: ; $(info $(M) running linter...) @ ## Run linter (requires ruff)
	$Q ruff format -v src/epr_mcp/ tests/ && ruff check --fix -v src/epr_mcp/ tests/

.PHONY: tests
tests: ; $(info $(M) running tests...) @ ## Run tests
	$Q tox --recreate

.PHONY: release
release: ; $(info $(M) running tox...) @ ## Run tox
	$Q tox -e release

.PHONY: wheel
wheel: ; $(info $(M) creating sdist bdist_wheel...) @ ## Create an sdist bdist_wheel
	$Q pip install --upgrade build && python -m build --sdist --wheel

.PHONY: docker-image
docker-image: wheel; $(info $(M) building docker image...) @ ## Build the docker image
	$Q docker build -t epr-mcp-python:latest .

.PHONY: clean
clean: ; $(info $(M) cleaning...)	@ ## Cleanup everything
	@rm -rvf bin tools vendor build dist
	@rm -rvf *.egg-info *.egg .pytest_cache .ruff_cache .tox .coverage src/*.egg-info 
	@rm -rvf src/epr_mcp/__pycache__ tests/__pycache__ tests/unit/__pycache__

.PHONY: help
help:
	@grep -E '^[ a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
