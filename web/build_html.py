# -*- coding: utf-8 -*-
"""Build a single self-contained HTML file for the 命理交叉验证系统.
Inlines web/lunar.js and web/engines.js, plus the report UI, into one file.
"""
import io, os

WEB = "/Users/linpengchen/WorkBuddy/2026-10-10-13-49-27/MingLi_System/web"
lunar = open(os.path.join(WEB, "lunar.js"), encoding="utf-8").read()
engines = open(os.path.join(WEB, "engines.js"), encoding="utf-8").read()

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>命理交叉验证系统 · 录入与报告</title>
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
  @media print{
    .disclaimer,.card#formCard,.card#savedCard,.actions,.note,.btn,#errBox{display:none!important;}
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
    <h1>命理交叉验证系统</h1>
    <div class="sub">四柱八字 · 紫微斗数 · 周易梅花易数 · 铁板神数 ｜ 四维交叉验证</div>
  </header>
  <div class="disclaimer">
    本系统用于传统文化研究、自我认知与性格参考，<b>不构成任何医疗、投资、法律或人生的决策建议</b>。
    命理之说，信则有参考，不信则作闲谈；请以理性与科学态度看待。
  </div>

  <!-- 录入表单 -->
  <div class="card" id="formCard">
    <h2>录入出生信息</h2>
    <div class="form-grid">
      <div class="field"><label>出生年份（阳历）</label><select id="f_year"></select></div>
      <div class="field"><label>月份</label><select id="f_month"></select></div>
      <div class="field"><label>日期</label><select id="f_day"></select></div>
      <div class="field"><label>出生时（24小时制）</label><select id="f_hour"></select></div>
      <div class="field"><label>分钟</label><select id="f_minute"></select></div>
      <div class="field"><label>性别</label>
        <select id="f_gender"><option value="男">男</option><option value="女">女</option></select></div>
      <div class="field"><label>出生地（用于真太阳时校正）</label><select id="f_city"></select></div>
    </div>
    <div class="actions">
      <button class="btn" id="btnRun">生成命理报告</button>
      <button class="btn ghost" id="btnDemo">看示例</button>
      <span class="note">提示：出生地越精确，真太阳时校正越准。系统会自动校正「真太阳时」后定四柱。</span>
    </div>
    <div id="errBox"></div>
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

  <footer>命理交叉验证系统 · 纯浏览器本地运算（数据不上传）· 传统文化研究工具</footer>
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
  // ---- 初始化表单 ----
  function fill(sel, items, val){ var el=document.getElementById(sel); items.forEach(function(it){
    var o=document.createElement("option"); o.value=it.v!=null?it.v:it; o.text=it.t!=null?it.t:it;
    if(val!=null && o.value===String(val)) o.selected=true; el.appendChild(o);});}
  (function(){
    var yrs=[]; for(var y=1925;y<=new Date().getFullYear();y++) yrs.push({v:y,t:y+"年"}); fill("f_year",yrs,1990);
    var mos=[]; for(var m=1;m<=12;m++) mos.push({v:m,t:m+"月"}); fill("f_month",mos,5);
    var ds=[]; for(var d=1;d<=31;d++) ds.push({v:d,t:d+"日"}); fill("f_day",ds,20);
    var hs=[]; for(var h=0;h<24;h++) hs.push({v:h,t:(h<10?"0"+h:h)+"时"}); fill("f_hour",hs,12);
    var mis=[]; for(var mi=0;mi<60;mi+=5) mis.push({v:mi,t:(mi<10?"0"+mi:mi)+"分"}); fill("f_minute",mis,0);
    var cities=Object.keys(ML.C.CITY_LONGITUDE).map(function(c){return {v:c,t:c};});
    fill("f_city",cities,"北京");
  })();

  function esc(s){ return String(s==null?"":s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];}); }
  function gz(g){ return g[0]+g[1]; }
  function clsOf(g){ return g==="吉"||g==="平偏吉"?"hi":(g==="平"?"mid":"lo"); }

  // ---- 渲染 ----
  function render(ctx){
    var b=ctx.bazi, z=ctx.ziwei, yj=ctx.yijing, tb=ctx.tieban, cv=ctx.cv, liu=ctx.liunian, geo=ctx.geo;
    var H=[];
    H.push('<div class="card"><h2>一、基本信息与真太阳时校正</h2>');
    H.push('<div class="kv">');
    H.push('<span class="k">录入：</span><span class="v">'+ctx.birth_input.year+'年'+ctx.birth_input.month+'月'+ctx.birth_input.day+'日 '+ctx.birth_input.hour+'时'+ctx.birth_input.minute+'分 · '+ctx.birth_input.gender+' · '+esc(ctx.birth_input.birthplace)+'</span>');
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
      H.push('</div></details>');
    });
    H.push('<div class="actions"><button class="btn ghost" id="btnCSV">导出多年运势 CSV</button>');
    H.push('<button class="btn ghost" id="btnSave">保存此排盘</button>');
    H.push('<button class="btn ghost" id="btnPDF">存为 PDF</button>');
    H.push('<span class="note">CSV 做逐年追踪；保存后可从「我的排盘」随时打开；PDF 可打印/分享。</span></div>');
    H.push('</div>');

    // 交叉验证
    H.push('<div class="card"><h2>七、四维交叉验证与分级结论</h2>');
    var gcls = cv.grade.indexOf("高一致")>=0?"grade-hi":(cv.grade.indexOf("分歧")>=0?"grade-bad":"grade-mid");
    H.push('<div class="grade-banner '+gcls+'">综合一致性：'+esc(cv.grade)+'</div>');
    H.push('<div class="kv" style="margin-top:8px"><span class="k">一致维度统计：</span>');
    H.push('<span class="cons-hi">高一致 '+cv.cons_counts["高一致"]+'</span> ｜ ');
    H.push('<span class="cons-mid">中一致 '+cv.cons_counts["中一致"]+'</span> ｜ ');
    H.push('<span class="cons-bad">分歧 '+cv.cons_counts["分歧"]+'</span></div>');
    H.push('<table style="margin-top:10px"><tr><th>维度</th><th>四柱八字</th><th>紫微斗数</th><th>周易卦象</th><th>铁板神数</th><th>一致性</th><th>综合评级</th></tr>');
    cv.matrix.forEach(function(m){
      var consCls = m.consistency==="高一致"?"cons-hi":(m.consistency==="分歧"?"cons-bad":"cons-mid");
      function cell(v){ return v?esc(v[0])+' <span class="pill '+(v[1]>=4?'hi':(v[1]>=3?'mid':'lo'))+'">'+(typeof v[1]==="number"?v[1].toFixed(1):v[1])+'</span>':'—'; }
      H.push('<tr><td><b>'+esc(m.dimension)+'</b></td>');
      H.push('<td style="text-align:left">'+cell(pick(m,"四柱八字"))+'</td>');
      H.push('<td style="text-align:left">'+cell(pick(m,"紫微斗数"))+'</td>');
      H.push('<td style="text-align:left">'+cell(pick(m,"周易卦象"))+'</td>');
      H.push('<td style="text-align:left">'+cell(pick(m,"铁板神数"))+'</td>');
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

    H.push('<div class="actions" style="margin-top:10px"><button class="btn ghost" id="btnBack">↑ 返回录入 / 修改信息</button></div>');

    // 人生指导总览
    H.push('<div class="card"><h2>八、人生指导总览</h2>');
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
    H.push('<div class="note">以上为基于四体系交叉验证的「自我认知与阶段参考」，并非宿命判定；重大人生决策请结合自身实际与现实反馈。</div>');
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
      var y=+document.getElementById("f_year").value, mo=+document.getElementById("f_month").value,
          d=+document.getElementById("f_day").value, h=+document.getElementById("f_hour").value,
          mi=+document.getElementById("f_minute").value,
          gender=document.getElementById("f_gender").value, city=document.getElementById("f_city").value;
      var maxd=new Date(y,mo,0).getDate();
      if(d>maxd) throw new Error(mo+"月最多"+maxd+"天，请重新选择日期。");
      var ctx=ML.analyze(y,mo,d,h,mi,gender,city);
      render(ctx);
    }catch(e){
      err.innerHTML='<div class="err">出错了：'+esc(e.message||e)+'</div>';
      document.getElementById("report").classList.add("hidden");
    }
  });

  // ---- 示例 ----
  document.getElementById("btnDemo").addEventListener("click",function(){
    document.getElementById("f_year").value=1990;document.getElementById("f_month").value=5;
    document.getElementById("f_day").value=20;document.getElementById("f_hour").value=12;
    document.getElementById("f_minute").value=0;document.getElementById("f_gender").value="男";
    document.getElementById("f_city").value="北京";
    document.getElementById("btnRun").click();
  });
  // ---- 本地保存 ----
  var LS_KEY="mingli_saved_v1";
  function getSaved(){ try{return JSON.parse(localStorage.getItem(LS_KEY)||"[]");}catch(e){return [];} }
  function setSaved(a){ try{localStorage.setItem(LS_KEY,JSON.stringify(a));}catch(e){} }
  function saveCurrent(ctx){
    var inp=ctx.birth_input;
    var rec={y:inp.year,mo:inp.month,d:inp.day,h:inp.hour,mi:inp.minute,gender:inp.gender,city:inp.birthplace,
      label:inp.year+"-"+inp.month+"-"+inp.day+" "+inp.gender+" "+inp.birthplace, ts:Date.now()};
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
      document.getElementById("f_year").value=r.y;document.getElementById("f_month").value=r.mo;
      document.getElementById("f_day").value=r.d;document.getElementById("f_hour").value=r.h;
      document.getElementById("f_minute").value=r.mi;document.getElementById("f_gender").value=r.gender;
      document.getElementById("f_city").value=r.city; document.getElementById("btnRun").click();
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

out = TEMPLATE.replace("<<<LUNAR_JS>>>", lunar).replace("<<<ENGINES_JS>>>", engines)
dest = os.path.join(WEB, "命理交叉验证系统.html")
open(dest, "w", encoding="utf-8").write(out)
print("written:", dest, "bytes:", len(out.encode("utf-8")), "lunar:", len(lunar), "engines:", len(engines))
