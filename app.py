# -*- coding: utf-8 -*-
"""天命系统 · Flask 交互原型。
启动：python app.py  -> 浏览器打开 http://127.0.0.1:5000

============================================================================
公网部署安全检查清单（仅在把本服务暴露到互联网时才需要全部满足）
============================================================================
本应用默认仅绑定 127.0.0.1（本机），属安全状态。若改为对外服务，请逐项确认：
  [1] 调试模式必须关闭：绝不可设 debug=True（见文件底部 app.run）。
      调试器一旦网络可达，攻击者可借控制台 PIN 远程执行代码（RCE）。
  [2] 设置强会话密钥：部署前 export FLASK_SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))")，
      且密钥不入库、不写死在代码里。
  [3] 绑定地址谨慎：不要直接 0.0.0.0 暴露。建议经 Nginx/Caddy 反向代理，
      由代理对外监听 443，Flask 仅监听本机或内网。
  [4] 强制 HTTPS：反向代理层启用 TLS（Let's Encrypt 免费证书），
      并配置 HSTS，避免中间人窃听/篡改。
  [5] 加访问鉴权：本接口无登录，公网直接暴露会被任意调用。
      至少加一层密码/Token 校验或放在 VPN/内网，再决定是否开放。
  [6] 限流防滥用：用 Flask-Limiter 等对接入频率限流，防刷接口/DoS。
  [7] 安全响应头：由代理加上 X-Content-Type-Options、X-Frame-Options(DENY)、
      Referrer-Policy、Content-Security-Policy 等。
  [8] 错误不泄露内部信息：生产环境关闭 Werkzeug 详细错误页（debug=False 已保证），
      不在页面/JSON 中回显堆栈或内部路径。
  [9] 依赖定期更新：pip install -r requirements.txt 的版本已 pin，
      但仍需关注 CVE 公告及时升级（flask / cnlunar 等）。
 [10] 不提交密钥：.env、*.token、含口令的构建脚本（如 enc.js）一律不入库
      （仓库 .gitignore 已忽略 .env / *.token）。
============================================================================
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template, request, jsonify

from engine import bazi as B, ziwei as Z, yijing as Y, tieban as T, cross_validation as CV, geo as G, constants as C, liunian as L, chart as CH

app = Flask(__name__)

# 会话密钥：优先读环境变量 FLASK_SECRET_KEY（部署时务必设置强随机值）；
# 未设置则每次启动随机生成（本应用当前无持久会话，仅作纵深防御，防未来会话伪造）。
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24).hex()

# 纵深防御：限制请求体大小（当前无文件上传，仅为防滥用/DoS）
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB


def _parse_birth(form):
    """校验并解析出生信息。失败抛出 ValueError（中文说明），由调用方捕获返回 400。"""
    try:
        y = int(form["year"]); m = int(form["month"]); d = int(form["day"])
        hh = int(form["hour"]); mm = int(form.get("minute", 0) or 0)
    except (KeyError, ValueError, TypeError):
        raise ValueError("请完整填写年/月/日/时，且必须为整数")
    if not (1900 <= y <= 2100):
        raise ValueError("年份需在 1900–2100 之间")
    if not (1 <= m <= 12):
        raise ValueError("月份需在 1–12 之间")
    if not (1 <= d <= 31):
        raise ValueError("日期需在 1–31 之间")
    if not (0 <= hh <= 23):
        raise ValueError("小时需在 0–23 之间")
    if not (0 <= mm <= 59):
        raise ValueError("分钟需在 0–59 之间")
    gender = form.get("gender", "男")
    if gender not in ("男", "女"):
        raise ValueError("性别取值不合法")
    # 出生地来自受控下拉框；限长 64 防超长/异常输入
    birthplace = (form.get("birthplace") or "北京时间(东经120°)")[:64]
    try:
        birth = datetime.datetime(y, m, d, hh, mm)
    except ValueError:
        raise ValueError("该日期不存在（如 2 月 30 日）")
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
    # 安全：默认关闭调试器。Werkzeug 调试器一旦开启且被网络可达，攻击者可借控制台 PIN 远程执行代码。
    # 仅在本地排错时通过环境变量临时开启：FLASK_DEBUG=1 python app.py
    debug = os.environ.get("FLASK_DEBUG") == "1"
    # 仅绑定本机回环地址，不对外暴露；如需对外请改用反向代理并强制 HTTPS。
    app.run(host="127.0.0.1", port=5000, debug=debug)
