all: fstar

FSTAR_HOME=../../FStar
HACL_HOME=../../hacl-star

fstar: chacha20.fst poly1305.fst sha2.fst
typecheck: chacha20.fst-verify poly1305.fst-verify

chacha20.fst: ../specs/chacha20.py
	python3.6 hacspec_to_fstar.py ../specs/chacha20.py > chacha20.fst

poly1305.fst: ../specs/poly1305.py
	python3.6 hacspec_to_fstar.py ../specs/poly1305.py > poly1305.fst

sha2.fst: ../specs/poly1305.py
	python3.6 hacspec_to_fstar.py ../specs/sha2.py > sha2.fst

%-verify: %
	$(FSTAR_HOME)/bin/fstar.exe --include $(HACL_HOME)/specs/lib $<

clean:
	rm -f chacha20.fst poly1305.fst sha2.fst *~ *.hints *.checked
