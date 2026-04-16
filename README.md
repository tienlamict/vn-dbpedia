# Vietnamese DBpedia — Historical & Political Figures

Phien ban DBpedia tieng Viet cho domain nhan vat lich su/chinh tri Viet Nam.

## Yeu cau
- Python 3.10+
- Docker & Docker Compose

## Cai dat
```bash
pip install -r requirements.txt
```

## Chay toan bo pipeline
```bash
python scripts/01_collect_data.py       # ~2-5 phut
python scripts/02_transform_to_rdf.py   # <1 phut
python scripts/03_link_dbpedia.py       # <1 phut
python scripts/merge_final.py           # <1 phut
bash scripts/04_load_fuseki.sh          # ~30 giay
```

## Truy cap SPARQL
- Web UI: http://localhost:3030
- Endpoint: http://localhost:3030/vndbpedia/sparql

## Demo query
Xem `queries/sample_queries.sparql`.
