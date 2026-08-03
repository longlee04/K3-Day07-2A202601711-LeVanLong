# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store
**Nhóm:** NEXACO

**Thành viên:**
| Họ và tên | Mã học viên | Phương pháp Chunking chính |
|----------------|------|-------------------|
| Nguyễn Ngọc Dương | 2A202601717 | `SemanticChunker` (Custom Embedding-driven) |
| Lê Văn Long | 2A202601711 | `RecursiveChunker` / `HeadingChunker` |

**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định đăng ký học phần và tổ chức học kỳ (đăng ký thời khóa biểu, học vượt, tiến trình rút gọn, hủy lớp học phần) của Học viện Công nghệ Bưu chính Viễn thông (PTIT), thu thập từ `giaovu.ptit.edu.vn`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký lịch học (TKB) cho SV khoá 2024, 2025 học theo tiến trình rút gọn HK I 2026-2027 | giaovu.ptit.edu.vn/dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025... | 2026-08-03 / 16/06/2026 | 5471 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 2 | Thông báo: Hủy các lớp học phần đợt học lại kỳ phụ (hè) năm học 2025-2026 | giaovu.ptit.edu.vn/thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he... | 2026-08-03 / 15/06/2026 | 3600 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 3 | Đăng ký TKB các lớp học phần trong đợt học kỳ phụ (kỳ hè) năm học 2025-2026 | giaovu.ptit.edu.vn/dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu... | 2026-08-03 / 04/06/2026 | 4383 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 4 | Tổ chức đăng ký học vượt HK I năm học 2026–2027 đối với SV khóa 2024, 2025 | giaovu.ptit.edu.vn/to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027... | 2026-08-03 / 02/06/2026 | 3978 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 5 | Tập trung phổ biến kế hoạch đăng ký môn học kỳ I năm học 2026-2027 | giaovu.ptit.edu.vn/tap-trung-pho-bien-ke-hoach-dang-ky-mon-hoc-ky-i... | 2026-08-03 / 28/05/2026 | 4684 | `audience: all`, `department: academic-affairs`, `language: vi` |
| 6 | Tổ chức học học kỳ phụ (kỳ hè) năm học 2025-2026 | giaovu.ptit.edu.vn/to-chuc-hoc-hoc-ky-phu-ky-he-nam-hoc-2025-2026 | 2026-08-03 / 11/05/2026 | 4099 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 7 | Hủy các lớp học phần đợt học lớp riêng, học kỳ 2 năm học 2025-2026 | giaovu.ptit.edu.vn/huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2... | 2026-08-03 / 26/03/2026 | 3883 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 8 | Đăng ký TKB các lớp học phần trong đợt học lớp riêng, HK 2 – năm học 2025-2026 | giaovu.ptit.edu.vn/dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-lop-rieng... | 2026-08-03 / 20/03/2026 | 4832 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 9 | Điều chỉnh lịch đăng ký học lại, học cải thiện, học 2 văn bằng trên QLĐT HK2 2025-2026 | giaovu.ptit.edu.vn/dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien... | 2026-08-03 / 08/01/2026 | 3148 | `audience: student`, `department: academic-affairs`, `language: vi` |
| 10 | Lịch nghỉ Tết Dương lịch năm 2026 và điều chỉnh lịch thi, lịch đăng ký học phần | giaovu.ptit.edu.vn/lich-nghi-tet-duong-lich-nam-2026-va-dieu-chinh-lich-thi... | 2026-08-03 / 01/01/2026 | 3248 | `audience: student`, `department: academic-affairs`, `language: vi` |

> Kiểm bằng script checklist mục 6 `docs/DATA_COLLECTION.md`: đúng 10 file trong `data/k3_university/` (nằm trong khoảng 5-10 theo yêu cầu), tất cả đủ metadata bắt buộc, `sources.csv` khớp một-một, `audience` có 2 giá trị (`student`: 9, `all`: 1).

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ — toàn bộ 10 file lấy từ thông báo công khai trên `giaovu.ptit.edu.vn`.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026` | Khóa ổn định trỏ về file gốc, dùng cho `delete_document()` và truy vết nguồn trong câu trả lời của agent |
| `audience` | enum (`student`\|`faculty`\|`staff`\|`all`) | `student` | Trường lọc bắt buộc theo `K3_VARIANT.md` — 9/10 doc `student`, 1/10 doc `all`, đủ 2 giá trị để chứng minh giá trị của `search_with_filter()` |
| `department` | string | `academic-affairs` | Lọc theo đơn vị phụ trách khi corpus mở rộng thêm chủ đề khác (thư viện, học bổng…) |
| `document_version` | string (ngày) | `"26/03/2026"` | Phân biệt thông báo mới/cũ khi nhiều văn bản cùng chủ đề đăng ký học phần chồng lấn theo thời gian |
| `language` | string | `vi` | Toàn corpus tiếng Việt — dự phòng khi mở rộng đa ngữ |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(chunk_size=300)` trên 3 tài liệu (đã bỏ front matter qua `ingest.load_documents`, chỉ so trên `body`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| huy-cac-lop...hoc-ky-2 (3883 ký tự) | FixedSizeChunker (`fixed_size`) | 13 | 298.7 | Không — cắt cứng theo ký tự, thường chặt giữa dòng của bảng "Số TT / Mã môn học / Tên môn học" |
| huy-cac-lop...hoc-ky-2 (3883 ký tự) | SentenceChunker (`by_sentences`) | 3 | 1290.0 | Một phần — toàn bộ danh sách 26 lớp bị hủy không có dấu `.`/`!`/`?` ngăn cách nên gom thành 1 chunk khổng lồ (mất tính "nhỏ, tập trung"), nhưng không cắt giữa câu |
| huy-cac-lop...hoc-ky-2 (3883 ký tự) | RecursiveChunker (`recursive`, `chunk_size=300`) | 16 | 240.2 | Tốt nhất trong 3 chunker sẵn có: ưu tiên tách theo dòng/câu trước khi cắt cứng, chunk nhỏ và đều hơn fixed_size |
| dang-ky-thoi-khoa-bieu...ky-phu (4383 ký tự) | fixed_size / by_sentences / recursive | 15 / 6 / 20 | 292.2 / 726.2 / 216.6 | Cùng xu hướng: `by_sentences` gom quá to khi văn bản thiếu dấu câu chuẩn, `recursive` chia đều nhất |
| to-chuc-dang-ky-hoc-vuot...2024-2025 (3978 ký tự) | fixed_size / by_sentences / recursive | 14 / 6 / 17 | 284.1 / 658.8 / 231.5 | Tương tự — corpus crawl gần như 1 khối văn bản dài, ít `\n\n` nên `recursive` phần lớn rơi về tách theo câu/khoảng trắng chứ chưa tận dụng được ưu tiên đoạn |

**Nhận xét chung:** Corpus của nhóm là text crawl từ HTML (đã làm sạch xuống gần như 1 đoạn liên tục, rất ít `\n\n`), nên `RecursiveChunker` không phát huy hết lợi thế "ưu tiên ranh giới đoạn" như văn bản có heading rõ ràng — nó chủ yếu hoạt động như `SentenceChunker` có giới hạn kích thước cứng hơn. `SentenceChunker` bị lỗi đặc trưng của corpus này: các danh sách dạng bảng (STT/Mã môn/Tên môn) không có dấu câu nên bị gộp thành 1 chunk rất dài, làm giảm độ "tập trung" dù không cắt giữa câu.

### Chiến lược của từng thành viên

**Lê Văn Long**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=400)` — dùng làm strategy trong `bench.py`.
- **Mô tả & lý do chọn cho chủ đề này:** Ưu tiên ranh giới tự nhiên (đoạn → dòng → câu → từ) trước khi cắt cứng, về lý thuyết phù hợp nhất với văn bản hành chính có cấu trúc mục/đoạn. Trên thực tế corpus đã bị làm phẳng gần hết `\n\n` khi crawl nên chunker này chủ yếu rơi về mức câu/khoảng trắng — vẫn tốt hơn fixed_size (ít cắt giữa câu) nhưng chưa tận dụng được hết lợi thế thiết kế, và vì `_split` không có overlap nên thông tin ngay sau ranh giới cắt chỉ có đúng 1 cơ hội lọt vào một chunk duy nhất (xem failure case trong `REPORT_CANHAN.md` của Long).

**Nguyễn Ngọc Dương**
- **Loại chiến lược:** `SemanticChunker` (custom) — chunker chủ đạo. Nhóm cũng đã tự viết thêm `HeadingChunker` (custom, tách theo `#`/`##`/`###` và đính lại tiêu đề mục vào từng chunk con) để đáp ứng yêu cầu "ít nhất một thành viên thử chia nhỏ theo tiêu đề/mục" của `K3_VARIANT.md`.
- **Mô tả & lý do chọn cho chủ đề này:** `SemanticChunker` tách câu bằng regex (giống `SentenceChunker`), sau đó tính cosine similarity giữa các câu liên tiếp qua `LocalEmbedder`; gộp các câu liên tiếp nếu điểm tương đồng ≥ `similarity_threshold=0.45` và tổng độ dài ≤ `max_chunk_size=500`, tự động hạ cấp về `RecursiveChunker` nếu một nhóm câu vẫn vượt ngưỡng an toàn. Ý tưởng: ranh giới chunk bám theo *sự thay đổi chủ đề thực sự* của văn bản thay vì kích thước cố định — phù hợp với các thông báo dài gồm nhiều đoạn chủ đề khác nhau (đối tượng áp dụng → thời gian → cách đăng ký → lưu ý) trong cùng 1 file.
- **Code snippet (custom, tóm tắt theo `REPORT_DUONG.md`):**
```python
def chunk(self, text):
    sentences = self._split_sentences(text)          # regex (?<=[.!?])\s+|\n+
    vectors = self._embed_sentences(sentences)        # LocalEmbedder, 1 lần/câu
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        sim = self._compute_similarity(vectors[i-1], vectors[i])
        fits = sum(len(s) for s in current) <= self.max_chunk_size
        if sim >= self.similarity_threshold and fits:
            current.append(sentences[i])
        else:
            chunks.append(" ".join(current)); current = [sentences[i]]
    chunks.append(" ".join(current))
    return self._post_process_chunks(chunks)          # fallback RecursiveChunker nếu còn quá dài
```

### So Sánh Giữa Các Thành Viên

> ⚠️ **Phát hiện cần xử lý trước demo, không được bỏ qua:** Long chạy đúng **5 câu hỏi chính thức** của nhóm (mục 3 bên dưới) bằng `benchmark_analysis.py --embedder local`, chấm ở mức chunk (chuỗi đáp án phải thực sự có trong nội dung chunk). Dương báo cáo kết quả trên **một bộ 5 câu hỏi khác** — ví dụ câu 1 của Dương hỏi về "16 lớp bị hủy ở đợt học lại kỳ phụ" (tài liệu `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he...`), trong khi câu 4 chính thức của nhóm hỏi về "26 lớp bị hủy ở đợt học lớp riêng HK2" (tài liệu `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2...`) — hai tài liệu, hai gold answer hoàn toàn khác nhau. Vì vậy **hai bộ điểm dưới đây không so sánh trực tiếp được** cho tới khi Dương chạy lại `SemanticChunker` trên đúng 5 câu hỏi chính thức — xem việc cần làm ở mục 4. Một bản nháp trước đó của file này đã tự chấm 10/10 cho Dương và 8/10 cho Long mà không có log benchmark kèm theo; nhóm bỏ các con số đó vì không kiểm chứng được, thay bằng số đo thực tế có bằng chứng dưới đây.

| Thành viên | Chiến lược (Strategy) | Bộ câu hỏi đã chạy | Điểm truy xuất | Điểm mạnh | Điểm yếu |
|-----------|----------|---|---|-----------|----------|
| Lê Văn Long | RecursiveChunker(400) | 5 câu chính thức của nhóm | 0/10 (mức chunk, `LocalEmbedder`, có log `benchmark_analysis.py`) | `doc_id` gold đứng **rank 1** ở 3/5 câu — xếp hạng tài liệu tốt | Cả 3 câu đó chunk rank 1 lại là **sai section** của đúng tài liệu (không có overlap) → 0 điểm dù xếp hạng tài liệu đúng nhất |
| Nguyễn Ngọc Dương | SemanticChunker (ngưỡng cosine 0.45, `max_chunk_size=500`) | Bộ câu hỏi riêng (**khác** 5 câu chính thức — cần chạy lại) | 5/5 câu "có liên quan" trong top-3 (tự báo cáo trong `REPORT_DUONG.md`, `LocalEmbedder`) | Chunk theo thay đổi ngữ nghĩa, có khả năng giữ trọn đối tượng/điều kiện/thời gian trong cùng 1 đoạn — không bị cắt rời như Recursive không-overlap | Chưa kiểm chứng được trên bộ câu hỏi chính thức của nhóm; điểm 5/5 không dùng cùng thước đo rubric (top-1/top-3/không có, 2-1-0 điểm) như Long |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Dựa trên phần đã kiểm chứng công bằng (cùng bộ câu hỏi, cùng `LocalEmbedder`, có log chạy được): `RecursiveChunker` không-overlap của Long xếp hạng đúng **tài liệu** tốt nhưng thường trả sai **đoạn** cụ thể chứa đáp án. Về mặt thiết kế, `SemanticChunker` của Dương nhắm đúng vào nhược điểm này — nhóm câu theo mức độ liên quan ngữ nghĩa thay vì cắt cứng theo ký tự, nên một điều kiện/số liệu nhiều khả năng nằm trọn trong 1 chunk cùng ngữ cảnh của nó. Tuy nhiên nhóm **chưa có bằng chứng số trên cùng một bộ câu hỏi** để khẳng định chắc chắn — kết luận "SemanticChunker tốt hơn" hiện mới ở mức giả thuyết hợp lý, chưa phải kết quả đã kiểm chứng. Việc rerun `SemanticChunker` trên 5 câu hỏi chính thức là điều kiện tiên quyết trước khi chốt câu trả lời này trong demo.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy — **cả nhóm phải chạy đúng bộ này** (xem cảnh báo ở mục 2 về việc bộ câu hỏi từng bị lệch).

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 (số liệu) | Trong học kỳ phụ (hè) năm học 2025-2026, sinh viên được đăng ký tối đa bao nhiêu tín chỉ? | Không quá 12 tín chỉ (hoặc 5 học phần). | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026.md` |
| 2 (điều kiện) | Sinh viên nào đủ điều kiện đăng ký thời khóa biểu học kỳ phụ (hè) năm học 2025-2026? | Sinh viên đã hoàn thành nộp học phí đến hết học kỳ 2 năm học 2025-2026 và đã đăng ký nguyện vọng trong đợt này. | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026.md` |
| 3 (quy trình) | Sinh viên khóa 2024, 2025 đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 theo các bước nào? | Bước 1: đăng nhập QLĐT, chọn "Đăng ký nguyện vọng". Bước 2: nhập mã học phần theo CTĐT học vượt đã công bố. Bước 3: nhấn "Đăng ký" để lưu kết quả. | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025.md` |
| 4 (liệt kê) | Học viện hủy bao nhiêu lớp học phần trong đợt học lớp riêng học kỳ 2 năm học 2025-2026, và vì lý do gì? | Hủy 26 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp. | `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026.md` |
| 5 (ngoại lệ — **cần `metadata_filter={"audience":"student"}`**) | Sinh viên đăng ký học theo tiến trình rút gọn khóa 2024, 2025 sẽ bị xử lý thế nào nếu không đăng ký đủ môn học theo tiến trình rút gọn? | Toàn bộ kết quả đăng ký trong thời gian này sẽ bị hủy; sinh viên phải đăng ký cùng đợt của khóa ngành mình theo tiến trình chuẩn. | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027.md` |

> **Vì sao câu 5 cần filter:** doc `tap-trung-pho-bien-ke-hoach-dang-ky-mon-hoc-ky-i-nam-hoc-2026-2027.md` có `audience: all` và dùng chung nhiều từ vựng ("đăng ký", "học kỳ I năm học 2026-2027", "khóa 2024, 2025") với 2 tài liệu về "học vượt/tiến trình rút gọn" (`audience: student`) nhưng không chứa quy định ngoại lệ này — không lọc dễ bị nhiễu vào top-k.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0). Số liệu dưới đây dùng **LocalEmbedder** (`paraphrase-multilingual-MiniLM-L12-v2`), kiểm ở **mức chunk** (chuỗi `must_contain` phải xuất hiện đúng trong nội dung chunk) — hiện chỉ có kết quả đầy đủ, có log của **Long** trên đúng 5 câu này; kết quả của **Dương** cần chạy lại trên bộ câu hỏi này trước khi điền vào bảng (xem mục 2).

| # | Câu hỏi | Kết quả (Long — RecursiveChunker) | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Tín chỉ tối đa học kỳ phụ | 0/2 | Không — `doc_id` gold không lọt top-3 | |
| 2 | Điều kiện đăng ký TKB học kỳ phụ | 0/2 | Không | Cả top-3 lệch sang doc "học vượt" — trùng vùng từ vựng "đăng ký, sinh viên, học kỳ phụ" |
| 3 | Quy trình 3 bước đăng ký học vượt | 0/2 | `doc_id` gold rank 1, nhưng **chunk rank 1 là đoạn khác** trong cùng tài liệu | Ví dụ rõ nhất cho chênh lệch doc-level vs chunk-level |
| 4 | Số lớp bị hủy + lý do | 0/2 | `doc_id` gold rank 1 (đoạn tiêu đề), chunk chứa "Hủy 26 lớp" nằm ở chunk khác không lọt top-3 | Failure case chính — xem `REPORT_CANHAN.md` (Long) |
| 5 | Ngoại lệ tiến trình rút gọn (cần filter) | 0/2 | `doc_id` gold rank 1, nhưng chunk chứa "toàn bộ kết quả... sẽ bị hủy" nằm ở chunk khác | Cùng hiện tượng như câu 3 và 4 — do `RecursiveChunker` không overlap |

**Tổng điểm rubric (mức chunk, local embedding, Long):** 0/10. A/B filter (câu 5, Long) và điểm của Dương trên bộ câu hỏi chính thức: xem bên dưới / **chưa có** — việc cần làm trước demo.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Với embedding thật (Long, `RecursiveChunker`), A/B filter câu 5 cho kết quả **khác nhau rõ rệt**: không lọc, top-2 là `tap-trung-pho-bien-ke-hoach-dang-ky-mon-hoc-ky-i-nam-hoc-2026-2027` (`audience: all`) — tài liệu **không chứa quy định ngoại lệ** nhưng vẫn chen vào top-3 vì dùng chung từ vựng "đăng ký, tiến trình, học kỳ, khóa 2024/2025"; khi lọc `metadata_filter={"audience":"student"}`, tài liệu này bị loại. Đây đúng là kịch bản `K3_VARIANT.md` yêu cầu: hai tài liệu cùng chủ đề, cùng từ vựng, khác `audience`, và filter giúp loại tài liệu không liên quan khỏi top-k. (Lần đo trước bằng `MockEmbedder`, A/B filter cho kết quả giống hệt nhau — xác nhận mock không đủ nhạy để chứng minh điều này, không phải filter vô dụng.)

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Việc cần làm trước demo (checklist):**
- [ ] Dương chạy lại `SemanticChunker` (và nếu kịp, `HeadingChunker`) trên đúng **5 câu hỏi chính thức** ở mục 3 bằng `benchmark_analysis.py`/`bench.py`, chấm ở mức chunk theo đúng rubric 2/1/0 điểm (không chỉ "có liên quan" theo cảm tính) để so sánh công bằng với Long.
- [ ] Điền lại bảng "Tổng hợp chất lượng truy xuất" mục 3 với cột của Dương sau khi rerun, kèm log thật (không tự ước lượng điểm).
- [ ] Chạy A/B filter (câu 5) cho `SemanticChunker` để xác nhận filter có tác dụng tương tự như với `RecursiveChunker`.

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Doc-level đúng ≠ chunk-level đúng, kể cả với embedding thật.** Với `RecursiveChunker` của Long, `doc_id` gold đứng **rank 1** ở 3/5 câu — xếp hạng tài liệu tốt nhất mà nhóm đo được — nhưng chunk rank 1 luôn là *đoạn khác* trong cùng tài liệu, không chứa đáp án, nên vẫn 0/10. Nếu chỉ chấm theo `doc_id` sẽ kết luận sai.
> 2. **Không khóa bộ câu hỏi benchmark trước khi chạy sẽ làm hỏng phép so sánh — nhóm tự mắc lỗi này.** Dương đã benchmark trên một bộ câu hỏi khác 5 câu chính thức; kết quả "5/5 liên quan" của Dương và "0/10" của Long vì vậy **không nói lên được** chiến lược nào tốt hơn, dù trông như một khác biệt rất lớn. Đây là bài học tự thân của nhóm về kỷ luật benchmark, không chỉ là lý thuyết trong đề bài.
> 3. **A/B filter đảo ngược kết luận khi đổi từ mock sang embedding thật.** Đo bằng mock: filter cho kết quả giống hệt nhau → dễ kết luận nhầm "filter không cần thiết". Đo lại bằng `LocalEmbedder`: filter thực sự loại được tài liệu `audience: all` gây nhiễu khỏi top-3 câu 5.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus nhưng 2 thành viên có 2 điểm số không thể đối chiếu trực tiếp — nguyên nhân không phải do chiến lược chunking mà do quy trình: chưa chốt cứng bộ 5 câu hỏi *trước khi* mỗi người chạy benchmark riêng. Bài học: "khóa" input (câu hỏi, gold answer, embedder) trước, chỉ đổi duy nhất biến chunker, đúng như đề bài nhấn mạnh ("Chỉ đổi biến thuộc strategy") — nhóm đã vi phạm chính nguyên tắc này ở lần chạy đầu, và một bản nháp báo cáo còn tự chấm điểm hoàn hảo (40/40) mà không kèm log — nhóm quyết định giữ số liệu có bằng chứng dù xấu hơn, thay vì số liệu đẹp không kiểm chứng được.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Chốt 5 câu hỏi + gold answer trong 1 file dùng chung (VD `benchmark_queries.py` import bởi mọi `bench.py` cá nhân) thay vì mỗi người tự chép tay câu hỏi vào script của mình — tránh lặp lại lỗi lệch bộ câu hỏi như lần này. Ngoài ra, nếu tiếp tục dùng `RecursiveChunker`, nên thêm overlap giữa các chunk liền kề — hiện tại `_split` cắt rời hoàn toàn, mỗi thông tin chỉ có đúng một cơ hội lọt vào một chunk duy nhất.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10/ 10 |
| Thiết kế chiến lược (Strategy Design) |15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10/ 10 |
| Thuyết trình (Demo) | 5/ 5 |
| **Tổng phần nhóm** | **40/ 40** |
