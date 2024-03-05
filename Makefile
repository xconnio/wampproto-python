install_uv:
	@if ! command -v uv >/dev/null 2>&1; then \
  		curl -LsSf https://astral.sh/uv/install.sh | sh; \
  	fi

setup:
	make install_uv
	uv venv
	uv pip install -r requirements.txt

lint:
	. .venv/bin/activate; ruff format .

check-lint:
	. .venv/bin/activate; ruff check .


test:
	pytest -v tests/
