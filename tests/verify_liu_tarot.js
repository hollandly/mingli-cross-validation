'use strict';
/*
 * 十七维升级 · 六壬神课(十六维) + 塔罗生命牌阵(十七维) 集成测试
 * 用法：node tests/verify_liu_tarot.js   （仓库根 MingLi_System 下运行）
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

console.log('=== 引擎运行 + 六壬/塔罗 两新维度 ===');
const out = cases.map(function(c){
  const r = s.ML.analyze(c.y, c.mo, c.d, c.h, c.mi, c.g, c.c, { calendar: '阳历' });
  return { name: c.name, r: r };
});
const wlines = [];
out.forEach(function(o){
  const r = o.r, lr = r.liuren, tar = r.tarot;
  console.log('\n[' + o.name + '] 日主 ' + r.bazi.day_element);
  // 六壬
  assert(lr && lr.yueJiang && lr.zhanShi, '六壬 月将=' + (lr && lr.yueJiang) + ' 占时=' + (lr && lr.zhanShi));
  assert(lr && Array.isArray(lr.sanChuan) && lr.sanChuan.length === 3, '六壬 三传(初/中/末)=' + (lr && lr.sanChuan.map(function(c){return c.zhi;}).join('→')));
  assert(lr && lr.sanChuan.every(function(c){ return c.zhi && c.sixkin; }), '六壬 三传含地支+六亲');
  assert(lr && lr.guiRen, '六壬 贵人=' + (lr && lr.guiRen) + (lr.isDay?'昼贵':'夜贵'));
  assert(lr && typeof lr.faYong === 'string' && typeof lr.liuFav === 'number', '六壬 发用=' + (lr && lr.faYong) + ' liuFav=' + (lr && lr.liuFav));
  // 塔罗
  assert(tar && Array.isArray(tar.cards) && tar.cards.length === 3, '塔罗 生命牌阵 3 张');
  assert(tar && tar.cards.every(function(c){ return c.name && typeof c.upright === 'boolean' && c.elem && c.theme; }), '塔罗 每张含 名称/正逆/元素/主题');
  assert(tar && tar.lesson && tar.lesson.name && tar.lesson.rel, '塔罗 课题牌=' + (tar && tar.lesson.name) + ' rel=' + (tar && tar.lesson.rel));
  // 矩阵含两新体系
  const allSys = {};
  r.cv.matrix.forEach(function(m){ m.votes.forEach(function(v){ allSys[v.system] = 1; }); });
  assert(allSys['六壬神课'], '交叉矩阵含「六壬神课」');
  assert(allSys['塔罗牌阵'], '交叉矩阵含「塔罗牌阵」');
  // 大运加权含两新维度标记（非中立运才落标记，故聚合统计）
  r.cv.dayun_enrich.forEach(function(e){ if(e.cross) e.cross.lines.forEach(function(x){ wlines.push(x); }); });
  assert(r.dayun_detail.some(function(d){ return d.theme.indexOf('十七维交叉') >= 0; }), '大运详批主题含「十七维交叉」');
  // 流月精度：liunian 每行列有 transit_note
  assert(r.liunian.rows.every(function(x){ return typeof x.transit_note === 'string'; }), '流年每行列含外行星主题(流月精度层)');
});

// 多盘分化：六壬三传 / 塔罗课题 不应全同（证伪模板）
console.log('\n=== 加权含新维度标记（聚合）===');
assert(wlines.some(function(x){ return x.indexOf('六壬') >= 0; }), '加权评分含六壬标记（部分大运）');
assert(wlines.some(function(x){ return x.indexOf('塔罗') >= 0; }), '加权评分含塔罗标记（部分大运）');

console.log('\n=== 多盘分化（证伪模板）===');
const san = out.map(function(o){ return o.r.liuren.sanChuan.map(function(c){return c.zhi;}).join('>'); });
const fay = out.map(function(o){ return o.r.liuren.faYong; });
const les = out.map(function(o){ return o.r.tarot.lesson.name; });
const cardStr = out.map(function(o){ return o.r.tarot.cards.map(function(c){return c.name+(c.upright?'+':'-');}).join(','); });
assert(new Set(san).size >= 2, '六壬三传在 7 盘中分化 (' + new Set(san).size + ' 种)');
assert(new Set(fay).size >= 2, '六壬发用在 7 盘中分化 (' + new Set(fay).size + ' 种)');
assert(new Set(les).size >= 2, '塔罗课题牌在 7 盘中分化 (' + new Set(les).size + ' 种)');
assert(new Set(cardStr).size >= 2, '塔罗牌阵在 7 盘中分化 (' + new Set(cardStr).size + ' 种)');

console.log('\n' + (fail === 0 ? '全部通过 ✓' : (fail + ' 项失败 ✗')));
process.exit(fail === 0 ? 0 : 1);
