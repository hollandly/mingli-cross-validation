# -*- coding: utf-8 -*-
"""Build a single self-contained HTML file for the 天命系统.
Inlines web/lunar.js and web/engines.js, plus the report UI, into one file.
"""
import io, os, base64

WEB = "/Users/linpengchen/WorkBuddy/2026-10-10-13-49-27/MingLi_System/web"
lunar = open(os.path.join(WEB, "lunar.js"), encoding="utf-8").read()
engines = open(os.path.join(WEB, "engines.js"), encoding="utf-8").read()
icon_svg = open(os.path.join(WEB, "icon.svg"), encoding="utf-8").read().strip()
favicon = "data:image/svg+xml;base64," + base64.b64encode(icon_svg.encode("utf-8")).decode("ascii")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>天命系统 · 录入与报告</title>
<link rel="icon" href="__FAVICON__" type="image/svg+xml">
<link rel="apple-touch-icon" href="__FAVICON__">
<style>
  :root{
    --ink:#2b2620; --paper:#f7f2e7; --paper2:#fffdf8; --line:#e3d9c2;
    --gold:#9a6a2f; --gold2:#c08a3e; --red:#b5402f; --green:#2f7d4f;
    --blue:#2f5d8a; --purple:#6b4a8a; --muted:#8a7f6c; --card:#fffefb;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;
    color:var(--ink);background:linear-gradient(180deg,#f3ecdc,#efe6d2);line-height:1.65;}
  .wrap{max-width:1080px;margin:0 auto;padding:22px 18px 80px;}
  header.top{text-align:center;padding:18px 0 6px;}
  .brand{display:inline-flex;align-items:center;justify-content:center;gap:14px;}
  .brand svg{width:54px;height:54px;flex:0 0 auto;filter:drop-shadow(0 3px 9px rgba(120,80,20,.35));}
  .brand-txt{text-align:left;}
  header.top h1{margin:0;font-size:25px;letter-spacing:3px;color:var(--gold);font-weight:700;}
  header.top .sub{color:var(--muted);font-size:13px;margin-top:4px;letter-spacing:1px;}
  .disclaimer{background:#fbf3e0;border:1px solid #ecd9b0;color:#7a6a44;font-size:12px;
    padding:8px 14px;border-radius:8px;margin:12px auto;max-width:880px;text-align:center;}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:18px 20px;margin:16px 0;box-shadow:0 2px 10px rgba(120,90,30,.06);}
  .card h2{margin:0 0 12px;font-size:18px;color:var(--gold);border-left:4px solid var(--gold2);
    padding-left:10px;letter-spacing:1px;}
  .card h3{font-size:15px;color:var(--ink);margin:16px 0 8px;}
  /* form */
  .form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;}
  .field label{display:block;font-size:12px;color:var(--muted);margin-bottom:4px;}
  .field select,.field input{width:100%;padding:8px 10px;border:1px solid var(--line);
    border-radius:8px;background:var(--paper2);font-size:14px;color:var(--ink);}
  .btn{display:inline-block;background:linear-gradient(180deg,var(--gold2),var(--gold));
    color:#fff;border:none;padding:11px 26px;border-radius:10px;font-size:15px;cursor:pointer;
    letter-spacing:2px;box-shadow:0 3px 8px rgba(154,106,47,.3);margin-top:14px;}
  .btn:hover{filter:brightness(1.05)}
  .btn.ghost{background:#fff;color:var(--gold);border:1px solid var(--gold);box-shadow:none;}
  .actions{display:flex;gap:12px;flex-wrap:wrap;align-items:center;}
  /* tables */
  table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0;}
  th,td{border:1px solid var(--line);padding:7px 9px;text-align:center;}
  th{background:#f6ecd6;color:#6b5526;font-weight:600;}
  tr:nth-child(even) td{background:#fbf7ee;}
  .pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600;}
  .hi{background:#e7f3ea;color:var(--green);}
  .mid{background:#f5efdd;color:#9a7a2f;}
  .lo{background:#f7e7e2;color:var(--red);}
  .cons-hi{color:var(--green);font-weight:700;}
  .cons-mid{color:#b07d2f;font-weight:700;}
  .cons-bad{color:var(--red);font-weight:700;}
  .pillar{font-size:20px;letter-spacing:4px;font-weight:700;color:var(--ink);}
  .pillar small{font-size:12px;letter-spacing:0;color:var(--muted);font-weight:400;display:block;margin-top:2px;}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  @media(max-width:720px){.two{grid-template-columns:1fr;}}
  .kv{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;}
  .kv .k{color:var(--muted);}
  .kv .v{font-weight:600;}
  .svgbox{text-align:center;overflow-x:auto;}
  .svgbox svg{max-width:100%;height:auto;}
  .note{font-size:12px;color:var(--muted);margin-top:6px;}
  .flag{background:#fbeee0;border:1px solid #e8c79a;color:#8a5a26;padding:8px 12px;border-radius:8px;
    font-size:13px;margin:6px 0;}
  .grade-banner{text-align:center;font-size:17px;font-weight:700;padding:12px;border-radius:10px;letter-spacing:1px;}
  .grade-hi{background:#e7f3ea;color:var(--green);border:1px solid #bcdcc4;}
  .grade-mid{background:#f6efda;color:#9a7a2f;border:1px solid #e3d2a3;}
  .grade-bad{background:#f8e7e1;color:var(--red);border:1px solid #e6bdae;}
  .hidden{display:none;}
  .star-row{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0;}
  .chip{background:#f4ead3;border:1px solid #e6d4a8;border-radius:6px;padding:2px 8px;font-size:12px;}
  .chip.main{background:#f0d9b0;border-color:#d9b777;font-weight:600;}
  .chip.bad{background:#f7e2dc;border-color:#e8bfb0;color:#a64a36;}
  footer{text-align:center;color:var(--muted);font-size:12px;margin-top:30px;}
  .err{background:#fde7e2;color:#b5402f;border:1px solid #e8b3a6;padding:10px;border-radius:8px;}
  .seg{display:inline-flex;border:1px solid var(--line);border-radius:10px;overflow:hidden;}
  .seg button{border:none;background:var(--paper2);color:var(--muted);padding:8px 20px;font-size:14px;cursor:pointer;letter-spacing:1px;}
  .seg button.active{background:linear-gradient(180deg,var(--gold2),var(--gold));color:#fff;font-weight:600;}
  .seg button:not(:last-child){border-right:1px solid var(--line);}
  .calhint{font-size:12px;color:var(--muted);margin-top:6px;display:block;line-height:1.6;}
  .leapbox{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--ink);padding-top:6px;}
  .leapbox input{width:auto;transform:scale(1.15);}
  .tablescroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:8px 0;}
  .btn.sm{padding:5px 12px;font-size:12px;margin:0;letter-spacing:0;}
  .saved-item{display:flex;align-items:center;gap:10px;padding:9px 2px;border-bottom:1px solid var(--line);}
  .tips{margin:6px 0;padding-left:20px;font-size:13px;line-height:1.85;}
  .tips li{margin:4px 0;}
  details.yearadv{border:1px solid var(--line);border-radius:9px;padding:7px 12px;margin:7px 0;background:var(--paper2);}
  details.yearadv>summary{cursor:pointer;font-weight:600;font-size:13.5px;}
  .yearadv .cat{margin-top:6px;font-size:13px;line-height:1.78;}
  .yearadv .cat b{color:var(--gold);}
  .saved-label{font-size:13px;flex:1;color:var(--ink);}
  /* 相学开关 + 采录 */
  .switch{display:inline-flex;align-items:center;gap:10px;font-size:14px;cursor:pointer;user-select:none;line-height:1.5;}
  .switch input{width:44px;height:23px;appearance:none;-webkit-appearance:none;background:#d9cdb2;border-radius:20px;position:relative;outline:none;cursor:pointer;transition:.2s;flex:0 0 auto;margin:0;}
  .switch input:checked{background:linear-gradient(180deg,var(--gold2),var(--gold));}
  .switch input::after{content:"";position:absolute;top:2px;left:2px;width:19px;height:19px;background:#fff;border-radius:50%;transition:.2s;box-shadow:0 1px 3px rgba(0,0,0,.2);}
  .switch input:checked::after{left:23px;}
  .cam-row{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start;margin-top:10px;}
  .cam-row video,.cam-row canvas{max-width:260px;max-height:260px;border:1px solid var(--line);border-radius:10px;background:#222;}
  .cam-btns{display:flex;flex-direction:column;gap:8px;}
  .tonebox{margin-top:10px;padding:8px 12px;background:#f3ecd6;border:1px solid #e3d2a3;border-radius:8px;font-size:13px;color:#6b5526;}
  .obs-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;}
  @media(max-width:720px){.obs-grid{grid-template-columns:1fr;}}
  .obs{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:0;}
  .obs legend{font-size:13px;color:var(--gold);font-weight:600;padding:0 6px;}
  .obs .chkrow{display:flex;flex-wrap:wrap;gap:10px;font-size:13px;}
  .obs .chkrow label{display:flex;align-items:center;gap:4px;}
  @media(max-width:600px){
    .wrap{padding:14px 10px 60px;}
    header.top h1{font-size:20px;letter-spacing:2px;}
    .form-grid{grid-template-columns:1fr 1fr;}
    .field select,.field input{padding:10px;font-size:15px;}
    .btn{width:100%;padding:13px;font-size:16px;}
    .btn.ghost{width:auto;padding:9px 16px;}
    .card{padding:14px 14px;margin:12px 0;}
    .pillar{font-size:17px;letter-spacing:2px;}
    table{font-size:12px;}
    th,td{padding:5px 6px;}
    .two{gap:10px;}
    .kv{font-size:12px;}
  }
  /* 人生行动指南（核心） */
  .win-banner{text-align:center;font-size:16px;font-weight:700;padding:12px;border-radius:10px;letter-spacing:1px;}
  .window-why{font-size:13px;color:var(--muted);margin-top:8px;line-height:1.85;text-align:left;}
  .act-h{font-size:15px;margin:16px 0 7px;font-weight:600;color:var(--ink);}
  .act-list{list-style:none;margin:4px 0;padding:0;}
  .act-list li{position:relative;padding:7px 12px 7px 34px;margin:6px 0;border-radius:9px;font-size:13.5px;line-height:1.7;}
  .act-do li{background:#eef6f0;border:1px solid #cfe4d6;}
  .act-do li::before{content:"✓";position:absolute;left:11px;top:7px;color:var(--green);font-weight:700;}
  .act-dont li{background:#fbeee9;border:1px solid #eccabf;}
  .act-dont li::before{content:"✕";position:absolute;left:12px;top:7px;color:var(--red);font-weight:700;}
  .act-watch li{background:#fbf3df;border:1px solid #ecd9a8;}
  .act-watch li::before{content:"!";position:absolute;left:13px;top:6px;color:#b07d2f;font-weight:700;}
  .decz{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px;}
  @media(max-width:720px){.decz{grid-template-columns:1fr;}}
  .dec{border:1px solid var(--line);border-radius:10px;padding:9px 12px;background:var(--paper2);}
  .dec .dn{font-weight:600;font-size:13.5px;}
  .dec .dt{font-size:12.5px;color:var(--muted);margin-top:3px;line-height:1.6;}
  .lt{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;vertical-align:middle;}
  .lt.green{background:var(--green);} .lt.amber{background:#d9a521;} .lt.red{background:var(--red);}
  /* 能量节奏 · 精确时间段 */
  .phase-best{background:linear-gradient(180deg,#fff7e6,#fdeecb);border:1px solid #e9c878;border-radius:12px;padding:12px 14px;margin:6px 0 10px;}
  .phase-best .pb-t{font-size:15px;font-weight:700;color:#9a6b00;}
  .phase-best .pb-sub{font-size:12.5px;color:#a9791f;margin:3px 0 6px;}
  .yr{display:inline-block;border-radius:8px;padding:3px 8px;font-size:12.5px;margin:3px 6px 3px 0;font-weight:600;}
  .yr.atk{background:#eef6f0;border:1px solid #cfe4d6;color:#1f7a3d;}
  .yr.def{background:#fbeee9;border:1px solid #eccabf;color:#b83b22;}
  .tl-title{font-size:12.5px;color:var(--muted);margin:12px 0 6px;}
  .tl{display:flex;flex-wrap:wrap;gap:7px;}
  .tl-chip{display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:58px;padding:6px 4px;border-radius:9px;font-size:13px;font-weight:700;line-height:1.25;border:1px solid var(--line);background:var(--paper2);}
  .tl-chip small{font-size:10px;font-weight:400;color:var(--muted);margin-top:2px;}
  .tl-chip.atk{background:#eef6f0;border-color:#cfe4d6;color:#1f7a3d;}
  .tl-chip.def{background:#fbeee9;border-color:#eccabf;color:#b83b22;}
  .tl-chip.mid{background:#fbf3df;border-color:#ecd9a8;color:#9a6b00;}
  @media print{
    .disclaimer,.card#formCard,.card#savedCard,.card#xiangCard,.actions,.note,.btn,#errBox{display:none!important;}
    body{background:#fff;color:#000;}
    .wrap{max-width:none;padding:0;}
    .card{box-shadow:none;border:1px solid #ccc;margin:10px 0;page-break-inside:avoid;}
    .svgbox svg{max-width:100%;height:auto;}
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      __ICON__
      <div class="brand-txt">
        <h1>天命系统</h1>
        <div class="sub">四柱八字 · 紫微斗数 · 周易梅花易数 · 铁板神数 ｜ 多维交叉验证（含面相 / 手相）</div>
      </div>
    </div>
  </header>
  <div class="disclaimer">
    本系统用于传统文化研究、自我认知与性格参考，<b>不构成任何医疗、投资、法律或人生的决策建议</b>。
    命理之说，信则有参考，不信则作闲谈；请以理性与科学态度看待。
  </div>

  <!-- 录入表单 -->
  <div class="card" id="formCard">
    <h2>录入出生信息</h2>
    <div class="field" style="grid-column:1/-1">
      <label>历法（默认农历，更贴合传统生辰报法）</label>
      <div class="seg" id="f_cal">
        <button type="button" data-cal="农历" class="active">农历</button>
        <button type="button" data-cal="阳历">阳历</button>
      </div>
      <span class="calhint" id="calHint">中国人多按农历报生辰；系统会自动换算成阳历，并按出生地校正「真太阳时」后再定四柱。</span>
    </div>
    <div class="field" style="grid-column:1/-1">
      <label class="switch"><input type="checkbox" id="f_xiang"> <span>开启相学分析（面相 / 手相）· 需要时勾选，<b>本地运算、照片不上传</b>（关闭则不占版面）</span></label>
    </div>
    <div class="form-grid">
      <div class="field"><label id="lbl_year">出生年份（农历）</label><select id="f_year"></select></div>
      <div class="field"><label id="lbl_month">月份（农历）</label><select id="f_month"></select></div>
      <div class="field"><label id="lbl_day">日期（农历）</label><select id="f_day"></select></div>
      <div class="field" id="wrap_shichen"><label>出生时辰</label><select id="f_shichen"></select></div>
      <div class="field hidden" id="wrap_hour"><label>出生时（24小时制）</label><select id="f_hour"></select></div>
      <div class="field"><label>分钟</label><select id="f_minute"></select></div>
      <div class="field hidden" id="wrap_leap"><label>是否闰月</label>
        <div class="leapbox"><input type="checkbox" id="f_leap"><label for="f_leap" style="margin:0">出生在闰月（如闰四月）</label></div></div>
      <div class="field"><label>性别</label>
        <select id="f_gender"><option value="男">男</option><option value="女">女</option></select></div>
      <div class="field"><label>出生地（用于真太阳时校正）</label><select id="f_city"></select></div>
    </div>
    <div class="actions">
      <button class="btn" id="btnRun">生成命理报告</button>
      <button class="btn ghost" id="btnDemo">看示例</button>
      <span class="note">提示：出生地越精确，真太阳时校正越准。农历生日请确认是否闰月，以免影响换算。</span>
    </div>
    <div id="errBox"></div>
  </div>

  <!-- 相学采录 -->
  <div class="card hidden" id="xiangCard">
    <h2>相学采录（面相 / 手相）</h2>
    <div class="note">照片仅在本地浏览器处理与绘制，<b>不会上传任何服务器</b>。面相/手相为辅助维度，须与命理四体系互参，结论不单独作断。</div>
    <div class="field" style="grid-column:1/-1">
      <label>照片类型（先选类型，再拍照 / 上传）</label>
      <div class="seg" id="f_xtype">
        <button type="button" data-xt="face" class="active">面相</button>
        <button type="button" data-xt="palm">手相</button>
      </div>
    </div>
    <div class="cam-row">
      <video id="cam" autoplay playsinline muted></video>
      <canvas id="camCanvas" class="hidden"></canvas>
      <div class="cam-btns">
        <button class="btn" id="btnCamOn">开启摄像头</button>
        <button class="btn ghost" id="btnCap">拍照</button>
        <label class="btn ghost">上传照片<input type="file" id="fileIn" accept="image/*" hidden></label>
      </div>
    </div>
    <div class="tonebox" id="toneBox">气色判定：待采集（先选上方「照片类型」，再拍照或上传）</div>
    <div class="note" style="margin-top:8px;line-height:1.8">
      <b>气色五行判定原理（浏览器本地计算 · 照片绝不上传）：</b>系统把照片缩为 40×40 采样，取平均 RGB 判定<b>主色</b>与<b>明亮度</b>，再按传统相学「五色配五行」映射为佐证之气——
      <span style="color:var(--red)">红=火</span>、<span style="color:var(--gold,#b8860b)">白=金</span>、<span style="color:var(--green)">青=木</span>、<span style="color:var(--blue,#2f6fdb)">黑=水</span>、<span style="color:var(--brown,#8a5a2b)">黄=土</span>；
      明亮度高=气色清朗、低=气色偏沉。此为<b>客观像素佐证</b>，须与您观察勾选的五官/掌纹特征、以及命理四柱互参，<b>不作医疗或命运定论</b>。
    </div>
    <div class="obs-grid">
      <fieldset class="obs"><legend>面相采录（看着照片勾选）</legend>
        <div class="field"><label>面型</label><select id="xf_mianxing"><option value="">—</option><option>圆润·水</option><option>方正·金</option><option>修长·木</option><option>上尖下阔·火</option><option>厚宽·土</option></select></div>
        <div class="field"><label>上停(额)</label><select id="xf_shangting"><option value="">—</option><option>饱满</option><option>平</option><option>窄陷</option></select></div>
        <div class="field"><label>中停(鼻)</label><select id="xf_zhongting"><option value="">—</option><option>鼻丰</option><option>平</option><option>鼻陷</option></select></div>
        <div class="field"><label>下停(颔)</label><select id="xf_xiating"><option value="">—</option><option>方圆</option><option>平</option><option>尖削</option></select></div>
        <div class="field"><label>耳(肾/水)</label><select id="xf_er"><option value="">—</option><option>佳</option><option>平</option><option>弱</option></select></div>
        <div class="field"><label>眉(肝/木)</label><select id="xf_mei"><option value="">—</option><option>佳</option><option>平</option><option>弱</option></select></div>
        <div class="field"><label>眼(心/火)</label><select id="xf_yan"><option value="">—</option><option>佳</option><option>平</option><option>弱</option></select></div>
        <div class="field"><label>鼻(脾/土)</label><select id="xf_bi"><option value="">—</option><option>佳</option><option>平</option><option>弱</option></select></div>
        <div class="field"><label>口(肺/金)</label><select id="xf_kou"><option value="">—</option><option>佳</option><option>平</option><option>弱</option></select></div>
        <div class="field"><label>气色(自感)</label><select id="xf_qise"><option value="">—</option><option>红润</option><option>黄润</option><option>青暗</option><option>苍白</option><option>晦暗</option></select></div>
        <div class="field" style="grid-column:1/-1"><label>痣 / 纹（可多选）</label>
          <div class="chkrow">
            <label><input type="checkbox" class="xf_zhiwen" value="奸门(眼尾)痣/纹"> 奸门痣纹</label>
            <label><input type="checkbox" class="xf_zhiwen" value="法令清晰"> 法令清晰</label>
            <label><input type="checkbox" class="xf_zhiwen" value="印堂窄/纹乱"> 印堂窄乱</label>
            <label><input type="checkbox" class="xf_zhiwen" value="人中有痣/陷"> 人中有痣/陷</label>
          </div>
        </div>
      </fieldset>
      <fieldset class="obs"><legend>手相采录（看着照片勾选）</legend>
        <div class="field"><label>掌型</label><select id="xp_palmxing"><option value="">—</option><option>金型·方硬</option><option>木型·修长</option><option>水型·圆润</option><option>火型·尖削</option><option>土型·厚实</option></select></div>
        <div class="field"><label>生命线</label><select id="xp_life"><option value="">—</option><option>深长清晰</option><option>平</option><option>浅短</option><option>中断/岛纹</option></select></div>
        <div class="field"><label>智慧线</label><select id="xp_wisdom"><option value="">—</option><option>长而清晰</option><option>平</option><option>短而乱</option></select></div>
        <div class="field"><label>感情线</label><select id="xp_emotion"><option value="">—</option><option>清晰无杂</option><option>平</option><option>断裂/杂纹多</option></select></div>
        <div class="field"><label>财运线</label><select id="xp_wealth"><option value="">—</option><option>清晰</option><option>平</option><option>不明显</option></select></div>
        <div class="field"><label>手指</label><select id="xp_finger"><option value="">—</option><option>修长</option><option>平</option><option>短粗</option></select></div>
        <div class="field"><label>掌色(自感)</label><select id="xp_pcolor"><option value="">—</option><option>红润</option><option>平</option><option>青白</option></select></div>
      </fieldset>
    </div>
  </div>

  <!-- 我的排盘 -->
  <div class="card hidden" id="savedCard">
    <h2>我的排盘（本地保存，不上传）</h2>
    <div id="savedList"></div>
    <div class="actions"><button class="btn ghost" id="btnClearSaved">清空记录</button>
      <span class="note">记录只存在你这台设备的浏览器里，换设备或清缓存会丢失。</span></div>
  </div>

  <!-- 报告容器 -->
  <div id="report" class="hidden"></div>

  <footer>天命系统 · 纯浏览器本地运算（数据不上传）· 传统文化研究工具 ｜ 著作人 <b>hollandly</b></footer>
</div>

<!-- ============ 历法底层 ============ -->
<script><<<LUNAR_JS>>></script>
<!-- ============ 命理引擎 ============ -->
<script><<<ENGINES_JS>>></script>

<!-- ============ 报告渲染 ============ -->
<script>
(function(){
  "use strict";
  var ML = window.ML;
  var ZH = ["正月","二月","三月","四月","五月","六月","七月","八月","九月","十月","冬月","腊月"];
  var SHICHEN = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"];
  var SHICHEN_HOUR = {"子":0,"丑":2,"寅":4,"卯":6,"辰":8,"巳":10,"午":12,"未":14,"申":16,"酉":18,"戌":20,"亥":22};
  var calMode = "农历";
  // ---- 初始化表单 ----
  function fill(sel, items, val){ var el=document.getElementById(sel); items.forEach(function(it){
    var o=document.createElement("option"); o.value=it.v!=null?it.v:it; o.text=it.t!=null?it.t:it;
    if(val!=null && o.value===String(val)) o.selected=true; el.appendChild(o);});}
  (function(){
    var yrs=[]; for(var y=1925;y<=new Date().getFullYear();y++) yrs.push({v:y,t:y+"年"}); fill("f_year",yrs,1990);
    var ds=[]; for(var d=1;d<=31;d++) ds.push({v:d,t:d+"日"}); fill("f_day",ds,27);
    var hs=[]; for(var h=0;h<24;h++) hs.push({v:h,t:(h<10?"0"+h:h)+"时"}); fill("f_hour",hs,12);
    var mis=[]; for(var mi=0;mi<60;mi+=5) mis.push({v:mi,t:(mi<10?"0"+mi:mi)+"分"}); fill("f_minute",mis,0);
    var shs=[]; for(var i=0;i<12;i++){ var sc=SHICHEN[i]; shs.push({v:sc,t:sc+"时"}); } fill("f_shichen",shs,"午");
    var cities=Object.keys(ML.C.CITY_LONGITUDE).map(function(c){return {v:c,t:c};});
    fill("f_city",cities,"北京");
    fillMonth(true);
    document.getElementById("f_month").value=4;
  })();

  function fillMonth(lunar){
    var sel=document.getElementById("f_month"); sel.innerHTML="";
    var mos=[]; for(var m=1;m<=12;m++) mos.push({v:m,t:lunar?ZH[m-1]:(m+"月")}); fill("f_month",mos,4);
  }
  function applyCalMode(){
    var lunar = calMode==="农历";
    document.getElementById("wrap_shichen").classList.toggle("hidden", !lunar);
    document.getElementById("wrap_hour").classList.toggle("hidden", lunar);
    document.getElementById("wrap_leap").classList.toggle("hidden", !lunar);
    document.getElementById("lbl_year").textContent = lunar ? "出生年份（农历）" : "出生年份（阳历）";
    document.getElementById("lbl_month").textContent = lunar ? "月份（农历）" : "月份（阳历）";
    document.getElementById("lbl_day").textContent = lunar ? "日期（农历）" : "日期（阳历）";
    fillMonth(lunar);
    document.getElementById("calHint").textContent = lunar
      ? "中国人多按农历报生辰；系统会自动换算成阳历，并按出生地校正「真太阳时」后再定四柱。"
      : "系统将直接按阳历生日校正真太阳时后定四柱。";
  }
  document.querySelectorAll("#f_cal button").forEach(function(btn){
    btn.addEventListener("click",function(){
      calMode = btn.getAttribute("data-cal");
      document.querySelectorAll("#f_cal button").forEach(function(b){ b.classList.toggle("active", b===btn); });
      applyCalMode();
    });
  });
  applyCalMode();

  // ---- 相学：开关 / 摄像头 / 上传 / 像素气色 ----
  var xiState = { face: null, palm: null };
  var xiType = "face";
  document.querySelectorAll("#f_xtype button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      xiType = btn.getAttribute("data-xt");
      document.querySelectorAll("#f_xtype button").forEach(function (b) { b.classList.toggle("active", b === btn); });
    });
  });
  document.getElementById("f_xiang").addEventListener("change", function () {
    document.getElementById("xiangCard").classList.toggle("hidden", !this.checked);
  });
  function classifyTone(imgData) {
    var d = imgData.data, n = d.length / 4, r = 0, g = 0, b = 0;
    for (var i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
    r /= n; g /= n; b /= n;
    var bright = (r + g + b) / (3 * 255);
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), sat = (mx - mn) / 255;
    var tone;
    if (bright < 0.28) tone = "黑·水";
    else if (bright > 0.82 && sat < 0.14) tone = "白·金";
    else if (r >= g && r >= b && (r - b) > 18) tone = "红·火";
    else if (g >= r && g >= b && (g - b) > 18) tone = "青·木";
    else tone = "黄·土";
    return { tone: tone, brightness: bright };
  }
  function ingestCanvas(canvas) {
    var s = document.createElement("canvas"); s.width = 40; s.height = 40;
    s.getContext("2d").drawImage(canvas, 0, 0, 40, 40);
    var id = s.getContext("2d").getImageData(0, 0, 40, 40);
    var tone = classifyTone(id);
    var dataURL = canvas.toDataURL("image/jpeg", 0.72);
    xiState[xiType] = { px: tone, img: dataURL };
    var name = xiType === "face" ? "面相" : "手相";
    document.getElementById("toneBox").innerHTML = "【自动·像素气色】当前「" + name + "」照片：主色偏 <b>" + tone.tone + "</b>，明亮度 " + (tone.brightness * 100).toFixed(0) + "%。如需调整可重新拍照 / 上传。";
  }
  var camStream = null;
  document.getElementById("btnCamOn").addEventListener("click", function () {
    if (camStream) { camStream.getTracks().forEach(function (t) { t.stop(); }); camStream = null; this.textContent = "开启摄像头"; return; }
    var v = document.getElementById("cam"), self = this;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { alert("当前浏览器不支持摄像头，请改用「上传照片」。"); return; }
    navigator.mediaDevices.getUserMedia({ video: true }).then(function (s) {
      camStream = s; v.srcObject = s; self.textContent = "关闭摄像头";
    }).catch(function (e) { alert("无法开启摄像头：" + (e.message || e) + "（可改用「上传照片」）"); });
  });
  document.getElementById("btnCap").addEventListener("click", function () {
    var v = document.getElementById("cam"), c = document.getElementById("camCanvas");
    if (!v.videoWidth) { alert("请先开启摄像头。"); return; }
    c.width = v.videoWidth; c.height = v.videoHeight; c.getContext("2d").drawImage(v, 0, 0);
    ingestCanvas(c);
  });
  document.getElementById("fileIn").addEventListener("change", function (e) {
    var f = e.target.files && e.target.files[0]; if (!f) return;
    var img = new Image();
    img.onload = function () {
      var c = document.getElementById("camCanvas"); c.width = img.width; c.height = img.height;
      c.getContext("2d").drawImage(img, 0, 0); ingestCanvas(c);
    };
    img.src = URL.createObjectURL(f);
  });
  function val(id) { var e = document.getElementById(id); return e ? e.value : ""; }
  function collectFace() {
    var zhiwen = []; document.querySelectorAll(".xf_zhiwen:checked").forEach(function (c) { zhiwen.push(c.value); });
    return {
      mianxing: val("xf_mianxing"), shangting: val("xf_shangting"), zhongting: val("xf_zhongting"), xiating: val("xf_xiating"),
      wuguan: { er: val("xf_er"), mei: val("xf_mei"), yan: val("xf_yan"), bi: val("xf_bi"), kou: val("xf_kou") },
      qise: val("xf_qise"), zhiwen: zhiwen
    };
  }
  function collectPalm() {
    return { palmxing: val("xp_palmxing"), life: val("xp_life"), wisdom: val("xp_wisdom"), emotion: val("xp_emotion"), wealth: val("xp_wealth"), finger: val("xp_finger"), pcolor: val("xp_pcolor") };
  }
  function anyObs(o) {
    if (!o) return false;
    for (var k in o) {
      if (k === "wuguan") { for (var k2 in o.wuguan) if (o.wuguan[k2]) return true; }
      else if (Array.isArray(o[k])) { if (o[k].length) return true; }
      else if (o[k]) return true;
    }
    return false;
  }

  function esc(s){ return String(s==null?"":s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];}); }
  function gz(g){ return g[0]+g[1]; }
  function clsOf(g){ return g==="吉"||g==="平偏吉"?"hi":(g==="平"?"mid":"lo"); }

  // ---- 渲染 ----
  function render(ctx){
    var b=ctx.bazi, z=ctx.ziwei, yj=ctx.yijing, tb=ctx.tieban, cv=ctx.cv, liu=ctx.liunian, geo=ctx.geo, ap=ctx.action_playbook;
    var H=[];
    H.push('<div class="card"><h2>一、基本信息与真太阳时校正</h2>');
    H.push('<div class="kv">');
    var bi=ctx.birth_input;
    if(bi.calendar==="农历"){
      H.push('<span class="k">录入（农历）：</span><span class="v">'+bi.ly+'年 '+ZH[bi.lmo-1]+(bi.lleap?"（闰）":"")+' '+bi.ld+'日 '+bi.lshichen+' · '+bi.gender+' · '+esc(bi.birthplace)+'</span>');
      H.push('</div><div class="kv">');
      H.push('<span class="k">对应阳历：</span><span class="v">'+bi.sy+'年'+bi.smo+'月'+bi.sd+'日 '+bi.sh+'时'+bi.smi+'分</span>');
    } else {
      H.push('<span class="k">录入（阳历）：</span><span class="v">'+bi.year+'年'+bi.month+'月'+bi.day+'日 '+bi.hour+'时'+bi.minute+'分 · '+bi.gender+' · '+esc(bi.birthplace)+'</span>');
    }
    H.push('</div>');
    H.push('<div class="kv">');
    H.push('<span class="k">真太阳时校正：</span><span class="v">'+geo.shichen_before+' → '+geo.shichen_after+(geo.shichen_changed?'（<b style="color:var(--red)">时辰已变，按校正后定盘</b>':'（时辰不变）')+'</span>');
    H.push('<span class="k">经度：</span><span class="v">'+geo.longitude+'°</span>');
    H.push('<span class="k">时差(真太阳时)：</span><span class="v">'+geo.delta_h+' 小时</span>');
    H.push('<span class="k">均时差EoT：</span><span class="v">'+geo.eot+' 分</span>');
    H.push('</div>');
    H.push('<div class="note">校正后阳历生日：'+geo.solar_birth.getFullYear()+'年'+(geo.solar_birth.getMonth()+1)+'月'+geo.solar_birth.getDate()+'日 '+geo.solar_birth.getHours()+'时'+geo.solar_birth.getMinutes()+'分</div>');
    H.push('</div>');

    // 四柱
    H.push('<div class="card"><h2>二、四柱八字</h2>');
    H.push('<div class="two"><div>');
    var fp=b.four_pillars;
    H.push('<table><tr><th>柱</th><th>干支</th><th>纳音</th><th>十神</th></tr>');
    [["年柱",fp.year],["月柱",fp.month],["日柱",fp.day],["时柱",fp.hour]].forEach(function(r){
      H.push('<tr><td>'+r[0]+'</td><td class="pillar">'+gz(r[1].gz)+'</td><td>'+esc(r[1].nayin)+'</td><td>'+esc(r[1].shi_shen)+'</td></tr>');
    });
    H.push('</table></div><div>');
    var strongColor = b.strength==="身旺"?"var(--red)":(b.strength==="身弱"?"var(--blue)":"var(--green)");
    H.push('<div class="kv"><span class="k">日主：</span><span class="v">'+b.day_master+'（'+b.day_element+'）</span>');
    H.push('<span class="k">旺衰：</span><span class="v" style="color:'+strongColor+'">'+b.strength+'</span>');
    H.push('<span class="k">生肖：</span><span class="v">'+esc(b.zodiac)+'</span></div>');
    H.push('<div class="kv"><span class="k">生扶/克泄：</span><span class="v">'+b.support+' / '+b.drain+'</span>');
    H.push('<span class="k">起运：</span><span class="v">约 '+b.dayun_start_age+' 岁</span>');
    H.push('<span class="k">大运顺逆：</span><span class="v">'+(b.dayun_forward?'顺行':'逆行')+'</span></div>');
    H.push('<h3>大运走势</h3><table><tr><th>步</th><th>干支</th><th>纳音</th><th>起运岁</th><th>交运岁</th></tr>');
    b.dayun.forEach(function(d){ H.push('<tr><td>'+d.step+'</td><td class="pillar" style="font-size:16px">'+gz(d.gz)+'</td><td>'+esc(d.nayin)+'</td><td>'+d.start_age+'</td><td>'+d.end_age+'</td></tr>'); });
    H.push('</table>');
    H.push('</div></div>');
    H.push('<div class="two"><div class="svgbox">'+ctx.radar_wuxing+'<div class="note">五行分布雷达</div></div>');
    H.push('<div class="svgbox">'+ctx.radar_shi_shen+'<div class="note">十神分布雷达</div></div></div>');
    H.push('</div>');

    // 紫微
    H.push('<div class="card"><h2>三、紫微斗数</h2>');
    H.push('<div class="kv"><span class="k">命宫：</span><span class="v">'+z.mingong_zhi+'宫（'+z.mingong_gz+'）</span>');
    H.push('<span class="k">五行局：</span><span class="v">'+esc(z.ju)+'</span>');
    H.push('<span class="k">命宫主星：</span><span class="v">'+esc(z.main_star)+'</span>');
    H.push('<span class="k">命宫生年四化：</span><span class="v">禄'+z.sihua["禄"]+' 权'+z.sihua["权"]+' 科'+z.sihua["科"]+' 忌'+z.sihua["忌"]+'</span></div>');
    H.push('<div class="svgbox">'+ctx.ziwei_svg+'</div>');
    H.push('<div class="two" style="margin-top:10px"><div><h3>三方四正</h3><div class="star-row">');
    z.sanfang_sizheng.forEach(function(s){ H.push('<span class="chip main">'+esc(s)+'</span>'); });
    H.push('</div></div><div><h3>十二宫主星概览</h3><div class="star-row">');
    z.palaces.forEach(function(p){ if(p.stars.length) H.push('<span class="chip main">'+esc(p.palace)+'：'+esc(p.stars.join(""))+'</span>'); });
    H.push('</div></div></div>');
    H.push('</div>');

    // 周易
    H.push('<div class="card"><h2>四、周易梅花易数</h2>');
    H.push('<div class="two"><div>');
    H.push('<div class="kv"><span class="k">本卦：</span><span class="v" style="font-size:16px">'+esc(yj.ben_gua)+'</span>');
    H.push('<span class="k">变卦：</span><span class="v" style="font-size:16px">'+esc(yj.bian_gua)+'</span>');
    H.push('<span class="k">动爻：</span><span class="v">第 '+yj.dong_yao+' 爻</span></div>');
    H.push('<div class="kv"><span class="k">上卦：</span><span class="v">'+yj.up_gua+'</span><span class="k">下卦：</span><span class="v">'+yj.lo_gua+'</span>');
    H.push('<span class="k">卦属五行：</span><span class="v">'+esc(yj.gua_elem)+'</span><span class="k">卦性：</span><span class="v">'+esc(yj.gua_nature)+'</span></div>');
    H.push('</div><div>');
    H.push('<div class="note" style="font-size:13px">'+esc(yj.meaning)+'</div>');
    H.push('</div></div></div>');

    // 铁板
    H.push('<div class="card"><h2>五、铁板神数（考时条文）</h2>');
    H.push('<div class="note">铁板以干支化数推演六亲条文，可作为「时辰考据」的互证线索（非定数，仅供研究）。</div>');
    H.push('<table><tr><th>维度</th><th>铁板数</th><th>推演</th><th>考时印证</th></tr>');
    tb.tiaowen.forEach(function(t){ H.push('<tr><td>'+esc(t.dimension)+'</td><td class="pillar" style="font-size:16px">'+esc(t.number)+'</td><td style="text-align:left">'+esc(t.text)+'</td><td style="text-align:left;color:var(--muted)">'+esc(t.verify)+'</td></tr>'); });
    H.push('</table></div>');

    // 相学分析（面相 / 手相）
    if(ctx.face || ctx.palm){
      H.push('<div class="card"><h2>相学分析（面相 / 手相）</h2>');
      H.push('<div class="note">相学为<b>辅助维度</b>：照片「气色五行」由浏览器<b>本地像素</b>自动判定（红=火 / 白=金 / 青=木 / 黑=水 / 黄=土，照片绝不上传），面相/手相特征由您对照照片勾选；所有信号须与命理四柱/紫微/易/铁板<b>互参</b>，不单独作断，亦非医疗诊断。</div>');
      H.push('<div class="two">');
      if(ctx.face){
        H.push('<div><h3>面相照片</h3>'+(ctx.face.img?'<img src="'+ctx.face.img+'" style="max-width:100%;border:1px solid var(--line);border-radius:10px">':'<div class="note">（未拍照，仅按勾选特征）</div>'));
        H.push('<div class="tonebox" style="margin-top:8px">'+(ctx.face.px?('自动气色：'+ctx.face.px.tone+'（红=火/白=金/青=木/黑=水/黄=土），明亮度 '+(ctx.face.px.brightness*100).toFixed(0)+'% —— 浏览器本地像素判定，照片未上传'):'未采集照片（无自动气色，可按勾选特征推算）')+'</div></div>');
      }
      if(ctx.palm){
        H.push('<div><h3>手相照片</h3>'+(ctx.palm.img?'<img src="'+ctx.palm.img+'" style="max-width:100%;border:1px solid var(--line);border-radius:10px">':'<div class="note">（未拍照，仅按勾选特征）</div>'));
        H.push('<div class="tonebox" style="margin-top:8px">'+(ctx.palm.px?('自动气色：'+ctx.palm.px.tone+'（红=火/白=金/青=木/黑=水/黄=土），明亮度 '+(ctx.palm.px.brightness*100).toFixed(0)+'% —— 浏览器本地像素判定，照片未上传'):'未采集照片（无自动气色，可按勾选特征推算）')+'</div></div>');
      }
      H.push('</div>');
      var DIMS7=["性格","事业","财运","婚姻","家庭(六亲)","健康","时机运势"];
      H.push('<h3>面相 / 手相 维度信号（含判定依据）</h3>');
      H.push('<table><tr><th>维度</th><th>面相判定</th><th>手相判定</th></tr>');
      DIMS7.forEach(function(dim){
        var f=ctx.face?ctx.face.signals[dim]:null, p=ctx.palm?ctx.palm.signals[dim]:null;
        function sigCell(s){ return s?esc(s[0])+' <span class="pill '+(s[1]>=4?'hi':(s[1]>=3?'mid':'lo'))+'">'+s[1].toFixed(1)+'</span>':'—'; }
        H.push('<tr><td><b>'+dim+'</b></td><td style="text-align:left">'+sigCell(f)+'</td><td style="text-align:left">'+sigCell(p)+'</td></tr>');
      });
      H.push('</table>');
      H.push('<div class="note">面相/手相信号已并入下方「多维交叉验证」，与各命理体系共同判定一致性。</div>');
      H.push('</div>');
    }

    // 命格综合论断（各体系归一）· 用神指引
    H.push('<div class="card"><h2>命格综合论断 · 用神指引（各体系归一）</h2>');
    var mg = ctx.mingge;
    H.push('<div class="grade-banner grade-mid" style="text-align:left;font-size:14px;font-weight:500;line-height:1.95;color:var(--ink)">' + esc(mg.paragraph) + '</div>');
    H.push('<div class="kv" style="margin-top:10px">');
    H.push('<span class="k">日主：</span><span class="v">' + b.day_master + '（' + b.day_element + '）' + b.strength + '</span>');
    H.push('<span class="k">喜用神：</span><span class="v" style="color:var(--green)">' + esc(mg.xi_text) + '</span>');
    H.push('<span class="k">忌神：</span><span class="v" style="color:var(--red)">' + esc(mg.ji_text) + '</span>');
    H.push('<span class="k">格局：</span><span class="v">' + esc(mg.pattern) + '</span></div>');
    H.push('<h3>用神人生映射（方位 / 行业 / 助运色 / 调候）</h3>');
    H.push('<table><tr><th>用神五行</th><th>利方位</th><th>行业倾向</th><th>助运色</th><th>日常调候</th></tr>');
    ctx.yongshen.rows.forEach(function (r) {
      H.push('<tr><td><b>' + esc(r.element) + '</b></td><td>' + esc(r.dir) + '</td><td style="text-align:left">' + esc(r.ind) + '</td><td>' + esc(r.col) + '</td><td style="text-align:left">' + esc(r.tiao) + '</td></tr>');
    });
    H.push('</table>');
    H.push('<details class="yearadv" style="margin-top:10px"><summary>推算依据（关键原始数据，供复核）</summary><div class="cat">');
    H.push('<div><b>四柱：</b>' + gz(fp.year.gz) + ' ' + gz(fp.month.gz) + ' ' + gz(fp.day.gz) + ' ' + gz(fp.hour.gz) + '</div>');
    H.push('<div><b>五行分布：</b>' + ML.C.ELEMENTS.map(function (e) { return e + ' ' + b.element_count[e]; }).join('、') + '</div>');
    H.push('<div><b>日主旺衰：</b>' + b.strength + '（生扶 ' + b.support + ' / 克泄 ' + b.drain + '）｜起运 ' + b.dayun_start_age + ' 岁</div>');
    H.push('<div><b>紫微命宫主星：</b>' + esc(z.main_star) + '｜生年四化 禄' + z.sihua["禄"] + ' 权' + z.sihua["权"] + ' 科' + z.sihua["科"] + ' 忌' + z.sihua["忌"] + '</div>');
    H.push('<div><b>周易：</b>本卦 ' + esc(yj.ben_gua) + ' · 变卦 ' + esc(yj.bian_gua) + ' · 动爻第' + yj.dong_yao + '爻</div>');
    H.push('<div><b>铁板考时数：</b>' + tb.tiaowen.map(function (t) { return t.dimension + t.number; }).join('、') + '</div>');
    H.push('<div><b>交叉验证：</b>高一致 ' + cv.cons_counts["高一致"] + ' · 中一致 ' + cv.cons_counts["中一致"] + ' · 分歧 ' + cv.cons_counts["分歧"] + '</div>');
    H.push('</div></details>');
    H.push('<div class="note">命格论断由命理各体系（含相学若开启）原始信号归纳而成，供自我认知与研究参考，非宿命判定。</div>');
    H.push('</div>');

    // 流年
    H.push('<div class="card"><h2>六、流年详批（'+liu.rows[0].year+'–'+liu.rows[liu.rows.length-1].year+'）</h2>');
    H.push('<div class="svgbox">'+ctx.liunian_sihua+'<div class="note">流年命宫四化盘（禄/权/科/忌 落宫）</div></div>');
    H.push('<div class="svgbox">'+ctx.fortune_svg+'<div class="note">运势评分折线（当前年居中）</div></div>');
    H.push('<table><tr><th>年份</th><th>岁</th><th>流年</th><th>纳音</th><th>十神</th><th>大运</th><th>流年命宫</th><th>四化</th><th>评分</th><th>等级</th><th>建议</th></tr>');
    liu.rows.forEach(function(r){
      var sihuaTxt=Object.keys(r.sihua).map(function(k){return k+r.sihua[k];}).join(" ");
      H.push('<tr'+(r.is_current?' style="background:#fff7e0"':'')+'><td>'+(r.is_current?'<b>'+r.year+'★</b>':r.year)+'</td><td>'+r.age+'</td><td class="pillar" style="font-size:15px">'+gz(r.gz)+'</td><td>'+esc(r.nayin)+'</td><td>'+esc(r.shi_shen)+'</td><td>'+(r.dayun_gz==="—"?"—":gz(r.dayun_gz))+'</td><td>'+esc(r.flow_palace)+'</td><td>'+(sihuaTxt||"—")+'</td><td>'+r.score+'</td><td><span class="pill '+clsOf(r.grade)+'">'+esc(r.grade)+'</span></td><td style="text-align:left">'+esc(r.advice)+'</td></tr>');
    });
    H.push('</table>');
    H.push('<h3>逐岁年度指导（事业 / 财运 / 人际 / 健康 / 时机）</h3>');
    liu.rows.forEach(function (r) {
      var cat = r.advice_cat || {};
      H.push('<details class="yearadv"' + (r.is_current ? ' open' : '') + '>');
      H.push('<summary>' + (r.is_current ? '<b>★ ' + r.year + ' 年（今年 · ' + r.age + ' 岁）</b>' : r.year + ' 年（' + r.age + ' 岁）') + ' · ' + gz(r.gz) + ' · <span class="pill ' + clsOf(r.grade) + '">' + esc(r.grade) + '</span></summary>');
      H.push('<div class="cat">');
      [["事业", "事业"], ["财运", "财运"], ["人际", "人际"], ["健康", "健康"], ["时机", "时机"]].forEach(function (kv) {
        if (cat[kv[0]]) H.push('<div><b>' + kv[1] + '：</b>' + esc(cat[kv[0]]) + '</div>');
      });
      if (r.mechanism) H.push('<div style="margin-top:4px"><b>机理：</b>' + esc(r.mechanism) + '</div>');
      var km = r.key_months || {};
      if (km.favor && km.favor.length) H.push('<div><b>✅ 宜把握月份：</b>' + esc(km.favor.join('；')) + '</div>');
      if (km.watch && km.watch.length) H.push('<div><b>⚠ 宜谨慎月份：</b>' + esc(km.watch.join('；')) + '</div>');
      H.push('</div></details>');
    });
    H.push('<div class="actions"><button class="btn ghost" id="btnCSV">导出多年运势 CSV</button>');
    H.push('<button class="btn ghost" id="btnSave">保存此排盘</button>');
    H.push('<button class="btn ghost" id="btnPDF">存为 PDF</button>');
    H.push('<span class="note">CSV 做逐年追踪；保存后可从「我的排盘」随时打开；PDF 可打印/分享。</span></div>');
    H.push('</div>');

    // 交叉验证
    H.push('<div class="card"><h2>七、多维交叉验证与分级结论</h2>');
    var gcls = cv.grade.indexOf("高一致")>=0?"grade-hi":(cv.grade.indexOf("分歧")>=0?"grade-bad":"grade-mid");
    H.push('<div class="grade-banner '+gcls+'">综合一致性：'+esc(cv.grade)+'</div>');
    H.push('<div class="kv" style="margin-top:8px"><span class="k">一致维度统计：</span>');
    H.push('<span class="cons-hi">高一致 '+cv.cons_counts["高一致"]+'</span> ｜ ');
    H.push('<span class="cons-mid">中一致 '+cv.cons_counts["中一致"]+'</span> ｜ ');
    H.push('<span class="cons-bad">分歧 '+cv.cons_counts["分歧"]+'</span></div>');
    var sysCols = ["四柱八字","紫微斗数","周易卦象","铁板神数"];
    if(ctx.face) sysCols.push("面相");
    if(ctx.palm) sysCols.push("手相");
    H.push('<table style="margin-top:10px"><tr><th>维度</th>'+sysCols.map(function(s){return '<th>'+s+'</th>';}).join('')+'<th>一致性</th><th>综合评级</th></tr>');
    cv.matrix.forEach(function(m){
      var consCls = m.consistency==="高一致"?"cons-hi":(m.consistency==="分歧"?"cons-bad":"cons-mid");
      function cell(v){ return v?esc(v[0])+' <span class="pill '+(v[1]>=4?'hi':(v[1]>=3?'mid':'lo'))+'">'+(typeof v[1]==="number"?v[1].toFixed(1):v[1])+'</span>':'—'; }
      H.push('<tr><td><b>'+esc(m.dimension)+'</b></td>');
      sysCols.forEach(function(s){ H.push('<td style="text-align:left">'+cell(pick(m,s))+'</td>'); });
      H.push('<td class="'+consCls+'">'+esc(m.consistency)+'</td>');
      var dir = m.mean_level>=4?"吉/强":(m.mean_level>=3?"平":"弱/宜守");
      H.push('<td><span class="pill '+(m.mean_level>=4?'hi':(m.mean_level>=3?'mid':'lo'))+'">'+dir+'</span></td></tr>');
    });
    H.push('</table>');
    if(cv.review_flags.length){ H.push('<h3>考时 / 复核提示</h3>'); cv.review_flags.forEach(function(f){ H.push('<div class="flag">⚠ '+esc(f)+'</div>'); }); }
    H.push('<h3>分维度结论</h3><div class="kv">');
    cv.conclusions.forEach(function(c){ H.push('<span class="v">'+esc(c.summary)+'</span>'); });
    H.push('</div>');
    H.push('</div>');

    // 人生行动指南（核心 · 用户视角：把交叉验证结论翻译成可执行的避坑手册）
    H.push('<div class="card"><h2>八、人生行动指南（核心建议）</h2>');
    H.push('<div class="note">这一节把前文的「多维交叉验证」结论，翻译成你<b>现在就能用</b>的避坑手册：先判断当下该进攻还是防守，再给六类重大决策亮红绿灯，最后列清该做 / 别做 / 留意。所有内容均为<b>决策参考与自我觉察</b>，非宿命判定。</div>');
    var wcls = ap.window.cls==="hi"?"grade-hi":(ap.window.cls==="lo"?"grade-bad":"grade-mid");
    H.push('<div class="win-banner '+wcls+'">当下判断：'+esc(ap.window.verdict)+'</div>');
    H.push('<div class="window-why">'+esc(ap.window.why)+'</div>');
    H.push('<h3 class="act-h">重大决策红绿灯（今年）</h3>');
    H.push('<div class="decz">');
    ap.decisions.forEach(function(d){ H.push('<div class="dec"><div class="dn"><span class="lt '+d.light+'"></span>'+esc(d.name)+'</div><div class="dt">'+esc(d.text)+'</div></div>'); });
    H.push('</div>');
    H.push('<div class="two" style="margin-top:14px"><div><h3 class="act-h" style="color:var(--green)">✅ 该做（趁势发力）</h3><ul class="act-list act-do">');
    ap.do_list.forEach(function(x){ H.push('<li>'+esc(x)+'</li>'); }); H.push('</ul></div>');
    H.push('<div><h3 class="act-h" style="color:var(--red)">⛔ 别做（规避弯路）</h3><ul class="act-list act-dont">');
    ap.dont_list.forEach(function(x){ H.push('<li>'+esc(x)+'</li>'); }); H.push('</ul></div></div>');
    H.push('<h3 class="act-h" style="color:#b07d2f">⚠ 留意（需现实校准）</h3><ul class="act-list act-watch">');
    ap.watch_list.forEach(function(x){ H.push('<li>'+esc(x)+'</li>'); }); H.push('</ul>');
    H.push('<h3 class="act-h">能量节奏 · 精确时间段（好年攻 / 坏年守）</h3>');
    // 最佳发力窗口（核心：最好的对应时间段，精确到年龄+年份区间）
    if (ap.rhythm.best_phase) {
      var bp = ap.rhythm.best_phase;
      var isGood = bp.good;
      H.push('<div class="phase-best"><div class="pb-t">' + (isGood ? "★ 最佳发力窗口：" : "◐ 后续偏稳窗口：") + esc(bp.age_range) + '（' + esc(bp.year_range) + '）</div>');
      H.push('<div class="pb-sub">大运「' + esc(bp.gz) + '」· 流年评分均值 ' + bp.avg + (isGood ? "" : "（偏收敛）") + '</div>');
      H.push('<div class="window-why">' + esc(bp.why) + '</div></div>');
    } else {
      H.push('<div class="window-why">未来皆为平 / 守之运，未定位到明显「发力大年」；可结合「流年详批」逐年查看评分起伏，逢平 / 吉年小步推进即可。</div>');
    }
    // 当前大运窗口
    if (ap.rhythm.current_phase) {
      var cp = ap.rhythm.current_phase;
      var badge = cp.fav ? '<span class="pill" style="background:var(--green);color:#fff">喜运·宜攻</span>' : (cp.bad ? '<span class="pill" style="background:var(--red);color:#fff">忌运·宜守</span>' : '<span class="pill" style="background:#d9c79a;color:#5a3a12">平运</span>');
      H.push('<div class="kv"><span class="k">当前大运：</span><span class="v">'+badge+' '+esc(cp.gz)+'（'+esc(cp.age_range)+(cp.year_range?(' · '+esc(cp.year_range)):'')+'）</span></div>');
      H.push('<div class="window-why">'+esc(cp.tip)+'</div>');
      if (cp.turning && cp.turning !== "无明显大变动年") H.push('<div class="kv"><span class="k">关键变动年：</span><span class="v">'+esc(cp.turning)+'</span></div>');
    }
    // 最近宜进攻 / 宜防守 的年份
    function fmtYears(arr, cls) {
      if (!arr.length) return '<span class="v" style="color:var(--muted)">未来数年无明显此类年份</span>';
      return arr.map(function(x){ return '<span class="yr '+cls+'">'+x.year+'年（'+x.age+'岁·'+x.gz+'·'+x.score+'）</span>'; }).join(' ');
    }
    H.push('<div class="kv"><span class="k">最近宜进攻：</span><span class="v">'+fmtYears(ap.rhythm.next_attack, 'atk')+'</span></div>');
    H.push('<div class="kv"><span class="k">最近宜防守：</span><span class="v">'+fmtYears(ap.rhythm.next_defend, 'def')+'</span></div>');
    // 未来逐年时间轴
    H.push('<div class="tl-title">未来逐年节奏（攻 / 平 / 守）</div>');
    H.push('<div class="tl">');
    (ap.rhythm.timeline || []).forEach(function(t){ H.push('<span class="tl-chip '+(t.cls==="hi"?"atk":(t.cls==="lo"?"def":"mid"))+'" title="评分 '+t.score+'">'+t.year+'<small>'+t.age+'岁·'+t.gz+'·'+t.tag+'</small></span>'); });
    H.push('</div>');
    H.push('<div class="window-why">'+esc(ap.rhythm.principle)+'</div>');
    H.push('<h3 class="act-h">自我觉察提示</h3><ul class="tips">');
    ap.self_aware.forEach(function(x){ H.push('<li>'+esc(x)+'</li>'); }); H.push('</ul>');
    if (ap.reflection) {
      if (ap.reflection.year_focus) {
        var yf = ap.reflection.year_focus;
        var ycls = yf.tone === "忍住" ? "grade-bad" : (yf.tone === "抓住" ? "grade-hi" : "grade-mid");
        H.push('<div class="win-banner ' + ycls + '" style="margin-bottom:8px">今年聚焦 · 最该' + esc(yf.tone) + '的一件事</div>');
        H.push('<div class="window-why" style="margin-bottom:10px">' + esc(yf.text) + '</div>');
      }
      H.push('<h3 class="act-h">按人生阶段的复盘问题' + (ap.reflection.age !== null ? ('（' + esc(ap.reflection.stage) + '）') : '') + '</h3>');
      H.push('<div class="window-why">' + esc(ap.reflection.note) + '</div>');
      H.push('<ul class="tips">');
      (ap.reflection.questions || []).forEach(function(q){ H.push('<li>'+esc(q)+'</li>'); }); H.push('</ul>');
    }
    H.push('<div class="note">人生决策最终在你手里：本系统帮你「看清局势、少走弯路」，但每一个选择仍由你自己承担与把握。</div>');
    H.push('</div>');

    H.push('<div class="actions" style="margin-top:10px"><button class="btn ghost" id="btnBack">↑ 返回录入 / 修改信息</button></div>');

    // 人生指导总览
    H.push('<div class="card"><h2>九、人生指导总览</h2>');
    var lg = cv.life_guidance;
    H.push('<div class="grade-banner grade-mid" style="text-align:left;font-size:14px;font-weight:500;line-height:1.9;color:var(--ink)">' + esc(lg.overall) + '</div>');
    H.push('<div class="two" style="margin-top:12px"><div><h3>✅ 你的优势领域</h3><ul class="tips">');
    lg.strengths.forEach(function (s) { H.push('<li>' + esc(s) + '</li>'); });
    H.push('</ul></div><div><h3>⚠️ 需留意的方面</h3><ul class="tips">');
    lg.cautions.forEach(function (c) { H.push('<li>' + esc(c) + '</li>'); });
    H.push('</ul></div></div>');
    H.push('<h3>分维度人生建议</h3><table><tr><th>维度</th><th>综合评级</th><th>指导建议</th></tr>');
    cv.conclusions.forEach(function (c) {
      var dirCls = c.direction === "吉/强" ? "hi" : (c.direction === "平" ? "mid" : "lo");
      H.push('<tr><td><b>' + esc(c.dimension) + '</b></td><td><span class="pill ' + dirCls + '">' + esc(c.direction) + '</span></td><td style="text-align:left">' + esc(c.advice) + '</td></tr>');
    });
    H.push('</table>');
    H.push('<h3>大运阶段策略</h3><table><tr><th>年龄段</th><th>大运</th><th>阶段建议</th></tr>');
    lg.by_phase.forEach(function (p) {
      H.push('<tr><td>' + esc(p.range) + '</td><td class="pillar" style="font-size:15px">' + gz(p.gz) + '</td><td style="text-align:left">' + esc(p.tip) + '</td></tr>');
    });
    H.push('</table>');
    H.push('<h3>大运阶段详批（主题 · 关键转折年）</h3><table><tr><th>年龄段</th><th>大运</th><th>阶段主题</th><th>关键转折年</th><th>阶段建议</th></tr>');
    ctx.dayun_detail.forEach(function (p) {
      H.push('<tr><td>' + esc(p.range) + '</td><td class="pillar" style="font-size:15px">' + gz(p.gz) + '</td><td style="text-align:left">' + esc(p.theme) + '</td><td style="text-align:left">' + esc(p.turning) + '</td><td style="text-align:left">' + esc(p.tip) + '</td></tr>');
    });
    H.push('</table>');
    H.push('<div class="note">以上为基于多维交叉验证的「自我认知与阶段参考」，并非宿命判定；重大人生决策请结合自身实际与现实反馈。</div>');
    H.push('</div>');

    var rep=document.getElementById("report");
    rep.innerHTML=H.join("");
    rep.querySelectorAll("table").forEach(function(t){ var w=document.createElement("div"); w.className="tablescroll"; t.parentNode.insertBefore(w,t); w.appendChild(t); });
    rep.classList.remove("hidden");
    rep.scrollIntoView({behavior:"smooth",block:"start"});
    document.getElementById("btnCSV").addEventListener("click",function(){ exportCSV(ctx); });
    document.getElementById("btnSave").addEventListener("click",function(){ saveCurrent(ctx); });
    document.getElementById("btnPDF").addEventListener("click",function(){ window.print(); });
    document.getElementById("btnBack").addEventListener("click",function(){ window.scrollTo({top:0,behavior:"smooth"}); });
  }
  function pick(m,sys){ for(var i=0;i<m.votes.length;i++) if(m.votes[i].system===sys) return [m.votes[i].text,m.votes[i].level]; return null; }

  function exportCSV(ctx){
    var rows=ctx.liunian.rows;
    var header=["年份","年龄","流年干支","纳音","流年十神","大运","大运十神","流年命宫","流年四化","评分","等级","建议","分维指导"];
    var lines=[header.join(",")];
    rows.forEach(function(r){
      var sihuaTxt=Object.keys(r.sihua).map(function(k){return k+r.sihua[k];}).join(" ");
      var advice=String(r.advice_long||r.advice).replace(/"/g,'""');
      var cat=r.advice_cat||{};
      var catStr=Object.keys(cat).map(function(k){return k+"："+cat[k];}).join("；");
      lines.push([r.year,r.age,gz(r.gz),r.nayin,r.shi_shen,(r.dayun_gz==="—"?"—":gz(r.dayun_gz)),r.dayun_shishen,r.flow_palace,sihuaTxt||"—",r.score,r.grade,'"'+advice+'"','"'+catStr.replace(/"/g,'""')+'"'].join(","));
    });
    var csv="﻿"+lines.join("\r\n");
    var blob=new Blob([csv],{type:"text/csv;charset=utf-8;"});
    var url=URL.createObjectURL(blob);
    var a=document.createElement("a");
    a.href=url; a.download="流年运势_"+ctx.birth_input.year+ctx.birth_input.month+ctx.birth_input.day+"_"+ctx.birth_input.gender+".csv";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){URL.revokeObjectURL(url);},1000);
  }

  document.getElementById("btnRun").addEventListener("click",function(){
    var err=document.getElementById("errBox"); err.innerHTML="";
    try{
      var gender=document.getElementById("f_gender").value, city=document.getElementById("f_city").value;
      var meta=null, sy,smo,sd,sh,smi;
      if(calMode==="农历"){
        var ly=+document.getElementById("f_year").value;
        var lmo=+document.getElementById("f_month").value;
        var ld=+document.getElementById("f_day").value;
        var lleap=document.getElementById("f_leap").checked;
        var lshichen=document.getElementById("f_shichen").value; // 如 "午"
        var mi=+document.getElementById("f_minute").value;
        var hour=SHICHEN_HOUR[lshichen];
        var lm = lleap ? -lmo : lmo;
        var S;
        try{
          S = Lunar.fromYmdHms(ly, lm, ld, hour, mi, 0).getSolar();
        }catch(e){
          var msg=e.message||"";
          if(msg.indexOf("month -")>=0) throw new Error("该农历年（"+ly+"）没有「闰"+ZH[lmo-1]+"」，请取消勾选闰月，或换一个月份。");
          var md=msg.match(/only (\d+) days/);
          if(md) throw new Error("农历"+ly+"年"+ZH[lmo-1]+(lleap?"（闰）":"")+"只有"+md[1]+"天，请重新选日期。");
          throw new Error("农历日期无效："+msg);
        }
        sy=S.getYear(); smo=S.getMonth(); sd=S.getDay(); sh=S.getHour(); smi=S.getMinute();
        meta={ calendar:"农历", ly:ly, lmo:lmo, ld:ld, lleap:lleap, lshichen:lshichen+"时", sy:sy, smo:smo, sd:sd, sh:sh, smi:smi };
      } else {
        sy=+document.getElementById("f_year").value; smo=+document.getElementById("f_month").value;
        sd=+document.getElementById("f_day").value; sh=+document.getElementById("f_hour").value;
        smi=+document.getElementById("f_minute").value;
        var maxd=new Date(sy,smo,0).getDate();
        if(sd>maxd) throw new Error(smo+"月最多"+maxd+"天，请重新选择日期。");
        meta={ calendar:"阳历", sy:sy, smo:smo, sd:sd, sh:sh, smi:smi };
      }
      if(document.getElementById("f_xiang").checked){
        var faceObs=collectFace(), palmObs=collectPalm();
        var faceUsed=!!(xiState.face || anyObs(faceObs));
        var palmUsed=!!(xiState.palm || anyObs(palmObs));
        if(faceUsed){ meta.faceObs=faceObs; meta.facePx=xiState.face?xiState.face.px:null; meta.faceImg=xiState.face?xiState.face.img:null; }
        if(palmUsed){ meta.palmObs=palmObs; meta.palmPx=xiState.palm?xiState.palm.px:null; meta.palmImg=xiState.palm?xiState.palm.img:null; }
        // 开关开启但未采集任何照片或特征时，视为未启用相学，静默跳过（避免默认开启时误报错）
      }
      var ctx=ML.analyze(sy,smo,sd,sh,smi,gender,city,meta);
      render(ctx);
    }catch(e){
      err.innerHTML='<div class="err">出错了：'+esc(e.message||e)+'</div>';
      document.getElementById("report").classList.add("hidden");
    }
  });

  // ---- 示例 ----
  document.getElementById("btnDemo").addEventListener("click",function(){
    calMode="农历";
    document.querySelectorAll("#f_cal button").forEach(function(b){ b.classList.toggle("active", b.getAttribute("data-cal")==="农历"); });
    applyCalMode();
    document.getElementById("f_year").value=1990;
    document.getElementById("f_month").value=4;
    document.getElementById("f_day").value=27;
    document.getElementById("f_shichen").value="午";
    document.getElementById("f_leap").checked=false;
    document.getElementById("f_minute").value=0;
    document.getElementById("f_gender").value="男";
    document.getElementById("f_city").value="北京";
    document.getElementById("btnRun").click();
  });
  // ---- 本地保存 ----
  var LS_KEY="mingli_saved_v1";
  function getSaved(){ try{return JSON.parse(localStorage.getItem(LS_KEY)||"[]");}catch(e){return [];} }
  function setSaved(a){ try{localStorage.setItem(LS_KEY,JSON.stringify(a));}catch(e){} }
  function saveCurrent(ctx){
    var inp=ctx.birth_input;
    var label = inp.calendar==="农历"
      ? (inp.ly+"年"+ZH[inp.lmo-1]+(inp.lleap?"闰":"")+inp.ld+"日"+inp.lshichen+" "+inp.gender+" "+inp.birthplace)
      : (inp.year+"-"+inp.month+"-"+inp.day+" "+inp.gender+" "+inp.birthplace);
    var rec={ input: inp, label: label, ts: Date.now() };
    var list=getSaved().filter(function(x){return x.label!==rec.label;});
    list.unshift(rec); if(list.length>20) list=list.slice(0,20);
    setSaved(list); renderSaved();
    alert("已保存到「我的排盘」（仅存于本机浏览器）");
  }
  function renderSaved(){
    var list=getSaved(); var box=document.getElementById("savedList"); var card=document.getElementById("savedCard");
    if(!list.length){ card.classList.add("hidden"); if(box) box.innerHTML=""; return; }
    card.classList.remove("hidden");
    box.innerHTML=list.map(function(r,i){
      return '<div class="saved-item"><span class="saved-label">'+esc(r.label)+'</span>'+
        '<button class="btn ghost sm" data-load="'+i+'">打开</button>'+
        '<button class="btn ghost sm" data-del="'+i+'">删</button></div>';
    }).join("");
    box.querySelectorAll("[data-load]").forEach(function(b){ b.addEventListener("click",function(){
      var r=list[+b.getAttribute("data-load")];
      var inp=r.input;
      calMode = inp.calendar;
      document.querySelectorAll("#f_cal button").forEach(function(x){ x.classList.toggle("active", x.getAttribute("data-cal")===inp.calendar); });
      applyCalMode();
      if(inp.calendar==="农历"){
        document.getElementById("f_year").value=inp.ly;
        document.getElementById("f_month").value=inp.lmo;
        document.getElementById("f_day").value=inp.ld;
        document.getElementById("f_leap").checked=!!inp.lleap;
        document.getElementById("f_shichen").value=(inp.lshichen||"子").replace("时","");
        document.getElementById("f_minute").value=inp.smi;
      } else {
        document.getElementById("f_year").value=inp.year;
        document.getElementById("f_month").value=inp.month;
        document.getElementById("f_day").value=inp.day;
        document.getElementById("f_hour").value=inp.hour;
        document.getElementById("f_minute").value=inp.minute;
      }
      document.getElementById("f_gender").value=inp.gender;
      document.getElementById("f_city").value=inp.birthplace;
      document.getElementById("btnRun").click();
    });});
    box.querySelectorAll("[data-del]").forEach(function(b){ b.addEventListener("click",function(){
      var l=getSaved(); l.splice(+b.getAttribute("data-del"),1); setSaved(l); renderSaved();
    });});
  }
  document.getElementById("btnClearSaved").addEventListener("click",function(){
    if(confirm("确定清空全部本地排盘记录？")){ setSaved([]); renderSaved(); }
  });
  renderSaved();
})();
</script>
</body>
</html>
"""

out = TEMPLATE.replace("<<<LUNAR_JS>>>", lunar).replace("<<<ENGINES_JS>>>", engines).replace("__FAVICON__", favicon).replace("__ICON__", icon_svg)
dest = os.path.join(WEB, "天命系统.html")
open(dest, "w", encoding="utf-8").write(out)
print("written:", dest, "bytes:", len(out.encode("utf-8")), "lunar:", len(lunar), "engines:", len(engines))
