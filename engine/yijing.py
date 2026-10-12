# -*- coding: utf-8 -*-
"""周易层：以出生四柱干支数，按梅花易数法定『命局本卦 / 变卦 / 动爻』，
作为运势与决策的交叉验证维度（非占卜问事，而是取卦象之象以参命）。"""
from . import constants as C

# 先天八卦数：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8
BAGUA_NUM = {"乾": 1, "兑": 2, "离": 3, "震": 4, "巽": 5, "坎": 6, "艮": 7, "坤": 8}
NUM_BAGUA = {v: k for k, v in BAGUA_NUM.items()}

# 64 卦简义（象+趋势），用于交叉验证的卦义关键词
HEX_MEANING = {
    "乾为天": "刚健中正，自强不息；宜进取，忌刚愎", "天泽履": "履虎尾，慎行免咎；守礼可成",
    "天火同人": "同人于野，和同协力；利交际", "天雷无妄": "无妄求实，不妄动；顺天休命",
    "天风姤": "邂逅不期，防阴长；宜守不宜攻", "天水讼": "讼则争，慎防口舌官非；宜止",
    "天山遁": "遁世避位，退保其身；时穷则隐", "天地否": "天地不交，闭塞之象；待时通",
    "泽天夬": "决而能和，刚决柔；果断去小人", "兑为泽": "丽泽相悦，口舌欢愉；重情义",
    "泽火革": "革故鼎新，顺天应人；变革之时", "泽雷随": "随时而动，从宜适变；随顺吉",
    "泽风大过": "大过栋桡，独立不惧；宜慎重任", "泽水困": "困穷守正，处险静守；待援",
    "泽山咸": "咸感相应，男女相悦；交感成", "泽地萃": "萃聚一堂，物以类聚；聚而散慎",
    "火天大有": "大有富有，遏恶扬善；盛而谦", "火泽睽": "睽违乖离，求同存异；谨慎合",
    "离为火": "明两作离，继明照四方；附丽守正", "火雷噬嗑": "噬嗑亨，刚柔决断；去间成",
    "火风鼎": "鼎新取象，烹饪养贤；革故鼎新", "火水未济": "未济事未成，慎终如始；待济",
    "火山旅": "旅琐琐，行旅在外；不安守", "火地晋": "晋进显明，旭日升天；进取得时",
    "雷天大壮": "大壮阳刚，壮勿妄动；守正", "雷泽归妹": "归妹征凶，男女终始；慎嫁娶",
    "雷火丰": "丰大光明，盛极当忧；保丰", "震为雷": "震来虩虩，恐惧修省；动而生",
    "雷风恒": "恒久不已，立不易方；持久吉", "雷水解": "解险舒难，险以动；解脱时",
    "雷山小过": "小过宜下，过而能改；守小", "雷地豫": "豫乐顺动，备豫不虞；乐勿极",
    "风天小畜": "小畜寡聚，密云不雨；积小", "风泽中孚": "中孚信及豚鱼，诚信感；信立",
    "风火家人": "家人有严君，正家道；内和", "风雷益": "益损上益下，与时偕行；受益",
    "巽为风": "巽顺以入，申命行事；谦入", "风水涣": "涣散其患，风行水上；散而聚",
    "风山渐": "渐女归吉，循序渐进；稳进", "风地观": "观国之光，省方观民；观察",
    "水天需": "需待也，饮食宴乐；待时", "水泽节": "节以制度，不伤财；节制",
    "水火既济": "既济初吉终乱，守成维艰；戒满", "水雷屯": "屯刚柔始交，难生；经纶",
    "水风井": "井养不穷，改邑不改井；养德", "坎为水": "习坎重险，维心亨；处险智",
    "水山蹇": "蹇难止行，反身修德；止而慎", "水地比": "比亲辅也，先王建万国；亲附",
    "山天大畜": "大畜厚积，刚上尚贤；蓄德", "山泽损": "损下益上，惩忿窒欲；损抑",
    "山火贲": "贲饰也，质有其文；文饰", "山雷颐": "颐养正，慎言语节饮食；养正",
    "山风蛊": "蛊坏终蛊，干父之蛊；整治", "山水蒙": "蒙以养正，山下出泉；启蒙",
    "艮为山": "艮止其背，时止则止；静守", "山地剥": "剥床以肤，剥落消阳；防损",
    "地天泰": "天地交泰，小往大来；通泰", "地泽临": "临元亨利贞，养成临民；临下",
    "地火明夷": "明夷伤夷，内难而能正；韬光", "地雷复": "复见天地心，一阳来复；复兴",
    "地风升": "升巽而顺，积小成高；升进", "地水师": "师众贞丈人，容民畜众；用众",
    "地山谦": "谦尊而光，裒多益寡；谦德", "坤为地": "坤厚载物，柔顺利贞；顺承",
}


def _trigram_lines(gua: str):
    return list(C.BAGUA_TRIGRAM[gua])  # [下,中,上] 1=阳 0=阴


def _num_to_trigram(num: int) -> str:
    return NUM_BAGUA[num]


def meihua_qigua(four_pillars: dict) -> dict:
    """four_pillars: {'year':{'gz':..}, 'month':{..}, 'day':{..}, 'hour':{..}}"""
    def num(gz):
        return C.GAN_INDEX[gz[0]] + 1, C.ZHI_INDEX[gz[1]] + 1  # 1-based

    yg, yz = num(four_pillars["year"]["gz"])
    mg, mz = num(four_pillars["month"]["gz"])
    dg, dz = num(four_pillars["day"]["gz"])
    hg, hz = num(four_pillars["hour"]["gz"])

    up = (yg + mg + dg) % 8
    if up == 0:
        up = 8
    lo = (yz + mz + dz) % 8
    if lo == 0:
        lo = 8
    dong = (yg + yz + mg + mz + dg + dz + hg + hz) % 6
    if dong == 0:
        dong = 6

    up_gua = _num_to_trigram(up)
    lo_gua = _num_to_trigram(lo)
    hex_idx = (up - 1) * 8 + (lo - 1)
    ben = C.HEX_NAMES[hex_idx]
    meaning = HEX_MEANING.get(ben, "")

    # 变卦：动爻 1..6，从下往上；<=3 在下卦，否则在上卦
    lo_lines = _trigram_lines(lo_gua)
    up_lines = _trigram_lines(up_gua)
    if dong <= 3:
        lo_lines[dong - 1] ^= 1
    else:
        up_lines[dong - 4] ^= 1
    lo_gua2 = [k for k, v in C.BAGUA_TRIGRAM.items() if list(v) == lo_lines][0]
    up_gua2 = [k for k, v in C.BAGUA_TRIGRAM.items() if list(v) == up_lines][0]
    bian_idx = (BAGUA_NUM[up_gua2] - 1) * 8 + (BAGUA_NUM[lo_gua2] - 1)
    bian = C.HEX_NAMES[bian_idx]

    # 卦的五行（取上卦五行为主，参下卦）
    gua_elem = C.BAGUA_ELEMENT[up_gua]
    gua_nature = C.BAGUA_NATURE[up_gua]

    # 关键词：上下卦性质 + 卦名意象
    keywords = [up_gua, lo_gua, ben.split("为")[0] if "为" in ben else ben[:2]]

    return {
        "up_gua": up_gua,
        "lo_gua": lo_gua,
        "ben_gua": ben,
        "bian_gua": bian,
        "dong_yao": dong,
        "meaning": meaning,
        "gua_elem": gua_elem,
        "gua_nature": gua_nature,
        "keywords": keywords,
    }
