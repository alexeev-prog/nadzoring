# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
CONFDIR       = .

.PHONY: help clean html

help:
	@$(SPHINXBUILD) -b html -C "$(CONFDIR)" "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

clean:
	@rm -rf $(BUILDDIR)

html:
	@$(SPHINXBUILD) -b html -C "$(CONFDIR)" "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" -C "$(CONFDIR)" $(SPHINXOPTS) $(O)
