
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

.PHONY: docs

docs: api_openapi_spec
	@$(MAKE) -C docs html

frontend_docs:
	mkdir -p frontend/out/docs
	cp -r docs/build/html/* frontend/out/docs


dev:
	poetry run python start_server.py --dev

version:
	python scripts/version.py


.PHONY: build
build: docs frontend frontend_docs version

#TODO:windows
#TODO:macos?

windows: build
	scp -r frontend/out/ 192.168.2.140:commandbay/frontend
	ssh -A 192.168.2.140 powershell "cd commandbay; poetry run pyinstaller --onefile --clean --name commandbay start_server.py --add-data 'start_server.py;.' -y --add-data 'static;static' --hidden-import commandbay.models --additional-hooks-dir=."

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
