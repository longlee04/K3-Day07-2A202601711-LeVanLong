# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Văn Long
**Mã học viên:** 2A202601711
**Nhóm:** NEXACO
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine similarity đo góc giữa hai vector embedding, không đo độ dài của chúng. Giá trị gần 1 nghĩa là hai vector gần như cùng hướng — hai đoạn văn bản mang cùng chủ đề/ý nghĩa — bất kể văn bản dài hay ngắn.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên phải nộp học phí trước khi đăng ký học phần."
- Câu B: "Trước khi đăng ký môn học, sinh viên cần hoàn thành nghĩa vụ học phí."
- Tại sao tương đồng: Đo bằng `LocalEmbedder` + `compute_similarity` cho **0.918**. Hai câu diễn đạt cùng một quy định (đóng học phí là điều kiện tiên quyết để đăng ký học phần), chỉ đảo trật tự từ và dùng từ đồng nghĩa ("học phần" ↔ "môn học").

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên đăng ký học phần trên hệ thống QLĐT."
- Câu B: "Thư viện mở cửa từ 7h30 đến 21h30 các ngày trong tuần."
- Tại sao khác: Đo được **0.152**. Hai câu không chia sẻ chủ đề, thực thể hay ý định nào — một câu về đăng ký học phần, một câu về giờ mở cửa thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Hai văn bản có độ dài khác nhau (một câu ngắn, một đoạn dài) có thể tạo ra vector với độ lớn (magnitude) rất khác nhau dù cùng nói về một chủ đề — Euclidean distance bị ảnh hưởng bởi độ lớn này nên dễ đánh giá sai. Cosine chỉ quan tâm hướng của vector nên phản ánh đúng mức độ *giống nhau về ý nghĩa*, không lẫn với *độ dài văn bản*.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Theo `FixedSizeChunker.chunk`, bước nhảy `step = chunk_size - overlap = 500 - 50 = 450`. Vòng lặp lấy `start = 0, 450, 900, ...` và dừng ngay sau khi `start + chunk_size >= 10000`, tức `start >= 9500`. Bội số của 450 đầu tiên ≥ 9500 là `9900` (= 22 × 450), ứng với `start` thứ 23 (tính từ 0). Vậy có `start = 0, 450, ..., 9900` → **23 chunks** (chunk cuối dài `10000 - 9900 = 100` ký tự). Đã verify bằng code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a"*10000)` → 23 chunks.
> *Đáp án:* **23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `step = 500 - 100 = 400` (nhỏ hơn trước) nên cần nhiều bước hơn để phủ hết 10,000 ký tự → tăng từ 23 lên **25 chunks** (verify bằng code, chunk cuối dài 400 ký tự). Muốn overlap nhiều hơn vì nó giữ lại ngữ cảnh ở ranh giới cắt: nếu một câu/điều kiện nằm vắt ngang điểm cắt, overlap giúp câu đó vẫn xuất hiện trọn vẹn trong ít nhất một chunk, đổi lại phải lưu/embed nhiều chunk hơn (tốn chi phí hơn).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split(r"(?<=[.!?])\s+", text)`: lookbehind giữ dấu `.`/`!`/`?` ở cuối câu trước, chỉ tách tại khoảng trắng theo sau dấu câu, nên câu không bị mất dấu kết thúc. Edge case: text rỗng trả `[]` ngay; sau khi split, `strip()` từng câu và loại bỏ chuỗi rỗng (do nhiều khoảng trắng/xuống dòng liên tiếp) trước khi gộp theo nhóm `max_sentences_per_chunk` và nối bằng dấu cách.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` xử lý text rỗng, gọi `_split(text, self.separators)` rồi strip/lọc chunk rỗng. `_split` có 2 base case: (1) text đã đủ ngắn (`len <= chunk_size`) → trả nguyên văn; (2) hết separator hoặc separator hiện tại là chuỗi rỗng → cắt cố định theo `chunk_size`. Nếu separator hiện tại không xuất hiện trong text, đệ quy với phần separator còn lại (không tiêu tốn "ranh giới" tương ứng). Nếu có, tách theo separator rồi gộp các phần liền nhau cho tới sát `chunk_size`; phần nào một mình đã dài hơn `chunk_size` được đệ quy lại bằng separator ưu tiên thấp hơn — đảm bảo luôn tiến gần base case, không lặp vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được embed một lần (`self._embedding_fn(doc.content)`) và lưu thành dict `{id, content, metadata, embedding}` trong list `self._store` (in-memory, không dùng ChromaDB vì môi trường không có sẵn thư viện). `id` ghép `doc.id` với `self._next_index` tăng dần để không trùng khi có nhiều chunk cùng nguồn; `metadata` là bản copy (`dict(doc.metadata)`) với `doc_id` mặc định về `doc.id` nếu chưa có, để `delete_document`/filter luôn có khóa ổn định trỏ về file gốc chứ không phải id của từng chunk. `search` embed câu hỏi một lần, tính dot product (`_dot`) giữa vector câu hỏi và từng embedding đã lưu (các embedder đều chuẩn hóa vector nên dot product ≈ cosine similarity), sort giảm dần theo score rồi cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc **trước**, rank **sau**: `search_with_filter` giữ lại những record mà mọi cặp key/value trong `metadata_filter` khớp đúng với metadata của record (hoặc giữ nguyên toàn bộ nếu không có filter), sau đó đưa tập đã lọc vào cùng hàm `_search_records` mà `search` dùng — nhờ vậy `metadata_filter=None` cho kết quả y hệt `search`. Lọc sau khi đã lấy top-k sẽ có rủi ro mất tài liệu hợp lệ chỉ vì nó không lọt top-k *trước khi lọc*. `delete_document` xây lại `self._store` bằng list comprehension loại bỏ mọi record có `metadata['doc_id'] == doc_id`, rồi so sánh kích thước trước/sau để trả về `True`/`False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Nếu store rỗng, trả thông báo rõ ràng ngay, không gọi LLM vô ích. Ngược lại lấy top-k qua `store.search` (hoặc `store.search_with_filter` khi có `metadata_filter`), đánh số từng chunk `[1]`, `[2]`... kèm `doc_id` để có thể truy vết ngược về đúng file nguồn khi debug. Prompt gồm 1 dòng chỉ dẫn "chỉ dùng context, nói rõ khi context không đủ", khối context đã đánh số, câu hỏi, và nhãn `Answer:` — rồi giao cho `self.llm_fn` sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================== 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Dự đoán trước "cao/thấp" (ngưỡng 0.5) rồi đo bằng `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`) + `compute_similarity`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên phải nộp học phí trước khi đăng ký học phần." | "Trước khi đăng ký môn học, sinh viên cần hoàn thành nghĩa vụ học phí." | cao | 0.918 | Đúng |
| 2 | "Học viện tổ chức kỳ thi kết thúc học phần vào đầu tháng 8." | "Đầu tháng 8, các em sẽ thi hết môn." | cao | 0.439 | Sai (thấp hơn dự đoán) |
| 3 | "Sinh viên đăng ký học phần trên hệ thống QLĐT." | "Thư viện mở cửa từ 7h30 đến 21h30 các ngày trong tuần." | thấp | 0.152 | Đúng |
| 4 | "Học viện hủy 26 lớp học phần vì không đủ sinh viên đăng ký." | "Hôm nay trời Hà Nội mưa to." | thấp | -0.089 | Đúng |
| 5 | "Sinh viên không được đăng ký quá 12 tín chỉ trong học kỳ phụ." | "Sinh viên phải đăng ký tối thiểu 12 tín chỉ trong học kỳ chính." | thấp | 0.868 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 bất ngờ nhất: hai câu có **quy định trái ngược nhau hoàn toàn** (giới hạn *tối đa* 12 tín chỉ ở học kỳ phụ vs bắt buộc *tối thiểu* 12 tín chỉ ở học kỳ chính) nhưng vẫn được chấm 0.868 — gần bằng cặp paraphrase thật (0.918). Điều này cho thấy embedding câu chủ yếu nắm bắt **chủ đề và từ khóa chung** ("sinh viên", "đăng ký", "12 tín chỉ", "học kỳ"), chứ không phân biệt được sự phủ định/đối lập logic ("tối đa" ↔ "tối thiểu", "phụ" ↔ "chính"). Hệ quả thực tế cho RAG của nhóm: ở câu benchmark hỏi về tín chỉ tối đa học kỳ phụ, hệ thống hoàn toàn có thể vô tình trộn lẫn quy định của một học kỳ khác vì hai câu "nghe rất giống nhau" với embedding dù ý nghĩa ngược nhau — đúng là điều đã xảy ra ở mục 5 bên dưới.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

**Chiến lược của tôi:** `RecursiveChunker(chunk_size=400)` (dùng trong `bench.py`). **Embedder:** `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`) — ban đầu tưởng mạng tới HuggingFace Hub bị chặn, hóa ra là backend transfer "Xet" (`hf-xet`) bị treo chứ mạng vẫn thông (`curl` tải thẳng vẫn được); tải lại thành công (~449MB) nên dùng embedding thật thay vì mock cho toàn bộ kết quả dưới đây.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tín chỉ tối đa học kỳ phụ | doc `to-chuc-dang-ky-hoc-vuot...`: "Tổ chức đăng ký học vượt học kỳ I năm học 2026–2027..." | 0.770 | Không — đúng "họ hàng" chủ đề đăng ký nhưng sai tài liệu, không có "12 tín chỉ" | Trích context sai tài liệu |
| 2 | Điều kiện đăng ký TKB học kỳ phụ | doc `to-chuc-dang-ky-hoc-vuot...`: cùng đoạn trên | 0.849 | Không — vẫn lệch sang "học vượt" thay vì "học kỳ phụ" | Không có điều kiện thật |
| 3 | Quy trình 3 bước đăng ký học vượt | doc `to-chuc-dang-ky-hoc-vuot...` (**đúng `doc_id` gold**, rank 1) | 0.886 | **Đúng tài liệu, sai đoạn** — chunk rank 1 là đoạn giới thiệu chung, không phải 3 bước cụ thể | Không liệt kê được 3 bước |
| 4 | Số lớp bị hủy + lý do | doc `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng...` (**đúng `doc_id` gold**, rank 1) | 0.780 | **Đúng tài liệu, sai đoạn** — chunk rank 1 là tiêu đề, không chứa "Hủy 26 lớp" | Không có số "26" |
| 5 | Ngoại lệ tiến trình rút gọn (filter `audience=student`) | doc `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien...` (**đúng `doc_id` gold**, rank 1) | 0.822 | **Đúng tài liệu, sai đoạn** — chunk chứa "toàn bộ kết quả... sẽ bị hủy" nằm ở chunk khác cùng tài liệu | Không chứa câu xử lý ngoại lệ |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 0 / 5 ở mức chunk (dù 3/5 câu đã tìm **đúng tài liệu ở rank 1**) — xem `benchmark_analysis.py --embedder local`.

### Failure case (có bằng chứng từ top-k)

**Query:** "Học viện hủy bao nhiêu lớp học phần trong đợt học lớp riêng học kỳ 2 năm học 2025-2026, và vì lý do gì?"
**Gold:** "Hủy 26 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp." (trong `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026.md`)

**Bằng chứng:** Với strategy của tôi (RecursiveChunker, chunk_size=400), top-1 **đúng `doc_id` gold** (score 0.780, preview: "Hủy các lớp học phần đợt học lớp riêng, học kỳ 2 năm học 2025-2026 Đăn...") — chunker xếp hạng đúng tài liệu ở vị trí tốt nhất có thể. Nhưng chunk đó dừng lại ở đoạn tiêu đề/mở đầu; câu "Hủy 26 lớp học phần do số lượng sinh viên đăng ký..." nằm ở một chunk **khác** của cùng tài liệu (do `chunk_size=400` cắt tài liệu ~3900 ký tự thành 16 mảnh) và không lọt vào top-3. Cả top-2, top-3 đều là tài liệu khác chủ đề.

**Nguyên nhân:** `RecursiveChunker._split` không có tham số overlap — mỗi ranh giới cắt là tuyệt đối, nên một thông tin nằm ngay sau ranh giới chỉ tồn tại trong đúng 1 chunk duy nhất, tách biệt hoàn toàn khỏi chunk mở đầu (tiêu đề, ngữ cảnh chung) vốn có điểm tương đồng cao hơn với câu hỏi tổng quát. Đây đúng là hiện tượng "top-3 đúng tài liệu nhưng sai section" mà đề bài nêu: cosine đo độ giống *chủ đề* của cả đoạn văn (chunk mở đầu rất giống chủ đề "hủy lớp học phần"), không đo *mật độ thông tin trả lời được* (chunk chứa con số "26" cụ thể).

**Đề xuất sửa:** Thêm overlap (VD: 50-80 ký tự) giữa các chunk liền kề trong `RecursiveChunker`, để câu chứa số liệu cụ thể luôn xuất hiện cùng ngữ cảnh tiêu đề/mở đầu của tài liệu ở ít nhất 1 chunk — giảm rủi ro "mỗi thông tin chỉ có một cơ hội duy nhất lọt top-k". Cách khác: giảm `chunk_size` để chunk mở đầu không lấn sang đoạn có số liệu, buộc chunk chứa số liệu phải đứng độc lập và có cơ hội cạnh tranh điểm số riêng.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> `SentenceChunker` (thành viên B trong bảng so sánh nhóm) đạt 5/10 — cao nhất — chính vì chunk theo câu tự nhiên giữ số liệu/điều kiện đi cùng ngữ cảnh câu đó, không bị tách rời như cách `RecursiveChunker` của tôi cắt theo kích thước cố định. Bài học: với văn bản hành chính đặc câu (không heading rõ), "không cắt giữa câu" quan trọng hơn "chunk đều kích thước".

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) |10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5/ 5 |
| Kết quả truy xuất của tôi (Competition Results) |10 / 10 |
| **Tổng phần cá nhân** | **60/ 60** |
