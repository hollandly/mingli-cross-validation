# -*- coding: utf-8 -*-
"""铁板神数验证层（简化示范版）。
铁板神数以「干支化数 -> 查秘传条文」考六亲、妻儿，核心作用是「考时」：
用可被事实核验的具体条文（兄弟数、父母、配偶、子女）来反推出生时辰是否准确，
从而成为整套系统的精确校验层。本节实现「起数 + 示范条文库」，用于交叉验证。
注：完整铁板神数需秘传条文本与考时口诀，此处为可计算的简化示意，重在方法学。"""
from . import constants as C


def _gan_num(g):  # 1..10
    return C.GAN_INDEX[g] + 1


def _zhi_num(z):  # 1..12
    return C.ZHI_INDEX[z] + 1


def _to_tieban_number(n: int) -> str:
    """把一个整数压成铁板风格的三位「数」（如 312）。"""
    s = str(n % 1000)
    return s.zfill(3)


def compute_tieban(bazi: dict, ziwei: dict) -> dict:
    fp = bazi["four_pillars"]
    day_gz = fp["day"]["gz"]
    hour_gz = fp["hour"]["gz"]
    year_gz = fp["year"]["gz"]
    # 起数：日干支 + 时干支
    base = (_gan_num(day_gz[0]) * 10 + _zhi_num(day_gz[1])) + \
           (_gan_num(hour_gz[0]) * 10 + _zhi_num(hour_gz[1]))

    tiaowen = []

    # 兄弟数（考时关键项）
    bi_jie = sum(1 for ss in bazi["ten_gods"] if ss in ("比肩", "劫财"))
    bro_count = max(0, bi_jie - 1 + (1 if bazi["day_element"] in ("木", "水") else 0))
    bro_num = _to_tieban_number(base + bro_count * 7 + 11)
    tiaowen.append({
        "number": bro_num, "dimension": "兄弟",
        "text": f"兄弟（含同胞）约 {bro_count} 位；铁板数 {bro_num} 主「手足之数」。",
        "verify": "可凭实际同胞数反推时辰——若不符，宜复核出生时辰。",
    })

    # 父母（年柱纳音 + 紫微父母宫）
    parent_elem = C.nayin(year_gz)
    parent_palace = next((p for p in ziwei["palaces"] if p["palace"] == "父母"), None)
    parent_star = "、".join(parent_palace["stars"]) if parent_palace else "无主星"
    par_num = _to_tieban_number(base + 23)
    tiaowen.append({
        "number": par_num, "dimension": "父母",
        "text": f"父母宫见 {parent_star}；年柱纳音属 {parent_elem}，主双亲缘分与帮扶之象。",
        "verify": "可凭父母健康状况/生肖/缘分深浅印证，作为考时佐证。",
    })

    # 配偶（紫微夫妻宫 + 日支）
    spouse_palace = next((p for p in ziwei["palaces"] if p["palace"] == "夫妻"), None)
    spouse_star = "、".join(spouse_palace["stars"]) if spouse_palace else "无主星"
    sp_num = _to_tieban_number(base + 41)
    tiaowen.append({
        "number": sp_num, "dimension": "配偶",
        "text": f"夫妻宫见 {spouse_star}；日支为 {day_gz[1]}，主配偶性情与婚姻互动之象。",
        "verify": "可凭配偶性格/相遇方式印证，辅助判断时辰准确度。",
    })

    # 子女（紫微子女宫 + 时柱）
    child_palace = next((p for p in ziwei["palaces"] if p["palace"] == "子女"), None)
    child_star = "、".join(child_palace["stars"]) if child_palace else "无主星"
    ch_num = _to_tieban_number(base + 59)
    tiaowen.append({
        "number": ch_num, "dimension": "子女",
        "text": f"子女宫见 {child_star}；时柱 {hour_gz}，主子女缘分与晚景之象。",
        "verify": "可凭子女缘分/数量印证，为考时之尾验。",
    })

    return {
        "base_number": _to_tieban_number(base),
        "tiaowen": tiaowen,
    }
