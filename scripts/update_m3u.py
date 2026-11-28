#!/usr/bin/env python3
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from pathlib import Path
import html
import json
import re
import sys

LIVE_URL = "https://maytv.my.id/extream3u26nov2026"
VOD_URL = "https://s.id/vod27"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "playlist"
OUTPUT_FULL = OUTPUT_DIR / "daftar2_full.m3u"
OUTPUT_WEB = OUTPUT_DIR / "web_ready.m3u"
SPLIT_BY_GROUP = True

OTT_USER_AGENT = "OTT Navigator/1.6.7.4 (Linux;Android 11) ExoPlayerLib/2.15.1"
WEB_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
WEB_ORIGIN = "https://sigit-p.github.io"

AUTO_GROUP_RULES = [
    ("INDONESIA", r"\b(rcti|sctv|indosiar|trans\s?tv|trans\s?7|mnctv|gtv|antv|tvone|metro\s?tv|kompas\s?tv|inews|tvri|net\.?\s?tv|mdtv|rtv|mochi|moji|garuda|nusantara|jtv|jak\s?tv|daai|banten|bali\s?tv|sriwijaya|tvmu|mqtv|wesal|rodja|insan\s?tv|surau|nabawi|fatwa|amm\s?tv)\b"),
    ("SPORTS", r"\b(sport|bein|espn|fox\s?sports|arena|bola|soccer|football|premiere|premier|champions|ucl|liga|motogp|f1|ufc|wwe|nba|golf|tennis|badminton|olympic|k-plus|spo\s?tv|spotv|astro\s?super|tnt\s?sports|sky\s?sports|dazn|mola|vidio\s?sport)\b"),
    ("MOVIES & DRAMA", r"\b(hbo|cinemax|fox\s?movies|axn|warner|thrill|celestial|hits|diva|kix|cmc|galaxy|pelangi|tvn|kbs\s?world|sbs|mbc|one\s?hd|gem|animax|zee|bollywood|untamed|rock\s?entertainment|rock\s?action|lifetime|history|discovery|nat\s?geo|animal\s?planet|bbc\s?earth|tlc)\b"),
    ("KIDS & ANIME", r"\b(kids|cartoon|nickelodeon|nick\s?jr|disney|baby|cocomelon|boomerang|animax|aniplus|muse|dreamworks|cbeebies|da\s?vinci|mentari)\b"),
    ("NEWS", r"\b(news|cnn|cnbc|bbc\s?world|al\s?jazeera|bloomberg|nhk|cgtn|dw|france\s?24|rt\s?news|sky\s?news|channel\s?news\s?asia|cna)\b"),
    ("MALAYSIA & SINGAPORE", r"\b(tv1|tv2|tv3|ntv7|8tv|tv9|astro|bernama|awwal|suria|vasantham|channel\s?5|channel\s?8|channel\s?u|mediacorp)\b"),
    ("MUSIC", r"\b(music|mtv|vh1|trace|myx|k-pop|dangdut|pop)\b"),
]


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


def fetch_url(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": OTT_USER_AGENT,
            "Accept": "*/*",
        },
    )
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


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


def guess_group_from_name(channel_name: str) -> str:
    for group_label, pattern in AUTO_GROUP_RULES:
        if re.search(pattern, channel_name, re.IGNORECASE):
            return group_label
    return "LAINNYA"


def clean_group_label(raw_group: str) -> str:
    cleaned = re.sub(r"^[▶►•\-\s]+", "", raw_group).strip()
    return cleaned.replace('"', "'")


def ensure_group_title_in_extinf(extinf_line: str, group_name: str) -> str:
    safe_group = clean_group_label(group_name)
    if re.search(r'group-title="[^"]*"', extinf_line, re.IGNORECASE):
        return re.sub(
            r'group-title="[^"]*"',
            f'group-title="{safe_group}"',
            extinf_line,
            count=1,
            flags=re.IGNORECASE,
        )
    if "," in extinf_line:
        meta, title = extinf_line.split(",", 1)
        return f'{meta} group-title="{safe_group}",{title}'
    return extinf_line


def append_lines_to_grouped(
    lines: list[str],
    grouped: dict[str, list[dict]],
    seen_entries: set,
    default_fallback_group: str = "",
):
    current_extinf = ""
    current_group = ""
    current_name = ""
    current_props = []

    for line in lines:
        upper_line = line.upper()
        if upper_line.startswith("#EXTM3U"):
            continue

        if upper_line.startswith("#EXTINF"):
            current_extinf = line
            current_props = []
            current_name = line.rsplit(",", 1)[-1].strip() if "," in line else "Unknown"

            group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            if group_match and group_match.group(1).strip():
                current_group = clean_group_label(group_match.group(1))
            else:
                current_group = ""

        elif upper_line.startswith(("#KODIPROP:", "#EXTVLCOPT:", "#EXTGRP:")):
            if current_extinf:
                if upper_line.startswith("#EXTGRP:"):
                    grp_val = clean_group_label(line.split(":", 1)[1])
                    if grp_val and not current_group:
                        current_group = grp_val
                else:
                    current_props.append(line)

        elif re.match(r"https?://", line, re.IGNORECASE):
            if current_extinf:
                if not current_group or current_group.upper() in ("UNCATEGORIZED", "UNDEFINED", "NONE", "GENERAL"):
                    current_group = default_fallback_group or guess_group_from_name(current_name)

                final_extinf = ensure_group_title_in_extinf(current_extinf, current_group)

                dedup_key = (current_group, current_name.lower(), line)
                if dedup_key not in seen_entries:
                    seen_entries.add(dedup_key)
                    grouped[current_group].append({
                        "name": current_name,
                        "group": current_group,
                        "extinf": final_extinf,
                        "props": current_props,
                        "url": line,
                    })
                current_extinf = ""
                current_props = []


def format_channel_block(ch: dict) -> list[str]:
    kodi_props = [p for p in ch["props"] if p.upper().startswith("#KODIPROP:")]
    vlc_opts = [p for p in ch["props"] if p.upper().startswith("#EXTVLCOPT:")]
    other_props = [
        p for p in ch["props"]
        if not p.upper().startswith(("#KODIPROP:", "#EXTVLCOPT:"))
    ]
    return [
        ch["extinf"],
        f"#EXTGRP:{ch['group']}",
        *kodi_props,
        *vlc_opts,
        *other_props,
        ch["url"],
    ]


def is_web_compatible(ch: dict) -> bool:
    """Scanner CORS & compatibility untuk browser (HTTPS, tanpa DRM/Referer wajib, lolos CORS)."""
    url = ch["url"]
    if not url.lower().startswith("https://"):
        return False

    # Tolak stream dengan DRM (#KODIPROP) atau Referer khusus yang diblokir browser standar
    for prop in ch["props"]:
        upper_p = prop.upper()
        if upper_p.startswith("#KODIPROP:") or "HTTP-REFERRER" in upper_p or "HTTP-REFERER" in upper_p:
            return False

    headers = {
        "User-Agent": WEB_USER_AGENT,
        "Origin": WEB_ORIGIN,
    }

    # Coba HEAD terlebih dahulu, fallback ke GET Range 0-1 jika server menolak HEAD (405)
    for method in ("HEAD", "GET"):
        req_headers = dict(headers)
        if method == "GET":
            req_headers["Range"] = "bytes=0-1"
        req = Request(url, method=method, headers=req_headers)
        try:
            with urlopen(req, timeout=6) as resp:
                acao = resp.headers.get("Access-Control-Allow-Origin", "")
                if resp.status in (200, 206) and (acao == "*" or WEB_ORIGIN in acao):
                    return True
                return False
        except Exception as exc:
            code = getattr(exc, "code", None)
            if method == "HEAD" and code in (403, 405, 501):
                continue
            return False
    return False


def slugify_filename(name: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return clean or "lainnya"


def atomic_write(target: Path, content: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def main():
    grouped: dict[str, list[dict]] = defaultdict(list)
    seen_entries = set()
    header = "#EXTM3U"

    # 1. Ambil & parse Live TV
    live_page = fetch_url(LIVE_URL)
    live_lines = parse_raw_lines(live_page)
    if live_lines and live_lines[0].startswith("#EXTM3U"):
        header = live_lines[0]
    append_lines_to_grouped(live_lines, grouped, seen_entries)

    # 2. Ambil & parse VOD
    try:
        vod_page = fetch_url(VOD_URL)
        vod_lines = parse_raw_lines(vod_page)
        append_lines_to_grouped(vod_lines, grouped, seen_entries, default_fallback_group="VOD LAINNYA")
    except Exception as vod_err:
        print(f"PERINGATAN VOD dilewati: {vod_err}", file=sys.stderr)

    total_items = sum(len(items) for items in grouped.values())
    if total_items < 10:
        raise RuntimeError(
            f"Hasil ekstraksi hanya memiliki {total_items} item valid; file lama tidak diubah."
        )

    # 3. Simpan daftar2_full.m3u (Lengkap untuk OTT Navigator / VLC / MPV)
    full_output_lines = [header]
    for group_name in sorted(grouped.keys()):
        full_output_lines.append("")
        full_output_lines.append(f"# ==================== {group_name} ====================")
        for ch in grouped[group_name]:
            full_output_lines.extend(format_channel_block(ch))

    atomic_write(OUTPUT_FULL, "\n".join(full_output_lines) + "\n")

    # 4. Simpan pecahan per kategori ke playlist/grup/
    if SPLIT_BY_GROUP:
        group_dir = OUTPUT_DIR / "grup"
        for group_name, channels in grouped.items():
            sub_lines = [header]
            for ch in channels:
                sub_lines.extend(format_channel_block(ch))
            sub_file = group_dir / f"{slugify_filename(group_name)}.m3u"
            atomic_write(sub_file, "\n".join(sub_lines) + "\n")

    # 5. Scan & simpan web_ready.m3u (Khusus Web Player / Browser CORS-safe)
    web_grouped: dict[str, list[dict]] = defaultdict(list)
    all_candidates = [
        ch for group_name in sorted(grouped.keys())
        for ch in grouped[group_name]
    ]

    with ThreadPoolExecutor(max_workers=24) as pool:
        scan_results = list(pool.map(is_web_compatible, all_candidates))

    for ch, ok in zip(all_candidates, scan_results):
        if ok:
            web_grouped[ch["group"]].append(ch)

    total_web = sum(len(items) for items in web_grouped.values())
    if total_web > 0:
        web_output_lines = [header]
        for group_name in sorted(web_grouped.keys()):
            web_output_lines.append("")
            web_output_lines.append(f"# ==================== {group_name} ====================")
            for ch in web_grouped[group_name]:
                web_output_lines.extend(format_channel_block(ch))
        atomic_write(OUTPUT_WEB, "\n".join(web_output_lines) + "\n")

    print(f"Berhasil Full : {OUTPUT_FULL} ({total_items} item)")
    print(f"Berhasil Web  : {OUTPUT_WEB} ({total_web} item lolos CORS)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"GAGAL: {exc}", file=sys.stderr)
        sys.exit(1)
