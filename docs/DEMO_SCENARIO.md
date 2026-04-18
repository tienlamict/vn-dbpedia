# Kịch Bản Demo — Vi-DBpedia

## Thống Kê Tổng Quan

| Chỉ số | Giá trị |
|--------|---------|
| **Classes (Ontology)** | **790** |
| **Object Properties** | **1,167** |
| **Datatype Properties** | **1,827** |
| **Tổng Properties** | **3,024** |
| **Tổng Instances** | **~175,200** |
| **owl:sameAs links (sang Wikidata)** | **1,056** |
| **Dung lượng dữ liệu** | **~102 MB** |

### Instances theo Class

| Class | Số lượng | Ví dụ |
|-------|----------|-------|
| `dbo:PopulatedPlace` | 127,702 | Hà Nội, TP.HCM, Huế |
| `dbo:Person` | 21,927 | Nguyễn Trãi, Trần Hưng Đạo |
| `dbo:AdministrativeRegion` | 11,418 | Tỉnh Nghệ An, Quảng Ninh |
| `dbo:Royalty` | 8,715 | Lê Thái Tổ, Lý Thường Kiệt |
| `dbo:Film` | 3,761 | 1917, 12 Angry Men |
| `dbo:MusicalArtist` | 1,176 | 1TYM, Adele |
| `dbo:Actor` | 501 | diễn viên |
| **Tổng** | **~175,200** | |

---

## Kịch Bản Demo (7–10 phút)

---

### [Tiêu chí 1] Định nghĩa Ontology

**Nói:** *"Chúng tôi xây dựng ontology theo chuẩn DBpedia tiếng Anh — tái sử dụng namespace `dbo:` để đảm bảo tương thích hoàn toàn."*

**Mở file** `data_final/ontology_dbpedia.ttl` và chỉ ra:

```turtle
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

dbo:Person a owl:Class ;
    rdfs:label "Person"@en .

dbo:PopulatedPlace a owl:Class ;
    rdfs:subClassOf dbo:Place .

dbo:Film a owl:Class ;
    rdfs:subClassOf dbo:Work .
```

**Thống kê nhanh:**
- 790 Classes phân cấp (Person → Royalty, Place → City → PopulatedPlace)
- 1,167 Object Properties (`dbo:birthPlace`, `dbo:nationality`)
- 1,827 Datatype Properties (`dbo:populationTotal`, `dbo:areaTotal`)

**Mở giao diện Ontology Browser** tại `http://localhost:8000/ontology` → hiển thị cây phân cấp lớp.

---

### [Tiêu chí 2] Thu thập bài viết Wikipedia tiếng Việt

**Nói:** *"Chúng tôi crawl trực tiếp từ dump XML của Wikipedia tiếng Việt — hơn 1.8 triệu bài viết — rồi parse infobox để trích xuất dữ liệu có cấu trúc."*

**Chỉ ra pipeline** trong `build_kg_wiki/extract_viwiki_to_ttl.py`:

```
Wikipedia VI dump (XML.bz2)
    → Parse MediaWiki template (mwparserfromhell)
    → Trích infobox parameters
    → Map sang RDF properties
    → Xuất ra viwiki_extracted_100mb.ttl (101 MB)
```

**Ví dụ kết quả trích xuất:**
```turtle
<http://vi.dbpedia.org/resource/Hà_Nội>
    a dbo:City ;
    rdfs:label "Hà Nội"@vi ;
    dbo:populationTotal "8053663"^^xsd:integer ;
    geo:lat "21.0278"^^xsd:float ;
    geo:long "105.8342"^^xsd:float .
```

---

### [Tiêu chí 3] Chuẩn hoá dữ liệu 4★

**Nói:** *"Dữ liệu đạt chuẩn 4★ Linked Data — RDF với URI dereferenceable theo URI Policy riêng."*

| Sao | Chuẩn | Thực hiện |
|-----|-------|-----------|
| ★ | Có trên web | Deploy FastAPI tại `http://vi.dbpedia.org` |
| ★★ | Có cấu trúc | File TTL (Turtle RDF) |
| ★★★ | Định dạng mở | RDF/OWL — không phụ thuộc vendor |
| ★★★★ | URI chuẩn W3C | `http://vi.dbpedia.org/resource/{name}` |

**Mở** `docs/URI_POLICY.md` — giải thích URI cool dereferenceable:

```
GET http://vi.dbpedia.org/resource/Hà_Nội
  → Accept: text/html         → trang HTML mô tả
  → Accept: text/turtle       → RDF/Turtle
  → Accept: application/ld+json → JSON-LD
```

**Mở trình duyệt** → `http://localhost:8000/resource/Hà_Nội` → hiển thị entity page với content negotiation.

---

### [Tiêu chí 4] Liên kết sang DBpedia tiếng Anh

**Nói:** *"Chúng tôi tạo 1,056 liên kết `owl:sameAs` sang Wikidata (cầu nối sang English DBpedia), đảm bảo entity vi.dbpedia.org resolve được sang dbpedia.org tương ứng."*

**Chỉ ra file** `data_final/viwiki_sameas_wikidata_overlay.ttl`:

```turtle
<http://vi.dbpedia.org/resource/Hà_Nội>
    owl:sameAs <http://www.wikidata.org/entity/Q1009> .

<http://vi.dbpedia.org/resource/Nguyễn_Trãi>
    owl:sameAs <http://www.wikidata.org/entity/Q708628> .

<http://vi.dbpedia.org/resource/127_giờ>
    owl:sameAs <http://www.wikidata.org/entity/Q174371> .
```

**Mapping class** trong `build_kg_wiki/mappings/wdclass_to_dbo.json`:

```
Wikidata Q5     → dbo:Person
Wikidata Q515   → dbo:City
Wikidata Q6256  → dbo:Country
Wikidata Q11424 → dbo:Film
```

---

### [Tiêu chí 5] SPARQL Endpoint

**Nói:** *"Hệ thống cung cấp SPARQL endpoint chuẩn W3C — truy vấn được qua giao diện web và terminal."*

**Mở** `http://localhost:8000/sparql` — giao diện YASGUI.

**Demo Query 1 — 10 thành phố đông dân nhất:**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?city ?label ?pop WHERE {
  ?city a dbo:City ;
        rdfs:label ?label ;
        dbo:populationTotal ?pop .
  FILTER(lang(?label) = "vi")
}
ORDER BY DESC(?pop)
LIMIT 10
```

**Demo Query 2 — Nhân vật lịch sử Việt Nam:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?person ?label ?birth WHERE {
  ?person a dbo:Royalty ;
          rdfs:label ?label ;
          dbo:birthDate ?birth .
  FILTER(lang(?label) = "vi")
}
ORDER BY ?birth
LIMIT 10
```

**Demo Query 3 — Liên kết sang Wikidata:**
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?vi_entity ?wikidata WHERE {
  ?vi_entity owl:sameAs ?wikidata .
  FILTER(STRSTARTS(STR(?wikidata), "http://www.wikidata.org"))
}
LIMIT 20
```

**Demo qua terminal (curl):**
```bash
curl -X POST http://localhost:8000/sparql/api \
  -H "Accept: application/sparql-results+json" \
  -d "query=SELECT * WHERE { ?s a <http://dbpedia.org/ontology/Film> } LIMIT 5"
```

---

## Luồng Demo Đề Xuất (timeline)

```
0:00  Giới thiệu kiến trúc tổng quan (sơ đồ)
1:00  [TC1] Mở ontology — 790 class, 3,024 property
2:30  [TC2] Chạy/mô phỏng pipeline crawl Wikipedia
4:00  [TC3] Mở entity page Hà_Nội — 4★, content negotiation
5:30  [TC4] Chỉ file owl:sameAs — 1,056 links sang Wikidata
7:00  [TC5] SPARQL UI — chạy 3 query live
9:00  Q&A + thống kê số liệu
```

---

## Điểm Mạnh Cần Nhấn Mạnh

- Toàn bộ pipeline tự động: crawl → parse → RDF → link → serve
- Dữ liệu 102 MB với 175,200 instances từ Wikipedia tiếng Việt
- URI namespace tương thích 100% với English DBpedia (`dbo:` prefix)
- SPARQL endpoint chuẩn W3C với content negotiation (HTML / Turtle / JSON-LD)
- 1,056 liên kết `owl:sameAs` sang Wikidata — cầu nối sang Linked Open Data toàn cầu
