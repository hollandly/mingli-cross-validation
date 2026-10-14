'use strict';
/*
 * Vimshottari 大运 + 玄空飞星·八宅命卦 集成验证
 * 目的：验证两个新维度（第十一·十二维）正确接入引擎，并在【不同人】上分化（非模板）。(系统已升十五维；本脚本聚焦 Vimshottari/玄空飞星)
 * 用法：node tests/verify_feng_vim.js   （在仓库根目录 MingLi_System 下运行）
 * 断言：1) analyze 返回 vimshottari(9 运序列 + 当前运) 与 fengshui(命卦/四吉方/四凶方/九运)
 *       2) cross_validate 矩阵含 Vimshottari 与玄空飞星两体系（共 10 体系，无面相/手相时）
 *       3) 两维度 DIMS 信号进入矩阵相应维度
 *       4) 大运交叉评分出现「梵运」标记
 *       5) 7 盘上 命卦(东四/西四) 与 当前 Vimshottari 行星 均分化（非同一模板）
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

const cases = [
  { name: 'A 男·杭州 ', y: 1990, mo: 1,  d: 1,  h: 9,  mi: 30, g: '男', c: '杭州' },
  { name: 'B 女·北京 ', y: 1988, mo: 8,  d: 8,  h: 12, mi: 0,  g: '女', c: '北京' },
  { name: 'C 男·上海 ', y: 1976, mo: 4,  d: 20, h: 3,  mi: 0,  g: '男', c: '上海' },
  { name: 'D 女·广州 ', y: 2000, mo: 11, d: 11, h: 18, mi: 0,  g: '女', c: '广州' },
  { name: 'E 男·成都 ', y: 1983, mo: 5,  d: 5,  h: 6,  mi: 0,  g: '男', c: '成都' },
  { name: 'F 女·西安 ', y: 1970, mo: 1,  d: 8,  h: 15, mi: 0,  g: '女', c: '西安' },
  { name: 'G 女·武汉 ', y: 1970, mo: 1,  d: 10, h: 21, mi: 0,  g: '女', c: '武汉' },
];

let bad = false;
function assert(cond, msg) { if (!cond) { console.log('  ❌ ' + msg); bad = true; } else console.log('  ✅ ' + msg); }

const fengGroups = new Set();
const vimPlanets = new Set();
const sysSet = new Set();

for (const c of cases) {
  let rep;
  try { rep = s.ML.analyze(c.y, c.mo, c.d, c.h, c.mi, c.g, c.c, null); }
  catch (e) { console.log('❌ ' + c.name + ' analyze 抛错: ' + e.message); bad = true; continue; }
  console.log('\n=== ' + c.name + ' | 日主 ' + rep.bazi.day_master + ' ===');
  const vim = rep.vimshottari, feng = rep.fengshui, cv = rep.cv;

  // Vimshottari 结构
  assert(vim && Array.isArray(vim.list) && vim.list.length === 9, 'Vimshottari 返回 9 段大运序列');
  assert(vim && vim.current && vim.current.planet, 'Vimshottari 含当前大运(' + (vim && vim.current && vim.current.planet) + ' ' + (vim && vim.current && vim.current.start_age) + '–' + (vim && vim.current && vim.current.end_age) + '岁)');
  assert(vim && vim.moon_nakshatra >= 1 && vim.moon_nakshatra <= 27, 'Vimshottari 月亮宿号合法(' + (vim && vim.moon_nakshatra) + ')');
  vimPlanets.add(vim.current.planet);

  // 玄空飞星·八宅
  assert(feng && [1,2,3,4,6,7,8,9].indexOf(feng.kua) >= 0, '玄空飞星 命卦数合法(' + (feng && feng.kua) + ')');
  assert(feng && (feng.group === '东四命' || feng.group === '西四命'), '玄空飞星 命卦分组(' + (feng && feng.group) + '·' + (feng && feng.trigram) + ')');
  assert(feng && feng.favorable.length === 4 && feng.unfavorable.length === 4, '玄空飞星 四吉方+四凶方齐全');
  assert(feng && feng.period === 9 && /九运/.test(feng.period_star), '玄空飞星 当前三元九运(九紫离火)');
  fengGroups.add(feng.group);

  // 矩阵体系
  const syss = [];
  cv.matrix.forEach(m => m.votes.forEach(v => syss.push(v.system)));
  syss.forEach(x => sysSet.add(x));
  assert(syss.indexOf('Vimshottari') >= 0, '矩阵含 Vimshottari 体系');
  assert(syss.indexOf('玄空飞星') >= 0, '矩阵含 玄空飞星 体系');

  // DIMS 信号
  const dimHas = (dim, kw) => { const v = cv.matrix.find(x => x.dimension === dim); if (!v) return false; return v.votes.some(z => z.system === '玄空飞星' || z.system === 'Vimshottari' ? (z.text || '').indexOf(kw) >= 0 : false); };
  const vimVote = cv.matrix.find(x => x.dimension === '时机运势') && cv.matrix.find(x => x.dimension === '时机运势').votes.find(z => z.system === 'Vimshottari');
  assert(vimVote && /Vimshottari/.test(vimVote.text), 'Vimshottari 信号进入「时机运势」维度');
  const fengVote = cv.matrix.find(x => x.dimension === '家庭(六亲)') && cv.matrix.find(x => x.dimension === '家庭(六亲)').votes.find(z => z.system === '玄空飞星');
  assert(fengVote && /玄空飞星/.test(fengVote.text), '玄空飞星 信号进入「家庭(六亲)」维度');

  // 大运交叉评分 — 梵运标记
  const crossLines = (rep.cv.dayun_enrich || []).map(e => e.cross && e.cross.lines ? e.cross.lines.join('') : '').join('');
  assert(/梵运/.test(crossLines), '大运交叉评分出现「梵运」互证标记');

  console.log('  玄空飞星 吉方: ' + feng.favorable.map(f => f.star + f.dir).join('、') + ' ｜ 对齐用神: ' + (feng.align_dirs.length ? feng.align_dirs.join('、') : '无'));
}

console.log('\n=== 分化性（非模板） ===');
console.log('  命卦分组出现: ' + [...fengGroups].join('、'));
console.log('  当前 Vimshottari 行星出现: ' + [...vimPlanets].join('、'));
assert(fengGroups.size >= 2, '命卦分组在东四/西四间分化（≥2 类，证明非同一模板）');
assert(vimPlanets.size >= 2, '当前 Vimshottari 行星在多盘间分化（≥2 种）');
assert(sysSet.size >= 10, '交叉验证矩阵体系数 ≥10（八字/紫微/周易/铁板/西洋/生肖/七政/灵数/Vimshottari/玄空飞星）');

console.log('\n' + (bad ? '❌ 存在失败断言' : '✅ 全部断言通过'));
process.exit(bad ? 1 : 0);
