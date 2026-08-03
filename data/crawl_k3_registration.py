#!/usr/bin/env python3
"""
Crawl data script for K3 university course registration documents.
Fetches 10 items matching '.item.type_1' selector from PTIT website,
parses detail pages, cleans content, and formats to Markdown with YAML front matter.
Also writes/updates data/k3_university/sources.csv.
"""

import csv
import html
import os
import re
import urllib.request
from datetime import date
from html.parser import HTMLParser


class ContentParser(HTMLParser):
    """Parser giúp bóc tách văn bản thuần từ HTML, tự động loại bỏ menu, footer, script, style."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'nav', 'footer', 'header']:
            self.skip = True
        elif tag in [
            'p',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'li',
            'div',
            'tr',
            'table',
            'br',
        ]:
            if not self.skip:
                self.text_parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'nav', 'footer', 'header']:
            self.skip = False
        elif tag in [
            'p',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'li',
            'div',
            'tr',
            'table',
        ]:
            if not self.skip:
                self.text_parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.text_parts.append(data)


def slugify(value: str) -> str:
    """Tạo doc_id chuẩn SEO (chữ thường, không dấu, nối bằng dấu gạch ngang)."""
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'document'


def main():
    url_listing = 'https://giaovu.ptit.edu.vn/ke-hoach-dao-tao/dang-ky-hoc-phan/'
    print(f'Fetching listing page: {url_listing}')
    req = urllib.request.Request(url_listing, headers={'User-Agent': 'Mozilla/5.0'})
    html_text = urllib.request.urlopen(req).read().decode('utf-8')

    # Tìm 10 item đầu tiên khớp selector <li class="item type_1">
    items_raw = re.findall(
        r'<li[^>]*class=\"[^\"]*item\s+type_1[^\"]*\"[^>]*>(.*?)</li>',
        html_text,
        re.DOTALL,
    )

    items = []
    for block in items_raw[:10]:
        m = re.search(
            r'<h2[^>]*class=\"[^\"]*post-title[^\"]*\"[^>]*>\s*<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>',
            block,
            re.DOTALL,
        )
        if not m:
            m = re.search(
                r'<a[^>]*href=\"([^\"]+)\"[^>]*title=\"([^\"]+)\"', block, re.DOTALL
            )
        if m:
            link = m.group(1).strip()
            title_raw = m.group(2).strip()
            title = html.unescape(re.sub(r'<[^>]+>', '', title_raw)).strip()
            items.append({'link': link, 'title': title})

    output_dir = 'data/k3_university'
    os.makedirs(output_dir, exist_ok=True)

    manifest_records = []
    retrieved_date = date.today().isoformat()

    for index, item in enumerate(items, start=1):
        link = item['link']
        title = item['title']

        url_path_stem = re.sub(r'/$', '', link).split('/')[-1]
        doc_id = slugify(url_path_stem)

        print(f'[{index}/10] Crawling: {title}')
        print(f'   URL: {link}')

        try:
            req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            detail_html = urllib.request.urlopen(req).read().decode('utf-8')

            m_content = re.search(
                r'<div[^>]*class=\"[^\"]*entry-content[^\"]*\"[^>]*>(.*?)</div>\s*</div>',
                detail_html,
                re.DOTALL,
            )
            body_html = m_content.group(1) if m_content else detail_html

            p = ContentParser()
            p.feed(body_html)
            text = ''.join(p.text_parts)
            text = re.sub(r'[ \t]+', ' ', text)
            text = re.sub(r'\n\s*\n+', '\n\n', text).strip()

            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', detail_html)
            doc_version = date_match.group(1) if date_match else 'not-stated'

        except Exception as e:
            print(f'   [ERROR] Failed to fetch detail: {e}')
            text = title
            doc_version = 'not-stated'

        md_content = f'''---
doc_id: {doc_id}
title: "{title}"
audience: student
department: academic-affairs
language: vi
source_url: {link}
retrieved_at: {retrieved_date}
document_version: "{doc_version}"
---

# {title}

{text}
'''
        file_name = f'{doc_id}.md'
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        manifest_records.append({
            'doc_id': doc_id,
            'file_path': f'data/k3_university/{file_name}',
            'title': title,
            'source_url': link,
            'retrieved_at': retrieved_date,
            'document_version': doc_version,
            'license_or_permission': 'public-page',
        })

    sources_path = os.path.join(output_dir, 'sources.csv')
    with open(sources_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'doc_id',
                'file_path',
                'title',
                'source_url',
                'retrieved_at',
                'document_version',
                'license_or_permission',
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_records)

    print(f'\nFinished! Successfully processed {len(manifest_records)} documents and updated {sources_path}.')


if __name__ == '__main__':
    main()
