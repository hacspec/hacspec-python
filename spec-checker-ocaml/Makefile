# -*- Makefile -*-

# --------------------------------------------------------------------
OCAMLBUILD_JOBS  ?= 1
OCAMLBUILD_BIN   ?= ocamlbuild
OCAMLBUILD_EXTRA ?= 
OCAMLBUILD_OPTS  := -use-ocamlfind -j $(OCAMLBUILD_JOBS)

# In Emacs, use classic display to enable error jumping.
ifeq ($(shell echo $$TERM), dumb)
OCAMLBUILD_OPTS += -classic-display
endif

OCAMLBUILD_OPTS += $(OCAMLBUILD_EXTRA)
OCAMLBUILD      := $(OCAMLBUILD_BIN) $(OCAMLBUILD_OPTS)

# --------------------------------------------------------------------
CHECKER := checker
FSTAR   := to_fstar
NAME    := hacspec
INSTALL := scripts/install-sh
DESTDIR ?= /usr/local

# --------------------------------------------------------------------
.PHONY: all build native byte install uninstall clean
.PHONY: %.ml %.mli %.inferred.mli

all: build
	@true

build: checker.native to_fstar.native

checker.byte:
	$(OCAMLBUILD) $@

checker.native:
	$(OCAMLBUILD) $@

install: checker.native
	$(INSTALL) checker.native $(DESTDIR)/bin/$(NAME)

uninstall:
	rm -f $(DESTDIR)/$(NAME)

to_fstar.native:
	$(OCAMLBUILD) $@

%.fst: to_fstar.native ../specs/%.py
	./to_fstar.native ../specs/$*.py > $*_pre.fst
	../../FStar/bin/fstar.exe --indent $*_pre.fst > $*.fst

clean:
	$(OCAMLBUILD) -clean
	rm -f $(MAIN).native $(MAIN).byte *.fst
