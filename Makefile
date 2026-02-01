.PHONY: test build clean publish publish-test install

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
