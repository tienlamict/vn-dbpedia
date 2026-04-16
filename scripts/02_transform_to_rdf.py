"""
02_transform_to_rdf.py
Chuyen JSON thanh RDF Turtle theo ontology vndbp.
"""
import json
from pathlib import Path
from urllib.parse import quote
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD, FOAF

VNDBP = Namespace("http://vi.dbpedia.org/ontology/")
VNDBPR = Namespace("http://vi.dbpedia.org/resource/")
DBO = Namespace("http://dbpedia.org/ontology/")
DCTERMS = Namespace("http://purl.org/dc/terms/")

INPUT_PATH = Path("data/raw/persons.json")
OUTPUT_PATH = Path("data/rdf/persons.ttl")


def make_person_uri(label: str, qid: str, used_uris: dict) -> URIRef:
    """Tao URI cho nhan vat. Dung ten + fallback QID de tranh trung."""
    if not label:
        return VNDBPR[qid]
    safe = label.replace(" ", "_")
    safe = quote(safe, safe="_")
    # Neu URI da duoc dung boi QID khac, them QID de phan biet
    uri_str = str(VNDBPR[safe])
    if uri_str in used_uris and used_uris[uri_str] != qid:
        safe = f"{safe}_{qid}"
    used_uris[str(VNDBPR[safe])] = qid
    return VNDBPR[safe]


def make_place_uri(label: str, qid: str) -> URIRef:
    if qid:
        return VNDBPR[f"Place_{qid}"]
    safe = quote(label.replace(" ", "_"), safe="_")
    return VNDBPR[safe]


def infer_class(occupations: list) -> URIRef:
    occs_lower = [o.lower() for o in occupations if o]
    text = " ".join(occs_lower)
    if any(k in text for k in ["vua", "hoang de", "monarch", "king", "emperor"]):
        return VNDBP.Monarch
    if any(k in text for k in ["tuong", "general", "military"]):
        return VNDBP.MilitaryPerson
    if any(k in text for k in ["chinh tri", "politician", "statesperson"]):
        return VNDBP.Politician
    return VNDBP.HistoricalFigure


def parse_date(value: str):
    """Wikidata tra ve dang '1900-01-01T00:00:00Z'. Lay phan date."""
    if not value:
        return None
    try:
        return value.split("T")[0]
    except Exception:
        return None


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        persons = json.load(f)

    g = Graph()
    g.bind("vndbp", VNDBP)
    g.bind("vndbpr", VNDBPR)
    g.bind("foaf", FOAF)
    g.bind("dbo", DBO)
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)

    used_uris = {}

    for p in persons:
        if not p.get("label_vi"):
            continue

        uri = make_person_uri(p["label_vi"], p["qid"], used_uris)
        cls = infer_class(p.get("occupations", []))

        g.add((uri, RDF.type, cls))
        g.add((uri, RDF.type, FOAF.Person))
        g.add((uri, RDFS.label, Literal(p["label_vi"], lang="vi")))
        g.add((uri, FOAF.name, Literal(p["label_vi"], lang="vi")))

        if p.get("description_vi"):
            g.add((uri, DCTERMS.description, Literal(p["description_vi"], lang="vi")))

        bd = parse_date(p.get("birth_date"))
        if bd:
            g.add((uri, VNDBP.birthDate, Literal(bd, datatype=XSD.date)))

        dd = parse_date(p.get("death_date"))
        if dd:
            g.add((uri, VNDBP.deathDate, Literal(dd, datatype=XSD.date)))

        if p.get("birth_place_label"):
            place_uri = make_place_uri(p["birth_place_label"], p.get("birth_place_qid"))
            g.add((uri, VNDBP.birthPlace, place_uri))
            g.add((place_uri, RDF.type, VNDBP.Place))
            g.add((place_uri, RDFS.label, Literal(p["birth_place_label"], lang="vi")))

        if p.get("death_place_label"):
            place_uri = make_place_uri(p["death_place_label"], p.get("death_place_qid"))
            g.add((uri, VNDBP.deathPlace, place_uri))
            g.add((place_uri, RDF.type, VNDBP.Place))
            g.add((place_uri, RDFS.label, Literal(p["death_place_label"], lang="vi")))

        for occ in p.get("occupations", []):
            g.add((uri, VNDBP.position, Literal(occ, lang="vi")))

        if p.get("vi_wiki_url"):
            g.add((uri, FOAF.isPrimaryTopicOf, URIRef(p["vi_wiki_url"])))

        if p.get("wikidata_uri"):
            g.add((uri, OWL.sameAs, URIRef(p["wikidata_uri"])))

    g.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Da xuat {len(g)} triples vao {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
