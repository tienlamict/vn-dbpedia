"""
01_collect_data.py
Thu thap nhan vat lich su/chinh tri Viet Nam tu Wikidata.
"""
import json
import time
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "VN-DBpedia-Assignment/1.0 (educational use)"
OUTPUT_PATH = Path("data/raw/persons.json")

# Chia thanh nhieu query theo occupation de tranh timeout
OCCUPATION_GROUPS = [
    {
        "name": "politicians & statespersons",
        "values": "wd:Q82955 wd:Q372436",  # politician, statesperson
    },
    {
        "name": "monarchs & emperors",
        "values": "wd:Q12097 wd:Q39018",  # monarch, emperor
    },
    {
        "name": "military",
        "values": "wd:Q189290 wd:Q121594 wd:Q47064",  # military officer, general, military leader
    },
    {
        "name": "revolutionaries & diplomats",
        "values": "wd:Q3242115 wd:Q193391",  # revolutionary, diplomat
    },
]

QUERY_TEMPLATE = """
SELECT DISTINCT ?person ?personLabelVi ?personDescVi
       ?birthDate ?deathDate
       ?birthPlace ?birthPlaceLabel
       ?deathPlace ?deathPlaceLabel
       ?occupation ?occupationLabel
       ?viWiki ?enWiki
WHERE {{
  ?person wdt:P27 wd:Q881 .
  ?person wdt:P106 ?occupation .
  VALUES ?occupation {{ {values} }}
  OPTIONAL {{ ?person wdt:P569 ?birthDate . }}
  OPTIONAL {{ ?person wdt:P570 ?deathDate . }}
  OPTIONAL {{ ?person wdt:P19 ?birthPlace . }}
  OPTIONAL {{ ?person wdt:P20 ?deathPlace . }}

  OPTIONAL {{
    ?viWiki schema:about ?person ;
            schema:isPartOf <https://vi.wikipedia.org/> .
  }}
  OPTIONAL {{
    ?enWiki schema:about ?person ;
            schema:isPartOf <https://en.wikipedia.org/> .
  }}

  FILTER EXISTS {{
    ?viWiki2 schema:about ?person ;
             schema:isPartOf <https://vi.wikipedia.org/> .
  }}

  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "vi,en" .
    ?person rdfs:label ?personLabelVi .
    ?person schema:description ?personDescVi .
    ?birthPlace rdfs:label ?birthPlaceLabel .
    ?deathPlace rdfs:label ?deathPlaceLabel .
    ?occupation rdfs:label ?occupationLabel .
  }}
}}
LIMIT 500
"""


def query_group(sparql, group):
    """Query mot nhom occupation tu Wikidata."""
    query = QUERY_TEMPLATE.format(values=group["values"])
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def parse_row(row):
    """Parse mot row ket qua thanh dict."""
    qid = row["person"]["value"].split("/")[-1]
    return {
        "qid": qid,
        "wikidata_uri": row["person"]["value"],
        "label_vi": row.get("personLabelVi", {}).get("value"),
        "description_vi": row.get("personDescVi", {}).get("value"),
        "birth_date": row.get("birthDate", {}).get("value"),
        "death_date": row.get("deathDate", {}).get("value"),
        "birth_place_qid": row.get("birthPlace", {}).get("value", "").split("/")[-1] or None,
        "birth_place_label": row.get("birthPlaceLabel", {}).get("value"),
        "death_place_qid": row.get("deathPlace", {}).get("value", "").split("/")[-1] or None,
        "death_place_label": row.get("deathPlaceLabel", {}).get("value"),
        "vi_wiki_url": row.get("viWiki", {}).get("value"),
        "en_wiki_url": row.get("enWiki", {}).get("value"),
        "occupations": [],
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    sparql = SPARQLWrapper(WIKIDATA_ENDPOINT, agent=USER_AGENT)

    persons = {}

    for group in tqdm(OCCUPATION_GROUPS, desc="Query groups"):
        print(f"\nDang query nhom: {group['name']}...")
        try:
            rows = query_group(sparql, group)
            print(f"  -> {len(rows)} rows")

            for row in rows:
                qid = row["person"]["value"].split("/")[-1]
                if qid not in persons:
                    persons[qid] = parse_row(row)

                occ_label = row.get("occupationLabel", {}).get("value")
                if occ_label and occ_label not in persons[qid]["occupations"]:
                    persons[qid]["occupations"].append(occ_label)

        except Exception as e:
            print(f"  Loi khi query nhom {group['name']}: {e}")

        # Delay giua cac query de tranh bi rate-limit
        time.sleep(2)

    print(f"\nTong cong thu duoc {len(persons)} nhan vat.")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(list(persons.values()), f, ensure_ascii=False, indent=2)

    print(f"Da luu vao {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
