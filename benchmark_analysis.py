"""benchmark_analysis.py — so sánh nhiều chiến lược chunking ở MỨC CHUNK, không chỉ doc_id.

Mô phỏng "mỗi thành viên chạy một strategy" bằng cách chạy tuần tự 3 chunker trên cùng
corpus, cùng 5 benchmark query, cùng embedder. Với mỗi query, kiểm tra một chuỗi đặc
trưng (must_contain) có thực sự xuất hiện trong nội dung chunk hay không, thay vì chỉ
kiểm doc_id gold có mặt trong top-3.

Chạy: python benchmark_analysis.py [--embedder mock|local]
"""
from __future__ import annotations

import argparse
import unicodedata

from ingest import build_knowledge_base
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import LocalEmbedder, _mock_embed

DATA_DIR = "data/k3_university"

STRATEGIES = {
    "Thanh_vien_A_FixedSize400": lambda: FixedSizeChunker(chunk_size=400, overlap=50),
    "Thanh_vien_B_Sentence4": lambda: SentenceChunker(max_sentences_per_chunk=4),
    "Thanh_vien_C_Recursive400": lambda: RecursiveChunker(chunk_size=400),
}

# 5 benchmark query đã chốt cùng nhóm (xem report/REPORT_NHOM.md mục 3).
# must_contain: chuỗi đặc trưng PHẢI có mặt trong nội dung chunk để tính là "chunk chứa đáp án"
# (kiểm ở mức chunk, không chỉ doc_id gold có xuất hiện hay không).
QUERIES = [
    {
        "question": "Trong học kỳ phụ (hè) năm học 2025-2026, sinh viên được đăng ký tối đa bao nhiêu tín chỉ?",
        "expected_doc_id": "dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026",
        "must_contain": "không được đăng ký quá 12 tín chỉ",
        "metadata_filter": None,
    },
    {
        "question": "Sinh viên nào đủ điều kiện đăng ký thời khóa biểu học kỳ phụ (hè) năm học 2025-2026?",
        "expected_doc_id": "dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026",
        "must_contain": "hoàn thành nộp học phí đến hết học kỳ 2 năm học 2025-2026",
        "metadata_filter": None,
    },
    {
        "question": "Sinh viên khóa 2024, 2025 đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 theo các bước nào?",
        "expected_doc_id": "to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025",
        "must_contain": "chương trình đào tạo học vượt đã được công bố",
        "metadata_filter": None,
    },
    {
        "question": "Học viện hủy bao nhiêu lớp học phần trong đợt học lớp riêng học kỳ 2 năm học 2025-2026, và vì lý do gì?",
        "expected_doc_id": "huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026",
        "must_contain": "hủy 26 lớp học phần",
        "metadata_filter": None,
    },
    {
        "question": (
            "Sinh viên đăng ký học theo tiến trình rút gọn khóa 2024, 2025 sẽ bị xử lý thế nào "
            "nếu không đăng ký đủ môn học theo tiến trình rút gọn?"
        ),
        "expected_doc_id": "dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027",
        "must_contain": "toàn bộ kết quả đăng ký trong thời gian này sẽ bị hủy",
        "metadata_filter": {"audience": "student"},
    },
]


def _fold(text: str) -> str:
    """Hạ chữ thường để so khớp must_contain không phân biệt hoa/thường."""
    return unicodedata.normalize("NFC", text).lower()


def _preview(text: str, width: int = 70) -> str:
    flat = " ".join(text.split())
    return flat[:width] + ("..." if len(flat) > width else "")


def score_query(results: list[dict], must_contain: str, expected_doc_id: str) -> dict:
    needle = _fold(must_contain)
    doc_hit_rank = None
    chunk_hit_rank = None
    for rank, result in enumerate(results, start=1):
        if doc_hit_rank is None and result["metadata"].get("doc_id") == expected_doc_id:
            doc_hit_rank = rank
        if chunk_hit_rank is None and needle in _fold(result["content"]):
            chunk_hit_rank = rank

    if chunk_hit_rank == 1:
        rubric_score = 2
    elif chunk_hit_rank is not None:
        rubric_score = 1
    else:
        rubric_score = 0

    return {
        "doc_hit_rank": doc_hit_rank,
        "chunk_hit_rank": chunk_hit_rank,
        "rubric_score": rubric_score,
    }


def run_strategy(name: str, chunker, embedding_fn) -> dict:
    store = build_knowledge_base(DATA_DIR, embedding_fn, chunker=chunker, collection_name=name)
    print(f"\n{'=' * 70}\nStrategy: {name}  (chunk count = {store.get_collection_size()})\n{'=' * 70}")

    total = 0
    per_query = []
    for index, item in enumerate(QUERIES, start=1):
        results = store.search(item["question"], top_k=3)
        outcome = score_query(results, item["must_contain"], item["expected_doc_id"])
        total += outcome["rubric_score"]

        print(f"\nQuery {index}: {item['question']}")
        for rank, r in enumerate(results, start=1):
            flag = "MUST_CONTAIN" if _fold(item["must_contain"]) in _fold(r["content"]) else ""
            print(
                f"  top-{rank}: score={r['score']:.3f} doc_id={r['metadata'].get('doc_id')} "
                f"{flag} preview={_preview(r['content'])!r}"
            )
        print(
            f"  -> doc_id gold ở rank {outcome['doc_hit_rank']}; "
            f"chunk chứa must_contain ở rank {outcome['chunk_hit_rank']}; "
            f"diem rubric = {outcome['rubric_score']}/2"
        )
        per_query.append({"question": item["question"], **outcome})

    # A/B filter cho query bắt buộc filter (query cuối)
    filt_item = QUERIES[-1]
    with_filter = store.search_with_filter(filt_item["question"], top_k=3, metadata_filter=filt_item["metadata_filter"])
    without_filter = store.search(filt_item["question"], top_k=3)
    ids_with = [r["metadata"].get("doc_id") for r in with_filter]
    ids_without = [r["metadata"].get("doc_id") for r in without_filter]
    print(f"\nA/B filter (query 5, filter={filt_item['metadata_filter']}):")
    print(f"  voi filter    -> {ids_with}")
    print(f"  khong filter  -> {ids_without}")
    print(f"  {'GIONG HET NHAU' if ids_with == ids_without else 'KHAC NHAU'}")

    print(f"\nTong diem rubric strategy '{name}': {total}/10")
    return {"name": name, "total": total, "per_query": per_query, "ab_same": ids_with == ids_without}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedder", choices=["mock", "local"], default="mock")
    args = parser.parse_args()

    if args.embedder == "local":
        embedding_fn = LocalEmbedder()
        print("Embedder: LocalEmbedder (paraphrase-multilingual-MiniLM-L12-v2)")
    else:
        embedding_fn = _mock_embed
        print(
            "Embedder: MockEmbedder (KHONG mang ngu nghia thuc, chi kiem luong ky thuat).\n"
            "-> Diem so/rank tuyet doi khong dang tin; chi dung de kiem tra so chunk, "
            "chunk coherence va provenance (metadata co truy vet duoc khong)."
        )

    summary = [run_strategy(name, builder(), embedding_fn) for name, builder in STRATEGIES.items()]

    print(f"\n{'=' * 70}\nTong hop\n{'=' * 70}")
    for row in summary:
        print(f"{row['name']:32} tong={row['total']}/10  AB_filter_giong_nhau={row['ab_same']}")


if __name__ == "__main__":
    main()
