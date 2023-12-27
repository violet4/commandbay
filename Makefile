
BASE_DIR=$(pwd)

export_requirements:
	poetry export --without-hashes -o requirements.txt

################################################################################
## only export openapi spec when there are changes
BUILD_MARKER := commandbay/.last_build
SRC_FILES := $(wildcard commandbay/server.py commandbay/resources/**/*)
.PHONY: api_openapi_spec
api_openapi_spec: $(BUILD_MARKER)
$(BUILD_MARKER): $(SRC_FILES)
	poetry run python -c "from commandbay.server import app; print(app.openapi())" > "docs/source/openapi.json"
	@touch $(BUILD_MARKER)
################################################################################


FRONTEND_SOURCES := $(wildcard frontend/src/pages/* frontend/src/components/* frontend/src/styles/*)

.PHONY: frontend

frontend:
	$(MAKE) -C frontend build

docs_clean:
	@$(MAKE) -C docs clean

.PHONY: docs
docs: docs_clean api_openapi_spec
	@$(MAKE) -C docs html

frontend_docs:
	if [ -e frontend/out/docs ] ; then rm -rf frontend/out/docs ; fi
	mkdir -p frontend/out/docs
	cp -r docs/build/html/* frontend/out/docs


# dev
backend_deps:
	poetry install --only=main
frontend_deps:
	cd frontend && npm install
dev: backend_deps frontend_deps docs
	poetry run python start_server.py --dev


coverage_report:
	poetry run coverage html
	@printf "\n\nOpen in your web browser:\n\n"
	@realpath htmlcov/index.html
	@echo

test:
	poetry run pytest --cov=commandbay tests/
	$(MAKE) coverage_report
test2:
	poetry run pytest --cov=commandbay tests/ --capture=no
	$(MAKE) coverage_report

version:
	python scripts/version.py

.PHONY: build
build: docs_clean docs frontend frontend_docs version

run: backend_deps frontend_deps build
	poetry run python start_server.py

#TODO:windows
#TODO:macos?

windows: build
	scp -r frontend/out/ 192.168.2.140:commandbay/frontend
	rsync --exclude='*.o' --exclude=build --exclude='*.cache' --exclude='.pytest_cache' --exclude='*.a' --exclude='*.db' --exclude='*.sqlite*' --exclude=.vscode --exclude='htmlcov' --exclude='_next' --exclude='.next' --exclude='*.pyc' --exclude=node_modules --exclude=.venv --exclude .git -r --rsync-path='C:\cygwin64\bin\rsync.exe' . 192.168.2.140:commandbay
	ssh -A 192.168.2.140 powershell "cd commandbay; poetry run pyinstaller --onefile --clean --name commandbay start_server.py --add-data 'start_server.py;.' --add-data 'alembic.ini;.' --add-data 'alembic;alembic' -y --add-data 'frontend/out;frontend' --add-data 'static;static' --hidden-import commandbay.version --hidden-import commandbay.models --additional-hooks-dir=. --icon 'frontend\src\app\favicon.ico'"

linux: build
	poetry run pyinstaller \
		--onefile \
		--name commandbay \
		--add-data start_server.py:. \
		--add-data alembic.ini:. \
		--add-data alembic:alembic \
		--add-data static:static \
		--add-data frontend/out:frontend \
		-y \
		start_server.py

all: linux
