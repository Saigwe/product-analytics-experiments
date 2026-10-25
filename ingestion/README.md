# Ingestion

`load_retailrocket.py` loads RetailRocket's `events.csv` into `bronze.events`. It checks the five expected columns first.

1. Download the dataset from [Kaggle: retailrocket/ecommerce-dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset). A free sign-in is needed.
2. Unzip it and save `events.csv` as `data/raw/events.csv`. The `data/` folder is gitignored.
3. Run `make all`.

The roadmap first named the GA4 sample in BigQuery. RetailRocket was chosen instead because it can be downloaded once, with no cloud account. It also has the same kind of view → cart → purchase events for sessions, funnels and retention.

CI uses `tests/fixtures/make_retailrocket_fixture.py`, which writes a file in the same format.
