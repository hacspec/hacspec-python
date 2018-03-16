all: fstar

fstar: chacha20.fst poly1305.fst

chacha20.fst: ../specs/chacha20.py
	python3.6 hacspec_to_fstar.py ../specs/chacha20.py > chacha20.fst

poly1305.fst: ../specs/poly1305.py
	python3.6 hacspec_to_fstar.py ../specs/poly1305.py > poly1305.fst

