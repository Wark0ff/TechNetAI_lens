#!/usr/bin/env python3
# Строит сводный data/reports_index.json по всему корпусу sources_text/.
# Аннотация и оглавление извлекаются дословно (без домысливания).
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT = os.path.join(ROOT, "sources_text")
catalog = json.load(open(os.path.join(ROOT, "data/reports_catalog.json"), encoding="utf-8"))

# --- curated deep entries (сохраняем то, что разобрано вручную) ---
prev_path = os.path.join(ROOT, "data/reports_index.json")
curated = {}
if os.path.exists(prev_path):
    prev = json.load(open(prev_path, encoding="utf-8"))
    id2file = {
        "SRC-TN-MATERIALS-2026": "2026_0630_nm_cpim_kompozicionnyh_materialov_tekhnet.pdf",
        "SRC-TN-BVS-MONO-2026": "2026_0630_tekhnet_bvs_itog.pdf",
        "SRC-TN-DIGEST-06": "2026_Tehnet_Digest_06.pdf",
        "SRC-TN-DIGEST-07": "2026_0624_Дайджест_Июнь_2026.pdf",
    }
    for r in prev.get("reports", []):
        f = id2file.get(r.get("source_id"))
        if f and r.get("key_theses"):
            curated[f] = {"key_theses": r["key_theses"], "locators": r.get("locators", {}), "source_id": r["source_id"]}

# файлы, чей текст получен OCR (возможны мелкие ошибки распознавания)
OCR_FILES = {
    "2022_1220_Rejting_kompanij_Tekhnet_zashchishchennyj.pdf",
    "2022_1226_Dajdzhest_2_KLYUCHEVYE_SOBYTIYA_RYNKA_VENCHURNOGO_FINANSIROVANIYA_PEREDOVYH_PROIZVODSTVENNYH_TEKHNOLOGIJ.pdf",
    "2022_1226_Dajdzhest_2_KLYUCHEVYE_SOBYTIYA_V_OBLASTI_GOSUDARSTVENNYH_PROGRAMM_I_MER_PODDERZHKI_PEREDOVYH_PROIZVODSTVENNYH_TEKHNOLOGIJ.pdf",
    "2022_1226_Dajdzhest_2_KLYUCHEVYE_SOBYTIYA_V_OBLASTI_PEREDOVYH_NAUCHNO-TEKHNOLOGICHESKIH_PROEKTOV_VEDUSHCHIH_ROSSIJSKIH_I_ZARUBEZHNYH_NAUCHNYH_.pdf",
    "2022_1226_Dajdzhest_2_KLYUCHEVYE_SOBYTIYA_V_OBLASTI_STARTAP-RAZRABOTOK_NA_BAZE_PEREDOVYH_PROIZVODSTVENNYH_TEKHNOLOGIJ.pdf",
    "2022_1229_Otchet_Additivnye_tekhnologii_zashchishchennyj.pdf",
}

def clean(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()

def slug(base, year):
    b = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()[:48]
    return f"SRC-TN-{year or 'x'}-{b}"

def _looks_like_toc(frag):
    # много точечных лидеров или высокая доля цифр => это оглавление, а не текст
    if len(re.findall(r"\.{3,}", frag)) >= 2:
        return True
    digits = sum(c.isdigit() for c in frag[:200])
    return digits > 40

def extract_abstract(txt):
    limit = int(len(txt) * 0.7)
    # перебираем ВСЕ вхождения маркеров; берём первое, за которым идёт проза, а не оглавление
    for mk in ["ВВЕДЕНИЕ", "АННОТАЦИЯ", "РЕФЕРАТ", "ВВЕДЕНИE"]:
        start = 0
        while True:
            i = txt.find(mk, start)
            if i == -1 or i > limit:
                break
            frag = clean(txt[i + len(mk): i + len(mk) + 1600])
            start = i + len(mk)
            if len(frag) > 200 and not _looks_like_toc(frag):
                return frag[:1200]
    # fallback: первый содержательный фрагмент прозы
    for para in re.split(r"\n", clean(txt)):
        p = para.strip()
        if len(p) > 250 and not _looks_like_toc(p):
            return p[:1000]
    return clean(txt)[:800]

HEAD_RE = re.compile(r"^(ГЛАВА\s+\d+.*|РАЗДЕЛ\s+\d+.*|\d+\.\s+[А-ЯЁA-Z].{4,}|[А-ЯЁ][А-ЯЁ \-«»,]{10,})$")
def extract_toc(txt):
    heads = []
    # приоритет: секция СОДЕРЖАНИЕ/ОГЛАВЛЕНИЕ
    m = re.search(r"(СОДЕРЖАНИЕ|ОГЛАВЛЕНИЕ)", txt)
    scope = txt[m.start(): m.start() + 4000] if m else txt[:6000]
    for line in scope.splitlines():
        line = line.strip()
        # строки с точечными лидерами оглавления
        if re.search(r"\.{3,}\s*\d+\s*$", line):
            h = re.sub(r"\s*\.{3,}.*$", "", line).strip()
            if 6 <= len(h) <= 120 and h not in heads:
                heads.append(h)
        elif HEAD_RE.match(line) and 8 <= len(line) <= 100 and line not in heads:
            heads.append(line)
        if len(heads) >= 20:
            break
    return heads

reports = []
img_based = 0
for r in sorted(catalog["reports"], key=lambda x: (-(x["year"] or 0), x["file"])):
    f = r["file"]
    base = os.path.splitext(f)[0]
    tpath = os.path.join(TXT, base + ".txt")
    txt = open(tpath, encoding="utf-8").read() if os.path.exists(tpath) else ""
    chars = len(txt)
    image_based = chars < 1500
    if image_based: img_based += 1
    cur = curated.get(f)
    entry = {
        "source_id": cur["source_id"] if cur else slug(base, r["year"]),
        "file": f,
        "text_file": f"sources_text/{base}.txt" if not image_based else None,
        "year": r["year"],
        "category": r["category"],
        "topics": r["topics"],
        "source_url": r["source_url"],
        "chars": chars,
        "image_based": image_based,
        "abstract": None if image_based else extract_abstract(txt),
        "toc": [] if image_based else extract_toc(txt),
        "key_theses": cur["key_theses"] if cur else [],
        "locators": cur["locators"] if cur else {},
        "ocr": f in OCR_FILES,
        "depth": "curated" if cur else ("metadata_only" if image_based else ("auto_ocr" if f in OCR_FILES else "auto")),
    }
    reports.append(entry)

out = {
    "version": "1.1.0",
    "purpose": "Сводный индекс всего корпуса отчётов ИЦ «Технет» СПбПУ для RAG-навигатора. abstract и toc извлечены дословно из sources_text/. key_theses заполнены для кураторски разобранных отчётов.",
    "citation_rule": "Цитируй по text_file с указанием source_id, года и раздела из toc. Не приписывай источнику того, чего нет в тексте. Для image_based отчётов текст не извлечён (нужен OCR) — опирайся на метаданные и topics.",
    "depth_legend": {
        "curated": "разобрано вручную: точные тезисы и локаторы",
        "auto": "есть полный текст (text_file) + авто-аннотация и оглавление",
        "auto_ocr": "текст получен OCR (возможны мелкие ошибки распознавания)",
        "metadata_only": "текст не извлечён"
    },
    "total": len(reports),
    "counts": {
        "curated": sum(1 for r in reports if r["depth"] == "curated"),
        "auto": sum(1 for r in reports if r["depth"] == "auto"),
        "auto_ocr": sum(1 for r in reports if r["depth"] == "auto_ocr"),
        "metadata_only": sum(1 for r in reports if r["depth"] == "metadata_only"),
    },
    "reports": reports,
}
json.dump(out, open(os.path.join(ROOT, "data/reports_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("reports:", out["total"], "| counts:", out["counts"])
