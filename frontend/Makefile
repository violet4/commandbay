
################################################################################
## only build frontend when there are changes
BUILD_MARKER := .last_build
SRC_FILES := $(wildcard src/**/*)
.PHONY: build
build: $(BUILD_MARKER)
$(BUILD_MARKER): $(SRC_FILES)
	npm run build
	@touch $(BUILD_MARKER)
################################################################################

.PHONY: dev lint start
dev:
	npm run dev
lint:
	npm run lint
start:
	npm run start
