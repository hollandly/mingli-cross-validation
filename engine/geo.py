# -*- coding: utf-8 -*-
"""真太阳时修正：把用户输入的出生时刻（按北京时间/东经120°标准时理解）
折算为出生地「地方真太阳时」，用于校正出生时辰——时辰一偏，八字/紫微/
周易/铁板四体系会整体漂移，故这是交叉验证可信度的前提。

说明：
- 标准时差：(出生地经度 - 120°) / 15 小时（东经每偏东1°，地方时早4分钟）。
- 时差方程(EoT)：真太阳时与平太阳时之差，采用标准天文近似公式，年变幅约±16分钟。
- 真太阳时 = 标准时 + 标准时差 + EoT/60。
"""
import datetime
import math


def equation_of_time(dt: datetime.datetime) -> float:
    """时差方程 EoT（真太阳时 − 平太阳时），单位：分钟。标准天文近似。"""
    n = (dt - datetime.datetime(dt.year, 1, 1)).days + 1
    d = 0.9856 * (n - 1)
    return -7.66 * math.sin(math.radians(d + 4.13)) + 9.87 * math.sin(math.radians(2 * d + 3.6))


def correct_to_solar(birth: datetime.datetime, longitude: float):
    """birth: 用户输入出生 datetime（按北京时间理解）；longitude: 出生地经度(度)。
    返回 (真太阳时datetime, 标准时差小时, 时差方程分钟, 经度)。"""
    delta_h = (longitude - 120.0) / 15.0
    partial = birth + datetime.timedelta(hours=delta_h)
    eot = equation_of_time(birth)
    solar = partial + datetime.timedelta(minutes=eot)
    return solar, delta_h, eot, longitude
