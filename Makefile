# Targets
.PHONY: help clean html apidoc

clean:
	rm -rf docs/build

apidoc:
	poetry run sphinx-apidoc -l -o docs/source py2mac

docs: apidoc
	poetry run sphinx-build -b html docs/source docs/build
