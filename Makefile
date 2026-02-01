.PHONY: test build clean publish publish-test install bump_minor

test:
	uv run pytest tests/ -v

build: clean
	uv run python -m build

clean:
	rm -rf dist/ build/ *.egg-info

publish-test: build
	uv run twine upload --repository testpypi dist/*

publish: build
	uv run twine upload dist/*

bump_patch:
	@CURRENT_VERSION=$$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"); \
	uv run bump2version --current-version $$CURRENT_VERSION --no-tag --no-commit patch pyproject.toml

bump_minor:
	@CURRENT_VERSION=$$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"); \
	uv run bump2version --current-version $$CURRENT_VERSION --no-tag --no-commit minor pyproject.toml

bump_major:
	@CURRENT_VERSION=$$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"); \
	uv run bump2version --current-version $$CURRENT_VERSION --no-tag --no-commit major pyproject.toml
