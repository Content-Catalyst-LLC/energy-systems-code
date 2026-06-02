.PHONY: smoke python clean

smoke:
	bash bash/run_smoke_tests.sh

python:
	python3 python/run_all.py

clean:
	rm -rf outputs/tmp
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	find . -name "*.o" -delete
	find . -name "*.out" -delete
