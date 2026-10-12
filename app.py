# -*- coding: utf-8 -*-
"""命理交叉验证系统 · Flask 交互原型。
启动：python app.py  -> 浏览器打开 http://127.0.0.1:5000
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template, request, jsonify

from engine import bazi as B, ziwei as Z, yijing as Y, tieban as T, cross_validation as CV, geo as G, constants as C, liunian as L, chart as CH

app = Flask(__name__)


def _parse_birth(form):
    y = int(form["year"]); m = int(form["month"]); d = int(form["day"])
    hh = int(form["hour"]); mm = int(form.get("minute", 0) or 0)
    gender = form.get("gender", "男")
    birthplace = form.get("birthplace", "北京时间(东经120°)")
    birth = datetime.datetime(y, m, d, hh, mm)
    return birth, gender, birthplace


def _report_context(birth, gender, birthplace):
    # 真太阳时修正：出生地经度 -> 地方真太阳时（用于校正时辰）
    lon = C.CITY_LONGITUDE.get(birthplace, 120.0)
    solar_birth, delta_h, eot, lon = G.correct_to_solar(birth, lon)
    geo = {
        "birthplace": birthplace, "longitude": lon,
        "delta_h": round(delta_h, 3), "eot": round(eot, 2),
        "solar_birth": solar_birth,
    }
    from engine.ziwei import _hour_to_shichen
    sc_before = _hour_to_shichen(birth.hour)
    sc_after = _hour_to_shichen(solar_birth.hour)
    geo["shichen_before"] = C.ZHI[sc_before - 1] + "时"
    geo["shichen_after"] = C.ZHI[sc_after - 1] + "时"
    geo["shichen_changed"] = sc_before != sc_after

    # 四体系均基于「地方真太阳时」排盘
    b = B.compute_bazi(solar_birth, gender)
    b["gender"] = gender
    z = Z.compute_ziwei(solar_birth, gender)
    yj = Y.meihua_qigua(b["four_pillars"])
    tb = T.compute_tieban(b, z)
    cv = CV.cross_validate(b, z, yj, tb)

    # 流年逐岁详批（推运层）
    liu = L.compute_liunian(b, z, solar_birth)
    # 紫微十二宫圆形星盘
    ziwei_svg = CH.build_ziwei_svg(z)
    # 十年运势走势折线图
    fortune_svg = CH.fortune_trend_svg(liu)

    # 五行可视化数据
    elem = b["element_count"]
    elem_data = [{"name": k, "value": v, "color": C.ELEMENT_COLOR[k]} for k, v in elem.items()]

    return dict(
        birth=birth, solar_birth=solar_birth, gender=gender, geo=geo,
        bazi=b, ziwei=z, yijing=yj, tieban=tb, cv=cv,
        liunian=liu, ziwei_svg=ziwei_svg, fortune_svg=fortune_svg,
        elem_data=elem_data,
    )


def _assemble_json(ctx):
    """把报告上下文转成可序列化 JSON 结构（去除 datetime 等非序列化对象）。"""
    b = ctx["bazi"]; z = ctx["ziwei"]; yj = ctx["yijing"]; tb = ctx["tieban"]
    cv = ctx["cv"]; geo = ctx["geo"]; liu = ctx["liunian"]
    return {
        "meta": {
            "birth_bj": ctx["birth"].strftime("%Y-%m-%d %H:%M"),
            "birth_solar_local": geo["solar_birth"].strftime("%Y-%m-%d %H:%M"),
            "gender": ctx["gender"],
            "birthplace": geo["birthplace"],
            "longitude": geo["longitude"],
            "std_time_diff_h": geo["delta_h"],
            "equation_of_time_min": geo["eot"],
            "shichen": (geo["shichen_after"]
                        if not geo["shichen_changed"]
                        else f"{geo['shichen_before']}→{geo['shichen_after']}"),
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "bazi": {
            "four_pillars": b["four_pillars"],
            "day_master": b["day_master"], "day_element": b["day_element"],
            "strength": b["strength"], "support": b["support"], "drain": b["drain"],
            "element_count": b["element_count"], "zodiac": b["zodiac"],
            "dayun_forward": b["dayun_forward"], "dayun_start_age": b["dayun_start_age"],
            "dayun": b["dayun"], "liu_year": b["liu_year"],
        },
        "ziwei": {
            "mingong_gz": z["mingong_gz"], "mingong_zhi": z["mingong_zhi"],
            "shichen": z["shichen"], "ju": z["ju"], "ziwei_zhi": z["ziwei_zhi"],
            "main_star": z["main_star"], "sihua": z["sihua"],
            "sihua_map": z["sihua_map"], "sanfang_sizheng": z["sanfang_sizheng"],
            "palaces": [{"palace": p["palace"], "zhi": p["zhi"],
                         "stars": p["stars"], "fu_stars": p["fu_stars"]}
                        for p in z["palaces"]],
        },
        "yijing": yj,
        "tieban": {"base_number": tb["base_number"], "tiaowen": tb["tiaowen"]},
        "cross_validation": {
            "grade": cv["grade"], "cons_counts": cv["cons_counts"],
            "review_flags": cv["review_flags"],
            "matrix": cv["matrix"], "conclusions": cv["conclusions"],
        },
        "liunian": {
            "now_year": liu["now_year"],
            "rows": [{k: v for k, v in r.items() if k != "is_current"} | {"is_current": r["is_current"]}
                     for r in liu["rows"]],
        },
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", cities=list(C.CITY_LONGITUDE.keys()))


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        birth, gender, birthplace = _parse_birth(request.form)
    except Exception as e:
        return render_template("index.html", error="出生日期/时间格式有误：" + str(e))
    ctx = _report_context(birth, gender, birthplace)
    return render_template("report.html", **ctx)


@app.route("/export_json", methods=["POST"])
def export_json():
    try:
        birth, gender, birthplace = _parse_birth(request.form)
    except Exception as e:
        return jsonify({"error": "出生日期/时间格式有误：" + str(e)}), 400
    ctx = _report_context(birth, gender, birthplace)
    return jsonify(_assemble_json(ctx))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
