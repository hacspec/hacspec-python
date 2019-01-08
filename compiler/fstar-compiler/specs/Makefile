FSTAR_HOME?=../../../../FStar
HACL_HOME?=../../../../hacl-star
FSTAR=$(FSTAR_HOME)/bin/fstar.exe --include $(HACL_HOME)/lib --include $(HACL_HOME)/lib/fst --expose_interfaces

SPECS=aes.fst gf128.fst chacha20.fst poly1305.fst curve25519.fst curve448.fst sha3.fst
BROKEN_SPECS=blake2.fst
LIBS = Lib.IntTypes.fst Lib.RawIntTypes.fst Lib.Sequence.fst Lib.ByteSequence.fst Lib.LoopCombinators.fst
LIBS_FILES= $(addprefix $(HACL_HOME)/lib/fst/, $(LIBS)) speclib.fst
LIBS_ML = Lib_IntTypes.ml Lib_RawIntTypes.ml Lib_LoopCombinators.ml Lib_Sequence.ml Lib_ByteSequence.ml Speclib.ml
LIBS_EX = --extract_module Speclib --extract_module Lib.IntTypes --extract_module Lib.RawIntTypes  --extract_module Lib.Sequence --extract_module Lib.ByteSequence  --extract_module Lib.LoopCombinators
include $(FSTAR_HOME)/ulib/ml/Makefile.include

SHELL:=/bin/bash

all: $(SPECS)

tests: $(SPECS:.fst=.exe)

# Not all specs pass right now.
check: chacha20.fst.checked poly1305.fst.checked gf128.fst.checked

.SECONDARY: %-ml
.PRECIOUS: %-ml

%.fst: ../../to_fstar.native ../../../specs/%.py speclib.fst
	../../to_fstar.native ../../../specs/$*.py > $*_pre.fst
	$(FSTAR) --indent $*_pre.fst > $*.fst
	rm $*_pre.fst

%.fst.lax: %.fst
	$(FSTAR) --lax $*.fst

%-ml: $(LIBS_FILES) %.fst
	mkdir -p $*-ml
	$(FSTAR) --lax --codegen OCaml $(LIBS_EX) --extract_module $* --odir $*-ml $(LIBS_FILES) $^
	touch $*-ml

%.exe: CAP = $(shell echo "$*" | sed 's/.*/\u&/')

%.exe: $(LIBS_FILES) %-ml tests/%_test.ml
	cp tests/testutil.ml $*-ml/
	cp tests/$*_test.ml $*-ml/
	$(OCAMLOPT) -w -8 -w -20 -g -I $*-ml $(addprefix $*-ml/, $(LIBS_ML))  $*-ml/$(CAP).ml $*-ml/testutil.ml $*-ml/$*_test.ml -o $*.exe
	./$*.exe

%.fst.checked: %.fst
	$(FSTAR) $*.fst

clean:
	rm -rf $(SPECS) *_pre.fst *~ *-ml
