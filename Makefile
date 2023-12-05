# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXAPIDOC   ?= poetry run sphinx-apidoc
SPHINXBUILD   ?= poetry run sphinx-build
SOURCEDIR     = docs/source
BUILDDIR      = docs/build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

export_requirements:
	poetry export --without-hashes -o requirements.txt

apidoc:
	$(SPHINXAPIDOC) -o "$(SOURCEDIR)" commandbay

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

check_links:
	$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck"

openapi:
	poetry run python -c "from commandbay.server import app; print(app.openapi())" > "$(SOURCEDIR)/openapi.json"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile export_requirements openapi apidoc
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
