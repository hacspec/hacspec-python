# -*- Makefile -*-

# --------------------------------------------------------------------
OCAMLBUILD_JOBS  ?= 2
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
BINS    := checker to_fstar
NAME    := hacspec
INSTALL := scripts/install-sh
DESTDIR ?= /usr/local

# --------------------------------------------------------------------
.PHONY: all build install uninstall check test clean __force__
.PHONY: %.byte %.native %.ml %.mli %.inferred.mli

all: build
	@true

build: $(BINS:%=%.native)

checker.%: __force__
	$(OCAMLBUILD) src/$@

to_fstar.%: __force__
	$(OCAMLBUILD) fstar-compiler/$@

install: $(BINS:%=%.native)
	$(INSTALL) checker.native $(DESTDIR)/bin/hacs
	$(INSTALL) to_fstar.native $(DESTDIR)/bin/to_fstar

uninstall:
	rm -f $(DESTDIR)/$(NAME)

check:
	make -C fstar-compiler/specs

test: check
	@true

clean:
	$(OCAMLBUILD) -clean
	rm -f $(BINS:%=%.native) $(BINS:%=%.byte) *.fst
	make -C fstar-compiler/specs clean
