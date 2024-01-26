# makefile for Sphinx documentation

SPHINXOPTS ?=
SPHINXBUILD ?= sphinx-build
SPHINXGENERATE ?= sphinx-apidoc
MODULEPATH = ../packages
SOURCEDIR = source
GENDIR = source/atproto
BUILDDIR = build
TEMPLATEDIR = source/templates

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

gen:
	@$(SPHINXGENERATE) -f -e -M -q -o "$(GENDIR)" -t "$(TEMPLATEDIR)" "$(MODULEPATH)" $(O) && make fix_gen && make gen_aliases_db

fix_gen:
	python fix_title_of_models.py

gen_aliases_db:
	python gen_aliases_db.py

.PHONY: gen Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
