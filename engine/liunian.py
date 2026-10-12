# -*- coding: utf-8 -*-
"""流年逐岁详批引擎：以命局四柱 + 大运 + 紫微流年宫 + 流年四化为输入，
对当前年起约十年逐年给出十神关系、重点宫位、吉凶评分与简评。

定位：运势推运层（与命局定局、紫微定盘、周易定性、铁板校验共同构成"局-运-验"闭环）。
"""
import datetime
from . import constants as C

# 吉/凶主星与辅星集合（用于流年宫位吉凶加权）
JI_MAIN = {"紫微", "太阳", "武曲", "天同", "天府", "太阴", "天相", "天梁"}
XIONG_MAIN = {"七杀", "破军", "廉贞", "贪狼", "巨门"}
JI_FU = {"文昌", "文曲", "左辅", "右弼", "天魁", "天钺", "禄存"}
XIONG_FU = {"擎羊", "陀罗", "火星", "铃星", "地空", "地劫"}
SIHUA_JI = {"禄", "权", "科"}
SIHUA_XIONG = {"忌"}


def _chong(a, b):
    return (a == "子" and b == "午") or (a == "午" and b == "子") or \
           (a == "丑" and b == "未") or (a == "未" and b == "丑") or \
           (a == "寅" and b == "申") or (a == "申" and b == "寅") or \
           (a == "卯" and b == "酉") or (a == "酉" and b == "卯") or \
           (a == "辰" and b == "戌") or (a == "戌" and b == "辰") or \
           (a == "巳" and b == "亥") or (a == "亥" and b == "巳")


def _he6(a, b):
    return (a == "子" and b == "丑") or (a == "丑" and b == "子") or \
           (a == "寅" and b == "亥") or (a == "亥" and b == "寅") or \
           (a == "卯" and b == "戌") or (a == "戌" and b == "卯") or \
           (a == "辰" and b == "酉") or (a == "酉" and b == "辰") or \
           (a == "巳" and b == "申") or (a == "申" and b == "巳") or \
           (a == "午" and b == "未") or (a == "未" and b == "午")


def _tg_elem(de, g):
    """十神 -> 五行。"""
    if g in ("比肩", "劫财"):
        return de
    if g in ("正印", "偏印"):
        for e in C.ELEMENTS:
            if C.SHENG.get(e) == de:
                return e
        return None
    if g in ("食神", "伤官"):
        return C.SHENG.get(de)
    if g in ("正财", "偏财"):
        return C.KE.get(de)
    if g in ("正官", "七杀"):
        for e in C.ELEMENTS:
            if C.KE.get(e) == de:
                return e
        return None
    return None


def _xi_ji_sets(bazi: dict):
    """根据日主强弱返回(喜神集, 忌神集)。中和时按全局最旺五行判断偏势，给出可调喜用。"""
    strength = bazi["strength"]
    de = bazi["day_element"]
    ec = bazi["element_count"]
    ke_xie_hao = {"正官", "七杀", "食神", "伤官", "正财", "偏财"}   # 克泄耗
    sheng_fu = {"比肩", "劫财", "正印", "偏印"}                       # 生扶
    if strength == "身旺":
        return ke_xie_hao, sheng_fu
    if strength == "身弱":
        return sheng_fu, ke_xie_hao
    # 中和：依全局最旺五行判断偏势
    top = max(ec, key=ec.get)
    sheng_elems = {de}
    for e in C.ELEMENTS:
        if C.SHENG.get(e) == de:
            sheng_elems.add(e)
    if top in sheng_elems:
        return ke_xie_hao, sheng_fu
    return sheng_fu, ke_xie_hao


def _liunian_mechanism(bazi: dict, row: dict) -> str:
    """流年机理：流年干支如何作用于日主/大运/命局。"""
    day_gan = bazi["day_master"]
    day_elem = bazi["day_element"]
    y_gan, y_zhi = row["gz"][0], row["gz"][1]
    rel = row["shi_shen"]
    rel_txt = {
        "正官": "约束规范，主责任与名位", "七杀": "克制挑战，主压力与变动",
        "正印": "生扶荫护，主学习与贵人", "偏印": "偏助暗养，主钻研与孤独",
        "食神": "泄秀生财，主才艺与安逸", "伤官": "发泄外露，主表达与是非",
        "正财": "我克之财，主稳定收入", "偏财": "流动之财，主机遇与风险",
        "比肩": "同辈分力，主协作与竞争", "劫财": "分夺之象，主破耗与争夺",
    }.get(rel, "中性平气")
    s = ("行「%s」大运（%s）" % (row["dayun_gz"], row["dayun_shishen"])) if row["dayun_gz"] != "—" else "尚未起运（依本命局）"
    mech = "流年「%s」，天干「%s」为日主「%s（%s）」之「%s」——%s；%s。" % (row["gz"], y_gan, day_gan, day_elem, rel, rel_txt, s)
    day_zhi = bazi["four_pillars"]["day"]["gz"][1]
    month_zhi = bazi["four_pillars"]["month"]["gz"][1]
    if _chong(y_zhi, day_zhi):
        note = "流年支「%s」冲日支「%s」，年内个人/婚姻/健康层面易有波动，宜稳" % (y_zhi, day_zhi)
    elif _chong(y_zhi, month_zhi):
        note = "流年支「%s」冲月令「%s」，环境与事业平台易生变动" % (y_zhi, month_zhi)
    elif _he6(y_zhi, day_zhi):
        note = "流年支「%s」合日支「%s」，自身与人际气场趋于和合" % (y_zhi, day_zhi)
    else:
        note = "流年支「%s」与命局无强冲合，顺势而为即可" % y_zhi
    return mech + note + "。"


def _liunian_key_months(bazi: dict, row: dict) -> dict:
    """流年关键月份：流月地支冲/合 流年支、日支、大运支。"""
    y_zhi = row["gz"][1]
    day_zhi = bazi["four_pillars"]["day"]["gz"][1]
    dy_zhi = row["dayun_gz"][1] if row["dayun_gz"] != "—" else None
    start_gan_idx = {"甲": 2, "己": 2, "乙": 4, "庚": 4, "丙": 6, "辛": 6, "丁": 8, "壬": 8, "戊": 0, "癸": 0}[row["gz"][0]]
    watch, favor = [], []
    for m in range(1, 13):
        mz = C.ZHI[(2 + (m - 1)) % 12]
        if _chong(mz, y_zhi) or (dy_zhi and _chong(mz, dy_zhi)) or _chong(mz, day_zhi):
            watch.append("%d月（流月「%s」冲动）" % (m, mz))
        elif _he6(mz, y_zhi):
            favor.append("%d月（流月「%s」合流年，气场和合）" % (m, mz))
    return {"watch": watch[:3], "favor": favor[:3]}


def _score_to_grade(score: float):
    if score >= 1.2:
        return "吉", "hi", "流年得力，是落地关键决策的窗口，但顺境别放松风控"
    if score >= 0.3:
        return "平偏吉", "hi", "稳中有进，顺势而为，重大变动先备退路"
    if score > -0.3:
        return "平", "mid", "平顺守常，年内不主动制造大变动"
    if score > -1.2:
        return "平偏凶", "lo", "多有牵绊，以避坑为主：不投资、不担保、合同反复审"
    return "凶", "lo", "阻力大，重大决策暂缓，先把风险敞口降到最低"


def _liunian_cat(bazi, shi_shen, dy_shishen, fp_name, fp_stars, fp_fu,
                 has_lu, has_ji, score, xi_set, ji_set, weak_elem, organ) -> dict:
    """流年逐岁「指导性意见」：依据十神喜忌 + 大运 + 紫微流年命宫 + 四化 + 评分，分五维给出直白可避坑的建议。"""
    cat = {}
    weak = bazi["strength"] == "身弱"
    # 事业 —— 直给：这一年具体别做什么、该把劲往哪使
    if shi_shen in ("正官", "七杀"):
        cat["事业"] = ("官杀之年，责任与考核明显加重。别冲动裸辞、别轻易替人担保或签连带责任；重要任务先写清权责边界再接。可借平台稳步上位，但不宜强出头揽超出自己能力的活。"
                       if weak
                       else "官杀之年利掌权、争取管理岗或专业突破。但官杀也主压力与是非：签约、人事变动务必留书面凭证，避免口头承诺；与上级/规则有冲突时先忍一步。")
    elif shi_shen in ("正印", "偏印"):
        cat["事业"] = "印星之年利学习、考证、沉淀专业。把时间花在提升硬本事上最划算；不宜大举投资或频繁跳槽，慢即是快。"
    elif shi_shen in ("食神", "伤官"):
        cat["事业"] = ("伤官之年利才艺表达、创新，但也最易惹口舌是非。发文、表态、签约前多想一步；尤其防与上级/客户/规则正面冲撞，重大人事变动缓一缓。"
                       if shi_shen == "伤官"
                       else "食神之年利才艺、表达与轻松输出。可大胆展示，但忌眼高手低、忌得意忘形祸从口出；做事留底。")
    elif shi_shen in ("正财", "偏财"):
        cat["事业"] = "财星之年务实为要，利业务落地与稳定收入。偏财可小试，忌贪多冒进、忌为业绩踩灰色线。"
    elif shi_shen in ("比肩", "劫财"):
        cat["事业"] = "比劫之年宜合作借力，但比劫也主争夺：防同侪抢功、合伙利益不清，事前把分账与权责白纸黑字定好。"
    else:
        cat["事业"] = "流年平气，事业平稳。把分内事做扎实、不躁不怠，别主动挑起变动。"
    # 财运 —— 直给：守还是攻，具体红线在哪
    if shi_shen in ("正财", "偏财") and shi_shen in xi_set:
        cat["财运"] = "财星为喜，进财机会较顺。但顺境最易放松风控：可稳健理财、留足应急金，偏财只动用闲钱，不追加杠杆。"
    elif shi_shen in ("正财", "偏财"):
        cat["财运"] = "财星现而于你非最利，财来财去之象。这一年重点是『守』：不新增贷款、不替人担保、大宗消费与投资延后，先保住现金流。"
    elif score >= 0.3:
        cat["财运"] = "流年整体向上，财运平顺。量入为出、可小布局，但仍不留大额应收账款、不替人背债。"
    elif score <= -0.3:
        cat["财运"] = "流年承压，财运宜守不宜攻：暂停新增借贷、不留大额应收、投资只做闲钱甚至不投，先把风险敞口降到最低。"
    else:
        cat["财运"] = "财运中性，宜稳守、不投机、不替人担保背债。"
    # 人际 —— 直给：哪类人/哪类事要设防
    if has_ji:
        cat["人际"] = f"流年忌落「{fp_name}」宫，该领域易有阻滞与反复——借钱要立字据、合伙先定分账、别替人做连带担保、防因人情破财生怨。"
    elif has_lu:
        cat["人际"] = f"流年禄落「{fp_name}」宫，相关事务易得助力，可积极推进；但仍要明算账，别因顺利就放松契约。"
    elif shi_shen in ("比肩", "劫财", "伤官"):
        cat["人际"] = "比劫/伤官之年人际活跃却易生竞争与口舌：择善而交、少争闲气，重要约定落纸面，别为面子逞强出资。"
    else:
        cat["人际"] = "人际平顺，维护旧缘即可，别为面子替人出头担责。"
    # 健康 —— 直给：哪类事要避、该查什么
    cat["健康"] = (f"命局五行偏弱在「{weak_elem}（{organ}）」。七杀/伤官加临之年，防过劳与突发小伤：避免熬夜透支、应酬无度、极限运动；安排一次针对「{organ}」的体检。"
                   if shi_shen in ("七杀", "伤官")
                   else f"命局五行偏弱在「{weak_elem}（{organ}）」。今年保持起居有常，重点保养「{organ}」，别拿身体好赌、别长期透支。")
    # 时机 —— 直给：这一年能不能动、动什么
    if score >= 1.2:
        cat["时机"] = "全年动能强，是落地关键决策的窗口：可推进酝酿已久的事，但别在顺境里放松风控、别盲目加注。"
    elif score >= 0.3:
        cat["时机"] = "稳中有进，顺势而为；换城市/买房/创业等重大变动可择机，但务必先做好预案与退路。"
    elif score > -0.3:
        cat["时机"] = "平顺守常，年内不主动制造大变动，先把现有摊子稳住、把债务和承诺理清。"
    elif score > -1.2:
        cat["时机"] = "多有牵绊，这一年以『避坑』为主：不辞职、不盲目投资、不替人担保、重要合同反复审、重大决策暂缓。"
    else:
        cat["时机"] = "阻力较大，宜低调收敛：婚/迁/投/创业等重大决策尽量缓一缓，先把风险敞口降到最低。"
    return cat


def _active_dayun(bazi: dict, age: int):
    """返回该虚岁对应的大运 gz，未起运返回 None（依命局）。"""
    for d in bazi["dayun"]:
        if d["start_age"] <= age < d["end_age"]:
            return d["gz"], d["step"]
    # 超过已排大运或未满起运
    if bazi["dayun"] and age < bazi["dayun"][0]["start_age"]:
        return None, 0
    if bazi["dayun"]:
        last = bazi["dayun"][-1]
        return last["gz"], last["step"]
    return None, 0


def compute_liunian(bazi: dict, ziwei: dict, birth: datetime.datetime,
                    span_back: int = 2, span_fwd: int = 8) -> dict:
    """返回流年详批列表。birth 用于算虚岁。"""
    day_gan = bazi["day_master"]
    xi_set, ji_set = _xi_ji_sets(bazi)
    now_year = datetime.date.today().year
    birth_year = birth.year
    palaces = ziwei["palaces"]
    zhi_palace_idx = {p["zhi"]: i for i, p in enumerate(palaces)}

    # 命局五行最弱者（用于健康提示）
    ec = bazi["element_count"]
    weak_elem = min(ec, key=ec.get)
    organ = {"木": "肝胆/筋骨", "火": "心脑/血脉", "土": "脾胃",
             "金": "肺/呼吸道", "水": "肾/膀胱/泌尿"}[weak_elem]

    rows = []
    for y in range(now_year - span_back, now_year + span_fwd + 1):
        gz = C.GZ60[(y - 4) % 60]
        y_gan, y_zhi = gz[0], gz[1]
        nayin = C.nayin_name(gz)
        shi_shen = C.ten_god(day_gan, y_gan)
        age = y - birth_year + 1  # 虚岁

        # 大运
        dy_gz, dy_step = _active_dayun(bazi, age)
        dy_shishen = C.ten_god(day_gan, dy_gz[0]) if dy_gz else "（未起运）"

        # 紫微流年命宫（地支对齐）
        fp_idx = zhi_palace_idx.get(y_zhi)
        fp = palaces[fp_idx] if fp_idx is not None else None
        fp_name = fp["palace"] if fp else "—"
        fp_stars = fp["stars"] if fp else []
        fp_fu = fp["fu_stars"] if fp else []

        # 流年四化
        lu, quan, ke, ji = C.SIHUA.get(y_gan, ("", "", "", ""))
        sihua = {"禄": lu, "权": quan, "科": ke, "忌": ji}
        sihua_hit = []
        for tag, star in sihua.items():
            if star and fp and star in fp_stars:
                sihua_hit.append(f"{tag}{star}")

        # ---- 评分 ----
        score = 0.0
        if xi_set or ji_set:
            if shi_shen in xi_set:
                score += 1.0
            elif shi_shen in ji_set:
                score -= 1.0
            if dy_gz and dy_shishen in xi_set:
                score += 1.0
            elif dy_gz and dy_shishen in ji_set:
                score -= 1.0
        for s in fp_stars:
            if s in JI_MAIN:
                score += 0.3
            elif s in XIONG_MAIN:
                score -= 0.3
        for s in fp_fu:
            if s in JI_FU:
                score += 0.3
            elif s in XIONG_FU:
                score -= 0.3
        for tag, star in sihua.items():
            if star and fp and star in fp_stars:
                if tag in SIHUA_JI:
                    score += 0.4
                else:
                    score -= 0.6
        grade, cls, advice = _score_to_grade(score)
        has_lu = any(s[0] == "禄" for s in sihua_hit)
        has_ji = any(s[0] == "忌" for s in sihua_hit)
        cat = _liunian_cat(bazi, shi_shen, dy_shishen, fp_name, fp_stars, fp_fu,
                           has_lu, has_ji, score, xi_set, ji_set, weak_elem, organ)
        long_parts = [advice]
        long_parts.append(f"流年重点在「{fp_name}」宫"
                          + (f"，主星{''.join(fp_stars)}；" if fp_stars else "（空宫借对宫）；"))
        if has_lu or has_ji:
            long_parts.append("四化" + ("禄" if has_lu else "") + ("忌" if has_ji else "") + "落此，"
                              + ("宜顺势借力、主动作为" if has_lu else "宜谨慎规划、明算账防反复") + "。")
        else:
            long_parts.append("流年四化不落本宫，按十神与大运顺势而为即可。")
        advice_long = "".join(long_parts)

        # ---- 简评 ----
        parts = []
        if xi_set or ji_set:
            sk = "喜" if shi_shen in xi_set else ("忌" if shi_shen in ji_set else "中性")
            parts.append(f"流年十神{shi_shen}（{sk}）")
        else:
            parts.append(f"流年十神{shi_shen}")
        if dy_gz:
            parts.append(f"行{dy_gz}大运（{dy_shishen}）")
        else:
            parts.append("未起运（依命局）")
        parts.append(f"重点在{fp_name}")
        if sihua_hit:
            parts.append(f"流年四化{'、'.join(sihua_hit)}落本宫")
        summary = "；".join(parts) + f"。{advice}。"

        # 流年机理 + 关键月份（深度字段，与前端一致）
        mech = _liunian_mechanism(bazi, {"gz": gz, "shi_shen": shi_shen,
                                         "dayun_gz": dy_gz or "—", "dayun_shishen": dy_shishen})
        km = _liunian_key_months(bazi, {"gz": gz, "dayun_gz": dy_gz})

        rows.append({
            "year": y, "gz": gz, "nayin": nayin, "age": age,
            "shi_shen": shi_shen, "dayun_gz": dy_gz or "—", "dayun_step": dy_step,
            "dayun_shishen": dy_shishen,
            "flow_palace": fp_name, "flow_palace_zhi": y_zhi,
            "flow_stars": fp_stars, "flow_fu_stars": fp_fu,
            "sihua": {k: v for k, v in sihua.items() if v},
            "sihua_hit": sihua_hit,
            "score": round(score, 2), "grade": grade, "cls": cls,
            "advice": advice, "advice_long": advice_long, "advice_cat": cat, "summary": summary,
            "mechanism": mech, "key_months": km, "is_current": y == now_year,
        })

    # 近三年趋势短语（供交叉验证/结论引用）
    trend = [r for r in rows if r["is_current"]][0]["summary"] if rows else ""
    return {"rows": rows, "trend": trend, "now_year": now_year}
