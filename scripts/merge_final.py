"""
merge_final.py
Gop ontology + persons + sameas links thanh file cuoi cung.
"""
from pathlib import Path
from rdflib import Graph

OUTPUT_PATH = Path("data/final/vn_dbpedia.ttl")

FILES = [
    "ontology/vn_dbpedia_ontology.ttl",
    "data/rdf/persons.ttl",
    "data/rdf/sameas_links.ttl",
]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    g = Graph()
    for f in FILES:
        print(f"Loading {f}...")
        g.parse(f, format="turtle")

    g.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Tong: {len(g)} triples")
    print(f"Da luu vao {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
