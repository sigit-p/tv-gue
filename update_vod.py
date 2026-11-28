#!/usr/bin/env python3
from collections import defaultdict
from urllib.request import Request, urlopen
from pathlib import Path
import html
import re
import sys

# Menggunakan s.id/vod27 agar selalu mengikuti redirect ke commit terbaru
SOURCE_URL = "https://s.id/vod27"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "vod_full.m3u"
SPLIT_BY_GROUP = True  # Membuat pecahan file per kategori film di folder vod_grup/

USER_AGENT = "OTT Navigator/1.6.7.4 (Linux;Android 11) ExoPlayerLib/2.15.1"


def parse_and_group_vod(raw_text: str) -> tuple[str, dict[str, list[dict]]]:
    raw_text = html.unescape(raw_text)
    start_idx = raw_text.find("#EXTM3U")
    if start_idx == -1:
        raise RuntimeError("Header #EXTM3U tidak ditemukan pada sumber VOD.")

    lines = [
        line.strip().replace("\ufeff", "")
        for line in raw_text[start_idx:].splitlines()
        if line.strip()
    ]

    header = lines[0]
    grouped: dict[str, list[dict]] = defaultdict(list)

    current_extinf = ""
    current_group = "VOD LAINNYA"
    current_name = ""
    current_props = []
    seen_entries = set()

    for line in lines[1:]:
        upper_line = line.upper()

        if upper_line.startswith("#EXTINF"):
            current_extinf = line
            current_props = []
            current_name = line.rsplit(",", 1)[-1].strip() if "," in line else "Unknown"

            group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            if group_match and group_match.group(1).strip():
                # Bersihkan simbol panah dekoratif agar nama grup rapi di IPTVnator
                clean_grp = re.sub(r"^[▶►•\-\s]+", "", group_match.group(1)).strip()
                current_group = clean_grp or "VOD LAINNYA"
                current_extinf = re.sub(
                    r'group-title="[^"]*"',
                    f'group-title="{current_group}"',
                    current_extinf,
                    count=1,
                    flags=re.IGNORECASE,
                )
            else:
                current_group = "VOD LAINNYA"
                if "," in line:
                    meta, title = line.split(",", 1)
                    current_extinf = f'{meta} group-title="VOD LAINNYA",{title}'

        elif upper_line.startswith(("#KODIPROP:", "#EXTVLCOPT:", "#EXTGRP:")):
            if current_extinf and not upper_line.startswith("#EXTGRP:"):
                current_props.append(line)

        elif re.match(r"https?://", line, re.IGNORECASE):
            if current_extinf:
                dedup_key = (current_group, current_name.lower(), line)
                if dedup_key not in seen_entries:
                    seen_entries.add(dedup_key)
                    grouped[current_group].append({
                        "name": current_name,
                        "group": current_group,
                        "extinf": current_extinf,
                        "props": current_props,
                        "url": line,
                    })
                current_extinf = ""
                current_props = []

    return header, grouped


def format_vod_block(item: dict) -> list[str]:
    return [
        item["extinf"],
        f"#EXTGRP:{item['group']}",
        *item["props"],
        item["url"],
    ]


def slugify_filename(name: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return clean or "vod_lainnya"


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

    header, grouped = parse_and_group_vod(page)

    total_vod = sum(len(items) for items in grouped.values())
    if total_vod < 5:
        raise RuntimeError(f"Hasil ekstraksi hanya memiliki {total_vod} VOD; file lama dipertahankan.")

    full_lines = [header]
    for group_name in sorted(grouped.keys()):
        full_lines.append("")
        full_lines.append(f"# ==================== {group_name} ====================")
        for item in grouped[group_name]:
            full_lines.extend(format_vod_block(item))

    atomic_write(OUTPUT_FILE, "\n".join(full_lines) + "\n")

    if SPLIT_BY_GROUP:
        vod_dir = OUTPUT_DIR / "vod_grup"
        for group_name, items in grouped.items():
            sub_lines = [header]
            for item in items:
                sub_lines.extend(format_vod_block(item))
            sub_file = vod_dir / f"{slugify_filename(group_name)}.m3u"
            atomic_write(sub_file, "\n".join(sub_lines) + "\n")

    print(f"Berhasil: {OUTPUT_FILE}")
    print(f"Total VOD unik: {total_vod} (dalam {len(grouped)} kategori)")
    print("-" * 45)
    for group_name in sorted(grouped.keys()):
        print(f"  - {group_name}: {len(grouped[group_name])} judul")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"GAGAL: {exc}", file=sys.stderr)
        sys.exit(1)
