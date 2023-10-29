.PHONY: help clean test install all init dev css ts js cog
.DEFAULT_GOAL := install
.PRECIOUS: requirements.%.in

HOOKS=$(.git/hooks/pre-commit)
REQS=$(wildcard requirements.*.txt)

PYTHON_VERSION:=$(shell python --version | cut -d " " -f 2)
PIP_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/pip
WHEEL_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/wheel
PIP_SYNC_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/pip-sync
PRE_COMMIT_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/pre-commit

COGABLE:=$(shell find ./photosite/assets/ -type f -exec grep -l "\[\[\[cog" {} \;)

help: ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.gitignore:
	curl -q "https://www.toptal.com/developers/gitignore/api/visualstudiocode,python,direnv" > $@

.git: .gitignore
	git init

.pre-commit-config.yaml: $(PRE_COMMIT_PATH) .git
	curl https://gist.githubusercontent.com/bengosney/4b1f1ab7012380f7e9b9d1d668626143/raw/.pre-commit-config.yaml > $@
	pre-commit autoupdate
	@touch $@

pyproject.toml:
	curl https://gist.githubusercontent.com/bengosney/f703f25921628136f78449c32d37fcb5/raw/pyproject.toml > $@
	@touch $@

requirements.%.txt: $(PIP_SYNC_PATH) pyproject.toml
	@echo "Builing $@"
	@python -m piptools compile --generate-hashes -q --extra $* -o $@ $(filter-out $<,$^)

requirements.txt: $(PIP_SYNC_PATH) pyproject.toml
	@echo "Builing $@"
	@python -m piptools compile --generate-hashes -q $(filter-out $<,$^)

.direnv: .envrc
	@python -m ensurepip
	@python -m pip install --upgrade pip
	@touch $@ $^

.git/hooks/pre-commit: .git $(PRE_COMMIT_PATH) .pre-commit-config.yaml
	pre-commit install

.envrc:
	@echo "Setting up .envrc then stopping"
	@echo "layout python python3.11" > $@
	@touch -d '+1 minute' $@
	@false

$(PIP_PATH):
	@python -m ensurepip
	@python -m pip install --upgrade pip

$(WHEEL_PATH): $(PIP_PATH)
	@python -m pip install wheel

$(PIP_SYNC_PATH): $(PIP_PATH) $(WHEEL_PATH)
	@python -m pip install pip-tools

$(PRE_COMMIT_PATH): $(PIP_PATH) $(WHEEL_PATH)
	@python -m pip install pre-commit

init: .direnv $(PIP_SYNC_PATH) requirements.dev.txt .git/hooks/pre-commit ## Initalise a enviroment
	@python -m pip install --upgrade pip

clean: ## Remove all build files
	find . -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache
	rm -f .testmondata

install: $(PIP_SYNC_PATH) requirements.txt $(REQS) ## Install development requirements (default)
	@echo "Installing $(filter-out $<,$^)"
	@python -m piptools sync requirements.txt $(REQS)

photosite/static/css/%.min.css: photosite/assets/css/%.css $(wildcard photosite/assets/css/**/*.css)
	@echo "Building $@"
	@npx lightningcss --sourcemap --bundle --minify -o $@ $<

css: $(patsubst photosite/assets/css/%.css,photosite/static/css/%.min.css,$(wildcard photosite/assets/css/*.css)) ## Build CSS files

photosite/static/js/%.min.js: photosite/assets/ts/%.ts $(wildcard photosite/assets/ts/%.ts)
	@echo "Building $@"
	@npx swc -o $@ $<

js: $(patsubst photosite/assets/ts/%.ts,photosite/static/js/%.min.js,$(wildcard photosite/assets/ts/*.ts)) ## Build JS files

ts: js

FORCE:

$(COGABLE): FORCE
	@cog -r $@

cog: $(COGABLE) ## Run cog on all cogable files

bs: ## Run browser-sync
	browser-sync start --proxy localhost:8000 --files "photosite/static/css/*.css" --files "googlephotostemplatees/**/*.html"

watch-%: photosite/assets/% ## Watch and build assets
	@echo "Watching $* - $@ - $<"
	@$(MAKE) $*
	@while inotifywait -qr -e close_write $</; do \
		$(MAKE) $*; \
	done
