#!/usr/bin/env python3
from collections import defaultdict
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from pathlib import Path
import html
import json
import re
import sys

SOURCE_URL = "https://maytv.my.id/extream3u26nov2026"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "daftar2_full.m3u"
SPLIT_BY_GROUP = True  # Ubah ke False jika hanya ingin membuat daftar2_full.m3u tanpa folder grup/

USER_AGENT = "OTT Navigator/1.6.7.4 (Linux;Android 11) ExoPlayerLib/2.15.1"


class PreParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.current = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "pre":
            if self.depth == 0:
                self.current = []
            self.depth += 1

    def handle_endtag(self, tag):
        if tag.lower() == "pre" and self.depth:
            self.depth -= 1
            if self.depth == 0:
                self.blocks.append("".join(self.current))

    def handle_data(self, data):
        if self.depth:
            self.current.append(data)


def extract_from_json_strings(page: str) -> list[str]:
    results = []
    for match in re.finditer(r"#EXTM3U", page):
        start_quote = page.rfind('"', 0, match.start())
        while start_quote != -1:
            if start_quote > 0 and page[start_quote - 1] == "\\":
                start_quote = page.rfind('"', 0, start_quote - 1)
                continue

            pos = match.end()
            while pos < len(page):
                end_quote = page.find('"', pos)
                if end_quote == -1:
                    break
                bs_count = 0
                idx = end_quote - 1
                while idx >= start_quote and page[idx] == "\\":
                    bs_count += 1
                    idx -= 1
                if bs_count % 2 == 0:
                    candidate_literal = page[start_quote : end_quote + 1]
                    try:
                        decoded = json.loads(candidate_literal)
                        if isinstance(decoded, str) and "#EXTINF" in decoded:
                            results.append(decoded)
                    except json.JSONDecodeError:
                        pass
                    break
                pos = end_quote + 1
            break
    return results


def parse_raw_lines(page: str) -> list[str]:
    parser = PreParser()
    parser.feed(page)

    candidates = [
        block for block in parser.blocks
        if "#EXTM3U" in block and "#EXTINF" in block
    ]
    if not candidates:
        candidates = extract_from_json_strings(page)

    if candidates:
        raw = max(candidates, key=lambda block: block.count("#EXTINF"))
    elif "#EXTM3U" in page and "#EXTINF" in page:
        raw = page
    else:
        raise RuntimeError("Blok playlist M3U tidak ditemukan pada halaman sumber.")

    raw = html.unescape(raw)
    raw = raw[raw.find("#EXTM3U"):]

    if "\\n" in raw and raw.count("\n") < 5:
        raw = (
            raw.replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace('\\"', '"')
            .replace("\\/", "/")
        )

    lines = []
    for original_line in raw.splitlines():
        line = original_line.strip().replace("\ufeff", "")
        if not line:
            continue
        if re.match(r"https?://", line, re.IGNORECASE):
            line = re.split(r'["<\\]', line, maxsplit=1)[0].strip()
        if line.startswith("#") or re.match(r"https?://", line, re.IGNORECASE):
            lines.append(line)

    if not lines or not lines[0].startswith("#EXTM3U"):
        raise RuntimeError("Hasil ekstraksi tidak diawali #EXTM3U.")

    return lines


def parse_and_group_channels(lines: list[str]) -> tuple[str, dict[str, list[dict]]]:
    """Memecah playlist menjadi blok channel utuh dan mengelompokkannya per group-title."""
    header = lines[0]
    grouped: dict[str, list[dict]] = defaultdict(list)

    current_extinf = ""
    current_group = "LAINNYA"
    current_name = ""
    current_props = []
    seen_entries = set()

    for line in lines[1:]:
        upper_line = line.upper()

        if upper_line.startswith("#EXTINF"):
            current_extinf = line
            current_props = []

            group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            if group_match and group_match.group(1).strip():
                current_group = group_match.group(1).strip()
            else:
                current_group = "LAINNYA"
                if "," in line:
                    meta, title = line.split(",", 1)
                    current_extinf = f'{meta} group-title="LAINNYA",{title}'

            current_name = line.rsplit(",", 1)[-1].strip() if "," in line else "Unknown"

        elif upper_line.startswith(("#KODIPROP:", "#EXTVLCOPT:", "#EXTGRP:")):
            if current_extinf:
                if upper_line.startswith("#EXTGRP:") and current_group == "LAINNYA":
                    grp_val = line.split(":", 1)[1].strip()
                    if grp_val:
                        current_group = grp_val
                else:
                    current_props.append(line)

        elif re.match(r"https?://", line, re.IGNORECASE):
            if current_extinf:
                dedup_key = (current_group, current_name.lower(), line)
                if dedup_key not in seen_entries:
                    seen_entries.add(dedup_key)
                    grouped[current_group].append({
                        "name": current_name,
                        "extinf": current_extinf,
                        "props": current_props,
                        "url": line,
                    })
                current_extinf = ""
                current_props = []

    return header, grouped


def format_channel_block(ch: dict) -> list[str]:
    """Merapikan urutan tag per channel: #EXTINF -> #KODIPROP -> #EXTVLCOPT -> URL."""
    kodi_props = [p for p in ch["props"] if p.upper().startswith("#KODIPROP:")]
    vlc_opts = [p for p in ch["props"] if p.upper().startswith("#EXTVLCOPT:")]
    other_props = [
        p for p in ch["props"]
        if not p.upper().startswith(("#KODIPROP:", "#EXTVLCOPT:"))
    ]
    return [ch["extinf"], *kodi_props, *vlc_opts, *other_props, ch["url"]]


def slugify_filename(name: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return clean or "lainnya"


def atomic_write(target: Path, content: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def main():
    request = Request(
        SOURCE_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        },
    )
    with urlopen(request, timeout=60) as response:
        page = response.read().decode("utf-8", errors="replace")

    raw_lines = parse_raw_lines(page)
    header, grouped = parse_and_group_channels(raw_lines)

    total_channels = sum(len(items) for items in grouped.values())
    if total_channels < 10:
        raise RuntimeError(
            f"Hasil ekstraksi hanya memiliki {total_channels} channel valid; file lama tidak diubah."
        )

    full_output_lines = [header]
    for group_name in grouped:
        full_output_lines.append("")
        full_output_lines.append(f"# ==================== {group_name} ====================")
        for ch in grouped[group_name]:
            full_output_lines.extend(format_channel_block(ch))

    atomic_write(OUTPUT_FILE, "\n".join(full_output_lines) + "\n")

    if SPLIT_BY_GROUP:
        group_dir = OUTPUT_DIR / "grup"
        for group_name, channels in grouped.items():
            sub_lines = [header]
            for ch in channels:
                sub_lines.extend(format_channel_block(ch))
            sub_file = group_dir / f"{slugify_filename(group_name)}.m3u"
            atomic_write(sub_file, "\n".join(sub_lines) + "\n")

    print(f"Berhasil: {OUTPUT_FILE}")
    print(f"Total channel unik: {total_channels} (dalam {len(grouped)} kategori)")
    print("-" * 45)
    for group_name, channels in grouped.items():
        print(f"  - {group_name}: {len(channels)} channel")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"GAGAL: {exc}", file=sys.stderr)
        sys.exit(1)
