"""
src/clean_data.py — Data Cleaning Pipeline for RAG Knowledge Base.

Cleans raw text/markdown documents in data/k3_university before chunking and embedding,
and outputs clean documents to data/k3_university_clean while preserving directory structure.

Pipeline Steps (in order):
    1. Truncate trailing content after "Tải về" (if present).
    2. Normalize line breaks:
        - Trim leading/trailing whitespace on each line.
        - Filter out whitespace-only lines.
        - Collapse multiple consecutive empty lines into a single blank line.
    3. Normalize inline whitespace:
        - Replace multiple consecutive spaces within a line with a single space.
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def clean_text(raw_text: str) -> str:
    """
    Clean text content following strict sequential pipeline rules.

    Args:
        raw_text: Raw string content from source file.

    Returns:
        Cleaned text string.
    """
    if not raw_text:
        return ""

    # Step 1: Cut off trailing footer content after cutoff markers (Tải về / Chia sẻ:)
    # Prefer checking after "Trân trọng" if present, or anywhere in text.
    cutoff_markers = ["Tải về", "Chia sẻ:"]

    # Check if "Trân trọng" exists in text
    tran_trong_idx = raw_text.find("Trân trọng")

    earliest_cutoff = -1
    for marker in cutoff_markers:
        # Search marker starting from "Trân trọng" position if it exists, otherwise from beginning
        start_search = tran_trong_idx if tran_trong_idx != -1 else 0
        idx = raw_text.find(marker, start_search)
        if idx != -1:
            if earliest_cutoff == -1 or idx < earliest_cutoff:
                earliest_cutoff = idx

    if earliest_cutoff != -1:
        raw_text = raw_text[:earliest_cutoff]

    # Step 2 & Step 3: Line-by-line normalization and space cleanup
    raw_lines = raw_text.splitlines()
    cleaned_lines: list[str] = []
    consecutive_empty = 0

    for line in raw_lines:
        # Trim leading and trailing whitespace on each line
        trimmed_line = line.strip()

        # Normalize multiple spaces inside the line to a single space
        normalized_line = " ".join(trimmed_line.split())

        if not normalized_line:
            # Empty line tracking
            consecutive_empty += 1
            if consecutive_empty == 1:
                cleaned_lines.append("")
        else:
            consecutive_empty = 0
            cleaned_lines.append(normalized_line)

    # Join cleaned lines into final text and strip leading/trailing newlines
    return "\n".join(cleaned_lines).strip()


def process_file(source_path: Path, destination_path: Path) -> bool:
    """
    Read, clean, and write a single text file.

    Args:
        source_path: Path to the input file.
        destination_path: Path to the target output file.

    Returns:
        True if processing succeeded, False otherwise.
    """
    logging.info(f"Processing file: {source_path}")
    try:
        content = source_path.read_text(encoding="utf-8")
        cleaned_content = clean_text(content)

        # Ensure parent directories exist
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(cleaned_content, encoding="utf-8")
        return True
    except Exception as error:
        logging.error(f"Failed to process {source_path}: {error}")
        return False


def process_directory(source_dir: Path, output_dir: Path) -> tuple[int, int, int]:
    """
    Recursively process all text files (.txt, .md) in source_dir and preserve directory structure.

    Args:
        source_dir: Input directory path.
        output_dir: Output directory path.

    Returns:
        Tuple of (total_files, successful_files, failed_files).
    """
    if not source_dir.exists():
        logging.error(f"Source directory does not exist: {source_dir}")
        return (0, 0, 0)

    all_files = [
        path for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    total_files = len(all_files)
    successful_files = 0
    failed_files = 0

    logging.info(f"Found {total_files} text file(s) in {source_dir}")

    for file_path in all_files:
        relative_path = file_path.relative_to(source_dir)
        target_path = output_dir / relative_path

        if process_file(file_path, target_path):
            successful_files += 1
        else:
            failed_files += 1

    return (total_files, successful_files, failed_files)


def main() -> int:
    source_dir = Path("data/k3_university")
    output_dir = Path("data/k3_university_clean")

    logging.info(f"Starting data cleaning pipeline: {source_dir} -> {output_dir}")

    total, success, failed = process_directory(source_dir, output_dir)

    logging.info("=" * 50)
    logging.info("Cleaning Pipeline Summary:")
    logging.info(f"  Total files found: {total}")
    logging.info(f"  Successfully cleaned: {success}")
    logging.info(f"  Failed: {failed}")
    logging.info("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())