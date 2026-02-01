.PHONY: test build clean publish publish-test install

test:
	.venv/bin/python -m pytest tests/ -v

build: clean
	.venv/bin/python -m build

clean:
	rm -rf dist/ build/ *.egg-info

install:
	uv pip install -e .

publish-test: build
	uvx twine upload --repository testpypi dist/*

publish: build
	uvx twine upload dist/*
