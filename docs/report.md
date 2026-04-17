# Báo cáo Assignment 2: Vietnamese DBpedia — Nhân Vật Lịch Sử & Chính Trị Việt Nam

**Môn học:** Semantic Web  
**Ngày:** 16/04/2026

---

## 1. Giới thiệu

### 1.1 Bối cảnh DBpedia

DBpedia là một dự án cộng đồng nhằm trích xuất thông tin có cấu trúc từ Wikipedia và công bố dữ liệu đó dưới dạng RDF (Resource Description Framework) trên Web. DBpedia đóng vai trò như một "trung tâm liên kết" (hub) trong hệ sinh thái Linked Open Data toàn cầu, kết nối hàng triệu tài nguyên từ nhiều nguồn khác nhau như Freebase, GeoNames, OpenCyc...

Trong khi DBpedia tiếng Anh đã rất phong phú (hơn 4 triệu entity), các phiên bản ngôn ngữ khác — đặc biệt là tiếng Việt — vẫn còn rất hạn chế về quy mô lẫn chất lượng liên kết. Đây là khoảng trống mà bài tập này hướng đến.

### 1.2 Mục tiêu

Bài tập yêu cầu xây dựng một phiên bản DBpedia tiếng Việt thu nhỏ, bao gồm:

1. **Định nghĩa ontology** mô tả domain được chọn
2. **Thu thập dữ liệu** từ nguồn mở (Wikipedia/Wikidata)
3. **Transform** dữ liệu sang định dạng RDF chuẩn 4-sao (4-star Linked Data)
4. **Tạo liên kết** `owl:sameAs` sang DBpedia phiên bản tiếng Anh
5. **Cung cấp SPARQL endpoint** để truy vấn dữ liệu

### 1.3 Domain được chọn và lý do

**Domain:** Nhân vật lịch sử và chính trị Việt Nam (vua, chính trị gia, tướng lĩnh, nhà ngoại giao, nhà cách mạng).

**Lý do lựa chọn:**

- **Tính đại diện cao:** Đây là nhóm có nhiều bài viết trên Wikipedia tiếng Việt nhất, đảm bảo đủ dữ liệu cho bài tập.
- **Dữ liệu có cấu trúc tốt:** Wikidata đã có mapping sẵn giữa các nhân vật lịch sử VN ↔ Wikipedia VI ↔ Wikipedia EN ↔ DBpedia EN, giúp tạo liên kết dễ dàng.
- **Ý nghĩa thực tiễn:** Dataset về nhân vật lịch sử VN có thể phục vụ các ứng dụng chatbot, hệ thống tra cứu, và nghiên cứu lịch sử.
- **Phân loại rõ ràng:** Các lớp như Vua, Chính trị gia, Tướng lĩnh có ranh giới ngữ nghĩa rõ ràng, phù hợp để xây dựng ontology phân cấp.

---

## 2. Tổng quan về Linked Data và DBpedia

### 2.1 RDF — Resource Description Framework

**RDF (Resource Description Framework)** là một chuẩn W3C được thiết kế để biểu diễn thông tin trên Web dưới dạng có thể xử lý bởi máy tính. Thay vì lưu dữ liệu trong bảng (như RDBMS) hoặc cây (như XML/JSON), RDF tổ chức dữ liệu dưới dạng **đồ thị có hướng** (directed graph).

#### 2.1.1 Triple — Đơn vị cơ bản của RDF

Mọi thông tin trong RDF được biểu diễn bằng các **triple** (bộ ba), mỗi triple gồm:

```
<Subject>   <Predicate>   <Object>
 Chủ thể      Vị từ         Đối tượng
```

Ba thành phần này tương ứng với câu đơn giản trong ngôn ngữ tự nhiên:

| Ngôn ngữ tự nhiên | RDF Triple |
|---|---|
| "Hồ Chí Minh sinh ngày 19/5/1890" | `vndbpr:Hồ_Chí_Minh vndbp:birthDate "1890-05-19"^^xsd:date` |
| "Hồ Chí Minh là một Chính trị gia" | `vndbpr:Hồ_Chí_Minh rdf:type vndbp:Politician` |
| "Hồ Chí Minh sinh tại Nghệ An" | `vndbpr:Hồ_Chí_Minh vndbp:birthPlace vndbpr:Place_Q41616` |

Tập hợp nhiều triple tạo thành một **RDF Graph** — mạng lưới tri thức có thể được máy tính suy diễn và truy vấn.

#### 2.1.2 Các loại node trong RDF Graph

RDF có 3 loại node:

| Loại | Ký hiệu | Mô tả | Ví dụ |
|------|---------|-------|-------|
| **IRI** (URI) | `<...>` | Định danh toàn cầu, duy nhất, derferenceable | `<http://vi.dbpedia.org/resource/Hồ_Chí_Minh>` |
| **Literal** | `"..."` | Giá trị dữ liệu cụ thể, có thể có kiểu và ngôn ngữ | `"1890-05-19"^^xsd:date`, `"Hồ Chí Minh"@vi` |
| **Blank Node** | `_:b1` | Node ẩn danh, không có URI, chỉ dùng nội bộ | Địa chỉ chưa được định danh |

**Quy tắc:** Subject và Predicate phải là IRI. Object có thể là IRI hoặc Literal.

#### 2.1.3 URI và Namespace

**URI (Uniform Resource Identifier)** là chuỗi định danh duy nhất một tài nguyên. Trong RDF, URI đóng vai trò "tên toàn cầu" — giúp phân biệt "Lê Lợi (vua)" với "Lê Lợi (đường phố ở TP.HCM)".

Để viết RDF ngắn gọn hơn, ta dùng **prefix** (tiền tố namespace):

```turtle
# Thay vì viết đầy đủ:
<http://vi.dbpedia.org/resource/Hồ_Chí_Minh>
    <http://vi.dbpedia.org/ontology/birthDate>
    "1890-05-19"^^<http://www.w3.org/2001/XMLSchema#date> .

# Có thể viết ngắn gọn với prefix:
@prefix vndbpr: <http://vi.dbpedia.org/resource/> .
@prefix vndbp:  <http://vi.dbpedia.org/ontology/> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .

vndbpr:Hồ_Chí_Minh  vndbp:birthDate  "1890-05-19"^^xsd:date .
```

#### 2.1.4 Các định dạng serialization của RDF

RDF là mô hình dữ liệu trừu tượng; nó có thể được "ghi ra file" theo nhiều định dạng:

| Định dạng | Đuôi file | Ưu điểm | Nhược điểm |
|-----------|-----------|---------|------------|
| **Turtle** | `.ttl` | Dễ đọc, ngắn gọn | Không phải chuẩn XML |
| **RDF/XML** | `.rdf` | Chuẩn W3C đầu tiên, tương thích XML | Rất dài dòng, khó đọc |
| **N-Triples** | `.nt` | Cực kỳ đơn giản, dễ stream | Không có prefix, file lớn |
| **JSON-LD** | `.jsonld` | Tích hợp tốt với web API | Phức tạp hơn JSON thường |
| **N-Quads** | `.nq` | Hỗ trợ named graph | Ít phổ biến |

Bài tập này sử dụng **Turtle** vì cân bằng giữa tính dễ đọc và tính ngắn gọn.

---

### 2.2 Ontology và OWL

#### 2.2.1 Ontology là gì?

**Ontology** (bản thể luận) trong Semantic Web là một đặc tả hình thức và tường minh về một conceptualization — tức là bộ định nghĩa chính thức về:
- **Class (Lớp):** Tập hợp các đối tượng có cùng bản chất (ví dụ: `vndbp:Monarch`)
- **Property (Thuộc tính):** Quan hệ giữa các đối tượng hoặc giữa đối tượng và giá trị (ví dụ: `vndbp:birthDate`)
- **Instance (Cá thể):** Đối tượng cụ thể thuộc về một class (ví dụ: `vndbpr:Hồ_Chí_Minh`)
- **Axiom (Tiên đề):** Ràng buộc logic về các class và property (ví dụ: `vndbp:Monarch rdfs:subClassOf vndbp:HistoricalFigure`)

Ontology khác với database schema ở chỗ nó có khả năng **suy diễn** (reasoning) — từ các axiom đã định nghĩa, máy tính có thể tự động suy ra tri thức mới.

#### 2.2.2 Tầng ngôn ngữ Semantic Web

```
Ứng dụng
   ↑
OWL (Web Ontology Language)     ← reasoning, logic phức tạp
   ↑
RDFS (RDF Schema)               ← class, subclass, domain, range
   ↑
RDF (Resource Description Framework) ← triple, URI, literal
   ↑
URI / IRI                       ← định danh tài nguyên
```

- **RDF** cung cấp cú pháp graph
- **RDFS** thêm khái niệm class (`rdfs:Class`), kế thừa (`rdfs:subClassOf`), domain/range của property
- **OWL** thêm logic mô tả đầy đủ: equality (`owl:sameAs`), cardinality, intersection/union of classes...

#### 2.2.3 Các thành phần OWL sử dụng trong project

**Định nghĩa Class:**
```turtle
vndbp:Monarch a owl:Class ;
    rdfs:subClassOf vndbp:HistoricalFigure ;
    rdfs:label "Monarch"@en, "Quân chủ"@vi ;
    rdfs:comment "Vua, chúa, hoàng đế Việt Nam"@vi .
```

**Datatype Property** (liên kết entity với giá trị literal):
```turtle
vndbp:birthDate a owl:DatatypeProperty ;
    rdfs:domain vndbp:Person ;   # subject phải là Person
    rdfs:range  xsd:date ;       # object phải là xsd:date
    rdfs:label "ngày sinh"@vi .
```

**Object Property** (liên kết entity với entity khác):
```turtle
vndbp:birthPlace a owl:ObjectProperty ;
    rdfs:domain vndbp:Person ;
    rdfs:range  vndbp:Place ;
    rdfs:label "nơi sinh"@vi .
```

**owl:sameAs** — thuộc tính đặc biệt khẳng định hai URI đại diện cùng một thực thể trong thế giới thực:
```turtle
vndbpr:Hồ_Chí_Minh  owl:sameAs  <http://dbpedia.org/resource/Ho_Chi_Minh> .
```
Khi một OWL reasoner gặp `A owl:sameAs B`, nó hiểu rằng mọi triple của A cũng đúng với B và ngược lại.

#### 2.2.4 Phân biệt RDFS và OWL

| Tính năng | RDFS | OWL |
|-----------|------|-----|
| Class và subclass | ✅ | ✅ |
| Domain và Range | ✅ | ✅ |
| Cardinality (exactly 1, max 3...) | ❌ | ✅ |
| Logical connectors (AND, OR, NOT) | ❌ | ✅ |
| owl:sameAs, owl:equivalentClass | ❌ | ✅ |
| Open World Assumption | ✅ | ✅ |
| Reasoner tự suy diễn | Hạn chế | Đầy đủ |

Project này dùng OWL vì cần `owl:sameAs` để tạo liên kết Linked Data.

---

### 2.3 SPARQL — Ngôn ngữ truy vấn RDF

#### 2.3.1 Tổng quan

**SPARQL (SPARQL Protocol and RDF Query Language)** là ngôn ngữ truy vấn tiêu chuẩn W3C dành cho dữ liệu RDF, tương tự SQL với relational database nhưng được thiết kế cho đồ thị RDF.

```
SQL      ← truy vấn bảng (table/row/column)
SPARQL   ← truy vấn đồ thị RDF (triple/graph/URI)
```

#### 2.3.2 Cấu trúc một SPARQL Query

Cấu trúc cơ bản:
```sparql
PREFIX prefix: <namespace-uri>     # Khai báo namespace (tùy chọn)

SELECT ?var1 ?var2                 # Chọn biến cần trả về
WHERE {
    # Graph Pattern — mô tả các triple cần khớp
    ?subject  predicate  ?object .
    OPTIONAL { ?subject  pred2  ?var2 . }
    FILTER ( điều kiện lọc )
}
ORDER BY ?var1                     # Sắp xếp
LIMIT 10                           # Giới hạn số kết quả
```

Biến SPARQL bắt đầu bằng `?` (hoặc `$`). SPARQL engine tìm tất cả các cách gán giá trị cho biến sao cho thoả mãn toàn bộ graph pattern trong WHERE.

#### 2.3.3 Các loại Query trong SPARQL 1.1

| Dạng | Mục đích | Ví dụ |
|------|---------|-------|
| `SELECT` | Trả về bảng kết quả (giống SELECT SQL) | Lấy danh sách nhân vật và ngày sinh |
| `ASK` | Trả về true/false | URI này có tồn tại không? |
| `CONSTRUCT` | Tạo ra một RDF graph mới | Xuất subgraph theo điều kiện |
| `DESCRIBE` | Mô tả một resource | Lấy toàn bộ triple về một URI |

#### 2.3.4 Các tính năng quan trọng của SPARQL

**OPTIONAL — Truy vấn dữ liệu không bắt buộc:**
```sparql
# Lấy tên và ngày sinh (nếu có); nếu không có ngày sinh vẫn trả về tên
SELECT ?name ?birth WHERE {
    ?p rdfs:label ?name .
    OPTIONAL { ?p vndbp:birthDate ?birth . }
}
```

**FILTER — Lọc kết quả theo điều kiện:**
```sparql
# Nhân vật sinh trước năm 1900
FILTER(?birth < "1900-01-01"^^xsd:date)

# Tên chứa chuỗi "Hồ"
FILTER(CONTAINS(?name, "Hồ"))

# URI bắt đầu bằng prefix DBpedia
FILTER(STRSTARTS(STR(?enUri), "http://dbpedia.org/resource/"))
```

**GROUP BY / HAVING — Tổng hợp:**
```sparql
# Đếm nhân vật theo loại
SELECT ?type (COUNT(?p) AS ?count) WHERE {
    ?p a ?type .
}
GROUP BY ?type
HAVING (COUNT(?p) > 10)
ORDER BY DESC(?count)
```

**SERVICE — Federated Query (truy vấn phân tán):**

Đây là tính năng nổi bật nhất của SPARQL 1.1, cho phép một query gọi đến nhiều SPARQL endpoint khác nhau trong cùng một câu lệnh:

```sparql
SELECT ?viName ?abstract WHERE {
    # Phần này query endpoint LOCAL (Fuseki)
    ?p rdfs:label ?viName ;
       owl:sameAs ?enUri .
    FILTER(STRSTARTS(STR(?enUri), "http://dbpedia.org/resource/"))

    # Phần này query endpoint REMOTE (DBpedia)
    SERVICE <https://dbpedia.org/sparql> {
        ?enUri dbo:abstract ?abstract .
        FILTER(LANG(?abstract) = "en")
    }
}
```

Federated query hiện thực hóa tầm nhìn của Linked Data: dữ liệu nằm ở nhiều nơi nhưng có thể được truy vấn như một thể thống nhất thông qua URI và `owl:sameAs`.

#### 2.3.5 SPARQL vs SQL — So sánh

| Tiêu chí | SQL | SPARQL |
|----------|-----|--------|
| Mô hình dữ liệu | Bảng quan hệ | Đồ thị RDF |
| Schema | Cứng nhắc, định trước | Linh hoạt (Open World) |
| Join | Explicit JOIN clause | Implicit qua biến chung |
| Dữ liệu thiếu | NULL | OPTIONAL pattern |
| Truy vấn nhiều nguồn | Không tự nhiên | SERVICE clause |
| Suy diễn | Không | Có (với OWL reasoner) |
| Chuẩn hóa | SQL-92/99/2003 | SPARQL 1.0/1.1 (W3C) |

---

### 2.4 Mô hình 5-sao Linked Data (Tim Berners-Lee)

Tim Berners-Lee đề xuất thang đo chất lượng Linked Data:

| Sao | Mô tả | Ví dụ |
|-----|-------|-------|
| ⭐ | Dữ liệu public, bất kỳ định dạng nào | File PDF scan |
| ⭐⭐ | Định dạng có cấu trúc, machine-readable | File Excel |
| ⭐⭐⭐ | Định dạng mở, không độc quyền | File CSV |
| ⭐⭐⭐⭐ | Dùng URI để định danh; dùng RDF | RDF Turtle |
| ⭐⭐⭐⭐⭐ | Liên kết đến dữ liệu của người khác | RDF + `owl:sameAs` |

**Bài tập này đạt mức 4-sao** vì:
- Dữ liệu được publish dưới dạng RDF Turtle (định dạng mở, chuẩn W3C)
- Mỗi entity được định danh bằng URI duy nhất (`http://vi.dbpedia.org/resource/...`)
- Có thể truy vấn qua SPARQL endpoint chuẩn W3C
- Có liên kết `owl:sameAs` sang DBpedia EN (tiệm cận 5-sao, nhưng endpoint chưa được publish công khai ra Internet nên chưa đạt 5-sao hoàn toàn)

---

### 2.5 Vai trò của DBpedia trong hệ sinh thái Linked Open Data

DBpedia hoạt động như một "knowledge graph" trung tâm trong **Linked Open Data Cloud** — mạng lưới hàng nghìn dataset RDF liên kết với nhau qua `owl:sameAs`.

Nhờ có DBpedia, một ứng dụng có thể:
- Tra cứu thông tin có cấu trúc về bất kỳ chủ đề nào có bài Wikipedia
- Liên kết dữ liệu riêng của mình với kho tri thức toàn cầu qua `owl:sameAs`
- Thực hiện **federated query** — truy vấn đồng thời nhiều SPARQL endpoint khác nhau
- Dùng DBpedia làm "anchor" để khớp entity giữa các dataset khác nhau (entity linking)

DBpedia tiếng Anh hiện có hơn **4 triệu entity**, hơn **3 tỷ RDF triple**, và liên kết đến hơn **50 dataset** khác trong LOD Cloud.

---

## 3. Thiết kế Ontology

### 3.1 Phân cấp class

```
owl:Thing
└── foaf:Person
    └── vndbp:Person
        ├── vndbp:HistoricalFigure (mặc định)
        │   └── vndbp:Monarch (vua, chúa, hoàng đế)
        ├── vndbp:Politician (chính trị gia, nhà nước)
        └── vndbp:MilitaryPerson (tướng lĩnh, sĩ quan)

vndbp:Dynasty  (triều đại — không phải Person)
vndbp:Place    (địa điểm — không phải Person)
```

Quyết định thiết kế:
- `vndbp:Person` kế thừa `foaf:Person` để tương thích với hệ sinh thái Linked Data sẵn có
- `vndbp:Monarch` là subclass của `vndbp:HistoricalFigure` vì vua luôn là nhân vật lịch sử
- `vndbp:Dynasty` và `vndbp:Place` là class độc lập, không phải con người

### 3.2 Bảng mô tả Property

#### Datatype Properties (giá trị là literal)

| Property | Domain | Range | Mô tả |
|----------|--------|-------|-------|
| `vndbp:birthDate` | Person | xsd:date | Ngày sinh |
| `vndbp:deathDate` | Person | xsd:date | Ngày mất |
| `vndbp:reignStart` | Monarch | xsd:gYear | Năm bắt đầu trị vì |
| `vndbp:reignEnd` | Monarch | xsd:gYear | Năm kết thúc trị vì |
| `vndbp:position` | Person | xsd:string | Chức vụ / nghề nghiệp |
| `vndbp:alternativeName` | Person | xsd:string | Tên gọi khác |

#### Object Properties (giá trị là URI)

| Property | Domain | Range | Mô tả |
|----------|--------|-------|-------|
| `vndbp:birthPlace` | Person | Place | Nơi sinh |
| `vndbp:deathPlace` | Person | Place | Nơi mất |
| `vndbp:dynasty` | Person | Dynasty | Thuộc triều đại nào |
| `vndbp:father` | Person | Person | Quan hệ cha con |
| `vndbp:successor` | Person | Person | Người kế vị |

### 3.3 Tái sử dụng vocabulary chuẩn

| Prefix | Namespace | Lý do sử dụng |
|--------|-----------|----------------|
| `foaf:` | http://xmlns.com/foaf/0.1/ | `foaf:Person`, `foaf:name`, `foaf:isPrimaryTopicOf` — chuẩn mô tả người |
| `dbo:` | http://dbpedia.org/ontology/ | Tham chiếu ontology DBpedia gốc |
| `owl:` | http://www.w3.org/2002/07/owl# | `owl:sameAs`, `owl:Class`, `owl:ObjectProperty` |
| `rdfs:` | http://www.w3.org/2000/01/rdf-schema# | `rdfs:label`, `rdfs:comment`, `rdfs:subClassOf` |
| `xsd:` | http://www.w3.org/2001/XMLSchema# | Kiểu dữ liệu: `xsd:date`, `xsd:string` |
| `dcterms:` | http://purl.org/dc/terms/ | `dcterms:description` — mô tả ngắn |

Việc tái sử dụng vocab chuẩn giúp dữ liệu **interoperable** — các hệ thống khác có thể hiểu và xử lý mà không cần tài liệu bổ sung.

---

## 4. Thu thập dữ liệu

### 4.1 Lý do chọn Wikidata thay vì parse HTML Wikipedia

| Tiêu chí | Parse HTML Wikipedia | Query Wikidata SPARQL |
|----------|---------------------|----------------------|
| Cấu trúc dữ liệu | Bán cấu trúc (infobox HTML) | Có cấu trúc hoàn toàn (JSON) |
| Độ tin cậy | Dễ bị lỗi khi format thay đổi | Ổn định, có schema rõ ràng |
| Mapping sang DBpedia EN | Phải tự xử lý | Có sẵn qua `sitelinks` |
| Thời gian lập trình | Cao (xử lý nhiều edge case) | Thấp (một câu SPARQL) |
| Rate limiting | Khắt khe hơn | API có quota rộng rãi |

Wikidata chứa mapping sẵn: `person → vi.wikipedia.org/wiki/... → en.wikipedia.org/wiki/... → dbpedia.org/resource/...`, không cần làm thêm bước nào.

### 4.2 Chiến lược query

Do Wikidata giới hạn timeout (~60 giây/query), dữ liệu được thu thập qua **4 query riêng biệt** theo nhóm occupation:

| Nhóm | Occupation codes | Kết quả |
|------|-----------------|---------|
| Politicians & Statespersons | Q82955, Q372436 | 500 rows |
| Monarchs & Emperors | Q12097, Q39018 | 1 row |
| Military | Q189290, Q121594, Q47064 | 333 rows |
| Revolutionaries & Diplomats | Q3242115, Q193391 | 173 rows |

**Bộ lọc quan trọng:** Chỉ lấy người có bài trên **Wikipedia tiếng Việt** (`FILTER EXISTS { ?viWiki schema:isPartOf <https://vi.wikipedia.org/> }`), đảm bảo tất cả entity đều có nguồn gốc tiếng Việt.

### 4.3 Thống kê dữ liệu thu thập được

| Chỉ số | Giá trị |
|--------|---------|
| **Tổng số nhân vật** | **872** |
| Có label tiếng Việt | 872 (100%) |
| Có ngày sinh | 807 (92.5%) |
| Có liên kết Wikipedia EN | 293 (33.6%) |
| Có occupation | 872 (100%) |

---

## 5. Transform sang RDF

### 5.1 Quy tắc tạo URI

```
URI nhân vật:  http://vi.dbpedia.org/resource/<Tên_URL_encoded>
URI địa điểm:  http://vi.dbpedia.org/resource/Place_<QID_Wikidata>
```

Ví dụ:
- `Hồ Chí Minh` → `http://vi.dbpedia.org/resource/H%E1%BB%93_Ch%C3%AD_Minh`
- Khi tên trùng nhau: thêm QID → `http://vi.dbpedia.org/resource/Nguyễn_Văn_An_Q12345`

URI cho địa điểm dùng QID Wikidata (ví dụ `Place_Q1766`) để tránh xung đột khi tên địa điểm giống nhau.

### 5.2 Mapping occupation → class RDF

```python
if any(k in text for k in ["vua", "hoàng đế", "monarch", "king", "emperor"]):
    → vndbp:Monarch
elif any(k in text for k in ["tướng", "general", "military"]):
    → vndbp:MilitaryPerson
elif any(k in text for k in ["chính trị", "politician", "statesperson"]):
    → vndbp:Politician
else:
    → vndbp:HistoricalFigure  # mặc định
```

### 5.3 Mỗi entity được map sang các triple

```turtle
vndbpr:Hồ_Chí_Minh
    a vndbp:Politician, foaf:Person ;
    rdfs:label "Hồ Chí Minh"@vi ;
    foaf:name "Hồ Chí Minh"@vi ;
    dcterms:description "nhà cách mạng và chính khách người Việt Nam"@vi ;
    vndbp:birthDate "1890-05-19"^^xsd:date ;
    vndbp:deathDate "1969-09-02"^^xsd:date ;
    vndbp:birthPlace vndbpr:Place_Q48880 ;
    vndbp:position "nhà cách mạng"@vi ;
    foaf:isPrimaryTopicOf <https://vi.wikipedia.org/wiki/Hồ_Chí_Minh> ;
    owl:sameAs <https://www.wikidata.org/entity/Q36014> .
```

### 5.4 Thống kê RDF

| Chỉ số | Giá trị |
|--------|---------|
| **Tổng triples (vn_dbpedia.ttl)** | **10,229** |
| Triples ontology | 89 |
| Triples data (persons.ttl) | 9,847 |
| Triples sameAs links | 293 |
| Trung bình triples/entity | ~11.3 |

---

## 6. Liên kết sang DBpedia EN

### 6.1 Phương pháp

Wikidata lưu sẵn `sitelinks` của mỗi entity — danh sách các bài Wikipedia tương ứng trên tất cả ngôn ngữ. Ta khai thác thông tin này:

```
Wikidata entity Q36014
  → vi.wikipedia.org/wiki/Hồ_Chí_Minh      ← ta có trong data
  → en.wikipedia.org/wiki/Ho_Chi_Minh       ← ta có trong data
  → dbpedia.org/resource/Ho_Chi_Minh        ← suy ra từ dòng trên
```

Quy tắc chuyển đổi:
```python
"https://en.wikipedia.org/wiki/Ho_Chi_Minh"
→ "http://dbpedia.org/resource/Ho_Chi_Minh"
```

Phương pháp này **không cần** query DBpedia để verify vì cơ chế `en.wikipedia ↔ dbpedia.org/resource/` là 1-1 và được DBpedia đảm bảo.

### 6.2 Kết quả

| Chỉ số | Giá trị |
|--------|---------|
| Tổng nhân vật | 872 |
| Có Wikipedia EN | 293 |
| Liên kết owl:sameAs thành công | **293** |
| Tỷ lệ link thành công | 33.6% |

```turtle
# Ví dụ triple owl:sameAs
vndbpr:Hồ_Chí_Minh  owl:sameAs  <http://dbpedia.org/resource/Ho_Chi_Minh> .
vndbpr:Võ_Nguyên_Giáp  owl:sameAs  <http://dbpedia.org/resource/Võ_Nguyên_Giáp> .
```

---

## 7. SPARQL Endpoint

### 7.1 Cấu hình Fuseki

Triple store được dựng bằng **Apache Jena Fuseki** chạy qua Docker:

```yaml
# docker-compose.yml
services:
  fuseki:
    image: stain/jena-fuseki:latest
    ports:
      - "3030:3030"
    environment:
      ADMIN_PASSWORD: admin
      FUSEKI_DATASET_1: vndbpedia
```

Data được load bằng lệnh HTTP POST:
```bash
curl -u admin:admin -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @data/final/vn_dbpedia.ttl \
  "http://localhost:3030/vndbpedia/data?default"
```

Kết quả load: `{ "tripleCount": 10229 }`

### 7.2 Truy cập SPARQL

| Loại | URL |
|------|-----|
| Web UI | http://localhost:3030 |
| SPARQL Query endpoint | http://localhost:3030/vndbpedia/sparql |
| SPARQL Update endpoint | http://localhost:3030/vndbpedia/update |
| Graph Store | http://localhost:3030/vndbpedia/data |

### 7.3 Query mẫu và kết quả

**Query 1 — Đếm tổng nhân vật:**
```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT (COUNT(DISTINCT ?p) AS ?total) WHERE {
  ?p a foaf:Person .
}
```
→ Kết quả: `total = 872`

**Query 2 — Phân bố theo loại:**
```sparql
PREFIX vndbp: <http://vi.dbpedia.org/ontology/>
SELECT ?type (COUNT(?p) AS ?count) WHERE {
  ?p a ?type .
  FILTER(?type IN (vndbp:Monarch, vndbp:Politician,
                   vndbp:MilitaryPerson, vndbp:HistoricalFigure))
}
GROUP BY ?type ORDER BY DESC(?count)
```
→ Kết quả mẫu:

| type | count |
|------|-------|
| vndbp:Politician | ~400 |
| vndbp:HistoricalFigure | ~300 |
| vndbp:MilitaryPerson | ~170 |
| vndbp:Monarch | ~2 |

**Query 3 — Nhân vật có liên kết DBpedia EN:**
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?name ?enUri WHERE {
  ?p rdfs:label ?name ;
     owl:sameAs ?enUri .
  FILTER(STRSTARTS(STR(?enUri), "http://dbpedia.org/resource/"))
}
LIMIT 10
```
→ Trả về 10 nhân vật có liên kết sang DBpedia EN.

**Query 4 — Federated query lấy abstract từ DBpedia EN:**
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT ?viName ?abstract WHERE {
  ?p rdfs:label ?viName ;
     owl:sameAs ?enUri .
  FILTER(STRSTARTS(STR(?enUri), "http://dbpedia.org/resource/"))
  SERVICE <https://dbpedia.org/sparql> {
    ?enUri dbo:abstract ?abstract .
    FILTER(LANG(?abstract) = "en")
  }
}
LIMIT 5
```
→ Trả về abstract tiếng Anh từ DBpedia EN, kết hợp với tên tiếng Việt từ endpoint local. Đây là minh chứng cho tính năng **federated query** của Linked Data.

---

## 8. Kết luận và Hạn chế

### 8.1 Những gì đã đạt được

| Mục tiêu | Kết quả |
|----------|---------|
| Ontology có ≥4 class, ≥10 property | ✅ 7 class, 11 property |
| Dataset ≥200 entity | ✅ 872 entity |
| RDF ≥2000 triples | ✅ 10,229 triples |
| ≥50 liên kết owl:sameAs | ✅ 293 liên kết |
| SPARQL endpoint hoạt động | ✅ Fuseki trên port 3030 |
| Federated query | ✅ SERVICE clause sang DBpedia |
| Báo cáo tiếng Việt đủ 9 phần | ✅ |

### 8.2 Hạn chế

1. **Thiếu full-text abstract tiếng Việt:** Dataset chỉ có mô tả ngắn (1 dòng) từ Wikidata, không có nội dung bài viết Wikipedia đầy đủ. DBpedia thật trích xuất cả đoạn abstract từ mở đầu bài Wikipedia.

2. **Thiếu quan hệ liên nhân vật:** Các property như `vndbp:father`, `vndbp:successor` được định nghĩa trong ontology nhưng chưa có data vì Wikidata không trả về quan hệ này trong query ban đầu.

3. **Tỷ lệ link sang DBpedia EN thấp (33.6%):** Nhiều nhân vật lịch sử Việt Nam chỉ có bài trên Wikipedia tiếng Việt, không có bài tiếng Anh tương ứng → không tạo được liên kết.

4. **Chưa verify link DBpedia EN:** Script hiện tại map theo quy tắc `en.wikipedia → dbpedia.org/resource/` mà không query DBpedia để xác nhận URI thực sự tồn tại.

5. **Endpoint chỉ chạy local:** Fuseki chưa được deploy lên server công khai, chưa đạt mức 5-sao Linked Data thực sự.

6. **Phân loại Monarch còn ít:** Do Wikidata sử dụng occupation "monarch" khá hạn chế cho nhân vật Việt Nam (nhiều vua chỉ được gắn occupation "politician"), dẫn đến số Monarch trong dataset rất ít.

### 8.3 Hướng mở rộng

- **Mở rộng data:** Thêm nhân vật văn hóa, khoa học, thể thao VN để dataset đa dạng hơn
- **Thêm quan hệ:** Query thêm Wikidata để lấy `P22` (father), `P40` (child), `P1365` (replaces/successor)
- **Abstract tiếng Việt:** Parse đoạn đầu bài Wikipedia VI để thêm `dbo:abstract`
- **Verify link:** Query DBpedia ASK endpoint để xác nhận từng URI tồn tại trước khi tạo triple
- **Deploy công khai:** Host Fuseki trên cloud (AWS, GCP...) để đạt 5-sao Linked Data

---

## 9. Tài liệu tham khảo

1. DBpedia Ontology: https://dbpedia.org/ontology/
2. Wikidata Query Service: https://query.wikidata.org/
3. Apache Jena Fuseki: https://jena.apache.org/documentation/fuseki2/
4. 5-star Linked Data: https://5stardata.info/
5. RDF 1.1 Concepts: https://www.w3.org/TR/rdf11-concepts/
6. OWL 2 Web Ontology Language: https://www.w3.org/TR/owl2-overview/
7. SPARQL 1.1 Query Language: https://www.w3.org/TR/sparql11-query/
8. FOAF Vocabulary Specification: http://xmlns.com/foaf/spec/
9. Dublin Core Terms: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
10. Bizer, C., Heath, T., Berners-Lee, T. (2009). Linked Data — The Story So Far. *International Journal on Semantic Web and Information Systems*, 5(3), 1–22.
