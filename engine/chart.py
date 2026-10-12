# -*- coding: utf-8 -*-
"""紫微十二宫圆形星盘图：纯 SVG 字符串生成（无外部依赖）。
命宫置于正上方，顺时针排列十二宫；三方四正（命/财/官/迁）高亮；
主星、辅星、四化落宫分别着色；中心显示五行局/紫微/命宫。
"""
import math
from . import constants as C

CX, CY = 320, 318
R_LABEL = 296   # 宫名环半径
R_MAIN = 168    # 主星环半径
R_FU = 150      # 辅星环半径（内侧）
R_DOT = 250     # 宫位节点半径


def _pt(r, deg):
    t = math.radians(deg)
    return (CX + r * math.cos(t), CY + r * math.sin(t))


def build_ziwei_svg(ziwei: dict) -> str:
    palaces = ziwei["palaces"]
    sihua_map = ziwei.get("sihua_map", {})
    sanfang = {0, 4, 8, 6}  # 命/财/官/迁

    parts = []
    parts.append(
        f'<svg viewBox="0 0 640 640" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="紫微斗数十二宫星盘" style="max-width:560px;width:100%;height:auto;display:block;margin:0 auto">'
    )
    # 背景圆
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="312" fill="#faf7f2" stroke="#e6e9ee"/>')
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="120" fill="#fff" stroke="#e6e9ee"/>')
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="308" fill="none" stroke="#e6e9ee"/>')

    for i, p in enumerate(palaces):
        deg = -90 + i * 30
        # 射线
        x2, y2 = _pt(R_DOT, deg)
        parts.append(f'<line x1="{CX}" y1="{CY}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#e6e9ee" stroke-width="1"/>')

        # 宫名
        lx, ly = _pt(R_LABEL, deg)
        hl = i in sanfang
        name_color = "#8a5a2b" if hl else "#1f2733"
        fw = "bold" if hl else "normal"
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'font-size="13" font-weight="{fw}" fill="{name_color}">{p["palace"]}</text>'
        )
        zx, zy = _pt(R_LABEL - 15, deg)
        parts.append(
            f'<text x="{zx:.1f}" y="{zy:.1f}" text-anchor="middle" font-size="10" fill="#6b7785">{p["zhi"]}</text>'
        )
        # 高亮节点
        dx, dy = _pt(R_DOT, deg)
        dot_fill = "#8a5a2b" if hl else "#cfd6dd"
        parts.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4" fill="{dot_fill}"/>')

        # 主星（环外侧，靠近节点）
        mx, my = _pt(R_DOT - 26, deg)
        stars = p["stars"]
        if stars:
            star_text = " ".join(stars)
            # 紫微加粗标红
            fill = "#2b5a8a"
            parts.append(
                f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" font-size="12" '
                f'font-weight="bold" fill="{fill}">{star_text}</text>'
            )
            # 四化后缀
            sihua_suffix = " ".join(f"({sihua_map[s]})" for s in stars if s in sihua_map)
            if sihua_suffix:
                sx, sy = _pt(R_DOT - 26, deg + 6)
                parts.append(
                    f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" font-size="9" fill="#c0392b">{sihua_suffix}</text>'
                )
        else:
            parts.append(
                f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" font-size="11" fill="#9aa4af">空宫</text>'
            )

        # 辅星（内侧）
        fu = p["fu_stars"]
        if fu:
            fx, fy = _pt(R_FU, deg)
            parts.append(
                f'<text x="{fx:.1f}" y="{fy:.1f}" text-anchor="middle" font-size="9.5" fill="#6b7785">{" ".join(fu)}</text>'
            )

    # 中心信息
    parts.append(f'<text x="{CX}" y="{CY-44}" text-anchor="middle" font-size="13" font-weight="bold" fill="#8a5a2b">紫微斗数</text>')
    parts.append(f'<text x="{CX}" y="{CY-22}" text-anchor="middle" font-size="12" fill="#1f2733">命宫 {ziwei["mingong_gz"]}</text>')
    parts.append(f'<text x="{CX}" y="{CY}" text-anchor="middle" font-size="12" fill="#1f2733">{ziwei["ju"]}</text>')
    parts.append(f'<text x="{CX}" y="{CY+22}" text-anchor="middle" font-size="12" fill="#1f2733">紫微在 {ziwei["ziwei_zhi"]}</text>')
    parts.append(f'<text x="{CX}" y="{CY+44}" text-anchor="middle" font-size="11" fill="#6b7785">命宫主星 {ziwei["main_star"]}</text>')

    # 图例
    parts.append(f'<text x="{CX}" y="600" text-anchor="middle" font-size="11" fill="#6b7785">○ 棕圈=三方四正（命/财/官/迁）｜ 蓝字=主星 灰字=辅星 红()=生年四化</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def fortune_trend_svg(liunian: dict) -> str:
    """十年运势走势折线图：纯 SVG（无外部依赖）。
    x=年份，y=吉凶评分（约 -3~+3，0 为基准线），点按吉凶配色。
    """
    rows = liunian["rows"]
    n = len(rows)
    W, H = 760, 250
    pad_l, pad_r, pad_t, pad_b = 46, 16, 18, 32
    plot_w = W - pad_l - pad_r
    plot_h = H - pad_t - pad_b
    SCORE_MIN, SCORE_MAX = -3.0, 3.0

    def y_of(score):
        s = max(SCORE_MIN, min(SCORE_MAX, score))
        return pad_t + (1 - (s - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)) * plot_h

    def x_of(i):
        return pad_l + (plot_w * i / (n - 1)) if n > 1 else pad_l + plot_w / 2

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="十年运势走势" style="max-width:760px;width:100%;height:auto;display:block;margin:0 auto">'
    )
    # 坐标轴
    parts.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#e6e9ee"/>')
    parts.append(f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{pad_l+plot_w}" y2="{pad_t+plot_h}" stroke="#e6e9ee"/>')
    # 网格 + 刻度
    for s in (-3, -2, -1, 1, 2, 3):
        yy = y_of(s)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{pad_l+plot_w}" y2="{yy:.1f}" stroke="#f0f2f5"/>')
        parts.append(f'<text x="{pad_l-8}" y="{yy+4:.1f}" text-anchor="end" font-size="10" fill="#9aa4af">{s:+d}</text>')
    # 0 基准线
    y0 = y_of(0)
    parts.append(f'<line x1="{pad_l}" y1="{y0:.1f}" x2="{pad_l+plot_w}" y2="{y0:.1f}" stroke="#cfd6dd" stroke-dasharray="4 3"/>')
    parts.append(f'<text x="{pad_l-8}" y="{y0+4:.1f}" text-anchor="end" font-size="10" fill="#9aa4af">0</text>')

    # 折线
    pts = [(x_of(i), y_of(r["score"])) for i, r in enumerate(rows)]
    if n > 1:
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        parts.append(f'<path d="{d}" fill="none" stroke="#8a5a2b" stroke-width="2"/>')
    # 数据点（按吉凶配色 + tooltip）
    cls_color = {"hi": "#1e7a3c", "mid": "#9a6b00", "lo": "#c0392b"}
    for i, (x, y) in enumerate(pts):
        r = rows[i]
        col = cls_color.get(r["cls"], "#9a6b00")
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}">'
            f'<title>{r["year"]} {r["gz"]}｜{r["grade"]}（评分 {r["score"]}）</title></circle>'
        )
        if r["is_current"]:
            parts.append(f'<text x="{x:.1f}" y="{y-11:.1f}" text-anchor="middle" font-size="11" font-weight="bold" fill="#8a5a2b">今</text>')
    # x 轴年份标签
    for i, r in enumerate(rows):
        x = x_of(i)
        parts.append(f'<text x="{x:.1f}" y="{pad_t+plot_h+16:.1f}" text-anchor="middle" font-size="10" fill="#6b7785">{str(r["year"])[2:]}</text>')
    # 图例
    parts.append(f'<text x="{pad_l+plot_w}" y="{pad_t-4:.1f}" text-anchor="end" font-size="10" fill="#9aa4af">绿=吉 黄=平 红=凶 · 数值=综合评分</text>')
    parts.append('</svg>')
    return "\n".join(parts)
