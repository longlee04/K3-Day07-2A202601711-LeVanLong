"""bench.py — chạy MỘT chiến lược chunking qua bộ 5 benchmark query đã chốt của nhóm K3.

Dùng lại ingest.build_knowledge_base() để nạp dữ liệu (parse front matter -> chunk ->
gắn metadata -> EmbeddingStore); phần việc còn lại của file này chỉ là:
    1. Chọn chunker (DÒNG DUY NHẤT nên khác nhau giữa các thành viên trong nhóm).
    2. Nạp cả thư mục corpus.
    3. Chạy 5 query qua search()/search_with_filter() và in kết quả.
"""
from __future__ import annotations

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import _mock_embed

DATA_DIR = "data/k3_university"

# 1. Chọn chunker của riêng bạn — đây là DÒNG DUY NHẤT khác với bạn cùng nhóm.
STRATEGY_NAME = "RecursiveChunker(chunk_size=400)"
chunker = RecursiveChunker(chunk_size=400)

# 5 benchmark query đã chốt cùng nhóm (đa dạng: số liệu, điều kiện, quy trình, liệt kê, ngoại lệ).
# Gold answer trích trực tiếp từ corpus data/k3_university/*.md.
BENCHMARK_QUERIES = [
    {
        "question": "Trong học kỳ phụ (hè) năm học 2025-2026, sinh viên được đăng ký tối đa bao nhiêu tín chỉ?",
        "gold_answer": "Không quá 12 tín chỉ (hoặc 5 học phần).",
        "expected_doc_id": "dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026",
        "metadata_filter": None,
    },
    {
        "question": "Sinh viên nào đủ điều kiện đăng ký thời khóa biểu học kỳ phụ (hè) năm học 2025-2026?",
        "gold_answer": (
            "Sinh viên đã hoàn thành nộp học phí đến hết học kỳ 2 năm học 2025-2026 theo "
            "thông báo của phòng Tài chính kế toán và đã đăng ký nguyện vọng trong đợt này."
        ),
        "expected_doc_id": "dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026",
        "metadata_filter": None,
    },
    {
        "question": "Sinh viên khóa 2024, 2025 đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 theo các bước nào?",
        "gold_answer": (
            "Bước 1: đăng nhập QLĐT, chọn \"Đăng ký nguyện vọng\". "
            "Bước 2: nhập mã học phần theo Chương trình đào tạo học vượt đã công bố. "
            "Bước 3: nhấn \"Đăng ký\" để lưu kết quả."
        ),
        "expected_doc_id": "to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025",
        "metadata_filter": None,
    },
    {
        "question": "Học viện hủy bao nhiêu lớp học phần trong đợt học lớp riêng học kỳ 2 năm học 2025-2026, và vì lý do gì?",
        "gold_answer": "Hủy 26 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp.",
        "expected_doc_id": "huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026",
        "metadata_filter": None,
    },
    {
        # Câu bắt buộc cần metadata_filter (K3_VARIANT.md): doc "tap-trung-pho-bien..." có
        # audience=all, dùng chung nhiều từ vựng (đăng ký, học kỳ I 2026-2027, khóa 2024/2025)
        # với doc "tiến trình rút gọn" (audience=student) nên dễ gây nhiễu nếu không lọc.
        "question": (
            "Sinh viên đăng ký học theo tiến trình rút gọn khóa 2024, 2025 sẽ bị xử lý thế nào "
            "nếu không đăng ký đủ môn học theo tiến trình rút gọn?"
        ),
        "gold_answer": (
            "Toàn bộ kết quả đăng ký trong thời gian này sẽ bị hủy; sinh viên phải đăng ký "
            "cùng đợt của khóa ngành mình theo tiến trình chuẩn."
        ),
        "expected_doc_id": "dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027",
        "metadata_filter": {"audience": "student"},
    },
]


def demo_llm(prompt: str) -> str:
    """LLM giả lập để chạy bench mà không cần API key."""
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


def _preview(text: str, width: int = 90) -> str:
    flat = " ".join(text.split())
    return flat[: width] + ("..." if len(flat) > width else "")


def main() -> None:
    print(f"=== Strategy: {STRATEGY_NAME} ===")
    store = build_knowledge_base(DATA_DIR, _mock_embed, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunk từ {DATA_DIR}\n")

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    for index, item in enumerate(BENCHMARK_QUERIES, start=1):
        question = item["question"]
        metadata_filter = item["metadata_filter"]

        print(f"--- Query {index}: {question}")
        if metadata_filter:
            print(f"    (metadata_filter={metadata_filter})")
            results = store.search_with_filter(question, top_k=3, metadata_filter=metadata_filter)
        else:
            results = store.search(question, top_k=3)

        for rank, result in enumerate(results, start=1):
            doc_id = result["metadata"].get("doc_id", result["id"])
            print(
                f"    top-{rank}: score={result['score']:.3f} doc_id={doc_id} "
                f"preview={_preview(result['content'])!r}"
            )

        answer = agent.answer(question, top_k=3, metadata_filter=metadata_filter)
        print(f"    gold answer : {item['gold_answer']}")
        print(f"    agent answer: {_preview(answer, 200)}\n")


if __name__ == "__main__":
    main()
