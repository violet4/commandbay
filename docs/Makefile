# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS     ?=
SPHINXAPIDOC   ?= poetry run sphinx-apidoc
SPHINXBUILD    ?= poetry run sphinx-build
SOURCEDIR       = source
BUILDDIR        = build
PROD_DOCS_DIR   = frontend/out/docs

# Put it first so that "make" without argument is like "make help".
help:
	echo help
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

################################################################################
## only build frontend when there are changes
APIDOC_BUILD_MARKER := .last_apidoc_build
APIDOC_SRC_FILES := $(wildcard source/openapi.json)
.PHONY: apidoc
apidoc: $(APIDOC_BUILD_MARKER)
$(APIDOC_BUILD_MARKER): $(APIDOC_SRC_FILES)
	$(SPHINXAPIDOC) -o "$(SOURCEDIR)" ../commandbay
	@touch $(APIDOC_BUILD_MARKER)
################################################################################

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

check_links:
	$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
html: Makefile apidoc
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
coverage: Makefile apidoc
	$(SPHINXBUILD) -M coverage "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
#%: Makefile apidoc
#	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
