# makefile for Sphinx documentation

SPHINXOPTS ?= -j auto
SPHINXBUILD ?= sphinx-build
SOURCEDIR = source
BUILDDIR = build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

gen:
	@python gen_api_docs.py && make gen_aliases_db

gen_aliases_db:
	@python gen_aliases_db.py

.PHONY: gen gen_aliases_db Makefile

# html -> dirhtml: the local build matches production (.readthedocs.yaml: builder: dirhtml).
html:
	@$(SPHINXBUILD) -M dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: html

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
