FSTAR_HOME?=../../../../FStar
HACL_HOME?=../../../../hacl-star
FSTAR=$(FSTAR_HOME)/bin/fstar.exe --include $(HACL_HOME)/lib

SPECS=aes.fst chacha20.fst poly1305.fst curve25519.fst

all: $(SPECS)

%.fst: ../../to_fstar.native ../../../specs/%.py speclib.fst
	../../to_fstar.native ../../../specs/$*.py > $*_pre.fst
	$(FSTAR) --indent $*_pre.fst > $*.fst
	rm $*_pre.fst

%.fst.lax: %.fst
	$(FSTAR) --lax $*.fst

%.fst.checked: %.fst
	$(FSTAR) $*.fst

clean:
	rm -rf $(SPECS) *_pre.fst *~
