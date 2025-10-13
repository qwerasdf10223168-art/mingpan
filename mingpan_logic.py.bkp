# -*- coding: utf-8 -*-
import re
from datetime import datetime

# ======================= 全域設定 =======================
DEBUG = True  # 預設開啟除錯
CYEAR = None  # ← 由 app.py 設定（流年年份）

# ======================= 開關設定 =======================
OUTPUT_SWITCH = {
    "DA_FOUR_HUA": {label: True for label in ["命","兄","夫","子","財","疾","遷","僕","官","田","福","父"]},
    "LIU_FOUR_HUA": {label: True for label in ["命","兄","夫","子","財","疾","遷","僕","官","田","福","父"]},
    "LIU_MING_FOUR_HUA": {"YEAR_STEM_LINE": True, "BRANCH_STEM_LINE": True},
    "LIU_YUE": {"SHOW_PALACE_ROW": True, "SHOW_HUA_ROW": True, "MONTHS": list(range(1,13))},
}

# ===== 白名單 =====
MAIN_STARS = ["紫微","天府","天相","天梁","武曲","七殺","破軍","廉貞","天機","太陽","太陰","巨門","天同","貪狼"]
AUX_STARS  = ["文曲","文昌","左輔","右弼"]
MINI_STARS = ["火星","鈴星","祿存","擎羊","陀螺"]
ALIASES = {"陀羅": "陀螺"}

PALACE_ABBR = {
    "命宮":"命","兄弟宮":"兄","夫妻宮":"夫","子女宮":"子","財帛宮":"財","疾厄宮":"疾",
    "遷移宮":"遷","交友宮":"僕","事業宮":"官","田宅宮":"田","福德宮":"福","父母宮":"父",
}

# ===== 生年四化對照 =====
YEAR_HUA = {
    "甲": {"祿":"廉貞","權":"破軍","科":"武曲","忌":"太陽"},
    "乙": {"祿":"天機","權":"天梁","科":"紫微","忌":"太陰"},
    "丙": {"祿":"天同","權":"天機","科":"文昌","忌":"廉貞"},
    "丁": {"祿":"太陰","權":"天同","科":"天機","忌":"巨門"},
    "戊": {"祿":"貪狼","權":"太陰","科":"右弼","忌":"天機"},
    "己": {"祿":"武曲","權":"貪狼","科":"天梁","忌":"文曲"},
    "庚": {"祿":"太陽","權":"武曲","科":"太陰","忌":"天同"},
    "辛": {"祿":"巨門","權":"太陽","科":"文曲","忌":"文昌"},
    "壬": {"祿":"天梁","權":"紫微","科":"左輔","忌":"武曲"},
    "癸": {"祿":"破軍","權":"巨門","科":"太陰","忌":"貪狼"},
}

# ===== 工具 =====
def normalize_token(t: str) -> str:
    t = t.strip()
    t = ALIASES.get(t, t)
    t = re.sub(r"(旺|陷|廟|地|平|權|科|祿|忌|利)+$", "", t)
    return t

def pick_whitelist(star_line: str):
    raw = re.split(r"[,\，\s、]+", star_line.strip())
    raw = [x for x in raw if x]
    found_main, found_aux, found_mini = [], [], []
    for tok in raw:
        norm = normalize_token(tok)
        if norm in MAIN_STARS and norm not in found_main:
            found_main.append(norm)
        elif norm in AUX_STARS and norm not in found_aux:
            found_aux.append(norm)
        elif norm in MINI_STARS and norm not in found_mini:
            found_mini.append(norm)
    return found_main, found_aux, found_mini

def palace_to_abbr(palace_name: str) -> str:
    if "命宮" in palace_name:
        return "命"
    for full, ab in PALACE_ABBR.items():
        if full in palace_name:
            return ab
    return ""

def parse_year_stem(raw_text: str) -> str:
    m = re.search(r"干支[:：︰]\s*([甲乙丙丁戊己庚辛壬癸])[子丑寅卯辰巳午未申酉戌亥]年", raw_text)
    return m.group(1) if m else ""

def parse_birth_year(raw_text: str) -> int:
    m = re.search(r"陽曆[:：︰]?\s*(\d{4})年", raw_text)
    return int(m.group(1)) if m else 0

def current_year() -> int:
    return datetime.now().year

# ===== 解析主函式 =====
def parse_chart(raw_text: str):
    block_pat = re.compile(
        r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])【([^】]+)】\s*"
        r"大限:([0-9]+)-([0-9]+)\s*小限:[^\n]*\n([^\n]+)"
    )
    data, col_order = {}, []
    for m in re.finditer(block_pat, raw_text):
        col = m.group(1)
        palace = m.group(2)
        dx_a, dx_b = m.group(3), m.group(4)
        star_line = m.group(5)

        main, aux, mini = pick_whitelist(star_line)
        abbr = palace_to_abbr(palace)
        data[col] = {
            "palace": palace,
            "main": main,
            "aux": aux,
            "mini": [ALIASES.get(x, x) for x in mini],
            "daxian": f"{dx_a}~{dx_b}",
            "abbr": abbr,
        }
        if col not in col_order:
            col_order.append(col)
    year_stem = parse_year_stem(raw_text)
    return data, col_order, year_stem

# ===== 以下功能直接來自 V10，未更動主要邏輯 =====
# === 各種輔助函式（省略重複註解） ===
PALACE_ORDER_CANONICAL = ["命","兄","夫","子","財","疾","遷","僕","官","田","福","父"]
ZODIAC = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
STEMS  = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]

def reorder_cols_by_palace(data, col_order):
    buckets = {abbr: None for abbr in PALACE_ORDER_CANONICAL}
    used = set()
    for col in col_order:
        abbr = (data.get(col, {}).get("abbr") or "").strip()
        if abbr in PALACE_ORDER_CANONICAL and buckets[abbr] is None:
            buckets[abbr] = col
            used.add(col)
    ordered = [buckets[a] for a in PALACE_ORDER_CANONICAL if buckets[a]]
    tail = [c for c in col_order if c not in used]
    return ordered + tail

def zodiac_of_year(year): return ZODIAC[(year - 1984) % 12]
def year_stem_of_year(year): return STEMS[(year - 1984) % 10]
def get_stem_from_col(col): return col[0] if col and col[0] in YEAR_HUA else ""
def get_col_with_branch(cols, branch): return next((c for c in cols if branch in c), "")
def find_col_for_label(cols, line, label): 
    for i, lab in enumerate(line):
        if lab == label: return cols[i]
    return ""

# === Debug 輔助 ===
def debug_four_hua_locate(tag, stem, cols, data):
    cells = {c: [] for c in cols}
    if not stem or stem not in YEAR_HUA:
        if DEBUG: print(f"DEBUG[HUA] {tag}：無有效天干（{stem}）")
        return cells
    for typ in ["祿","權","科","忌"]:
        star = YEAR_HUA[stem].get(typ,"")
        located = [c for c in cols if (star in data[c]["main"]) or (star in data[c]["aux"]) or (star in data[c]["mini"])]
        for c in located:
            cells[c].append(f"{star}{typ}")
    return cells

# === v7 主輸出 ===
def render_markdown_table_v7(data, col_order, year_stem, raw_text):
    cols = reorder_cols_by_palace(data, col_order)
    header = ["原始資料", "宮干支"] + cols
    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["----","---"] + ["----"]*len(cols)) + " |")

    # 主輔小大
    for label, key in [("主星","main"),("輔星","aux"),("小星","mini"),("大限","daxian")]:
        row = ["", label]
        for c in cols:
            val = data[c][key] if key != "daxian" else data[c][key]
            row.append("/".join(val) if isinstance(val, list) else val)
        lines.append("| " + " | ".join(row) + " |")

    # 本命
    row = ["本命","宮位"]
    for c in cols: row.append(data[c]["abbr"])
    lines.append("| " + " | ".join(row) + " |")

    # 生年四化
    if year_stem and year_stem in YEAR_HUA:
        cell_map = debug_four_hua_locate("生年四化", year_stem, cols, data)
        row = ["", f"生年四化（{year_stem}）"]
        for c in cols: row.append("/".join(cell_map[c]) if cell_map[c] else "")
        lines.append("| " + " | ".join(row) + " |")

    # 流年命
    liu_row = ["命","兄","夫","子","財","疾","遷","僕","官","田","福","父"]
    row = [f"流年命（{CYEAR}）","宮位"]
    [row.append(v) for v in liu_row]
    lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

# 預設 CYEAR
if 'CYEAR' not in globals() or CYEAR is None:
    CYEAR = 2026
