# -*- coding: utf-8 -*-
"""交叉验证与综合结论引擎。
把四套体系的信号映射到同一组人生维度，计算一致性，对分歧维度触发『考时复核』，
最终给出分级结论（高一致 / 中一致 / 分歧需复核）。"""
from . import constants as C
from .liunian import _xi_ji_sets, _tg_elem, _chong

DIMS = ["性格", "事业", "财运", "婚姻", "家庭(六亲)", "健康", "时机运势"]

# 紫微主星性质（简化）
STAR_NATURE = {
    "紫微": "尊贵领导，好胜有主见", "天机": "机敏善谋，喜变动", "太阳": "光明磊落，重名誉",
    "武曲": "刚毅果决，主财帛奋斗", "天同": "温和知足，尚安享", "廉贞": "敏慧重情，带桃花波折",
    "天府": "稳重保守，库藏充盈", "太阴": "阴柔内秀，重情感细节", "贪狼": "多才欲强，善交际偏桃花",
    "巨门": "口才明辨，易生口舌", "天相": "端庄辅佐，衣食安稳", "天梁": "慈荫化解，遇难呈祥",
    "七杀": "刚烈开创，孤克进取", "破军": "破旧立新，多波折变动",
}
JI_STARS = {"紫微", "太阳", "武曲", "天同", "天府", "太阴", "天相", "天梁"}
# 辅星性质（吉/凶用于交叉验证微调）
FU_STAR_NATURE = {
    "文昌": "文采才学，利考试文书", "文曲": "才艺口才，利文艺",
    "左辅": "帮扶助力，人缘贵气", "右弼": "辅佐协力，团队得利",
    "天魁": "阳贵，逢凶化吉得长辈助", "天钺": "阴贵，暗处女性贵人",
    "禄存": "财库稳固，聚财不露", "天马": "奔波变动，利远行迁移",
    "擎羊": "刚烈波折，主竞争伤灾", "陀罗": "纠缠反复，做事拖延",
    "火星": "火急爆发，成败迅速", "铃星": "暗火闷进，隐患慢性",
    "地空": "虚耗落空，宜务实", "地劫": "劫夺损耗，防破财",
}
FU_GOOD = {"文昌", "文曲", "左辅", "右弼", "天魁", "天钺", "禄存", "天马"}
FU_BAD = {"擎羊", "陀罗", "火星", "铃星", "地空", "地劫"}


def _clamp(x):
    return max(1, min(5, x))


def bazi_signals(bazi: dict) -> dict:
    """八字 -> 各维度信号 {dim: (text, level)}。level 1..5。"""
    dm = bazi["day_master"]
    elem = bazi["day_element"]
    tg = bazi["ten_gods"]
    four = bazi["four_pillars"]
    strength = bazi["strength"]
    s_level = {"身旺": 4, "中和": 3, "身弱": 2}[strength]

    # 性格
    char_parts = [f"日主{elem}（{dm}）{strength}"]
    key_gods = [g for g in set(tg) if g in ("伤官", "食神", "正印", "偏印", "七杀", "比肩", "劫财")]
    char_parts.append("，十神见" + "、".join(key_gods) if key_gods else "")
    char_text = "性格：" + "".join(char_parts)
    char_level = _clamp(s_level + (1 if "伤官" in tg or "食神" in tg else 0)
                        - (1 if "正印" in tg or "偏印" in tg else 0))

    # 事业（官杀为事业星，看日主能否担）
    guan = sum(1 for g in tg if g in ("正官", "七杀"))
    if guan and strength != "身弱":
        career = ("事业星（官杀）得力，宜公职/管理/专业赛道", 4)
    elif guan and strength == "身弱":
        career = ("事业星现但身弱，压力大、宜借平台与人扶", 2)
    else:
        career = ("无显官杀，宜自由业/技术/自我经营", 3)

    # 财运（财星为用，看日主能否担）
    cai = sum(1 for g in tg if g in ("正财", "偏财"))
    if cai and strength != "身弱":
        wealth = ("财星得用，财源可聚，宜理财生财", 4)
    elif cai and strength == "身弱":
        wealth = ("财星现而身弱，财来财去，宜稳守", 2)
    else:
        wealth = ("财星不显，财凭技艺/因缘，宜节流", 3)

    # 婚姻（男看财星为妻星，女看官星为夫星；兼看日支夫妻宫）
    spouse_star = "财" if bazi.get("gender", "男") == "男" else "官"
    if cai and strength != "身弱":
        marriage = ("夫妻宫与配偶星相称，婚姻较稳，宜择性格互补者", 4)
    elif cai:
        marriage = ("配偶星现而身弱，婚缘有波，宜晚婚/互谅", 2)
    else:
        marriage = ("配偶星不显，婚姻平淡或晚成，重精神契合", 3)

    # 家庭（父母-年柱印星；兄弟-比劫；子女-食伤/时柱）
    bi_jie = sum(1 for g in tg if g in ("比肩", "劫财"))
    yin = sum(1 for g in tg if g in ("正印", "偏印"))
    shi_shang = sum(1 for g in tg if g in ("食神", "伤官"))
    fam_text = (f"父母缘（印星{'有' if yin else '弱'}）、手足（比劫{bi_jie}）、"
                f"子女缘（食伤{'有' if shi_shang else '弱'}）")
    fam_level = _clamp(3 + (1 if yin else 0) + (1 if bi_jie >= 2 else 0)
                       - (1 if not shi_shang else 0))

    # 健康（五行偏枯）
    ec = bazi["element_count"]
    weak_elem = min(ec, key=ec.get)
    if ec[weak_elem] == 0:
        organ = {"木": "肝/筋骨", "火": "心/血脉", "土": "脾胃", "金": "肺/呼吸道", "水": "肾/泌尿"}[weak_elem]
        health = (f"五行缺{weak_elem}（{organ}系统偏弱），宜早养", 2)
    else:
        health = ("五行尚匀，先天体质平顺，仍须起居有常", 4)

    # 时机（当前大运/流年与日主关系）
    now = bazi["liu_year"]
    cur = next((y for y in now if y["year"] == __import__("datetime").date.today().year), now[2])
    ss = cur["shi_shen"]
    if ss in ("正印", "偏印", "比肩", "劫财", "正财", "偏财"):
        timing = (f"流年 {cur['year']} {cur['gz']}（{ss}），利守成积累", 4)
    elif ss in ("七杀", "伤官"):
        timing = (f"流年 {cur['year']} {cur['gz']}（{ss}），变动挑战并存，宜谨慎", 2)
    else:
        timing = (f"流年 {cur['year']} {cur['gz']}（{ss}），平运渐进", 3)

    return {
        "性格": (char_text, char_level),
        "事业": career, "财运": wealth, "婚姻": marriage,
        "家庭(六亲)": (fam_text, fam_level), "健康": health, "时机运势": timing,
    }


def ziwei_signals(ziwei: dict) -> dict:
    res = {}
    # 性格：命宫主星 + 辅星
    mg = ziwei["mingong_stars"]
    mg_fu = ziwei["palaces"][0].get("fu_stars", [])
    all_mg = mg + mg_fu
    if all_mg:
        nat = "；".join(STAR_NATURE.get(s, FU_STAR_NATURE.get(s, s)) for s in all_mg)
        lvl = 4 if any(s in JI_STARS for s in mg) else 3
        if any(s in FU_BAD for s in mg_fu):
            lvl = _clamp(lvl - 0.3)
        fu_txt = (" + " + "、".join(mg_fu)) if mg_fu else ""
        res["性格"] = (f"命宫 {(mg[0] if mg else '借对宫')}{fu_txt}：{nat}", lvl)
    else:
        res["性格"] = ("命宫无主星（借对宫），性情随环境而变", 3)

    # 各宫主星 + 辅星 -> 维度
    palace_map = {
        "官禄": "事业", "财帛": "财运", "夫妻": "婚姻",
        "父母": "家庭(六亲)", "兄弟": "家庭(六亲)", "子女": "家庭(六亲)",
        "疾厄": "健康", "迁移": "时机运势",
    }
    for palace in ziwei["palaces"]:
        dim = palace_map.get(palace["palace"])
        if not dim:
            continue
        stars = palace["stars"] + palace.get("fu_stars", [])
        if stars:
            nat = "；".join(STAR_NATURE.get(s, FU_STAR_NATURE.get(s, s)) for s in stars)
            lvl = 4 if any(s in JI_STARS for s in palace["stars"]) else 3
        else:
            nat = "空宫（借对宫星情）"
            lvl = 3
        # 主星四化修正
        for s in palace["stars"]:
            if ziwei["sihua_map"].get(s) in ("禄", "权", "科"):
                lvl = _clamp(lvl + 0.5)
            elif ziwei["sihua_map"].get(s) == "忌":
                lvl = _clamp(lvl - 1)
        # 辅星修正
        for s in palace.get("fu_stars", []):
            if s in FU_GOOD:
                lvl = _clamp(lvl + 0.3)
            elif s in FU_BAD:
                lvl = _clamp(lvl - 0.3)
        text = f"{palace['palace']}宫：{nat}"
        if dim in res:
            res[dim] = (res[dim][0] + "；" + text, _clamp((res[dim][1] + lvl) / 2))
        else:
            res[dim] = (text, lvl)
    if "时机运势" not in res:
        res["时机运势"] = ("三方四正：" + "、".join(ziwei["sanfang_sizheng"]) +
                          f"；四化禄{ziwei['sihua']['禄']}权{ziwei['sihua']['权']}"
                          f"科{ziwei['sihua']['科']}忌{ziwei['sihua']['忌']}", 3)
    return res


def yijing_signals(yijing: dict, bazi: dict) -> dict:
    elem = bazi["day_element"]
    ge = yijing["gua_elem"]
    if C.SHENG.get(ge) == elem or ge == elem:
        polar = 4  # 卦助日主
    elif C.KE.get(ge) == elem or C.KE.get(elem) == ge:
        polar = 2  # 卦克/被克日主
    else:
        polar = 3
    char = (f"本卦 {yijing['ben_gua']}（{yijing['gua_nature']}），主性格取向："
            f"{yijing['meaning']}", _clamp(polar))
    timing = (f"卦象五行属 {ge}，对日主{elem}为"
              f"{'生扶' if polar == 4 else ('克泄' if polar == 2 else '中和')}之象；"
              f"变卦 {yijing['bian_gua']} 示动爻{yijing['dong_yao']}之转机", polar)
    return {"性格": char, "时机运势": timing}


def tieban_signals(tieban: dict, bazi: dict) -> dict:
    res = {}
    votes = {x["dimension"]: x for x in tieban["tiaowen"]}
    dim_map = {"兄弟": "家庭(六亲)", "父母": "家庭(六亲)", "配偶": "婚姻", "子女": "家庭(六亲)"}
    for d, t in votes.items():
        dim = dim_map.get(d, "家庭(六亲)")
        text = f"铁板数 {t['number']}（{d}）：{t['text']}"
        if dim in res:
            res[dim] = (res[dim][0] + "；" + text, 3)
        else:
            res[dim] = (text, 3)
    return res, votes


def _life_guidance(matrix, bazi, xi_set, ji_set, cons_counts, review_flags) -> dict:
    """人生指导总览：综合四体系交叉验证结果，产出分维度建议 + 优势/短板 + 大运阶段策略 + 综合总览。"""
    day_gan = bazi["day_master"]
    strengths, cautions, dim_tips = [], [], {}
    DIM_ADVICE = {
        "性格": lambda d: ("你自我认知清晰、气质鲜明。把长处用在建立个人口碑与专业标签上，少在不相干的人面前过度暴露底牌。"
                           if d == "吉/强" else "你性情中和、可塑性强。别急着给自己贴固定标签，多在不同环境里试，靠反馈校准自我。"
                           if d == "平" else "你内在有矛盾张力。遇事多自省，借可信赖的外界反馈校准定位，别在情绪头上下决定。"),
        "事业": lambda d: ("事业动能强。主动争取、承担更大责任、打磨专业壁垒；但顺境里也别放松风控、别盲目加注。"
                           if d == "吉/强" else "稳中有进。先把手艺做深、把人脉做厚，不急于跳槽或跃迁，等窗口。"
                           if d == "平" else "事业承压期。借平台与团队、别单兵冒进，也别频繁跳槽——越动越乱，先稳住再图。"),
        "财运": lambda d: ("财源顺。稳健理财、留应急金，偏财只动闲钱，不追加杠杆。"
                           if d == "吉/强" else "守成为主。控支出、防借贷与冲动消费，别替人担保背债。"
                           if d == "平" else "财运偏弱。留足应急、降杠杆、以技能变现为本，投资能不碰就不碰。"),
        "婚姻": lambda d: ("感情配对较顺。在互补中经营、择时而定，别因顺利就忽略沟通。"
                           if d == "吉/强" else "重精神契合、多沟通，晚婚或成熟后更稳，别被催婚推着走。"
                           if d == "平" else "婚缘有波折之象。互相体谅、重大决定缓步，防外部干扰与旧账翻腾，婚前把财产与期待谈清。"),
        "家庭(六亲)": lambda d: ("六亲缘分与家庭支持较足。珍惜亲情、反哺长辈，也别因顾家耽误自身成长。"
                                 if d == "吉/强" else "维系纽带、尽责尽份，平淡中见真情，别让忙成为疏远的借口。"
                                 if d == "平" else "亲缘或有疏离/牵挂。主动联络、尽早在关键处尽心力，别等事了才后悔。"),
        "健康": lambda d: ("先天体质尚可。保持起居有常、定期体检即可，别仗着底子好透支。"
                           if d == "吉/强" else "规律作息、适度锻炼，盯紧薄弱环节，小毛病别拖。"
                           if d == "平" else "健康提示偏多。定期体检、早养薄弱环节、绝不透支，把身体当资产管。"),
        "时机运势": lambda d: ("近年窗口偏吉。把握节奏主动作为，但也别在顺境里放松风控。"
                               if d == "吉/强" else "顺势而为、择机而动，不强行，重大变动先备预案。"
                               if d == "平" else "时机偏守。蓄势待时、以静制动，重大决策暂缓，先把风险敞口降下来。"),
    }
    for m in matrix:
        d = "吉/强" if m["mean_level"] >= 4 else ("平" if m["mean_level"] >= 3 else "弱/宜守")
        dim_tips[m["dimension"]] = DIM_ADVICE[m["dimension"]](d) if m["dimension"] in DIM_ADVICE else "参考综合评级顺势而为。"
        if m["consistency"] == "高一致" and m["mean_level"] >= 4:
            strengths.append(f"{m['dimension']}：四体系高度一致且评级强，是你可以重点发力、放心投入的人生领域")
        if m["consistency"] == "分歧" or m["mean_level"] < 3:
            cautions.append(f"{m['dimension']}：结论分歧或评级偏弱，是容易踩坑的方面——重大决策放慢、以现实反馈校准，别凭感觉冲")
    if not strengths:
        strengths.append("四体系整体以「平」为主，没有特别突出的长板，宜在均衡中稳步积累，不必急于求成")
    if not cautions:
        cautions.append("暂无明显短板预警，但「平」也意味着没有躺赢的运气，保持节奏、居安思危即可")

    phase = []
    if bazi["dayun"]:
        sa0 = bazi["dayun"][0]["start_age"]
        if sa0 > 0:
            phase.append({"range": f"0–{int(round(sa0)) - 1}岁（起运前）",
                          "gz": "命局",
                          "tip": "未起运，依本命局之势：以学业、心性养成与家庭支持为主，别急着闯荡或大额押注"})
        for d in bazi["dayun"]:
            god = C.ten_god(day_gan, d["gz"][0])
            fav = god in xi_set
            bad = god in ji_set
            tip = ("此运干支为喜，十年动能偏顺——宜把握机会、主动进取、扩大成果；但顺境也别放松风控、别盲目加注。"
                   if fav else "此运干支为忌，是守成蓄势的十年——控风险、重大决策三思、不替人担保、不盲目加杠杆，以稳换空间。"
                   if bad else "此运平气，稳扎稳打、积累实力与资源，不躁不怠，别主动制造大变动。")
            phase.append({"range": f"{int(round(d['start_age']))}–{int(round(d['end_age'])) - 1}岁", "gz": d["gz"], "tip": tip})

    overall = (f"综合四体系交叉验证：高一致 {cons_counts['高一致']} 项、中一致 {cons_counts['中一致']} 项、"
               f"分歧 {cons_counts['分歧']} 项。可以重点发力的领域：「{'；'.join(strengths)}」；"
               f"需要设防、别踩坑的方面：「{'；'.join(cautions)}」。"
               f"人生策略上，你身{bazi['strength']}，用神宜取"
               f"{'印比（学习、合作、稳健托底）' if bazi['strength'] == '身弱' else '食伤财官（表达、务实、进取兑现）'}"
               f"——喜运的十年主动出击、放大成果，忌运的十年收着点、先把风险敞口降下来。")
    if review_flags:
        overall += " 另：" + "".join(review_flags)
    return {"overall": overall, "strengths": strengths, "cautions": cautions,
            "dimension_tips": dim_tips, "by_phase": phase}


# ============ 命格综合论断 · 用神人生映射 · 大运阶段详批（与前端 engines.js 对齐） ============
def _mingge_zonglun(bazi: dict, yijing: dict, cv: dict) -> dict:
    """命格综合论断：格局判定 + 喜用神推导 + 四体系交叉判读 + 本命卦互参。"""
    day_gan = bazi["day_master"]
    dm = bazi["day_element"]
    strength = bazi["strength"]
    xi, ji = _xi_ji_sets(bazi)
    ec = bazi["element_count"]
    top, bot, tm, bm = C.ELEMENTS[0], C.ELEMENTS[0], -1, 99
    for e in C.ELEMENTS:
        if ec[e] > tm:
            tm, top = ec[e], e
        if ec[e] < bm:
            bm, bot = ec[e], e
    tg = bazi["ten_gods"]
    if strength == "身旺":
        if "正官" in tg or "七杀" in tg:
            pattern = "身旺官杀为用，主有担当、宜在规则与责任中建功"
        elif "食神" in tg or "伤官" in tg:
            pattern = "身旺食伤泄秀，主才思外显、宜以才艺表达立身"
        elif "正财" in tg or "偏财" in tg:
            pattern = "身旺财星得根，主务实进取、宜以经营生财"
        else:
            pattern = "身旺比劫林立，主自力自强、宜借协作与竞争成长"
    elif strength == "身弱":
        if "正印" in tg or "偏印" in tg:
            pattern = "身弱印星为根，主得荫护、宜以学习与沉淀立基"
        elif "比肩" in tg or "劫财" in tg:
            pattern = "身弱比劫帮扶，主得同辈助力、宜合而不宜独"
        else:
            pattern = "身弱官杀/财星偏重，主外压内耗、宜借平台与人托底、勿单兵冒进"
    else:
        pattern = "日主中和，刚柔可调，宜因时顺势、不偏不倚"
    xi_text = "、".join(xi) if xi else "（需结合全局细参）"
    ji_text = "、".join(ji) if ji else "（需结合全局细参）"
    xi_is_shengfu = ("正印" in xi or "偏印" in xi or "比肩" in xi or "劫财" in xi)
    xi_phrase = "生扶我身、稳托根基" if xi_is_shengfu else "克泄耗我、引动成果"
    ji_phrase = "再耗再克则根基更虚" if xi_is_shengfu else "再助再旺则物极必反"
    hi = cv["cons_counts"]["高一致"]
    div = cv["cons_counts"]["分歧"]
    if div == 0 and hi >= 4:
        xjudge = "四体系高度一致，结论可信度较高，可在高一致维度放心发力；"
    elif div == 0:
        xjudge = "四体系以中一致为主，整体可作稳健参考，关键决策仍辅以现实反馈；"
    else:
        xjudge = ("四体系有 %d 个维度存在分歧（多为『一守一攻』之互补：如八字偏守、紫微见贵，综合取『借平台稳进』），"
                  "建议以『交叉共识＋现实印证』双保险，避免单凭一家之言下注；" % div)
    meaning = (yijing.get("meaning") or "")[:22]
    para = ("日主%s（%s），%s，五行%s。" % (dm, day_gan, strength,
                "趋于平和" if top == bot else ("以「%s」偏盛、「%s」偏弱" % (top, bot)))
            + "格局上" + pattern + "。用神宜取「" + xi_text + "」——" + xi_phrase + "；"
            + "忌「" + ji_text + "」——" + ji_phrase + "。"
            + xjudge
            + "本命卦「%s」(%s)，动爻第 %s 爻，主%s——卦象与命局互参，整体取向%s。"
              % (yijing["ben_gua"], yijing["gua_nature"], yijing["dong_yao"], meaning,
                 "同气相应" if yijing["gua_elem"] == dm else "相成而可调"))
    return {"paragraph": para, "xi_set": xi, "ji_set": ji, "pattern": pattern,
            "top_element": top, "weak_element": bot, "xi_text": xi_text, "ji_text": ji_text}


def _yongshen_map(bazi: dict, mingge: dict) -> dict:
    """用神人生映射：方位 / 行业 / 助运色 / 调候（由喜用五行推导）。"""
    de = bazi["day_element"]
    xi = mingge["xi_set"]
    elems = {}
    for g in xi:
        e = _tg_elem(de, g)
        if e:
            elems[e] = 1
    if bazi["strength"] == "身弱":
        elems[de] = 1
    DIR = {"木": "东方", "火": "南方", "土": "中原/本地", "金": "西方", "水": "北方"}
    IND = {"木": "文化教育、农林园艺、创意设计、出版", "火": "能源电力、传媒餐饮、互联网、文化演艺",
           "土": "地产建筑、金融实业、服务管理、仓储", "金": "机械制造、法律司法、金融精算、五金",
           "水": "贸易流通、咨询策划、交通运输、旅游"}
    COL = {"木": "青/绿", "火": "红/紫", "土": "黄/褐", "金": "白/金", "水": "黑/蓝"}
    TIAO = {"木": "多接触自然与新知、主动拓展人际", "火": "勇于表达与展示、保持行动力",
            "土": "重积累与信用、行事稳妥少变", "金": "讲规则重契约、精炼专业壁垒",
            "水": "灵活应变、以柔克刚、多走动"}
    rows = []
    for e in elems:
        rows.append({"element": e, "dir": DIR[e], "ind": IND[e], "col": COL[e], "tiao": TIAO[e]})
    if not rows:
        rows.append({"element": de, "dir": DIR[de], "ind": IND[de], "col": COL[de], "tiao": TIAO[de]})
    return {"elements": list(elems.keys()), "rows": rows}


def _dayun_detail(bazi: dict, birth_year: int) -> list:
    """大运阶段详批：主题 + 关键转折年（岁运并临 / 天克地冲）+ 阶段建议。"""
    day_gan = bazi["day_master"]
    xi, ji = _xi_ji_sets(bazi)

    def theme(god):
        if god in ("正官", "七杀"):
            return "事业进阶：责任与考核加重，宜争位、掌权、立专业壁垒"
        if god in ("正印", "偏印"):
            return "沉淀蓄能：利学习考证、得长辈/平台荫护，宜厚积"
        if god in ("正财", "偏财"):
            return "务实生财：重现金流与业务落地，偏财年须防贪"
        if god in ("食神", "伤官"):
            return "才艺外显：利表达创新与变动，也须防口舌是非"
        if god in ("比肩", "劫财"):
            return "协作竞争：宜合伙借力，但分账权责须白纸黑字"
        return "平运守成：稳扎稳打、积累资源，不躁不怠"

    out = []
    if bazi["dayun"][0]["start_age"] > 0:
        out.append({"range": "0–%d岁" % (round(bazi["dayun"][0]["start_age"]) - 1), "gz": "命局",
                    "theme": "本命奠基：以学业、心性养成与家庭支持为主，不急于闯荡",
                    "turning": "—", "tip": "未起运，顺势养根基；大额押注与远行宜缓。"})
    for d in bazi["dayun"]:
        god = C.ten_god(day_gan, d["gz"][0])
        fav = god in xi
        bad = god in ji
        turning = []
        a0 = round(d["start_age"])
        a1 = round(d["end_age"] - 1)
        for a in range(a0, a1 + 1):
            yr = birth_year + a - 1
            gz = C.GZ60[(yr - 4) % 60]
            if gz == d["gz"]:
                turning.append("%d岁（岁运并临）" % a)
            else:
                gk = C.KE.get(gz[0]) == d["gz"][0] or C.KE.get(d["gz"][0]) == gz[0]
                if gk and _chong(gz[1], d["gz"][1]):
                    turning.append("%d岁（天克地冲·大变动）" % a)
        tip = ("此运干支为喜，十年动能偏顺——宜把握窗口、主动进取、放大成果；顺境也别放松风控。"
               if fav else "此运干支为忌，守成蓄势的十年——控风险、重大决策三思、不替人担保、不盲目加杠杆，以稳换空间。"
               if bad else "此运平气，稳扎稳打、积累实力与资源，不主动制造大变动。")
        out.append({"range": "%d–%d岁" % (a0, a1), "gz": d["gz"],
                    "theme": theme(god) + ("（喜运）" if fav else "（忌运）" if bad else ""),
                    "turning": "；".join(turning[:2]) if turning else "无明显大变动年", "tip": tip})
    return out


def cross_validate(bazi, ziwei, yijing, tieban) -> dict:
    bs = bazi_signals(bazi)
    zs = ziwei_signals(ziwei)
    ys = yijing_signals(yijing, bazi)
    ts, tieban_votes = tieban_signals(tieban, bazi)

    matrix = []
    for dim in DIMS:
        votes = []
        for sysname, sig in (("四柱八字", bs), ("紫微斗数", zs), ("周易卦象", ys), ("铁板神数", ts)):
            if dim in sig:
                text, level = sig[dim]
                votes.append({"system": sysname, "text": text, "level": level})
        levels = [v["level"] for v in votes]
        if levels:
            mean = sum(levels) / len(levels)
            rng = max(levels) - min(levels)
        else:
            mean, rng = 3, 0
        # 一致性判定
        if rng <= 1:
            consistency = "高一致"
        elif rng <= 2:
            consistency = "中一致"
        else:
            consistency = "分歧"
        matrix.append({
            "dimension": dim, "votes": votes,
            "mean_level": round(mean, 1), "range": rng, "consistency": consistency,
        })

    # 考时复核信号：铁板兄弟数 与 八字比劫 是否冲突
    review_flags = []
    bi_jie = sum(1 for g in bazi["ten_gods"] if g in ("比肩", "劫财"))
    bro_vote = tieban_votes.get("兄弟", {})
    # 极简：若八字比劫>=2 但铁板兄弟数<=1（且非独生暗示），提示复核
    if bi_jie >= 2 and bro_vote:
        review_flags.append("八字比劫偏旺而铁板兄弟数偏少，时辰或存疑，建议考时复核。")
    conflicts = [m["dimension"] for m in matrix if m["consistency"] == "分歧"]
    if conflicts:
        review_flags.append("维度「" + "、".join(conflicts) + "」四体系结论分歧较大，建议复核。")

    # 综合分级
    cons_counts = {"高一致": 0, "中一致": 0, "分歧": 0}
    for m in matrix:
        cons_counts[m["consistency"]] += 1
    if cons_counts["分歧"] == 0 and cons_counts["高一致"] >= 4:
        grade = "高一致 · 结论可信度较高"
    elif cons_counts["分歧"] == 0:
        grade = "中一致 · 结论可作参考"
    else:
        grade = "分歧需复核 · 时辰或参数待考证"

    # 综合结论文字（每维度给一句 + 指导建议）
    xi_set2, ji_set2 = _xi_ji_sets(bazi)
    life = _life_guidance(matrix, bazi, xi_set2, ji_set2, cons_counts, review_flags)
    conclusions = []
    for m in matrix:
        direction = "吉/强" if m["mean_level"] >= 4 else ("平" if m["mean_level"] >= 3 else "弱/宜守")
        conclusions.append({
            "dimension": m["dimension"],
            "direction": direction,
            "consistency": m["consistency"],
            "summary": f"{m['dimension']}：综合评级 {direction}（一致性 {m['consistency']}）。",
            "advice": life["dimension_tips"][m["dimension"]],
        })

    # 命格综合论断 · 用神人生映射 · 大运阶段详批（深度模块）
    mingge = _mingge_zonglun(bazi, yijing, {"cons_counts": cons_counts})
    yongshen = _yongshen_map(bazi, mingge)
    dayun_detail = _dayun_detail(bazi, bazi["birth_year"])

    return {
        "matrix": matrix,
        "review_flags": review_flags,
        "cons_counts": cons_counts,
        "grade": grade,
        "conclusions": conclusions,
        "life_guidance": life,
        "mingge": mingge,
        "yongshen": yongshen,
        "dayun_detail": dayun_detail,
    }
