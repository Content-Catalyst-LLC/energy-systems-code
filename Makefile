.PHONY: smoke python advanced clean

smoke:
	bash bash/run_smoke_tests.sh

python:
	python3 python/energy_balance.py

advanced:
	python3 python/advanced_energy_plots.py

clean:
	rm -f outputs/tables/*.csv outputs/figures/*.png outputs/logs/*.log
