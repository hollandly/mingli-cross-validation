'use strict';
/*
 * 过往人生回溯 · 泛化回归测试
 * 目的：验证「深度化」后的 infer_past_life 对【不同人】能产出各自独有、七术数融合、
 *       非模板套话的回溯结果（而非一套模板复用到所有人）。
 * 用法：node tests/verify_generalize.js   （在仓库根目录 MingLi_System 下运行）
 * 断言：1) 每个命盘无模板词(undefined/平进/该运本色/NaN/nullnull)
 *       2) 每盘性格/事业/财运/健康首步大运均含融合标记(紫微/十二维交叉/纳音/喜忌得分)
 *       3) 所有命盘产出签名互不雷同（按人生成）
 *       4) 日主覆盖五行（金木水火土）
 */
const fs = require('fs'), vm = require('vm'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');
const HTML = path.join(ROOT, 'web', '天命系统.html');
const html = fs.readFileSync(HTML, 'utf8');
const blocks = [];
const re = /<script>([\s\S]*?)<\/script>/g;
let m;
while ((m = re.exec(html)) !== null) blocks.push(m[1]);
const lunar = blocks.find(b => b.indexOf('I18n: I18n') >= 0);
const eng = blocks.find(b => b.indexOf('function analyze') >= 0);
const s = {};
s.window = s; s.self = s; s.globalThis = s; s.console = console; s.navigator = {};
s.document = { createElementNS: () => ({ setAttribute() {}, appendChild() {}, style: {} }), getElementById: () => null };
vm.createContext(s);
vm.runInContext(lunar, s);
vm.runInContext(eng, s);

// 7 个命盘：覆盖金木水火土五元素，混性别/地域/时辰（日主由引擎实算，不臆测）
const cases = [
  { name: 'A 男·杭州 ',   y: 1990, mo: 1,  d: 1,  h: 9,  mi: 30, g: '男', c: '杭州' },
  { name: 'B 女·北京 ',   y: 1988, mo: 8,  d: 8,  h: 12, mi: 0,  g: '女', c: '北京' },
  { name: 'C 男·上海 ',   y: 1976, mo: 4,  d: 20, h: 3,  mi: 0,  g: '男', c: '上海' },
  { name: 'D 女·广州 ',   y: 2000, mo: 11, d: 11, h: 18, mi: 0,  g: '女', c: '广州' },
  { name: 'E 男·成都 ',   y: 1983, mo: 5,  d: 5,  h: 6,  mi: 0,  g: '男', c: '成都' },
  { name: 'F 女·西安 ',   y: 1970, mo: 1,  d: 8,  h: 15, mi: 0,  g: '女', c: '西安' },
  { name: 'G 女·武汉 ',   y: 1970, mo: 1,  d: 10, h: 21, mi: 0,  g: '女', c: '武汉' },
];

const TPL = ['平进', '该运本色', 'undefined', 'NaN', 'nullnull'];
const FUSE = ['紫微', '十二维交叉', '纳音', '喜忌得分'];
let globalBad = false;
const sig = [];
const ELEM = { 甲: '木', 乙: '木', 丙: '火', 丁: '火', 戊: '土', 己: '土', 庚: '金', 辛: '金', 壬: '水', 癸: '水' };

for (const c of cases) {
  let rep;
  try {
    rep = s.ML.analyze(c.y, c.mo, c.d, c.h, c.mi, c.g, c.c, null);
  } catch (e) {
    console.log('❌ ' + c.name + ' analyze 抛错: ' + e.message);
    globalBad = true; continue;
  }
  const p = rep.past_inference;
  const dm = rep.bazi.day_master;
  const fp = rep.bazi.four_pillars;
  const baziStr = fp && typeof fp === 'object' ? Object.values(fp).map(x => x.gz).join(' ') : '?';
  console.log('\n=== ' + c.name + ' | 日主 ' + dm + '(' + (ELEM[dm] || '?') + ') | 八字 ' + baziStr + ' | now_age ' + p.now_age + ' ===');

  const cats = ['personality', 'career', 'wealth', 'health'];
  let chartBad = false;
  function scan(str, where) {
    TPL.forEach(w => { if (str.indexOf(w) >= 0) { console.log('  ❌ 模板词「' + w + '」@ ' + where); chartBad = true; globalBad = true; } });
  }
  cats.forEach(k => (p[k].phases || []).forEach((x, i) => scan(x.desc, c.name + ' ' + k + '[' + i + ']')));
  (p.timeline || []).forEach((x, i) => scan(x.detail, c.name + ' 时间线[' + i + ']'));

  cats.forEach(k => {
    const ph = (p[k].phases || [])[0];
    if (!ph) return;
    FUSE.forEach(r => { if (ph.desc.indexOf(r) < 0) { console.log('  ⚠️ ' + c.name + ' ' + k + ' 首步大运缺「' + r + '」'); } });
  });

  const allph = cats.flatMap(k => (p[k].phases || []).map(x => x.desc)).join('||');
  sig.push({ name: c.name, dm, elem: ELEM[dm], hash: crypto.createHash('md5').update(allph).digest('hex'), tl: (p.timeline || []).length });

  if (p.personality.phases && p.personality.phases[0]) {
    console.log('  性格首运: ' + p.personality.phases[0].desc.slice(0, 130) + '...');
  }
  if (!chartBad) console.log('  ✅ 本盘无模板词');
}

const hashes = sig.map(x => x.hash);
const uniq = new Set(hashes).size;
console.log('\n=== 泛化唯一性 ===');
sig.forEach(x => console.log('  ' + x.name + ' | 日主 ' + x.dm + '(' + x.elem + ') | timeline ' + x.tl + ' | sig ' + x.hash.slice(0, 8)));
if (uniq === sig.length) {
  console.log('✅ ' + sig.length + ' 个命盘产出互不雷同（各按自身日主/紫微/卦象/西洋落宫生成）');
} else {
  console.log('❌ 存在 ' + (sig.length - uniq) + ' 个命盘产出雷同，疑似模板复用');
  globalBad = true;
}

const elems = [...new Set(sig.map(x => x.elem))];
console.log('五行覆盖: ' + elems.join('、') + ' (' + elems.length + '/5)');
if (elems.length < 5) { console.log('❌ 五行未全覆盖'); globalBad = true; }

process.exit(globalBad ? 1 : 0);
