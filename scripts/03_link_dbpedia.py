"""
03_link_dbpedia.py
Tao owl:sameAs tu vndbpr:... sang dbpedia:...
"""
import json
from pathlib import Path
from urllib.parse import quote
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL

VNDBPR = Namespace("http://vi.dbpedia.org/resource/")
DBR = Namespace("http://dbpedia.org/resource/")

INPUT_PATH = Path("data/raw/persons.json")
OUTPUT_PATH = Path("data/rdf/sameas_links.ttl")


def wiki_url_to_dbpedia(url: str):
    """https://en.wikipedia.org/wiki/Ho_Chi_Minh -> http://dbpedia.org/resource/Ho_Chi_Minh"""
    if not url or "en.wikipedia.org/wiki/" not in url:
        return None
    name = url.split("/wiki/")[-1]
    return URIRef(f"http://dbpedia.org/resource/{name}")


def make_person_uri(label: str, qid: str, used_uris: dict):
    if not label:
        return VNDBPR[qid]
    safe = label.replace(" ", "_")
    safe = quote(safe, safe="_")
    uri_str = str(VNDBPR[safe])
    if uri_str in used_uris and used_uris[uri_str] != qid:
        safe = f"{safe}_{qid}"
    used_uris[str(VNDBPR[safe])] = qid
    return VNDBPR[safe]


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        persons = json.load(f)

    g = Graph()
    g.bind("owl", OWL)
    g.bind("vndbpr", VNDBPR)
    g.bind("dbr", DBR)

    # Dung cung logic URI nhu 02_transform de dam bao consistency
    used_uris = {}
    # First pass: register all URIs (same order as transform script)
    for p in persons:
        if not p.get("label_vi"):
            continue
        make_person_uri(p["label_vi"], p["qid"], used_uris)

    # Second pass: reset and create links
    used_uris = {}
    count = 0
    for p in persons:
        if not p.get("label_vi") or not p.get("en_wiki_url"):
            continue

        vi_uri = make_person_uri(p["label_vi"], p["qid"], used_uris)
        en_uri = wiki_url_to_dbpedia(p["en_wiki_url"])

        if en_uri:
            g.add((vi_uri, OWL.sameAs, en_uri))
            count += 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Da tao {count} lien ket owl:sameAs sang DBpedia EN")
    print(f"Luu vao {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
