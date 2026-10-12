# -*- coding: utf-8 -*-
"""四柱八字引擎：基于 cnlunar 计算四柱，并推导十神、五行强弱、大运、流年。"""
import datetime
import cnlunar
from . import constants as C


def _gan_zhi_index(gz: str) -> int:
    """干支在 60 甲子中的序号（甲子=0）。"""
    return C.GZ60_INDEX[gz]


def _jiezhi_list(year: int):
    """返回某公历年的 12 个『节』[(datetime, 名)]，用于起运推算。"""
    jie_names = ["小寒", "立春", "惊蛰", "清明", "立夏", "芒种",
                 "小暑", "立秋", "白露", "寒露", "立冬", "大雪"]
    dummy = cnlunar.Lunar(datetime.datetime(year, 6, 1))
    dic = dummy.thisYearSolarTermsDic
    out = []
    for name in jie_names:
        if name in dic:
            m, d = dic[name]
            out.append((datetime.datetime(year, m, d), name))
    return out


def compute_bazi(birth: datetime.datetime, gender: str) -> dict:
    """birth: 阳历 datetime（已含时辰）；gender: '男'/'女'。"""
    lunar = cnlunar.Lunar(birth)
    year_gz = lunar.year8Char
    month_gz = lunar.month8Char
    day_gz = lunar.day8Char
    hour_gz = lunar.twohour8Char
    four = [year_gz, month_gz, day_gz, hour_gz]
    day_gan = day_gz[0]

    # 十神
    shi_shen = [C.ten_god(day_gan, gz[0]) for gz in four]

    # 五行计分（天干+地支本气）
    element_count = {e: 0 for e in C.ELEMENTS}
    for gz in four:
        element_count[C.GAN_ELEMENT[C.GAN_INDEX[gz[0]]]] += 1
        element_count[C.ZHI_ELEMENT[C.ZHI_INDEX[gz[1]]]] += 1
    day_elem = C.GAN_ELEMENT[C.GAN_INDEX[day_gan]]

    # 日主强弱：生扶(比劫+印) vs 克泄耗(官杀+食伤+财)
    support = 0.0
    drain = 0.0
    for gz, ss in zip(four, shi_shen):
        if ss in ("比肩", "劫财", "正印", "偏印"):
            support += 1.0
        else:
            drain += 1.0
    # 月令（月支本气）加权：得令则生扶+0.6
    month_zhi_elem = C.ZHI_ELEMENT[C.ZHI_INDEX[month_gz[1]]]
    if C.SHENG.get(month_zhi_elem) == day_elem or month_zhi_elem == day_elem:
        support += 0.6
    elif C.KE.get(month_zhi_elem) == day_elem or C.KE.get(day_elem) == month_zhi_elem:
        drain += 0.4
    ratio = support / (drain + 1e-9)
    if ratio >= 1.5:
        strength = "身旺"
    elif ratio <= 0.7:
        strength = "身弱"
    else:
        strength = "中和"

    # 大运（起运 + 顺逆 + 序列）
    yin = C.GAN_YINYANG[C.GAN_INDEX[year_gz[0]]] == "阳"
    male = gender == "男"
    forward = (yin and male) or (not yin and not male)  # 阳男/阴女顺排，阴男/阳女逆排

    # 找出生前后最近的『节』
    all_jie = []
    for y in (birth.year - 1, birth.year, birth.year + 1):
        all_jie.extend(_jiezhi_list(y))
    all_jie.sort()
    prev_jie = max([d for d, _ in all_jie if d <= birth], default=None)
    next_jie = min([d for d, _ in all_jie if d > birth], default=None)
    if forward and next_jie:
        days = (next_jie - birth).days
    elif (not forward) and prev_jie:
        days = (birth - prev_jie).days
    else:
        days = 0
    start_age = days / 3.0  # 三天为一岁

    mi = _gan_zhi_index(month_gz)
    dayun = []
    for i in range(8):
        idx = (mi + (i + 1) if forward else mi - (i + 1)) % 60
        g = C.GAN[idx % 10]
        z = C.ZHI[idx % 12]
        dayun.append({
            "step": i + 1,
            "gz": g + z,
            "start_age": round(start_age + i * 10, 1),
            "end_age": round(start_age + (i + 1) * 10, 1),
            "nayin": C.nayin_name(g + z),
        })

    # 流年（当前公历年）
    now_year = datetime.date.today().year
    liu_year = []
    for y in range(now_year - 2, now_year + 4):
        gz = C.GZ60[(y - 4) % 60]
        liu_year.append({"year": y, "gz": gz, "nayin": C.nayin_name(gz),
                         "shi_shen": C.ten_god(day_gan, gz[0])})

    return {
        "four_pillars": {
            "year": {"gz": year_gz, "nayin": C.nayin_name(year_gz), "shi_shen": shi_shen[0]},
            "month": {"gz": month_gz, "nayin": C.nayin_name(month_gz), "shi_shen": shi_shen[1]},
            "day": {"gz": day_gz, "nayin": C.nayin_name(day_gz), "shi_shen": shi_shen[2]},
            "hour": {"gz": hour_gz, "nayin": C.nayin_name(hour_gz), "shi_shen": shi_shen[3]},
        },
        "day_master": day_gan,
        "day_element": day_elem,
        "birth_year": birth.year,
        "ten_gods": shi_shen,
        "element_count": element_count,
        "strength": strength,
        "support": round(support, 1),
        "drain": round(drain, 1),
        "zodiac": lunar.chineseYearZodiac,
        "dayun_forward": forward,
        "dayun_start_age": round(start_age, 2),
        "dayun": dayun,
        "liu_year": liu_year,
    }
