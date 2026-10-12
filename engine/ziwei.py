# -*- coding: utf-8 -*-
"""紫微斗数引擎：命宫定位、五行局、十四主星安星、生年四化、三方四正格局，
以及十四辅星（文昌文曲、左辅右弼、天魁天钺、禄存、擎羊陀罗、火星铃星、地空地劫、天马）。

约定：采用传统安星诀（中州派简化）——命宫纳音定五行局，紫微由命宫顺数(局数-1)步；
辅星按年干/年支/生月/生时之主流诀安布（流派细节已锁定以保证可复现）。
"""
import datetime
import cnlunar
from . import constants as C


def _norm(n: int) -> int:
    """把地支序号规整到 1..12（子=1 ... 亥=12）。"""
    n = n % 12
    return n if n != 0 else 12


def _hour_to_shichen(hour: int) -> int:
    """小时 -> 时辰序号 1..12（子=1: 23-1时；丑=2: 1-3时；... 午=7: 11-13时）。"""
    h = hour % 24
    if h == 23 or h < 1:
        return 1  # 子时
    return (h - 1) // 2 + 2  # 丑=2 ... 午=7 ... 亥=12


def _wuhu_dun(year_gan: str) -> int:
    """五虎遁：返回正月(寅)天干序号（甲=0）。"""
    table = {"甲": 2, "己": 2, "乙": 4, "庚": 4, "丙": 6, "辛": 6,
             "丁": 8, "壬": 8, "戊": 0, "癸": 0}
    return table[year_gan]


# ---- 辅星安星诀（年干/年支/生月/生时）----
CHANG = {"甲": "巳", "乙": "午", "丙": "未", "丁": "申", "戊": "酉",
         "己": "戌", "庚": "亥", "辛": "子", "壬": "丑", "癸": "寅"}      # 文昌
WEN = {"甲": "亥", "乙": "戌", "丙": "酉", "丁": "申", "戊": "未",
       "己": "午", "庚": "巳", "辛": "辰", "壬": "卯", "癸": "寅"}        # 文曲
TIANKUI = {"甲": "丑", "戊": "丑", "庚": "丑", "乙": "子", "己": "子",
           "丙": "亥", "丁": "亥", "壬": "卯", "癸": "卯", "辛": "寅"}    # 天魁(阳贵)
TIANYUE = {"甲": "未", "戊": "未", "庚": "未", "乙": "申", "己": "申",
           "丙": "酉", "丁": "酉", "壬": "巳", "癸": "巳", "辛": "午"}    # 天钺(阴贵)
LUCUN = {"甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳", "丁": "午",
         "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}      # 禄存
HORSE = {"寅": "申", "午": "申", "戌": "申", "申": "寅", "子": "寅", "辰": "寅",
         "巳": "亥", "酉": "亥", "丑": "亥", "亥": "巳", "卯": "巳", "未": "巳"}  # 天马(驿马)
HUOXING_START = {"寅": 2, "午": 2, "戌": 2, "申": 3, "子": 3, "辰": 3,
                 "巳": 4, "酉": 4, "丑": 4, "亥": 10, "卯": 10, "未": 10}  # 火星起宫
LINGXING_START = {"寅": 4, "午": 4, "戌": 4, "申": 11, "子": 11, "辰": 11,
                  "巳": 11, "酉": 11, "丑": 11, "亥": 3, "卯": 3, "未": 3}  # 铃星起宫


def compute_ziwei(birth: datetime.datetime, gender: str) -> dict:
    lunar = cnlunar.Lunar(birth)
    year_gz = lunar.year8Char
    year_gan, year_zhi = year_gz[0], year_gz[1]
    month_lunar = lunar.lunarMonth  # 农历月 1..12
    shichen = _hour_to_shichen(birth.hour)  # 1..12
    shichen_name = C.ZHI[shichen - 1] + "时"

    # 命宫地支序 M (1..12)
    M = _norm(3 + month_lunar - shichen)
    M_zhi = C.ZHI[M - 1]

    # 命宫天干（五虎遁 + 顺数到命宫地支）
    start = _wuhu_dun(year_gan)
    mg_gan_idx = (start + (M - 3)) % 10
    mg_gan = C.GAN[mg_gan_idx]
    mg_gz = mg_gan + M_zhi

    # 五行局
    ju_elem = C.nayin(mg_gz)
    N = C.JU.get(ju_elem, 5)

    # 紫微星位置：命宫顺数 (局数-1) 步
    P = _norm(M + N - 1)

    # 紫微系（逆布）
    ziwei_pos = {}
    ziwei_pos["紫微"] = P
    ziwei_pos["天机"] = _norm(P - 1)
    ziwei_pos["太阳"] = _norm(P - 2)
    ziwei_pos["武曲"] = _norm(P - 3)
    ziwei_pos["天同"] = _norm(P - 4)
    ziwei_pos["廉贞"] = _norm(P - 5)
    # 天府系：天府 = 14 - 紫微，顺布八星
    Q = _norm(14 - P)
    ziwei_pos["天府"] = Q
    ziwei_pos["太阴"] = _norm(Q + 1)
    ziwei_pos["贪狼"] = _norm(Q + 2)
    ziwei_pos["巨门"] = _norm(Q + 3)
    ziwei_pos["天相"] = _norm(Q + 4)
    ziwei_pos["天梁"] = _norm(Q + 5)
    ziwei_pos["七杀"] = _norm(Q + 6)
    ziwei_pos["破军"] = _norm(Q + 7)

    # ---- 辅星安布 ----
    fuxing_pos = {}
    fuxing_pos["文昌"] = C.ZHI_INDEX[CHANG[year_gan]] + 1
    fuxing_pos["文曲"] = C.ZHI_INDEX[WEN[year_gan]] + 1
    fuxing_pos["左辅"] = _norm(month_lunar + 4)
    fuxing_pos["右弼"] = _norm(month_lunar + 10)
    fuxing_pos["天魁"] = C.ZHI_INDEX[TIANKUI[year_gan]] + 1
    fuxing_pos["天钺"] = C.ZHI_INDEX[TIANYUE[year_gan]] + 1
    lu_idx = C.ZHI_INDEX[LUCUN[year_gan]] + 1
    fuxing_pos["禄存"] = lu_idx
    fuxing_pos["擎羊"] = _norm(lu_idx + 1)
    fuxing_pos["陀罗"] = _norm(lu_idx - 1)
    fuxing_pos["天马"] = C.ZHI_INDEX[HORSE[year_zhi]] + 1
    fuxing_pos["火星"] = _norm(HUOXING_START[year_zhi] + (shichen - 1))
    fuxing_pos["铃星"] = _norm(LINGXING_START[year_zhi] + (shichen - 1))
    fuxing_pos["地空"] = _norm(12 + (shichen - 1))
    fuxing_pos["地劫"] = _norm(13 - shichen)

    # 12 宫（命宫顺行）
    palaces = []
    for i, pname in enumerate(C.ZIWEI_PALACES):
        palace_zhi_idx = _norm(M + i)  # 该宫地支序
        main = [s for s, pos in ziwei_pos.items() if pos == palace_zhi_idx]
        fu = [s for s, pos in fuxing_pos.items() if pos == palace_zhi_idx]
        palaces.append({
            "palace": pname,
            "zhi": C.ZHI[palace_zhi_idx - 1],
            "stars": main,
            "fu_stars": fu,
        })

    # 生年四化
    lu, quan, ke, ji = C.SIHUA.get(year_gan, ("", "", "", ""))
    sihua = {"禄": lu, "权": quan, "科": ke, "忌": ji}
    sihua_map = {lu: "禄", quan: "权", ke: "科", ji: "忌"}

    # 三方四正（命宫、官禄、财帛、迁移）
    sanfang = [0, 8, 4, 6]
    sanfang_stars = []
    for idx in sanfang:
        sanfang_stars.extend(palaces[idx]["stars"])

    # 命宫主星
    mg_stars = palaces[0]["stars"]
    main_star = mg_stars[0] if mg_stars else "无主星(借对宫)"

    return {
        "mingong_zhi": M_zhi,
        "mingong_gz": mg_gz,
        "shichen": shichen_name,
        "ju": f"{ju_elem}{N}局",
        "ziwei_zhi": C.ZHI[P - 1],
        "stars_pos": {s: C.ZHI[v - 1] for s, v in ziwei_pos.items()},
        "fu_stars_pos": {s: C.ZHI[v - 1] for s, v in fuxing_pos.items()},
        "palaces": palaces,
        "sihua": sihua,
        "sihua_map": sihua_map,
        "sanfang_sizheng": sanfang_stars,
        "main_star": main_star,
        "mingong_stars": mg_stars,
    }
