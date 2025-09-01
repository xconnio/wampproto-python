install_uv:
	@if ! command -v uv >/dev/null 2>&1; then \
  		curl -LsSf https://astral.sh/uv/install.sh | sh; \
  	fi

setup:
	make install_uv
	uv venv
	uv pip install .[test]

format:
	. .venv/bin/activate; ruff format .

lint:
	. .venv/bin/activate; ruff check .

test:
	. .venv/bin/activate; pytest -v tests/

coverage:
	. .venv/bin/activate; coverage run -m pytest -v tests && coverage html && open htmlcov/index.html

build:
	uv build

publish:
	uv publish

clean:
	rm -rf .venv build dist wampproto.egg-info

