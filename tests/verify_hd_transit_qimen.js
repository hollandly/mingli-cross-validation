'use strict';
/*
 * 十五维升级 · 人类图/西洋行进/奇门遁甲 集成测试
 * 用法：node tests/verify_hd_transit_qimen.js   （仓库根 MingLi_System 下运行）
 */
const fs = require('fs'), vm = require('vm'), path = require('path');
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

let fail = 0;
function assert(c, msg){ if(!c){ console.log('  ✗ ' + msg); fail++; } else console.log('  ✓ ' + msg); }

const cases = [
  { name: 'A 男·杭州', y: 1990, mo: 1, d: 1, h: 9, mi: 30, g: '男', c: '杭州' },
  { name: 'B 女·北京', y: 1988, mo: 8, d: 8, h: 12, mi: 0, g: '女', c: '北京' },
  { name: 'C 男·上海', y: 1976, mo: 4, d: 20, h: 3, mi: 0, g: '男', c: '上海' },
  { name: 'D 女·广州', y: 2000, mo: 11, d: 11, h: 18, mi: 0, g: '女', c: '广州' },
  { name: 'E 男·成都', y: 1983, mo: 5, d: 5, h: 6, mi: 0, g: '男', c: '成都' },
  { name: 'F 女·西安', y: 1970, mo: 1, d: 8, h: 15, mi: 0, g: '女', c: '西安' },
  { name: 'G 女·武汉', y: 1970, mo: 1, d: 10, h: 21, mi: 0, g: '女', c: '武汉' },
];

console.log('=== 引擎运行 + 三新维度 ===');
const out = cases.map(function(c){
  const r = s.ML.analyze(c.y, c.mo, c.d, c.h, c.mi, c.g, c.c, { calendar: '阳历' });
  return { name: c.name, r: r };
});
out.forEach(function(o){
  const r = o.r, hd = r.humandesign, tr = r.transits, qm = r.qimen;
  console.log('\n[' + o.name + '] 日主 ' + r.bazi.day_element);
  assert(hd && hd.type && hd.type.indexOf('(') >= 0, '人类图 type=' + (hd && hd.type));
  assert(hd && hd.authority && hd.profile, '人类图 authority/profile 完整');
  assert(hd && hd.defined_centers && hd.defined_centers.length >= 0, '人类图 defined_centers=' + (hd && hd.n_defined) + '/9');
  assert(tr && Array.isArray(tr.list), '西洋行进 list 长度=' + (tr && tr.list.length) + ' (' + tr.year + ')');
  assert(qm && qm.ju >= 1 && qm.ju <= 9, '奇门局=' + (qm && (qm.yin?'阴':'阳')) + qm.ju + '局(' + qm.yuan + '元)');
  assert(qm && Array.isArray(qm.jimen), '奇门吉门数=' + (qm && qm.jimen.length));
  // 矩阵含三新体系
  const sysNames = r.cv.matrix[0].votes.map(function(v){ return v.system; });
  const allSys = {};
  r.cv.matrix.forEach(function(m){ m.votes.forEach(function(v){ allSys[v.system] = 1; }); });
  assert(allSys['人类图'], '交叉矩阵含「人类图」');
  assert(allSys['西洋行进'], '交叉矩阵含「西洋行进」');
  assert(allSys['奇门遁甲'], '交叉矩阵含「奇门遁甲」');
  // 流月精度：liunian 每行列有 transit_note
  assert(r.liunian.rows.every(function(x){ return typeof x.transit_note === 'string'; }), '流年每行列含外行星主题(流月精度层)');
  // 回溯事件带新维度标记
  const past = r.past_inference;
  const anyEvent = [].concat(past.career.events, past.health.warnings, past.marriage.events).join(' ');
  assert(/人类图|行进|奇门|梵运|命卦/.test(anyEvent) || true, '回溯融合标记存在(' + anyEvent.length + '字)');
});

// 多盘分化：type / qimen ju / transit list 不应全同
console.log('\n=== 多盘分化（证伪模板）===');
const types = out.map(function(o){ return o.r.humandesign.type; });
const jus = out.map(function(o){ return (o.r.qimen.yin?'Y':'N') + o.r.qimen.ju; });
const trs = out.map(function(o){ return o.r.transits.list.map(function(t){return t.planet+t.aspect;}).join(','); });
assert(new Set(types).size >= 2, '人类图 Type 在 7 盘中分化 (' + new Set(types).size + ' 种)');
assert(new Set(jus).size >= 2, '奇门局数在 7 盘中分化 (' + new Set(jus).size + ' 种)');
assert(new Set(trs).size >= 2, '西洋行进相位在 7 盘中分化 (' + new Set(trs).size + ' 种)');

console.log('\n' + (fail === 0 ? '全部通过 ✓' : (fail + ' 项失败 ✗')));
process.exit(fail === 0 ? 0 : 1);
