PY ?= python
DB ?= warehouse/product.duckdb
CSV ?= data/raw/events.csv
FIXTURE_DB ?= warehouse/fixture.duckdb
DBT = cd dbt && DUCKDB_PATH=../$(DB) dbt

.PHONY: all fixture-all pytest bronze bronze-fixture dbt experiments clean

all: pytest bronze dbt experiments                        ## real RetailRocket (download it first, see README)
fixture-all: pytest                                       ## RetailRocket-format fixture (CI)
	$(PY) tests/fixtures/make_retailrocket_fixture.py --out data/fixture/events.csv
	$(MAKE) bronze dbt DB=$(FIXTURE_DB) CSV=data/fixture/events.csv
	$(PY) analysis/simulate_experiments.py --db $(FIXTURE_DB) --sims 30 --out warehouse/fixture_experiments.md

pytest:
	$(PY) -m pytest -q tests

bronze:
	$(PY) ingestion/load_retailrocket.py --db $(DB) --csv $(CSV)

dbt:
	$(DBT) build --profiles-dir .

experiments:
	$(PY) analysis/simulate_experiments.py --db $(DB) --sims 500

clean:
	rm -rf warehouse dbt/target dbt/logs data/fixture
