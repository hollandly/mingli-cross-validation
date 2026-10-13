/* 命理交叉验证系统 · 浏览器端引擎（纯 JS，无外部依赖，除 lunar.js 提供历法底层）
 * 四体系：四柱八字 / 紫微斗数 / 周易梅花易数 / 铁板神数。
 * 交叉验证：多维信号归一 + 一致性判定 + 考时复核 + 分级结论。
 * 全部流派约定与 Python 版(framework.md)保持一致。
 */
(function (root, factory) {
  if (typeof module !== "undefined" && module.exports) module.exports = factory();
  else root.ML = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // ============ 常量 ============
  var GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
  var GAN_ELEMENT = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"];
  var GAN_YINYANG = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"];
  var GAN_INDEX = {}; GAN.forEach(function (g, i) { GAN_INDEX[g] = i; });

  var ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
  var ZHI_ELEMENT = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"];
  var ZHI_YINYANG = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"];
  var ZHI_INDEX = {}; ZHI.forEach(function (z, i) { ZHI_INDEX[z] = i; });

  var ZHI_CANGAN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"], "卯": ["乙"],
    "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"], "午": ["丁", "己"],
    "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"], "酉": ["辛"],
    "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
  };

  var ELEMENTS = ["木", "火", "土", "金", "水"];
  var SHENG = { "木": "火", "火": "土", "土": "金", "金": "水", "水": "木" };
  var KE = { "木": "土", "土": "水", "水": "火", "火": "金", "金": "木" };
  var ELEMENT_COLOR = { "木": "#2e7d32", "火": "#c62828", "土": "#8d6e63", "金": "#f9a825", "水": "#1565c0" };

  var _NAYIN_ORDER = [
    "金", "金", "火", "火", "木", "木", "土", "土", "金", "金",
    "火", "火", "水", "水", "木", "木", "土", "土", "金", "金",
    "水", "水", "土", "土", "木", "木", "火", "火", "金", "金",
    "木", "木", "水", "水", "土", "土", "火", "火", "金", "金",
    "土", "土", "木", "木", "水", "水", "火", "火", "金", "金",
    "木", "木", "水", "水", "土", "土", "火", "火", "水", "水"
  ];
  var _NAYIN_NAME_PAIRS = [
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火", "涧下水", "城头土", "白蜡金", "杨柳木",
    "泉中水", "屋上土", "霹雳火", "松柏木", "长流水", "沙中金", "山下火", "平地木", "壁上土", "金箔金",
    "覆灯火", "天河水", "大驿土", "钗钏金", "桑柘木", "大溪水", "沙中土", "天上火", "石榴木", "大海水"
  ];
  var _NAYIN_NAME = []; _NAYIN_NAME_PAIRS.forEach(function (n) { _NAYIN_NAME.push(n); _NAYIN_NAME.push(n); });

  var GZ60 = []; for (var i = 0; i < 60; i++) GZ60.push(GAN[i % 10] + ZHI[i % 12]);
  var GZ60_INDEX = {}; GZ60.forEach(function (gz, i) { GZ60_INDEX[gz] = i; });

  function nayin(gz) { var s = GZ60_INDEX[gz]; return s == null ? "" : _NAYIN_ORDER[s]; }
  function nayin_name(gz) { var s = GZ60_INDEX[gz]; return s == null ? "" : _NAYIN_NAME[s]; }

  var TEN_GOD = ["比肩", "劫财", "食神", "伤官", "正财", "偏财", "正官", "七杀", "正印", "偏印"];
  function ten_god(day_gan, other_gan) {
    var dw = GAN_ELEMENT[GAN_INDEX[day_gan]], dy = GAN_YINYANG[GAN_INDEX[day_gan]];
    var ow = GAN_ELEMENT[GAN_INDEX[other_gan]], oy = GAN_YINYANG[GAN_INDEX[other_gan]];
    if (ow === dw) return oy === dy ? "比肩" : "劫财";
    if (SHENG[ow] === dw) return oy !== dy ? "正印" : "偏印";
    if (SHENG[dw] === ow) return oy === dy ? "食神" : "伤官";
    if (KE[ow] === dw) return oy !== dy ? "正官" : "七杀";
    if (KE[dw] === ow) return oy === dy ? "偏财" : "正财";
    return "?";
  }

  var ZIWEI_STARS = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"];
  var ZIWEI_PALACES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "交友", "官禄", "田宅", "福德", "父母"];
  var SIHUA = {
    "甲": ["廉贞", "破军", "武曲", "太阳"], "乙": ["天机", "天梁", "紫微", "太阴"],
    "丙": ["天同", "天机", "文昌", "廉贞"], "丁": ["太阴", "天同", "天机", "巨门"],
    "戊": ["贪狼", "太阴", "右弼", "天机"], "己": ["武曲", "贪狼", "天梁", "文曲"],
    "庚": ["太阳", "武曲", "太阴", "天同"], "辛": ["巨门", "太阳", "文曲", "文昌"],
    "壬": ["天梁", "紫微", "左辅", "武曲"], "癸": ["破军", "巨门", "太阴", "贪狼"]
  };
  var JU = { "金": 4, "木": 3, "水": 2, "火": 6, "土": 5 };

  var CITY_LONGITUDE = {
    "北京时间(东经120°)": 120.0, "北京": 116.41, "上海": 121.47, "广州": 113.26, "深圳": 114.06,
    "成都": 104.07, "重庆": 106.55, "杭州": 120.15, "武汉": 114.30, "西安": 108.95, "南京": 118.78,
    "天津": 117.20, "苏州": 120.62, "郑州": 113.62, "长沙": 112.94, "沈阳": 123.43, "大连": 121.62,
    "青岛": 120.38, "济南": 117.00, "哈尔滨": 126.65, "长春": 125.19, "石家庄": 114.51, "太原": 112.55,
    "合肥": 117.30, "福州": 119.30, "厦门": 118.10, "南昌": 115.89, "昆明": 102.71, "贵阳": 106.71,
    "南宁": 108.37, "海口": 110.35, "兰州": 103.83, "西宁": 101.78, "银川": 106.27, "乌鲁木齐": 87.62,
    "拉萨": 91.11, "呼和浩特": 111.75, "香港": 114.17, "澳门": 113.55, "台北": 121.56, "桂林": 110.29,
    "温州": 120.70, "宁波": 121.55, "无锡": 120.30, "常州": 119.95, "徐州": 117.18, "南通": 120.86,
    "东莞": 113.75, "佛山": 113.12, "珠海": 113.55, "泉州": 118.58, "纽约": -74.0, "洛杉矶": -118.24,
    "旧金山": -122.42, "温哥华": -123.12, "伦敦": -0.13, "巴黎": 2.35, "东京": 139.69, "首尔": 126.98,
    "新加坡": 103.85, "悉尼": 151.21, "曼谷": 100.50, "多伦多": -79.38
  };

  var BAGUA = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"];
  var BAGUA_TRIGRAM = {
    "乾": [1, 1, 1], "兑": [0, 1, 1], "离": [1, 0, 1], "震": [0, 0, 1],
    "巽": [1, 1, 0], "坎": [0, 1, 0], "艮": [1, 0, 0], "坤": [0, 0, 0]
  };
  var BAGUA_ELEMENT = { "乾": "金", "兑": "金", "离": "火", "震": "木", "巽": "木", "坎": "水", "艮": "土", "坤": "土" };
  var BAGUA_NATURE = {
    "乾": "刚健中正，主动、主动力、领导", "兑": "喜悦口舌，主交流、表达",
    "离": "光明依附，主文采、礼仪、明察", "震": "震动奋起，主行动、开创、变动",
    "巽": "谦逊入内，主渗透、柔进、谋略", "坎": "险陷流动，主智慧、隐伏、险难",
    "艮": "静止笃实，主稳重、守成、阻滞", "坤": "厚载柔顺，主包容、承载、顺应"
  };
  var HEX_NAMES = [
    "乾为天", "天泽履", "天火同人", "天雷无妄", "天风姤", "天水讼", "天山遁", "天地否",
    "泽天夬", "兑为泽", "泽火革", "泽雷随", "泽风大过", "泽水困", "泽山咸", "泽地萃",
    "火天大有", "火泽睽", "离为火", "火雷噬嗑", "火风鼎", "火水未济", "火山旅", "火地晋",
    "雷天大壮", "雷泽归妹", "雷火丰", "震为雷", "雷风恒", "雷水解", "雷山小过", "雷地豫",
    "风天小畜", "风泽中孚", "风火家人", "风雷益", "巽为风", "风水涣", "风山渐", "风地观",
    "水天需", "水泽节", "水火既济", "水雷屯", "水风井", "坎为水", "水山蹇", "水地比",
    "山天大畜", "山泽损", "山火贲", "山雷颐", "山风蛊", "山水蒙", "艮为山", "山地剥",
    "地天泰", "地泽临", "地火明夷", "地雷复", "地风升", "地水师", "地山谦", "坤为地"
  ];
  var HEX_MEANING = {
    "乾为天": "刚健中正，自强不息；宜进取，忌刚愎", "天泽履": "履虎尾，慎行免咎；守礼可成",
    "天火同人": "同人于野，和同协力；利交际", "天雷无妄": "无妄求实，不妄动；顺天休命",
    "天风姤": "邂逅不期，防阴长；宜守不宜攻", "天水讼": "讼则争，慎防口舌官非；宜止",
    "天山遁": "遁世避位，退保其身；时穷则隐", "天地否": "天地不交，闭塞之象；待时通",
    "泽天夬": "决而能和，刚决柔；果断去小人", "兑为泽": "丽泽相悦，口舌欢愉；重情义",
    "泽火革": "革故鼎新，顺天应人；变革之时", "泽雷随": "随时而动，从宜适变；随顺吉",
    "泽风大过": "大过栋桡，独立不惧；宜慎重任", "泽水困": "困穷守正，处险静守；待援",
    "泽山咸": "咸感相应，男女相悦；交感成", "泽地萃": "萃聚一堂，物以类聚；聚而散慎",
    "火天大有": "大有富有，遏恶扬善；盛而谦", "火泽睽": "睽违乖离，求同存异；谨慎合",
    "离为火": "明两作离，继明照四方；附丽守正", "火雷噬嗑": "噬嗑亨，刚柔决断；去间成",
    "火风鼎": "鼎新取象，烹饪养贤；革故鼎新", "火水未济": "未济事未成，慎终如始；待济",
    "火山旅": "旅琐琐，行旅在外；不安守", "火地晋": "晋进显明，旭日升天；进取得时",
    "雷天大壮": "大壮阳刚，壮勿妄动；守正", "雷泽归妹": "归妹征凶，男女终始；慎嫁娶",
    "雷火丰": "丰大光明，盛极当忧；保丰", "震为雷": "震来虩虩，恐惧修省；动而生",
    "雷风恒": "恒久不已，立不易方；持久吉", "雷水解": "解险舒难，险以动；解脱时",
    "雷山小过": "小过宜下，过而能改；守小", "雷地豫": "豫乐顺动，备豫不虞；乐勿极",
    "风天小畜": "小畜寡聚，密云不雨；积小", "风泽中孚": "中孚信及豚鱼，诚信感；信立",
    "风火家人": "家人有严君，正家道；内和", "风雷益": "益损上益下，与时偕行；受益",
    "巽为风": "巽顺以入，申命行事；谦入", "风水涣": "涣散其患，风行水上；散而聚",
    "风山渐": "渐女归吉，循序渐进；稳进", "风地观": "观国之光，省方观民；观察",
    "水天需": "需待也，饮食宴乐；待时", "水泽节": "节以制度，不伤财；节制",
    "水火既济": "既济初吉终乱，守成维艰；戒满", "水雷屯": "屯刚柔始交，难生；经纶",
    "水风井": "井养不穷，改邑不改井；养德", "坎为水": "习坎重险，维心亨；处险智",
    "水山蹇": "蹇难止行，反身修德；止而慎", "水地比": "比亲辅也，先王建万国；亲附",
    "山天大畜": "大畜厚积，刚上尚贤；蓄德", "山泽损": "损下益上，惩忿窒欲；损抑",
    "山火贲": "贲饰也，质有其文；文饰", "山雷颐": "颐养正，慎言语节饮食；养正",
    "山风蛊": "蛊坏终蛊，干父之蛊；整治", "山水蒙": "蒙以养正，山下出泉；启蒙",
    "艮为山": "艮止其背，时止则止；静守", "山地剥": "剥床以肤，剥落消阳；防损",
    "地天泰": "天地交泰，小往大来；通泰", "地泽临": "临元亨利贞，养成临民；临下",
    "地火明夷": "明夷伤夷，内难而能正；韬光", "地雷复": "复见天地心，一阳来复；复兴",
    "地风升": "升巽而顺，积小成高；升进", "地水师": "师众贞丈人，容民畜众；用众",
    "地山谦": "谦尊而光，裒多益寡；谦德", "坤为地": "坤厚载物，柔顺利贞；顺承"
  };
  var BAGUA_NUM = { "乾": 1, "兑": 2, "离": 3, "震": 4, "巽": 5, "坎": 6, "艮": 7, "坤": 8 };
  var NUM_BAGUA = {}; for (var bk in BAGUA_NUM) NUM_BAGUA[BAGUA_NUM[bk]] = bk;

  // ============ 真太阳时 ============
  function equation_of_time(y, m, d) {
    var dt = new Date(y, 0, 1);
    var n = Math.floor((new Date(y, m - 1, d) - dt) / 86400000) + 1;
    var dd = 0.9856 * (n - 1);
    var r = Math.PI / 180;
    return -7.66 * Math.sin(r * (dd + 4.13)) + 9.87 * Math.sin(r * (2 * dd + 3.6));
  }
  function correct_to_solar(y, mo, d, h, mi, longitude) {
    var delta_h = (longitude - 120.0) / 15.0;
    var partial = new Date(y, mo - 1, d, h, mi, 0);
    partial = new Date(partial.getTime() + delta_h * 3600000);
    var eot = equation_of_time(partial.getFullYear(), partial.getMonth() + 1, partial.getDate());
    var solar = new Date(partial.getTime() + eot * 60000);
    return { solar: solar, delta_h: delta_h, eot: eot, longitude: longitude };
  }

  // ============ 八字 ============
  function _gan_zhi_index(gz) { return GZ60_INDEX[gz]; }
  function _wuxu_dun(day_gan) {
    // 五鼠遁：返回该日「子时」天干序号（0-基）。甲己→甲,乙庚→丙,丙辛→戊,丁壬→庚,戊癸→壬。
    var t = { "甲": 0, "己": 0, "乙": 2, "庚": 2, "丙": 4, "辛": 4, "丁": 6, "壬": 6, "戊": 8, "癸": 8 };
    return t[day_gan];
  }
  function compute_bazi(y, mo, d, h, mi, gender) {
    var solar = new Date(y, mo - 1, d, h, mi, 0);
    var S = Solar.fromYmdHms(y, mo, d, h, mi, 0);
    var lu = S.getLunar();
    // 年/月/日柱按「当日中午」取，避免 lunar.js 在 23:00 按晚子时把日柱推进次日
    // （与 Python/cnlunar 版一致：以午夜为日界，23:xx 仍属当日）。
    var refS = Solar.fromYmdHms(y, mo, d, 12, 0, 0);
    var refLu = refS.getLunar();
    var year_gz = refLu.getYearInGanZhi();
    var month_gz = refLu.getMonthInGanZhi();
    var day_gz = refLu.getDayInGanZhi();
    var shichen = _hour_to_shichen(h);
    var hour_gan = GAN[(_wuxu_dun(day_gz[0]) + (shichen - 1)) % 10];
    var hour_gz = hour_gan + ZHI[shichen - 1];
    var four = [year_gz, month_gz, day_gz, hour_gz];
    var day_gan = day_gz[0];

    var shi_shen = four.map(function (gz) { return ten_god(day_gan, gz[0]); });

    var element_count = {}; ELEMENTS.forEach(function (e) { element_count[e] = 0; });
    four.forEach(function (gz) {
      element_count[GAN_ELEMENT[GAN_INDEX[gz[0]]]] += 1;
      element_count[ZHI_ELEMENT[ZHI_INDEX[gz[1]]]] += 1;
    });
    var day_elem = GAN_ELEMENT[GAN_INDEX[day_gan]];

    var support = 0, drain = 0;
    four.forEach(function (gz, idx) {
      if (["比肩", "劫财", "正印", "偏印"].indexOf(shi_shen[idx]) >= 0) support += 1;
      else drain += 1;
    });
    var month_zhi_elem = ZHI_ELEMENT[ZHI_INDEX[month_gz[1]]];
    if (SHENG[month_zhi_elem] === day_elem || month_zhi_elem === day_elem) support += 0.6;
    else if (KE[month_zhi_elem] === day_elem || KE[day_elem] === month_zhi_elem) drain += 0.4;
    var ratio = support / (drain + 1e-9);
    var strength = ratio >= 1.5 ? "身旺" : (ratio <= 0.7 ? "身弱" : "中和");

    var yin = GAN_YINYANG[GAN_INDEX[year_gz[0]]] === "阳";
    var male = gender === "男";
    var forward = (yin && male) || (!yin && !male);

    // 起运：取前后最近『节』
    function jieDates(year) {
      var tbl = Solar.fromYmdHms(year, 1, 1, 0, 0, 0).getLunar().getJieQiTable();
      var names = ["小寒", "立春", "惊蛰", "清明", "立夏", "芒种", "小暑", "立秋", "白露", "寒露", "立冬", "大雪"];
      var out = [];
      names.forEach(function (nm) {
        if (tbl[nm]) { var s = tbl[nm]; out.push(new Date(s.getYear(), s.getMonth() - 1, s.getDay())); }
      });
      return out;
    }
    var allJie = [];
    [y - 1, y, y + 1].forEach(function (yy) { jieDates(yy).forEach(function (dt) { allJie.push(dt); }); });
    allJie.sort(function (a, b) { return a - b; });
    var prevJie = null, nextJie = null;
    for (var k = 0; k < allJie.length; k++) {
      if (allJie[k] <= solar) prevJie = allJie[k];
      if (allJie[k] > solar) { nextJie = allJie[k]; break; }
    }
    var days = 0;
    if (forward && nextJie) days = (nextJie - solar) / 86400000;
    else if (!forward && prevJie) days = (solar - prevJie) / 86400000;
    var start_age = days / 3.0;

    var mi = _gan_zhi_index(month_gz);
    var dayun = [];
    for (var i = 0; i < 8; i++) {
      var idx = (forward ? mi + (i + 1) : mi - (i + 1)) % 60;
      if (idx < 0) idx += 60;
      var g = GAN[idx % 10], z = ZHI[idx % 12];
      dayun.push({
        step: i + 1, gz: g + z,
        start_age: Math.round((start_age + i * 10) * 10) / 10,
        end_age: Math.round((start_age + (i + 1) * 10) * 10) / 10,
        nayin: nayin_name(g + z)
      });
    }

    var now_year = new Date().getFullYear();
    var liu_year = [];
    for (var yy = now_year - 2; yy <= now_year + 3; yy++) {
      var gz = GZ60[(yy - 4) % 60];
      liu_year.push({ year: yy, gz: gz, nayin: nayin_name(gz), shi_shen: ten_god(day_gan, gz[0]) });
    }

    return {
      four_pillars: {
        year: { gz: year_gz, nayin: nayin_name(year_gz), shi_shen: shi_shen[0] },
        month: { gz: month_gz, nayin: nayin_name(month_gz), shi_shen: shi_shen[1] },
        day: { gz: day_gz, nayin: nayin_name(day_gz), shi_shen: shi_shen[2] },
        hour: { gz: hour_gz, nayin: nayin_name(hour_gz), shi_shen: shi_shen[3] }
      },
      day_master: day_gan, day_element: day_elem, ten_gods: shi_shen,
      element_count: element_count, strength: strength, support: Math.round(support * 10) / 10,
      drain: Math.round(drain * 10) / 10, zodiac: lu.getYearShengXiao(),
      dayun_forward: forward, dayun_start_age: Math.round(start_age * 100) / 100,
      dayun: dayun, liu_year: liu_year
    };
  }

  // ============ 紫微 ============
  function _norm(n) { n = ((n % 12) + 12) % 12; return n === 0 ? 12 : n; }
  function _hour_to_shichen(hour) {
    var h = hour % 24;
    if (h === 23 || h < 1) return 1;
    return Math.floor((h - 1) / 2) + 2;
  }
  function _wuhu_dun(year_gan) {
    var t = { "甲": 2, "己": 2, "乙": 4, "庚": 4, "丙": 6, "辛": 6, "丁": 8, "壬": 8, "戊": 0, "癸": 0 };
    return t[year_gan];
  }
  var CHANG = { "甲": "巳", "乙": "午", "丙": "未", "丁": "申", "戊": "酉", "己": "戌", "庚": "亥", "辛": "子", "壬": "丑", "癸": "寅" };
  var WEN = { "甲": "亥", "乙": "戌", "丙": "酉", "丁": "申", "戊": "未", "己": "午", "庚": "巳", "辛": "辰", "壬": "卯", "癸": "寅" };
  var TIANKUI = { "甲": "丑", "戊": "丑", "庚": "丑", "乙": "子", "己": "子", "丙": "亥", "丁": "亥", "壬": "卯", "癸": "卯", "辛": "寅" };
  var TIANYUE = { "甲": "未", "戊": "未", "庚": "未", "乙": "申", "己": "申", "丙": "酉", "丁": "酉", "壬": "巳", "癸": "巳", "辛": "午" };
  var LUCUN = { "甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳", "丁": "午", "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子" };
  var HORSE = { "寅": "申", "午": "申", "戌": "申", "申": "寅", "子": "寅", "辰": "寅", "巳": "亥", "酉": "亥", "丑": "亥", "亥": "巳", "卯": "巳", "未": "巳" };
  var HUOXING_START = { "寅": 2, "午": 2, "戌": 2, "申": 3, "子": 3, "辰": 3, "巳": 4, "酉": 4, "丑": 4, "亥": 10, "卯": 10, "未": 10 };
  var LINGXING_START = { "寅": 4, "午": 4, "戌": 4, "申": 11, "子": 11, "辰": 11, "巳": 11, "酉": 11, "丑": 11, "亥": 3, "卯": 3, "未": 3 };

  function compute_ziwei(y, mo, d, h, mi, gender) {
    var S = Solar.fromYmdHms(y, mo, d, h, mi, 0);
    var lu = S.getLunar();
    var year_gz = lu.getYearInGanZhi();
    var year_gan = year_gz[0], year_zhi = year_gz[1];
    var month_lunar = lu.getMonth();
    if (month_lunar < 0) month_lunar = -month_lunar; // 闰月取绝对值（安星按实数）
    var shichen = _hour_to_shichen(h);
    var shichen_name = ZHI[shichen - 1] + "时";

    var M = _norm(3 + month_lunar - shichen);
    var M_zhi = ZHI[M - 1];
    var start = _wuhu_dun(year_gan);
    var mg_gan = GAN[(start + (M - 3)) % 10];
    var mg_gz = mg_gan + M_zhi;

    var ju_elem = nayin(mg_gz);
    var N = JU[ju_elem] || 5;
    var P = _norm(M + N - 1);

    var zp = {};
    zp["紫微"] = P; zp["天机"] = _norm(P - 1); zp["太阳"] = _norm(P - 2); zp["武曲"] = _norm(P - 3);
    zp["天同"] = _norm(P - 4); zp["廉贞"] = _norm(P - 5);
    var Q = _norm(14 - P);
    zp["天府"] = Q; zp["太阴"] = _norm(Q + 1); zp["贪狼"] = _norm(Q + 2); zp["巨门"] = _norm(Q + 3);
    zp["天相"] = _norm(Q + 4); zp["天梁"] = _norm(Q + 5); zp["七杀"] = _norm(Q + 6); zp["破军"] = _norm(Q + 7);

    var fp = {};
    fp["文昌"] = ZHI_INDEX[CHANG[year_gan]] + 1;
    fp["文曲"] = ZHI_INDEX[WEN[year_gan]] + 1;
    fp["左辅"] = _norm(month_lunar + 4);
    fp["右弼"] = _norm(month_lunar + 10);
    fp["天魁"] = ZHI_INDEX[TIANKUI[year_gan]] + 1;
    fp["天钺"] = ZHI_INDEX[TIANYUE[year_gan]] + 1;
    var lu_idx = ZHI_INDEX[LUCUN[year_gan]] + 1;
    fp["禄存"] = lu_idx; fp["擎羊"] = _norm(lu_idx + 1); fp["陀罗"] = _norm(lu_idx - 1);
    fp["天马"] = ZHI_INDEX[HORSE[year_zhi]] + 1;
    fp["火星"] = _norm(HUOXING_START[year_zhi] + (shichen - 1));
    fp["铃星"] = _norm(LINGXING_START[year_zhi] + (shichen - 1));
    fp["地空"] = _norm(12 + (shichen - 1));
    fp["地劫"] = _norm(13 - shichen);

    var palaces = [];
    for (var i = 0; i < ZIWEI_PALACES.length; i++) {
      var pz = _norm(M + i);
      var main = [], fu = [];
      for (var s in zp) if (zp[s] === pz) main.push(s);
      for (var s2 in fp) if (fp[s2] === pz) fu.push(s2);
      palaces.push({ palace: ZIWEI_PALACES[i], zhi: ZHI[pz - 1], stars: main, fu_stars: fu });
    }

    var sh = SIHUA[year_gan] || ["", "", "", ""];
    var sihua = { "禄": sh[0], "权": sh[1], "科": sh[2], "忌": sh[3] };
    var sihua_map = {}; sihua_map[sh[0]] = "禄"; sihua_map[sh[1]] = "权"; sihua_map[sh[2]] = "科"; sihua_map[sh[3]] = "忌";

    var sanfang = [0, 8, 4, 6], sanfang_stars = [];
    sanfang.forEach(function (idx) { palaces[idx].stars.forEach(function (s) { sanfang_stars.push(s); }); });

    var mg_stars = palaces[0].stars;
    return {
      mingong_zhi: M_zhi, mingong_gz: mg_gz, shichen: shichen_name, ju: ju_elem + N + "局",
      ziwei_zhi: ZHI[P - 1], stars_pos: zp, fu_stars_pos: fp, palaces: palaces,
      sihua: sihua, sihua_map: sihua_map, sanfang_sizheng: sanfang_stars,
      main_star: mg_stars[0] || "无主星(借对宫)", mingong_stars: mg_stars
    };
  }

  // ============ 周易 ============
  function _trigram_lines(gua) { return BAGUA_TRIGRAM[gua].slice(); }
  function meihua_qigua(four_pillars) {
    function num(gz) { return GAN_INDEX[gz[0]] + 1, ZHI_INDEX[gz[1]] + 1; }
    var yg = GAN_INDEX[four_pillars.year.gz[0]] + 1, yz = ZHI_INDEX[four_pillars.year.gz[1]] + 1;
    var mg = GAN_INDEX[four_pillars.month.gz[0]] + 1, mz = ZHI_INDEX[four_pillars.month.gz[1]] + 1;
    var dg = GAN_INDEX[four_pillars.day.gz[0]] + 1, dz = ZHI_INDEX[four_pillars.day.gz[1]] + 1;
    var hg = GAN_INDEX[four_pillars.hour.gz[0]] + 1, hz = ZHI_INDEX[four_pillars.hour.gz[1]] + 1;
    var up = (yg + mg + dg) % 8; if (up === 0) up = 8;
    var lo = (yz + mz + dz) % 8; if (lo === 0) lo = 8;
    var dong = (yg + yz + mg + mz + dg + dz + hg + hz) % 6; if (dong === 0) dong = 6;
    var up_gua = NUM_BAGUA[up], lo_gua = NUM_BAGUA[lo];
    var ben = HEX_NAMES[(up - 1) * 8 + (lo - 1)];
    var meaning = HEX_MEANING[ben] || "";
    var lo_lines = _trigram_lines(lo_gua), up_lines = _trigram_lines(up_gua);
    if (dong <= 3) lo_lines[dong - 1] ^= 1; else up_lines[dong - 4] ^= 1;
    var lo_gua2 = "", up_gua2 = "";
    for (var k in BAGUA_TRIGRAM) if (arrEq(BAGUA_TRIGRAM[k], lo_lines)) lo_gua2 = k;
    for (var k2 in BAGUA_TRIGRAM) if (arrEq(BAGUA_TRIGRAM[k2], up_lines)) up_gua2 = k2;
    var bian = HEX_NAMES[(BAGUA_NUM[up_gua2] - 1) * 8 + (BAGUA_NUM[lo_gua2] - 1)];
    return {
      up_gua: up_gua, lo_gua: lo_gua, ben_gua: ben, bian_gua: bian, dong_yao: dong,
      meaning: meaning, gua_elem: BAGUA_ELEMENT[up_gua], gua_nature: BAGUA_NATURE[up_gua],
      keywords: [up_gua, lo_gua, ben.indexOf("为") >= 0 ? ben.split("为")[0] : ben.slice(0, 2)]
    };
  }
  function arrEq(a, b) { if (a.length !== b.length) return false; for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false; return true; }

  // ============ 铁板 ============
  function _gan_num(g) { return GAN_INDEX[g] + 1; }
  function _zhi_num(z) { return ZHI_INDEX[z] + 1; }
  function _to_tieban_number(n) { var s = String(((n % 1000) + 1000) % 1000); return ("000" + s).slice(-3); }
  function compute_tieban(bazi, ziwei) {
    var fp = bazi.four_pillars;
    var day_gz = fp.day.gz, hour_gz = fp.hour.gz, year_gz = fp.year.gz;
    var base = (_gan_num(day_gz[0]) * 10 + _zhi_num(day_gz[1])) + (_gan_num(hour_gz[0]) * 10 + _zhi_num(hour_gz[1]));
    var tiaowen = [];
    var bi_jie = bazi.ten_gods.filter(function (s) { return s === "比肩" || s === "劫财"; }).length;
    var bro_count = Math.max(0, bi_jie - 1 + (bazi.day_element === "木" || bazi.day_element === "水" ? 1 : 0));
    var bro_num = _to_tieban_number(base + bro_count * 7 + 11);
    tiaowen.push({ number: bro_num, dimension: "兄弟", text: "兄弟（含同胞）约 " + bro_count + " 位；铁板数 " + bro_num + " 主「手足之数」。", verify: "可凭实际同胞数反推时辰——若不符，宜复核出生时辰。" });
    var parent_elem = nayin(year_gz);
    var parent_palace = ziwei.palaces.filter(function (p) { return p.palace === "父母"; })[0];
    var parent_star = parent_palace.stars.join("、") || "无主星";
    var par_num = _to_tieban_number(base + 23);
    tiaowen.push({ number: par_num, dimension: "父母", text: "父母宫见 " + parent_star + "；年柱纳音属 " + parent_elem + "，主双亲缘分与帮扶之象。", verify: "可凭父母健康/生肖/缘分深浅印证，作为考时佐证。" });
    var spouse_palace = ziwei.palaces.filter(function (p) { return p.palace === "夫妻"; })[0];
    var spouse_star = spouse_palace.stars.join("、") || "无主星";
    var sp_num = _to_tieban_number(base + 41);
    tiaowen.push({ number: sp_num, dimension: "配偶", text: "夫妻宫见 " + spouse_star + "；日支为 " + day_gz[1] + "，主配偶性情与婚姻互动之象。", verify: "可凭配偶性格/相遇方式印证，辅助判断时辰准确度。" });
    var child_palace = ziwei.palaces.filter(function (p) { return p.palace === "子女"; })[0];
    var child_star = child_palace.stars.join("、") || "无主星";
    var ch_num = _to_tieban_number(base + 59);
    tiaowen.push({ number: ch_num, dimension: "子女", text: "子女宫见 " + child_star + "；时柱 " + hour_gz + "，主子女缘分与晚景之象。", verify: "可凭子女缘分/数量印证，为考时之尾验。" });
    return { base_number: _to_tieban_number(base), tiaowen: tiaowen };
  }

  // ============ 交叉验证 ============
  var DIMS = ["性格", "事业", "财运", "婚姻", "家庭(六亲)", "健康", "时机运势"];
  var STAR_NATURE = {
    "紫微": "尊贵领导，好胜有主见", "天机": "机敏善谋，喜变动", "太阳": "光明磊落，重名誉",
    "武曲": "刚毅果决，主财帛奋斗", "天同": "温和知足，尚安享", "廉贞": "敏慧重情，带桃花波折",
    "天府": "稳重保守，库藏充盈", "太阴": "阴柔内秀，重情感细节", "贪狼": "多才欲强，善交际偏桃花",
    "巨门": "口才明辨，易生口舌", "天相": "端庄辅佐，衣食安稳", "天梁": "慈荫化解，遇难呈祥",
    "七杀": "刚烈开创，孤克进取", "破军": "破旧立新，多波折变动"
  };
  var JI_STARS = { "紫微": 1, "太阳": 1, "武曲": 1, "天同": 1, "天府": 1, "太阴": 1, "天相": 1, "天梁": 1 };
  var FU_STAR_NATURE = {
    "文昌": "文采才学，利考试文书", "文曲": "才艺口才，利文艺", "左辅": "帮扶助力，人缘贵气", "右弼": "辅佐协力，团队得利",
    "天魁": "阳贵，逢凶化吉得长辈助", "天钺": "阴贵，暗处女性贵人", "禄存": "财库稳固，聚财不露", "天马": "奔波变动，利远行迁移",
    "擎羊": "刚烈波折，主竞争伤灾", "陀罗": "纠缠反复，做事拖延", "火星": "火急爆发，成败迅速", "铃星": "暗火闷进，隐患慢性",
    "地空": "虚耗落空，宜务实", "地劫": "劫夺损耗，防破财"
  };
  var FU_GOOD = { "文昌": 1, "文曲": 1, "左辅": 1, "右弼": 1, "天魁": 1, "天钺": 1, "禄存": 1, "天马": 1 };
  var FU_BAD = { "擎羊": 1, "陀罗": 1, "火星": 1, "铃星": 1, "地空": 1, "地劫": 1 };
  function _clamp(x) { return Math.max(1, Math.min(5, x)); }

  function bazi_signals(bazi) {
    var dm = bazi.day_master, elem = bazi.day_element, tg = bazi.ten_gods, four = bazi.four_pillars, strength = bazi.strength;
    var s_level = { "身旺": 4, "中和": 3, "身弱": 2 }[strength];
    var char_parts = ["日主" + elem + "（" + dm + "）" + strength];
    var key_gods = tg.filter(function (g) { return ["伤官", "食神", "正印", "偏印", "七杀", "比肩", "劫财"].indexOf(g) >= 0; });
    if (key_gods.length) char_parts.push("，十神见" + key_gods.join("、"));
    var char_text = "性格：" + char_parts.join("");
    var char_level = _clamp(s_level + (tg.indexOf("伤官") >= 0 || tg.indexOf("食神") >= 0 ? 1 : 0) - (tg.indexOf("正印") >= 0 || tg.indexOf("偏印") >= 0 ? 1 : 0));
    var guan = tg.filter(function (g) { return g === "正官" || g === "七杀"; }).length;
    var career = guan && strength !== "身弱" ? ["事业星（官杀）得力，宜公职/管理/专业赛道", 4]
      : guan && strength === "身弱" ? ["事业星现但身弱，压力大、宜借平台与人扶", 2]
        : ["无显官杀，宜自由业/技术/自我经营", 3];
    var cai = tg.filter(function (g) { return g === "正财" || g === "偏财"; }).length;
    var wealth = cai && strength !== "身弱" ? ["财星得用，财源可聚，宜理财生财", 4]
      : cai && strength === "身弱" ? ["财星现而身弱，财来财去，宜稳守", 2]
        : ["财星不显，财凭技艺/因缘，宜节流", 3];
    var spouse_star = bazi.gender === "女" ? "官" : "财";
    var marriage = cai && strength !== "身弱" ? ["夫妻宫与配偶星相称，婚姻较稳，宜择性格互补者", 4]
      : cai ? ["配偶星现而身弱，婚缘有波，宜晚婚/互谅", 2]
        : ["配偶星不显，婚姻平淡或晚成，重精神契合", 3];
    var bi_jie = tg.filter(function (g) { return g === "比肩" || g === "劫财"; }).length;
    var yin = tg.filter(function (g) { return g === "正印" || g === "偏印"; }).length;
    var shi_shang = tg.filter(function (g) { return g === "食神" || g === "伤官"; }).length;
    var fam_text = "父母缘（印星" + (yin ? "有" : "弱") + "）、手足（比劫" + bi_jie + "）、子女缘（食伤" + (shi_shang ? "有" : "弱") + "）";
    var fam_level = _clamp(3 + (yin ? 1 : 0) + (bi_jie >= 2 ? 1 : 0) - (shi_shang ? 0 : 1));
    var ec = bazi.element_count, weak_elem = ELEMENTS[0], we = 99;
    ELEMENTS.forEach(function (e) { if (ec[e] < we) { we = ec[e]; weak_elem = e; } });
    var organ = { "木": "肝/筋骨", "火": "心/血脉", "土": "脾胃", "金": "肺/呼吸道", "水": "肾/泌尿" }[weak_elem];
    var health = ec[weak_elem] === 0 ? ["五行缺" + weak_elem + "（" + organ + "系统偏弱），宜早养", 2] : ["五行尚匀，先天体质平顺，仍须起居有常", 4];
    var now = bazi.liu_year, cur = now[2], ss = cur.shi_shen;
    var timing = ["正印", "偏印", "比肩", "劫财", "正财", "偏财"].indexOf(ss) >= 0 ? ["流年 " + cur.year + " " + cur.gz + "（" + ss + "），利守成积累", 4]
      : ["七杀", "伤官"].indexOf(ss) >= 0 ? ["流年 " + cur.year + " " + cur.gz + "（" + ss + "），变动挑战并存，宜谨慎", 2]
        : ["流年 " + cur.year + " " + cur.gz + "（" + ss + "），平运渐进", 3];
    return { "性格": [char_text, char_level], "事业": career, "财运": wealth, "婚姻": marriage, "家庭(六亲)": [fam_text, fam_level], "健康": health, "时机运势": timing };
  }
  function ziwei_signals(ziwei) {
    var res = {}, mg = ziwei.mingong_stars, mg_fu = (ziwei.palaces[0].fu_stars || []), all_mg = mg.concat(mg_fu);
    if (all_mg.length) {
      var nat = all_mg.map(function (s) { return STAR_NATURE[s] || FU_STAR_NATURE[s] || s; }).join("；");
      var lvl = mg.some(function (s) { return JI_STARS[s]; }) ? 4 : 3;
      if (mg_fu.some(function (s) { return FU_BAD[s]; })) lvl = _clamp(lvl - 0.3);
      var fu_txt = mg_fu.length ? (" + " + mg_fu.join("、")) : "";
      res["性格"] = ["命宫 " + (mg[0] || "借对宫") + fu_txt + "：" + nat, lvl];
    } else res["性格"] = ["命宫无主星（借对宫），性情随环境而变", 3];
    var palace_map = { "官禄": "事业", "财帛": "财运", "夫妻": "婚姻", "父母": "家庭(六亲)", "兄弟": "家庭(六亲)", "子女": "家庭(六亲)", "疾厄": "健康", "迁移": "时机运势" };
    ziwei.palaces.forEach(function (palace) {
      var dim = palace_map[palace.palace]; if (!dim) return;
      var stars = (palace.stars || []).concat(palace.fu_stars || []);
      var nat, lvl;
      if (stars.length) { nat = stars.map(function (s) { return STAR_NATURE[s] || FU_STAR_NATURE[s] || s; }).join("；"); lvl = palace.stars.some(function (s) { return JI_STARS[s]; }) ? 4 : 3; }
      else { nat = "空宫（借对宫星情）"; lvl = 3; }
      palace.stars.forEach(function (s) {
        if (ziwei.sihua_map[s] === "禄" || ziwei.sihua_map[s] === "权" || ziwei.sihua_map[s] === "科") lvl = _clamp(lvl + 0.5);
        else if (ziwei.sihua_map[s] === "忌") lvl = _clamp(lvl - 1);
      });
      (palace.fu_stars || []).forEach(function (s) { if (FU_GOOD[s]) lvl = _clamp(lvl + 0.3); else if (FU_BAD[s]) lvl = _clamp(lvl - 0.3); });
      var text = palace.palace + "宫：" + nat;
      if (res[dim]) res[dim] = [res[dim][0] + "；" + text, _clamp((res[dim][1] + lvl) / 2)];
      else res[dim] = [text, lvl];
    });
    if (!res["时机运势"]) res["时机运势"] = ["三方四正：" + ziwei.sanfang_sizheng.join("、") + "；四化禄" + ziwei.sihua["禄"] + "权" + ziwei.sihua["权"] + "科" + ziwei.sihua["科"] + "忌" + ziwei.sihua["忌"], 3];
    return res;
  }
  function yijing_signals(yijing, bazi) {
    var elem = bazi.day_element, ge = yijing.gua_elem;
    var polar = (SHENG[ge] === elem || ge === elem) ? 4 : (KE[ge] === elem || KE[elem] === ge) ? 2 : 3;
    var char = ["本卦 " + yijing.ben_gua + "（" + yijing.gua_nature + "），主性格取向：" + yijing.meaning, _clamp(polar)];
    var timing = ["卦象五行属 " + ge + "，对日主" + elem + "为" + (polar === 4 ? "生扶" : polar === 2 ? "克泄" : "中和") + "之象；变卦 " + yijing.bian_gua + " 示动爻" + yijing.dong_yao + "之转机", polar];
    return { "性格": char, "时机运势": timing };
  }
  function tieban_signals(tieban) {
    var res = {}, votes = {};
    tieban.tiaowen.forEach(function (x) { votes[x.dimension] = x; });
    var dim_map = { "兄弟": "家庭(六亲)", "父母": "家庭(六亲)", "配偶": "婚姻", "子女": "家庭(六亲)" };
    for (var d in votes) {
      var dim = dim_map[d] || "家庭(六亲)";
      var text = "铁板数 " + votes[d].number + "（" + d + "）：" + votes[d].text;
      if (res[dim]) res[dim] = [res[dim][0] + "；" + text, 3]; else res[dim] = [text, 3];
    }
    return [res, votes];
  }

  // ============ 相学（面相 / 手相）信号 ============
  // 五行配属（传统相学框架，透明可考；面相/手相为辅助维度，须与命理四体系互参）
  var FACE_MIANXING = { "圆润·水": "水", "方正·金": "金", "修长·木": "木", "上尖下阔·火": "火", "厚宽·土": "土" };
  var PALM_XING = { "金型·方硬": "金", "木型·修长": "木", "水型·圆润": "水", "火型·尖削": "火", "土型·厚实": "土" };
  var TONE_ELEM = { "红·火": "火", "白·金": "金", "青·木": "木", "黑·水": "水", "黄·土": "土" };
  var XIANG_ELEM_DIM = { "木": "性格", "火": "时机运势", "土": "财运", "金": "婚姻", "水": "家庭(六亲)" };
  function _xiang_aggregate(contrib, ev) {
    var out = {};
    DIMS.forEach(function (dim) {
      var s = contrib[dim] || 0;
      var lvl = _clamp(Math.round(3 + s));
      var txt = ev.filter(function (e) { return e.dim === dim; }).map(function (e) { return e.t; }).join("；");
      out[dim] = [txt || "（面相/手相未提供该维度显著特征信号）", lvl];
    });
    return out;
  }
  function face_signals(obs, px) {
    var contrib = {}, ev = [];
    function add(dim, w, t) { contrib[dim] = (contrib[dim] || 0) + w; ev.push({ dim: dim, t: t }); }
    var mx = FACE_MIANXING[obs.mianxing];
    if (mx === "水") add("家庭(六亲)", 0.3, "面型圆润属水（传统相学「水形主智、主荫」）：肾气通于耳，六亲缘分与人缘较润泽");
    else if (mx === "金") { add("性格", 0.3, "面型方正属金（金主义、性刚）：有原则、决断明快"); add("婚姻", 0.2, "面型方正属金：义气分明，感情中有主见"); }
    else if (mx === "木") { add("性格", 0.4, "面型修长属木（木主仁、主生发）：仁直上进、善规划"); add("事业", 0.2, "面型修长属木：宜成长型赛道与专业深耕"); }
    else if (mx === "火") { add("性格", 0.3, "面型上尖下阔属火（火主礼、外露）：热情反应快、易显达"); add("时机运势", 0.2, "面型属火：机遇与起伏并存，宜乘势亦防躁"); }
    else if (mx === "土") { add("财运", 0.4, "面型厚宽属土（土主信、主库）：诚信稳重，财有根基"); add("事业", 0.2, "面型厚宽属土：踏实可信，事业靠积累而成"); }
    if (obs.shangting === "饱满") { add("家庭(六亲)", 0.4, "上停（额为离火、主早年与父荫）饱满：早年顺、智力佳"); add("性格", 0.2, "上停饱满：思虑清明、胸有丘壑"); }
    else if (obs.shangting === "窄陷") { add("家庭(六亲)", -0.3, "上停窄陷：早年与父缘或欠顺，宜自强立基"); add("性格", -0.2, "上停窄陷：易多思、临事宜果断"); }
    if (obs.zhongting === "鼻丰") { add("事业", 0.4, "中停鼻丰（鼻为土、财帛宫）丰隆：中年事业有靠、执行力强"); add("财运", 0.3, "鼻丰为财帛宫得地：财源可聚、宜理财"); }
    else if (obs.zhongting === "鼻陷") { add("事业", -0.3, "中停鼻陷：中年事业助力偏弱，宜借平台"); add("财运", -0.3, "鼻陷：守财宜谨慎、防漏财"); }
    if (obs.xiating === "方圆") { add("财运", 0.3, "下停（颔腮为地阁）方圆：晚景与子禄丰实"); add("家庭(六亲)", 0.2, "下停方圆：晚年家庭安稳、有依靠"); }
    else if (obs.xiating === "尖削") { add("财运", -0.3, "下停尖削：晚景财禄宜早蓄、忌散漫"); }
    var wg = obs.wuguan || {};
    if (wg.er === "佳") { add("家庭(六亲)", 0.3, "耳（肾开窍于耳、属水）轮廓分明：肾气足、祖荫与听力好"); add("健康", 0.2, "耳佳：肾系统平顺、先天禀赋好"); }
    else if (wg.er === "弱") { add("家庭(六亲)", -0.3, "耳弱/招风：肾气偏弱，早年间或有耗散"); add("健康", -0.2, "耳弱：留意肾与听力、勿过劳"); }
    if (wg.mei === "佳") { add("性格", 0.2, "眉（肝华在眉、属木）清秀：性情中和"); add("事业", 0.2, "眉佳：谋略有序、善协调"); }
    else if (wg.mei === "弱") { add("性格", -0.2, "眉杂/逆：性急易躁、宜修涵养"); }
    if (wg.yan === "佳") { add("性格", 0.2, "眼（心之官、属火）有神：心智明亮、判断清"); add("时机运势", 0.2, "眼神清亮：临机有断、时机判断佳"); }
    else if (wg.yan === "弱") { add("时机运势", -0.2, "眼神黯/无神：临事宜缓、多核再决"); }
    if (wg.bi === "佳") { add("财运", 0.3, "鼻（脾之部、属土）挺阔：财库丰盈"); add("事业", 0.2, "鼻佳：中年运稳、承载力强"); }
    else if (wg.bi === "弱") { add("财运", -0.3, "鼻弱/露孔：财易漏，宜储蓄节流"); }
    if (wg.kou === "佳") { add("婚姻", 0.2, "口（肺之窍、属金）端正：言语有度，感情沟通佳"); add("健康", 0.2, "口佳：脾胃纳运好、后天之本足"); }
    else if (wg.kou === "弱") { add("婚姻", -0.2, "口歪/薄：沟通易生误，感情多体谅包容"); }
    if (obs.qise === "红润") { add("时机运势", 0.3, "气色红润（火得其位）：气血畅达、时机佳"); add("健康", 0.2, "红润：心气足、营卫和"); }
    else if (obs.qise === "黄润") { add("财运", 0.2, "气色黄润（土气充）：脾胃纳运好、财稳"); add("健康", 0.2, "黄润：土气充、中州安"); }
    else if (obs.qise === "青暗") { add("健康", -0.3, "气色青暗（木郁）：肝/气机不舒，宜疏解"); add("时机运势", -0.2, "青暗：近期宜守、忌躁进"); }
    else if (obs.qise === "苍白") { add("健康", -0.2, "气色苍白（金过伤营）：肺卫偏弱，防外感"); }
    else if (obs.qise === "晦暗") { add("时机运势", -0.3, "气色晦暗：运势暂滞，蓄势待时"); }
    if (px && px.tone && TONE_ELEM[px.tone]) {
      var pe = TONE_ELEM[px.tone], pdim = XIANG_ELEM_DIM[pe];
      add(pdim, px.brightness > 0.55 ? 0.6 : 0.3, "【自动·像素气色】照片主色偏" + px.tone + "、明亮度" + (px.brightness > 0.55 ? "高" : "中") + "（红=火/白=金/青=木/黑=水/黄=土）：以客观像素佐证" + pdim + "（" + pe + "行）之气");
    }
    (obs.zhiwen || []).forEach(function (z) {
      if (z === "奸门(眼尾)痣/纹") add("婚姻", -0.2, "奸门（眼尾、妻妾宫）见痣纹：夫妻宫受扰，感情宜多沟通");
      else if (z === "法令清晰") add("事业", 0.2, "法令（主威仪、晚年权柄）清晰：执行力与口碑佳");
      else if (z === "印堂窄/纹乱") add("性格", -0.2, "印堂（主思虑）窄乱：易忧思，临事缓决");
      else if (z === "人中有痣/陷") add("家庭(六亲)", -0.2, "人中（主子女、沟洫）有痣/陷：子女缘宜留意养护");
    });
    return _xiang_aggregate(contrib, ev);
  }
  function palm_signals(obs, px) {
    var contrib = {}, ev = [];
    function add(dim, w, t) { contrib[dim] = (contrib[dim] || 0) + w; ev.push({ dim: dim, t: t }); }
    var px_ = PALM_XING[obs.palmxing];
    if (px_ === "金") { add("婚姻", 0.3, "掌型方硬属金（金主义、有界）：果决、感情有边界"); add("性格", 0.2, "金型掌：刚毅、重信诺"); }
    else if (px_ === "木") { add("性格", 0.4, "掌型修长属木（木主仁、善思）：仁善、宜文技艺业"); add("事业", 0.2, "木型掌：宜文职/技艺、靠专业立身"); }
    else if (px_ === "水") { add("家庭(六亲)", 0.3, "掌型圆润属水（水主智、主变）：聪慧、人缘润"); add("时机运势", 0.2, "水型掌：机变灵活、善借势"); }
    else if (px_ === "火") { add("性格", 0.3, "掌型尖削属火（火主礼、易动）：热情、易起伏"); add("时机运势", 0.2, "火型掌：易有机遇亦易波动，宜稳进"); }
    else if (px_ === "土") { add("财运", 0.4, "掌型厚实属土（土主信、主库）：诚信、财有根基"); add("事业", 0.2, "土型掌：踏实积累、靠口碑成事"); }
    if (obs.life === "深长清晰") add("健康", 0.5, "生命线（主先天体质与生命力）深长清晰：禀赋强、抗病佳");
    else if (obs.life === "浅短") add("健康", -0.4, "生命线浅短：体质偏弱，宜早养、勿透支");
    else if (obs.life === "中断/岛纹") add("健康", -0.5, "生命线见中断/岛纹：健康有波，定期体检、重大事宜谨慎");
    if (obs.wisdom === "长而清晰") { add("性格", 0.4, "智慧线（主思维与谋略）长清：缜密善谋"); add("事业", 0.2, "智慧线佳：专业力强、宜技术路线"); }
    else if (obs.wisdom === "短而乱") add("性格", -0.2, "智慧线短乱：思虑易散，重大决策多核");
    if (obs.emotion === "清晰无杂") add("婚姻", 0.4, "感情线（主情缘）清晰：情感稳定、婚恋顺");
    else if (obs.emotion === "断裂/杂纹多") add("婚姻", -0.4, "感情线断裂杂：情感波折，宜多沟通、晚婚更稳");
    if (obs.wealth === "清晰") add("财运", 0.4, "财运线/玉柱纹（主财源）清晰：财可聚、有规划");
    else if (obs.wealth === "不明显") add("财运", -0.2, "财运线不显：财凭技艺与因缘，宜节流蓄");
    if (obs.finger === "修长") add("性格", 0.2, "手指修长：心细、善艺");
    else if (obs.finger === "短粗") add("性格", -0.1, "手指短粗：性直、重实干");
    if (px && px.tone && TONE_ELEM[px.tone]) {
      var pe = TONE_ELEM[px.tone], pdim = XIANG_ELEM_DIM[pe];
      add(pdim, px.brightness > 0.55 ? 0.5 : 0.3, "【自动·像素气色】掌色偏" + px.tone + "、明亮度" + (px.brightness > 0.55 ? "高" : "中") + "（红=火/白=金/青=木/黑=水/黄=土）：以客观像素佐证" + pdim + "（" + pe + "行）之气");
    }
    if (obs.pcolor === "红润") { add("健康", 0.2, "掌色红润（火得其位）：气血足"); add("时机运势", 0.2, "掌色红润：时机佳、可主动"); }
    else if (obs.pcolor === "青白") add("健康", -0.2, "掌色青白（木金偏胜）：气血偏弱，宜调补");
    return _xiang_aggregate(contrib, ev);
  }
  // 人生指导总览：综合四体系交叉验证结果，产出分维度建议 + 优势/短板 + 大运阶段策略 + 综合总览
  function _life_guidance(matrix, bazi, xi_set, ji_set, cons_counts, review_flags, nSys) {
    var day_gan = bazi.day_master;
    var strengths = [], cautions = [], dim_tips = {};
    var DIM_ADVICE = {
      "性格": function (dir) { return dir === "吉/强" ? "你自我认知清晰、气质鲜明。把长处用在建立个人口碑与专业标签上，少在不相干的人面前过度暴露底牌。" : dir === "平" ? "你性情中和、可塑性强。别急着给自己贴固定标签，多在不同环境里试，靠反馈校准自我。" : "你内在有矛盾张力。遇事多自省，借可信赖的外界反馈校准定位，别在情绪头上下决定。"; },
      "事业": function (dir) { return dir === "吉/强" ? "事业动能强。主动争取、承担更大责任、打磨专业壁垒；但顺境里也别放松风控、别盲目加注。" : dir === "平" ? "稳中有进。先把手艺做深、把人脉做厚，不急于跳槽或跃迁，等窗口。" : "事业承压期。借平台与团队、别单兵冒进，也别频繁跳槽——越动越乱，先稳住再图。"; },
      "财运": function (dir) { return dir === "吉/强" ? "财源顺。稳健理财、留应急金，偏财只动闲钱，不追加杠杆。" : dir === "平" ? "守成为主。控支出、防借贷与冲动消费，别替人担保背债。" : "财运偏弱。留足应急、降杠杆、以技能变现为本，投资能不碰就不碰。"; },
      "婚姻": function (dir) { return dir === "吉/强" ? "感情配对较顺。在互补中经营、择时而定，别因顺利就忽略沟通。" : dir === "平" ? "重精神契合、多沟通，晚婚或成熟后更稳，别被催婚推着走。" : "婚缘有波折之象。互相体谅、重大决定缓步，防外部干扰与旧账翻腾，婚前把财产与期待谈清。"; },
      "家庭(六亲)": function (dir) { return dir === "吉/强" ? "六亲缘分与家庭支持较足。珍惜亲情、反哺长辈，也别因顾家耽误自身成长。" : dir === "平" ? "维系纽带、尽责尽份，平淡中见真情，别让忙成为疏远的借口。" : "亲缘或有疏离/牵挂。主动联络、尽早在关键处尽心力，别等事了才后悔。"; },
      "健康": function (dir) { return dir === "吉/强" ? "先天体质尚可。保持起居有常、定期体检即可，别仗着底子好透支。" : dir === "平" ? "规律作息、适度锻炼，盯紧薄弱环节，小毛病别拖。" : "健康提示偏多。定期体检、早养薄弱环节、绝不透支，把身体当资产管。"; },
      "时机运势": function (dir) { return dir === "吉/强" ? "近年窗口偏吉。把握节奏主动作为，但也别在顺境里放松风控。" : dir === "平" ? "顺势而为、择机而动，不强行，重大变动先备预案。" : "时机偏守。蓄势待时、以静制动，重大决策暂缓，先把风险敞口降下来。"; }
    };
    matrix.forEach(function (m) {
      var dir = m.mean_level >= 4 ? "吉/强" : (m.mean_level >= 3 ? "平" : "弱/宜守");
      dim_tips[m.dimension] = DIM_ADVICE[m.dimension] ? DIM_ADVICE[m.dimension](dir) : "参考综合评级顺势而为。";
      if (m.consistency === "高一致" && m.mean_level >= 4) strengths.push(m.dimension + "：" + (nSys || 4) + "体系高度一致且评级强，是你可以重点发力、放心投入的人生领域");
      if (m.consistency === "分歧" || m.mean_level < 3) cautions.push(m.dimension + "：结论分歧或评级偏弱，是容易踩坑的方面——重大决策放慢、以现实反馈校准，别凭感觉冲");
    });
    if (!strengths.length) strengths.push((nSys || 4) + "体系整体以「平」为主，没有特别突出的长板，宜在均衡中稳步积累，不必急于求成");
    if (!cautions.length) cautions.push("暂无明显短板预警，但「平」也意味着没有躺赢的运气，保持节奏、居安思危即可");
    var phase = [];
    if (bazi.dayun.length) {
      if (bazi.dayun[0].start_age > 0) phase.push({ range: "0–" + (Math.round(bazi.dayun[0].start_age) - 1) + "岁（起运前）", gz: "命局", tip: "未起运，依本命局之势：以学业、心性养成与家庭支持为主，别急着闯荡或大额押注" });
      bazi.dayun.forEach(function (d) {
        var god = ten_god(day_gan, d.gz[0]);
        var fav = xi_set.indexOf(god) >= 0, bad = ji_set.indexOf(god) >= 0;
        var tip = fav ? "此运干支为喜，十年动能偏顺——宜把握机会、主动进取、扩大成果；但顺境也别放松风控、别盲目加注。"
          : bad ? "此运干支为忌，是守成蓄势的十年——控风险、重大决策三思、不替人担保、不盲目加杠杆，以稳换空间。"
          : "此运平气，稳扎稳打、积累实力与资源，不躁不怠，别主动制造大变动。";
        phase.push({ range: Math.round(d.start_age) + "–" + Math.round(d.end_age - 1) + "岁", gz: d.gz, tip: tip });
      });
    }
    var overall = "综合" + (nSys || 4) + "体系交叉验证：高一致 " + cons_counts["高一致"] + " 项、中一致 " + cons_counts["中一致"] + " 项、分歧 " + cons_counts["分歧"] +
      " 项。可以重点发力的领域：「" + strengths.join("；") + "」；需要设防、别踩坑的方面：「" + cautions.join("；") + "」。" +
      "人生策略上，你身" + bazi.strength + "，用神宜取" + (bazi.strength === "身弱" ? "印比（学习、合作、稳健托底）" : "食伤财官（表达、务实、进取兑现）") +
      "——喜运的十年主动出击、放大成果，忌运的十年收着点、先把风险敞口降下来。";
    if (review_flags.length) overall += " 另：" + review_flags.join("");
    return { overall: overall, strengths: strengths, cautions: cautions, dimension_tips: dim_tips, by_phase: phase };
  }

  // ============ 人生行动指南（用户视角：把多维交叉验证结论翻译成可执行的「避坑手册」）============
  // 目标：用户不只看到一堆术语，而是清楚「当下该进攻还是防守、哪些重大决策今年能碰、该做/别做/留意什么」。
  function _action_playbook(bazi, cv, liu) {
    function gz2(g) { return g && g.length === 2 ? g[0] + g[1] : "—"; }
    var day_gan = bazi.day_master;
    var xiji = _xi_ji_sets(bazi), xi_set = xiji[0], ji_set = xiji[1];
    var cur = null; liu.rows.forEach(function (r) { if (r.is_current) cur = r; });
    var dy = cur ? cur.dayun_gz : "—";
    var dy_god = dy !== "—" ? ten_god(day_gan, dy[0]) : null;
    var dy_fav = !!dy_god && xi_set.indexOf(dy_god) >= 0;
    var dy_bad = !!dy_god && ji_set.indexOf(dy_god) >= 0;
    var cons_hi = cv.cons_counts["高一致"];
    var curScore = cur ? cur.score : 0;
    var curGrade = cur ? cur.grade : "平";
    var dimOf = {}; cv.matrix.forEach(function (m) { dimOf[m.dimension] = m; });

    // 1) 当下窗口判定：进攻 / 防守 / 蓄力（综合大运喜忌 + 流年评分 + 交叉一致性）
    var win, winCls, winWhy;
    if (dy_fav && curScore >= 0.3 && curGrade !== "凶" && curGrade !== "平偏凶") {
      win = "进攻窗口 · 宜主动推进"; winCls = "hi";
      winWhy = "当前大运「" + gz2(dy) + "」属你喜用，且流年" + gz2(cur.gz) + "动能偏顺（评分 " + curScore + "）。多重信号同向，是落地关键目标的窗口——可主动争取、扩大成果，但仍须保留风控底线，不盲目加注。";
    } else if (dy_bad || curScore <= -0.3 || curGrade === "凶" || curGrade === "平偏凶") {
      win = "防守蓄势 · 宜稳不宜动"; winCls = "lo";
      winWhy = "当前" + (dy_bad ? ("大运「" + gz2(dy) + "」为忌") : "") + (curScore <= -0.3 ? ("、流年动能偏弱（评分 " + curScore + "）") : "") + (dy === "—" ? "、尚依本命局" : "") + "。信号偏收敛，这一年以「避坑、守成、降风险」为主：重大决策暂缓，不辞职、不盲目投资、不替人担保、合同反复审。";
    } else {
      win = "平稳蓄力 · 顺势而为"; winCls = "mid";
      winWhy = "当前大运「" + gz2(dy) + "」(" + (dy_god || "本命") + ") 属平气，流年评分 " + curScore + " 居中。不强行、不躁进，把现有摊子稳住、把能力与资源做厚，等下一个进攻窗口。";
    }
    winWhy += (cons_hi >= 4 ? " 交叉验证高一致维度多，判断可信度较高，可放心据此发力。"
      : cons_hi >= 1 ? " 交叉验证以中一致为主，关键动作仍辅以现实反馈校准。"
        : " 交叉验证存在分歧，重大动作前先小步试错、以现实反馈校准。");

    // 2) 重大决策红绿灯（六类常见重大决定）
    var decisions = [];
    (function () { // 跳槽 / 求职
      var ss = cur ? cur.shi_shen : "", light, text;
      if (cur && xi_set.indexOf(ss) >= 0 && (ss === "正官" || ss === "七杀" || ss === "正印" || ss === "偏印")) { light = "green"; text = "今年利掌权、进阶与考证，可主动争取管理岗或专业突破；签约留书面凭证。"; }
      else if (cur && ji_set.indexOf(ss) >= 0 && (ss === "七杀" || ss === "伤官")) { light = "red"; text = "今年职场压力与是非偏重，不宜裸辞或强出头，人事变动先忍一步、缓一缓。"; }
      else { light = "amber"; text = "职场平稳。跳槽/转岗可择机，但务必先备退路、写清权责边界再动。"; }
      decisions.push({ name: "跳槽 / 求职", light: light, text: text });
    })();
    (function () { // 投资 / 理财
      var ss = cur ? cur.shi_shen : "", light, text;
      if (cur && xi_set.indexOf(ss) >= 0 && (ss === "正财" || ss === "偏财") && curScore >= 0.3) { light = "green"; text = "财星为喜，可稳健理财、留足应急金，偏财只动闲钱，不追加杠杆。"; }
      else if (curScore <= -0.3 || (cur && ji_set.indexOf(ss) >= 0 && (ss === "正财" || ss === "偏财"))) { light = "red"; text = "今年财运宜守：不新增贷款、不替人担保、投资只做闲钱甚至不投，先保现金流。"; }
      else { light = "amber"; text = "财运中性，量入为出、不投机、不替人担保背债。"; }
      decisions.push({ name: "投资 / 理财", light: light, text: text });
    })();
    (function () { // 创业 / 副业
      var ss = cur ? cur.shi_shen : "", light, text;
      if (cur && xi_set.indexOf(ss) >= 0 && (ss === "食神" || ss === "伤官" || ss === "正财" || ss === "偏财") && dy_fav) { light = "green"; text = "食伤/财星为喜且运程相佐，可小步试水副业或创业，验证后再放大投入。"; }
      else if (dy_bad || curScore <= -0.3) { light = "red"; text = "忌运/动能偏弱，不宜押重金创业，先以主业稳收、控制试错成本。"; }
      else { light = "amber"; text = "创业可先以副业试水，控制投入、跑通模式后再考虑放大。"; }
      decisions.push({ name: "创业 / 副业", light: light, text: text });
    })();
    (function () { // 婚恋 / 同居
      var m = dimOf["婚姻"]; var lv = m ? m.mean_level : 3; var cons = m ? m.consistency : "中一致"; var light, text;
      if (lv >= 4 && cons === "高一致") { light = "green"; text = "感情缘分较顺且体系一致，可稳步推进关系、择时而定。"; }
      else if (lv < 3) { light = "red"; text = "今年婚缘波折之象偏重，重大决定缓步，婚前把财产与期待谈清、防外部干扰。"; }
      else { light = "amber"; text = "重精神契合、多沟通；晚婚或成熟后更稳，别被催婚推着走。"; }
      decisions.push({ name: "婚恋 / 同居", light: light, text: text });
    })();
    (function () { // 买房 / 大宗消费
      var ss = cur ? cur.shi_shen : "", light, text;
      if (curScore <= -0.3) { light = "red"; text = "今年不宜大宗支出与新增负债，先保现金流、留足备用金。"; }
      else if (curScore >= 0.3 && !(cur && ji_set.indexOf(ss) >= 0 && (ss === "正财" || ss === "偏财"))) { light = "green"; text = "可择机购置，但先做好预算与退路，不透支、不勉强加杠杆。"; }
      else { light = "amber"; text = "大宗消费可择机，量入为出、留足备用金，不冲动负债。"; }
      decisions.push({ name: "买房 / 大宗消费", light: light, text: text });
    })();
    (function () { // 远行 / 搬家 / 换城市
      var m = dimOf["时机运势"]; var lv = m ? m.mean_level : 3; var light, text;
      if (lv >= 4) { light = "green"; text = "今年利变动与远行，换城市/搬迁可把握窗口推进。"; }
      else if (lv < 3) { light = "red"; text = "今年宜静不宜动，远行/搬家/大迁徙尽量缓一缓。"; }
      else { light = "amber"; text = "变动可择机，但先安顿好现有摊子、备好退路再动。"; }
      decisions.push({ name: "远行 / 搬家", light: light, text: text });
    })();

    // 3) 该做 / 别做 / 留意（按优先级合成）
    var doL = [], dontL = [], watchL = [];
    (cv.life_guidance.strengths || []).slice(0, 2).forEach(function (s) { doL.push(s); });
    if (winCls === "hi") doL.push("把握今年「进攻窗口」，把酝酿已久的关键目标（晋升 / 考证 / 重要合作）往前推。");
    else if (winCls === "mid") doL.push("把能力与资源做厚、把口碑做扎实，为下一个进攻窗口蓄力。");
    else doL.push("防守年里，把风险敞口降到最低、先稳住现有摊子；也是补齐能力短板与信用的好时机——少动多看，等窗口回来再出手。");
    (cv.life_guidance.cautions || []).slice(0, 3).forEach(function (c) { dontL.push(c); });
    if (winCls !== "hi") dontL.push("今年不辞职、不盲目投资、不替人担保、重大合同反复审、重大决策暂缓。");
    var healthM = dimOf["健康"];
    if (healthM && healthM.mean_level < 3) dontL.push("健康提示偏多：别拿身体好赌、别长期透支，安排一次针对性体检。");
    cv.review_flags.forEach(function (f) { watchL.push(f); });
    cv.matrix.forEach(function (m) { if (m.consistency === "分歧") watchL.push("维度「" + m.dimension + "」各体系结论分歧较大，相关决策放慢、以现实反馈校准。"); });
    if (cur && cur.key_months && cur.key_months.watch && cur.key_months.watch.length)
      watchL.push("今年宜谨慎月份：" + cur.key_months.watch.join("；") + "（冲动/变动多在此类月份，重大决策尽量避开）。");
    function uniq(a) { var seen = {}, out = []; a.forEach(function (x) { if (!seen[x]) { seen[x] = 1; out.push(x); } }); return out; }
    doL = uniq(doL).slice(0, 4); dontL = uniq(dontL).slice(0, 4); watchL = uniq(watchL).slice(0, 4);

    // 4) 能量节奏管理（教用户用运势曲线自我管理：好年攻、坏年守）
    var nowYear = cur ? cur.year : liu.now_year;
    var nextWin = null, nextDef = null;
    liu.rows.forEach(function (r) {
      if (r.year <= nowYear) return;
      if (!nextWin && (r.score >= 1.2 || (r.dayun_gz !== "—" && xi_set.indexOf(ten_god(day_gan, r.dayun_gz[0])) >= 0))) nextWin = r;
      if (!nextDef && r.score <= -1.2) nextDef = r;
    });
    var rhythm = {
      next_window: nextWin ? (nextWin.year + " 年（约 " + (nextWin.year - nowYear) + " 年后，" + gz2(nextWin.gz) + "，评分 " + nextWin.score + "）") : "未来数年以平/守为主，暂无明显进攻大年",
      next_defend: nextDef ? (nextDef.year + " 年（约 " + (nextDef.year - nowYear) + " 年后，" + gz2(nextDef.gz) + "，评分 " + nextDef.score + "）") : "暂无显著下行大年",
      principle: "好年攻、坏年守：在「进攻窗口」集中资源办大事、敢争取；在「防守期」收敛开支、降杠杆、把决策节奏放慢。用这份逐年曲线，你就能自己判断——接下来哪几年该冲、哪几年该忍。"
    };

    // 5) 自我觉察提示（把术语翻译成自省，而非宿命恐吓）
    var weakAct = bazi.strength === "身弱" ? "独立扛事、单兵冒进、不好意思求助"
      : bazi.strength === "身旺" ? "过度进取、什么都想抓、赢了面子输了里子" : "时而冒进、时而犹疑，节奏容易乱";
    var xiPhrase = bazi.strength === "中和" ? ("「" + (xi_set.join("、") || "需细参") + "」（中和之日主，喜用随大运流转，临事可借喜运发力）") : ("「" + (xi_set.join("、") || "需细参") + "」");
    var selfAware = [
      "你日主" + bazi.day_element + "（" + day_gan + "）" + bazi.strength + "，用神宜取" + xiPhrase + "。这提示你天生在「" + weakAct + "」上容易吃亏。",
      "做重大决定前，先问自己两问：(1) 这是顺势而为，还是赌一口气？(2) 最坏情况我兜不兜得住？——两个答案都踏实，再下手。",
      "本系统所有结论都是「决策参考 + 自我觉察」而非定数：把交叉验证里高一致的维度当「预警与机会」，把分歧的维度当「需现实验证的假设」。"
    ];

    return {
      window: { verdict: win, cls: winCls, why: winWhy },
      decisions: decisions,
      do_list: doL, dont_list: dontL, watch_list: watchL,
      rhythm: rhythm, self_aware: selfAware
    };
  }

  function cross_validate(bazi, ziwei, yijing, tieban, face, palm) {
    var bs = bazi_signals(bazi), zs = ziwei_signals(ziwei), ys = yijing_signals(yijing, bazi), ts_v = tieban_signals(tieban);
    var ts = ts_v[0], tieban_votes = ts_v[1];
    var systems = [["四柱八字", bs], ["紫微斗数", zs], ["周易卦象", ys], ["铁板神数", ts]];
    if (face) systems.push(["面相", face]);
    if (palm) systems.push(["手相", palm]);
    var nSys = systems.length;
    var matrix = [];
    DIMS.forEach(function (dim) {
      var votes = [];
      systems.forEach(function (kv) {
        if (kv[1][dim]) votes.push({ system: kv[0], text: kv[1][dim][0], level: kv[1][dim][1] });
      });
      var levels = votes.map(function (v) { return v.level; });
      var mean = levels.length ? levels.reduce(function (a, b) { return a + b; }, 0) / levels.length : 3;
      var rng = levels.length ? Math.max.apply(null, levels) - Math.min.apply(null, levels) : 0;
      var consistency = rng <= 1 ? "高一致" : (rng <= 2 ? "中一致" : "分歧");
      matrix.push({ dimension: dim, votes: votes, mean_level: Math.round(mean * 10) / 10, range: rng, consistency: consistency });
    });
    var review_flags = [];
    var bi_jie = bazi.ten_gods.filter(function (g) { return g === "比肩" || g === "劫财"; }).length;
    if (bi_jie >= 2 && tieban_votes["兄弟"]) review_flags.push("八字比劫偏旺而铁板兄弟数偏少，时辰或存疑，建议考时复核。");
    if (face || palm) review_flags.push("相学（面相/手相）为辅助维度：由照片像素气色自动判定 + 您观察勾选的特征共同得出，结论须与命理" + (nSys - (face ? 1 : 0) - (palm ? 1 : 0)) + "体系互参，不单独作断。");
    var conflicts = matrix.filter(function (m) { return m.consistency === "分歧"; }).map(function (m) { return m.dimension; });
    if (conflicts.length) review_flags.push("维度「" + conflicts.join("、") + "」" + nSys + "体系结论分歧较大，建议复核。");
    var cons_counts = { "高一致": 0, "中一致": 0, "分歧": 0 };
    matrix.forEach(function (m) { cons_counts[m.consistency]++; });
    var grade = cons_counts["分歧"] === 0 && cons_counts["高一致"] >= 4 ? "高一致 · 结论可信度较高"
      : cons_counts["分歧"] === 0 ? "中一致 · 结论可作参考" : "分歧需复核 · 时辰或参数待考证";
    var xi_ji = _xi_ji_sets(bazi), xi_set2 = xi_ji[0], ji_set2 = xi_ji[1];
    var life = _life_guidance(matrix, bazi, xi_set2, ji_set2, cons_counts, review_flags, nSys);
    var conclusions = matrix.map(function (m) {
      var direction = m.mean_level >= 4 ? "吉/强" : (m.mean_level >= 3 ? "平" : "弱/宜守");
      return { dimension: m.dimension, direction: direction, consistency: m.consistency, summary: m.dimension + "：综合评级 " + direction + "（一致性 " + m.consistency + "）。", advice: life.dimension_tips[m.dimension] };
    });
    return { matrix: matrix, review_flags: review_flags, cons_counts: cons_counts, grade: grade, conclusions: conclusions, life_guidance: life };
  }

  // ============ 深度增强：命格综合论断 / 用神映射 / 流年机理 / 大运详批 ============
  function _chong(a, b) {
    return (a === "子" && b === "午") || (a === "午" && b === "子") ||
           (a === "丑" && b === "未") || (a === "未" && b === "丑") ||
           (a === "寅" && b === "申") || (a === "申" && b === "寅") ||
           (a === "卯" && b === "酉") || (a === "酉" && b === "卯") ||
           (a === "辰" && b === "戌") || (a === "戌" && b === "辰") ||
           (a === "巳" && b === "亥") || (a === "亥" && b === "巳");
  }
  function _he6(a, b) {
    return (a === "子" && b === "丑") || (a === "丑" && b === "子") ||
           (a === "寅" && b === "亥") || (a === "亥" && b === "寅") ||
           (a === "卯" && b === "戌") || (a === "戌" && b === "卯") ||
           (a === "辰" && b === "酉") || (a === "酉" && b === "辰") ||
           (a === "巳" && b === "申") || (a === "申" && b === "巳") ||
           (a === "午" && b === "未") || (a === "未" && b === "午");
  }
  // 十神 → 五行
  function _tg_elem(de, g) {
    if (g === "比肩" || g === "劫财") return de;
    if (g === "正印" || g === "偏印") return ELEMENTS.filter(function (e) { return SHENG[e] === de; })[0];
    if (g === "食神" || g === "伤官") return SHENG[de];
    if (g === "正财" || g === "偏财") return KE[de];
    if (g === "正官" || g === "七杀") return ELEMENTS.filter(function (e) { return KE[e] === de; })[0];
    return null;
  }
  // 命格综合论断：专业叙事 + 喜用神推导 + 四体系交叉判读
  function _mingge_zonglun(bazi, yijing, cv) {
    var day_gan = bazi.day_master, dm = bazi.day_element, strength = bazi.strength;
    var xiji = _xi_ji_sets(bazi), xi = xiji[0], ji = xiji[1];
    var ec = bazi.element_count, top = ELEMENTS[0], bot = ELEMENTS[0], tm = -1, bm = 99;
    ELEMENTS.forEach(function (e) { if (ec[e] > tm) { tm = ec[e]; top = e; } if (ec[e] < bm) { bm = ec[e]; bot = e; } });
    var tg = bazi.ten_gods, pattern;
    if (strength === "身旺") {
      if (tg.indexOf("正官") >= 0 || tg.indexOf("七杀") >= 0) pattern = "身旺官杀为用，主有担当、宜在规则与责任中建功";
      else if (tg.indexOf("食神") >= 0 || tg.indexOf("伤官") >= 0) pattern = "身旺食伤泄秀，主才思外显、宜以才艺表达立身";
      else if (tg.indexOf("正财") >= 0 || tg.indexOf("偏财") >= 0) pattern = "身旺财星得根，主务实进取、宜以经营生财";
      else pattern = "身旺比劫林立，主自力自强、宜借协作与竞争成长";
    } else if (strength === "身弱") {
      if (tg.indexOf("正印") >= 0 || tg.indexOf("偏印") >= 0) pattern = "身弱印星为根，主得荫护、宜以学习与沉淀立基";
      else if (tg.indexOf("比肩") >= 0 || tg.indexOf("劫财") >= 0) pattern = "身弱比劫帮扶，主得同辈助力、宜合而不宜独";
      else pattern = "身弱官杀/财星偏重，主外压内耗、宜借平台与人托底、勿单兵冒进";
    } else pattern = "日主中和，刚柔可调，宜因时顺势、不偏不倚";
    var xi_text = xi.length ? xi.join("、") : "（需结合全局细参）";
    var ji_text = ji.length ? ji.join("、") : "（需结合全局细参）";
    var xi_is_shengfu = xi.indexOf("正印") >= 0 || xi.indexOf("偏印") >= 0 || xi.indexOf("比肩") >= 0 || xi.indexOf("劫财") >= 0;
    var xi_phrase = xi_is_shengfu ? "生扶我身、稳托根基" : "克泄耗我、引动成果";
    var ji_phrase = xi_is_shengfu ? "再耗再克则根基更虚" : "再助再旺则物极必反";
    var hi = cv.cons_counts["高一致"], div = cv.cons_counts["分歧"];
    var xjudge;
    if (div === 0 && hi >= 4) xjudge = "四体系高度一致，结论可信度较高，可在高一致维度放心发力；";
    else if (div === 0) xjudge = "四体系以中一致为主，整体可作稳健参考，关键决策仍辅以现实反馈；";
    else xjudge = "四体系有 " + div + " 个维度存在分歧（多为『一守一攻』之互补：如八字偏守、紫微见贵，综合取『借平台稳进』），建议以『交叉共识＋现实印证』双保险，避免单凭一家之言下注；";
    var para = "日主" + dm + "（" + day_gan + "），" + strength + "，五行" + (top === bot ? "趋于平和" : ("以「" + top + "」偏盛、「" + bot + "」偏弱")) + "。" +
      "格局上" + pattern + "。用神宜取「" + xi_text + "」——" + xi_phrase + "；" +
      "忌「" + ji_text + "」——" + ji_phrase + "。" +
      xjudge +
      "本命卦「" + yijing.ben_gua + "」(" + yijing.gua_nature + ")，动爻第 " + yijing.dong_yao + " 爻，主" + (yijing.meaning || "").slice(0, 22) + "——卦象与命局互参，整体取向" + (yijing.gua_elem === dm ? "同气相应" : "相成而可调") + "。";
    return { paragraph: para, xi_set: xi, ji_set: ji, pattern: pattern, top_element: top, weak_element: bot, xi_text: xi_text, ji_text: ji_text };
  }
  // 用神人生映射：方位 / 行业 / 助运色 / 调候（由喜用五行推导）
  function _yongshen_map(bazi, mingge) {
    var de = bazi.day_element, xi = mingge.xi_set;
    var elems = {}; xi.forEach(function (g) { var e = _tg_elem(de, g); if (e) elems[e] = 1; });
    if (bazi.strength === "身弱") elems[de] = 1;
    var DIR = { "木": "东方", "火": "南方", "土": "中原/本地", "金": "西方", "水": "北方" };
    var IND = { "木": "文化教育、农林园艺、创意设计、出版", "火": "能源电力、传媒餐饮、互联网、文化演艺", "土": "地产建筑、金融实业、服务管理、仓储", "金": "机械制造、法律司法、金融精算、五金", "水": "贸易流通、咨询策划、交通运输、旅游" };
    var COL = { "木": "青/绿", "火": "红/紫", "土": "黄/褐", "金": "白/金", "水": "黑/蓝" };
    var TIAO = { "木": "多接触自然与新知、主动拓展人际", "火": "勇于表达与展示、保持行动力", "土": "重积累与信用、行事稳妥少变", "金": "讲规则重契约、精炼专业壁垒", "水": "灵活应变、以柔克刚、多走动" };
    var rows = [];
    Object.keys(elems).forEach(function (e) { rows.push({ element: e, dir: DIR[e], ind: IND[e], col: COL[e], tiao: TIAO[e] }); });
    if (!rows.length) rows.push({ element: de, dir: DIR[de], ind: IND[de], col: COL[de], tiao: TIAO[de] });
    return { elements: Object.keys(elems), rows: rows };
  }
  // 流年机理：流年干支如何作用于日主 / 大运 / 命局
  function _liunian_mechanism(bazi, row) {
    var day_gan = bazi.day_master, day_elem = bazi.day_element;
    var y_gan = row.gz[0], y_zhi = row.gz[1], rel = row.shi_shen;
    var rel_txt = {
      "正官": "约束规范，主责任与名位", "七杀": "克制挑战，主压力与变动", "正印": "生扶荫护，主学习与贵人",
      "偏印": "偏助暗养，主钻研与孤独", "食神": "泄秀生财，主才艺与安逸", "伤官": "发泄外露，主表达与是非",
      "正财": "我克之财，主稳定收入", "偏财": "流动之财，主机遇与风险", "比肩": "同辈分力，主协作与竞争", "劫财": "分夺之象，主破耗与争夺"
    }[rel] || "中性平气";
    var s = (row.dayun_gz && row.dayun_gz !== "—") ? ("行「" + row.dayun_gz + "」大运（" + row.dayun_shishen + "）") : "尚未起运（依本命局）";
    var mech = "流年「" + row.gz + "」，天干「" + y_gan + "」为日主「" + day_gan + "（" + day_elem + "）」之「" + rel + "」——" + rel_txt + "；" + s + "。";
    var day_zhi = bazi.four_pillars.day.gz[1], month_zhi = bazi.four_pillars.month.gz[1];
    var note;
    if (_chong(y_zhi, day_zhi)) note = "流年支「" + y_zhi + "」冲日支「" + day_zhi + "」，年内个人/婚姻/健康层面易有波动，宜稳";
    else if (_chong(y_zhi, month_zhi)) note = "流年支「" + y_zhi + "」冲月令「" + month_zhi + "」，环境与事业平台易生变动";
    else if (_he6(y_zhi, day_zhi)) note = "流年支「" + y_zhi + "」合日支「" + day_zhi + "」，自身与人际气场趋于和合";
    else note = "流年支「" + y_zhi + "」与命局无强冲合，顺势而为即可";
    mech += note + "。";
    return mech;
  }
  // 流年关键月份：流月地支冲/合 流年支、日支、大运支
  function _liunian_key_months(bazi, row) {
    var y_zhi = row.gz[1];
    var day_zhi = bazi.four_pillars.day.gz[1];
    var dy_zhi = (row.dayun_gz && row.dayun_gz !== "—") ? row.dayun_gz[1] : null;
    var start_gan_idx = { "甲": 2, "己": 2, "乙": 4, "庚": 4, "丙": 6, "辛": 6, "丁": 8, "壬": 8, "戊": 0, "癸": 0 }[row.gz[0]];
    var watch = [], favor = [];
    for (var m = 1; m <= 12; m++) {
      var mz = ZHI[(2 + (m - 1)) % 12];
      if (_chong(mz, y_zhi) || (dy_zhi && _chong(mz, dy_zhi)) || _chong(mz, day_zhi)) watch.push(m + "月（流月「" + mz + "」冲动）");
      else if (_he6(mz, y_zhi)) favor.push(m + "月（流月「" + mz + "」合流年，气场和合）");
    }
    return { watch: watch.slice(0, 3), favor: favor.slice(0, 3) };
  }
  // 大运阶段详批：主题 + 关键转折年（岁运并临/天克地冲）+ 阶段建议
  function _dayun_detail(bazi, birth_year) {
    var day_gan = bazi.day_master, xiji = _xi_ji_sets(bazi), xi = xiji[0], ji = xiji[1];
    function theme(god) {
      if (god === "正官" || god === "七杀") return "事业进阶：责任与考核加重，宜争位、掌权、立专业壁垒";
      if (god === "正印" || god === "偏印") return "沉淀蓄能：利学习考证、得长辈/平台荫护，宜厚积";
      if (god === "正财" || god === "偏财") return "务实生财：重现金流与业务落地，偏财年须防贪";
      if (god === "食神" || god === "伤官") return "才艺外显：利表达创新与变动，也须防口舌是非";
      if (god === "比肩" || god === "劫财") return "协作竞争：宜合伙借力，但分账权责须白纸黑字";
      return "平运守成：稳扎稳打、积累资源，不躁不怠";
    }
    var out = [];
    if (bazi.dayun[0].start_age > 0) out.push({ range: "0–" + (Math.round(bazi.dayun[0].start_age) - 1) + "岁", gz: "命局", theme: "本命奠基：以学业、心性养成与家庭支持为主，不急于闯荡", turning: "—", tip: "未起运，顺势养根基；大额押注与远行宜缓。" });
    bazi.dayun.forEach(function (d) {
      var god = ten_god(day_gan, d.gz[0]);
      var fav = xi.indexOf(god) >= 0, bad = ji.indexOf(god) >= 0;
      var turning = [];
      var a0 = Math.round(d.start_age), a1 = Math.round(d.end_age - 1);
      for (var a = a0; a <= a1; a++) {
        var yr = birth_year + a - 1, gz = GZ60[(yr - 4) % 60];
        if (gz === d.gz) turning.push(a + "岁（岁运并临）");
        else {
          var gk = KE[gz[0]] === d.gz[0] || KE[d.gz[0]] === gz[0];
          if (gk && _chong(gz[1], d.gz[1])) turning.push(a + "岁（天克地冲·大变动）");
        }
      }
      var tip = fav ? "此运干支为喜，十年动能偏顺——宜把握窗口、主动进取、放大成果；顺境也别放松风控。"
        : bad ? "此运干支为忌，守成蓄势的十年——控风险、重大决策三思、不替人担保、不盲目加杠杆，以稳换空间。"
          : "此运平气，稳扎稳打、积累实力与资源，不主动制造大变动。";
      out.push({ range: a0 + "–" + a1 + "岁", gz: d.gz, theme: theme(god) + (fav ? "（喜运）" : bad ? "（忌运）" : ""), turning: turning.length ? turning.slice(0, 2).join("；") : "无明显大变动年", tip: tip });
    });
    return out;
  }

  // ============ 流年 ============
  var JI_MAIN = { "紫微": 1, "太阳": 1, "武曲": 1, "天同": 1, "天府": 1, "太阴": 1, "天相": 1, "天梁": 1 };
  var XIONG_MAIN = { "七杀": 1, "破军": 1, "廉贞": 1, "贪狼": 1, "巨门": 1 };
  var JI_FU = { "文昌": 1, "文曲": 1, "左辅": 1, "右弼": 1, "天魁": 1, "天钺": 1, "禄存": 1 };
  var XIONG_FU = { "擎羊": 1, "陀罗": 1, "火星": 1, "铃星": 1, "地空": 1, "地劫": 1 };
  var SIHUA_JI = { "禄": 1, "权": 1, "科": 1 }; var SIHUA_XIONG = { "忌": 1 };
  // 流年逐岁「指导性意见」生成器：依据十神喜忌 + 大运 + 紫微流年命宫 + 四化 + 评分，分五维给出直白可避坑的建议
  function _liunian_cat(bazi, shi_shen, dy_shishen, fp_name, fp_stars, fp_fu, has_lu, has_ji, score, xi_set, ji_set, weak_elem, organ) {
    var cat = {};
    var weak = bazi.strength === "身弱";
    // 事业 —— 直给：这一年具体别做什么、该把劲往哪使
    var career;
    if (["正官", "七杀"].indexOf(shi_shen) >= 0)
      career = weak
        ? "官杀之年，责任与考核明显加重。别冲动裸辞、别轻易替人担保或签连带责任；重要任务先写清权责边界再接。可借平台稳步上位，但不宜强出头揽超出自己能力的活。"
        : "官杀之年利掌权、争取管理岗或专业突破。但官杀也主压力与是非：签约、人事变动务必留书面凭证，避免口头承诺；与上级/规则有冲突时先忍一步。";
    else if (["正印", "偏印"].indexOf(shi_shen) >= 0)
      career = "印星之年利学习、考证、沉淀专业。把时间花在提升硬本事上最划算；不宜大举投资或频繁跳槽，慢即是快。";
    else if (["食神", "伤官"].indexOf(shi_shen) >= 0)
      career = (shi_shen === "伤官")
        ? "伤官之年利才艺表达、创新，但也最易惹口舌是非。发文、表态、签约前多想一步；尤其防与上级/客户/规则正面冲撞，重大人事变动缓一缓。"
        : "食神之年利才艺、表达与轻松输出。可大胆展示，但忌眼高手低、忌得意忘形祸从口出；做事留底。";
    else if (["正财", "偏财"].indexOf(shi_shen) >= 0)
      career = "财星之年务实为要，利业务落地与稳定收入。偏财可小试，忌贪多冒进、忌为业绩踩灰色线。";
    else if (["比肩", "劫财"].indexOf(shi_shen) >= 0)
      career = "比劫之年宜合作借力，但比劫也主争夺：防同侪抢功、合伙利益不清，事前把分账与权责白纸黑字定好。";
    else career = "流年平气，事业平稳。把分内事做扎实、不躁不怠，别主动挑起变动。";
    cat["事业"] = career;
    // 财运 —— 直给：守还是攻，具体红线在哪
    var wealth;
    if (["正财", "偏财"].indexOf(shi_shen) >= 0 && xi_set.indexOf(shi_shen) >= 0)
      wealth = "财星为喜，进财机会较顺。但顺境最易放松风控：可稳健理财、留足应急金，偏财只动用闲钱，不追加杠杆。";
    else if (["正财", "偏财"].indexOf(shi_shen) >= 0)
      wealth = "财星现而于你非最利，财来财去之象。这一年重点是『守』：不新增贷款、不替人担保、大宗消费与投资延后，先保住现金流。";
    else if (score >= 0.3)
      wealth = "流年整体向上，财运平顺。量入为出、可小布局，但仍不留大额应收账款、不替人背债。";
    else if (score <= -0.3)
      wealth = "流年承压，财运宜守不宜攻：暂停新增借贷、不留大额应收、投资只做闲钱甚至不投，先把风险敞口降到最低。";
    else wealth = "财运中性，宜稳守、不投机、不替人担保背债。";
    cat["财运"] = wealth;
    // 人际 —— 直给：哪类人/哪类事要设防
    var rel;
    if (has_ji)
      rel = "流年忌落「" + fp_name + "」宫，该领域易有阻滞与反复——借钱要立字据、合伙先定分账、别替人做连带担保、防因人情破财生怨。";
    else if (has_lu)
      rel = "流年禄落「" + fp_name + "」宫，相关事务易得助力，可积极推进；但仍要明算账，别因顺利就放松契约。";
    else if (["比肩", "劫财", "伤官"].indexOf(shi_shen) >= 0)
      rel = "比劫/伤官之年人际活跃却易生竞争与口舌：择善而交、少争闲气，重要约定落纸面，别为面子逞强出资。";
    else rel = "人际平顺，维护旧缘即可，别为面子替人出头担责。";
    cat["人际"] = rel;
    // 健康 —— 直给：哪类事要避、该查什么
    cat["健康"] = (["七杀", "伤官"].indexOf(shi_shen) >= 0)
      ? "命局五行偏弱在「" + weak_elem + "（" + organ + "）」。七杀/伤官加临之年，防过劳与突发小伤：避免熬夜透支、应酬无度、极限运动；安排一次针对「" + organ + "」的体检。"
      : "命局五行偏弱在「" + weak_elem + "（" + organ + "）」。今年保持起居有常，重点保养「" + organ + "」，别拿身体好赌、别长期透支。";
    // 时机 —— 直给：这一年能不能动、动什么
    var timing;
    if (score >= 1.2)
      timing = "全年动能强，是落地关键决策的窗口：可推进酝酿已久的事，但别在顺境里放松风控、别盲目加注。";
    else if (score >= 0.3)
      timing = "稳中有进，顺势而为；换城市/买房/创业等重大变动可择机，但务必先做好预案与退路。";
    else if (score > -0.3)
      timing = "平顺守常，年内不主动制造大变动，先把现有摊子稳住、把债务和承诺理清。";
    else if (score > -1.2)
      timing = "多有牵绊，这一年以『避坑』为主：不辞职、不盲目投资、不替人担保、重要合同反复审、重大决策暂缓。";
    else timing = "阻力较大，宜低调收敛：婚/迁/投/创业等重大决策尽量缓一缓，先把风险敞口降到最低。";
    cat["时机"] = timing;
    return cat;
  }
  function _xi_ji_sets(bazi) {
    var strength = bazi.strength, de = bazi.day_element, ec = bazi.element_count;
    var ke_xie = ["正官", "七杀", "食神", "伤官", "正财", "偏财"], sheng_fu = ["比肩", "劫财", "正印", "偏印"];
    if (strength === "身旺") return [ke_xie, sheng_fu];
    if (strength === "身弱") return [sheng_fu, ke_xie];
    // 中和：依全局最旺五行判断偏势，给出可调喜用（日主中和但被耗则喜生扶，偏助则喜克泄）
    var top = ELEMENTS[0], tm = -1;
    ELEMENTS.forEach(function (e) { if (ec[e] > tm) { tm = ec[e]; top = e; } });
    var sheng_elems = [de]; ELEMENTS.forEach(function (e) { if (SHENG[e] === de) sheng_elems.push(e); });
    if (sheng_elems.indexOf(top) >= 0) return [ke_xie, sheng_fu];
    return [sheng_fu, ke_xie];
  }
  function _score_to_grade(score) {
    if (score >= 1.2) return ["吉", "hi", "流年得力，是落地关键决策的窗口，但顺境别放松风控"];
    if (score >= 0.3) return ["平偏吉", "hi", "稳中有进，顺势而为，重大变动先备退路"];
    if (score > -0.3) return ["平", "mid", "平顺守常，年内不主动制造大变动"];
    if (score > -1.2) return ["平偏凶", "lo", "多有牵绊，以避坑为主：不投资、不担保、合同反复审"];
    return ["凶", "lo", "阻力大，重大决策暂缓，先把风险敞口降到最低"];
  }
  function _active_dayun(bazi, age) {
    for (var i = 0; i < bazi.dayun.length; i++) {
      var d = bazi.dayun[i];
      if (d.start_age <= age && age < d.end_age) return [d.gz, d.step];
    }
    if (bazi.dayun.length && age < bazi.dayun[0].start_age) return [null, 0];
    if (bazi.dayun.length) { var last = bazi.dayun[bazi.dayun.length - 1]; return [last.gz, last.step]; }
    return [null, 0];
  }
  function compute_liunian(bazi, ziwei, birth, span_back, span_fwd) {
    span_back = span_back || 2; span_fwd = span_fwd || 8;
    var day_gan = bazi.day_master, xi_ji = _xi_ji_sets(bazi), xi_set = xi_ji[0], ji_set = xi_ji[1];
    var now_year = new Date().getFullYear(), birth_year = birth.getFullYear();
    var palaces = ziwei.palaces, zhi_palace_idx = {};
    palaces.forEach(function (p, i) { zhi_palace_idx[p.zhi] = i; });
    var rows = [];
    var ec = bazi.element_count, weak_elem = ELEMENTS[0], we = 99;
    ELEMENTS.forEach(function (e) { if (ec[e] < we) { we = ec[e]; weak_elem = e; } });
    var organ = { "木": "肝胆/筋骨", "火": "心脑/血脉", "土": "脾胃", "金": "肺/呼吸道", "水": "肾/膀胱/泌尿" }[weak_elem];
    for (var y = now_year - span_back; y <= now_year + span_fwd; y++) {
      var gz = GZ60[(y - 4) % 60], y_gan = gz[0], y_zhi = gz[1];
      var nayin = nayin_name(gz), shi_shen = ten_god(day_gan, y_gan);
      var age = y - birth_year + 1;
      var dy = _active_dayun(bazi, age), dy_gz = dy[0], dy_step = dy[1];
      var dy_shishen = dy_gz ? ten_god(day_gan, dy_gz[0]) : "（未起运）";
      var fp_idx = zhi_palace_idx[y_zhi], fp = fp_idx != null ? palaces[fp_idx] : null;
      var fp_name = fp ? fp.palace : "—", fp_stars = fp ? fp.stars : [], fp_fu = fp ? fp.fu_stars : [];
      var sh = SIHUA[y_gan] || ["", "", "", ""], sihua = { "禄": sh[0], "权": sh[1], "科": sh[2], "忌": sh[3] };
      var sihua_hit = [];
      for (var tag in sihua) if (sihua[tag] && fp && fp_stars.indexOf(sihua[tag]) >= 0) sihua_hit.push(tag + sihua[tag]);
      var score = 0;
      if (xi_set.length || ji_set.length) {
        if (xi_set.indexOf(shi_shen) >= 0) score += 1; else if (ji_set.indexOf(shi_shen) >= 0) score -= 1;
        if (dy_gz && xi_set.indexOf(dy_shishen) >= 0) score += 1; else if (dy_gz && ji_set.indexOf(dy_shishen) >= 0) score -= 1;
      }
      fp_stars.forEach(function (s) { if (JI_MAIN[s]) score += 0.3; else if (XIONG_MAIN[s]) score -= 0.3; });
      fp_fu.forEach(function (s) { if (JI_FU[s]) score += 0.3; else if (XIONG_FU[s]) score -= 0.3; });
      for (var tag2 in sihua) if (sihua[tag2] && fp && fp_stars.indexOf(sihua[tag2]) >= 0) { if (SIHUA_JI[tag2]) score += 0.4; else score -= 0.6; }
      var gr = _score_to_grade(score);
      var has_lu = sihua_hit.some(function (s) { return s[0] === "禄"; });
      var has_ji = sihua_hit.some(function (s) { return s[0] === "忌"; });
      var cat = _liunian_cat(bazi, shi_shen, dy_shishen, fp_name, fp_stars, fp_fu, has_lu, has_ji, score, xi_set, ji_set, weak_elem, organ);
      var mech = _liunian_mechanism(bazi, { gz: gz, shi_shen: shi_shen, dayun_gz: dy_gz || "—", dayun_shishen: dy_shishen });
      var km = _liunian_key_months(bazi, { gz: gz, dayun_gz: dy_gz });
      var longParts = [gr[2]];
      longParts.push("流年重点在「" + fp_name + "」宫" + (fp_stars.length ? ("，主星" + fp_stars.join("") + "；") : "（空宫借对宫）；"));
      if (has_lu || has_ji) longParts.push("四化" + (has_lu ? "禄" : "") + (has_ji ? "忌" : "") + "落此，" + (has_lu ? "宜顺势借力、主动作为" : "宜谨慎规划、明算账防反复") + "。");
      else longParts.push("流年四化不落本宫，按十神与大运顺势而为即可。");
      var advice_long = longParts.join("");
      var parts = [];
      if (xi_set.length || ji_set.length) parts.push("流年十神" + shi_shen + "（" + (xi_set.indexOf(shi_shen) >= 0 ? "喜" : ji_set.indexOf(shi_shen) >= 0 ? "忌" : "中性") + "）");
      else parts.push("流年十神" + shi_shen);
      if (dy_gz) parts.push("行" + dy_gz + "大运（" + dy_shishen + "）"); else parts.push("未起运（依命局）");
      parts.push("重点在" + fp_name);
      if (sihua_hit.length) parts.push("流年四化" + sihua_hit.join("、") + "落本宫");
      var summary = parts.join("；") + "。" + gr[2] + "。";
      var sihua_out = {}; for (var t3 in sihua) if (sihua[t3]) sihua_out[t3] = sihua[t3];
      rows.push({
        year: y, gz: gz, nayin: nayin, age: age, shi_shen: shi_shen, dayun_gz: dy_gz || "—", dayun_step: dy_step,
        dayun_shishen: dy_shishen, flow_palace: fp_name, flow_palace_zhi: y_zhi,
        flow_stars: fp_stars, flow_fu_stars: fp_fu, sihua: sihua_out, sihua_hit: sihua_hit,
        score: Math.round(score * 100) / 100, grade: gr[0], cls: gr[1], advice: gr[2], advice_long: advice_long, advice_cat: cat, summary: summary, mechanism: mech, key_months: km, is_current: y === now_year
      });
    }
    return { rows: rows, trend: rows.filter(function (r) { return r.is_current; })[0].summary, now_year: now_year };
  }

  // ============ 图表（SVG）============
  function build_ziwei_svg(ziwei) {
    var CX = 320, CY = 318, R_LABEL = 296, R_DOT = 250, R_FU = 150;
    var palaces = ziwei.palaces, sihua_map = ziwei.sihua_map || {}, sanfang = { 0: 1, 4: 1, 8: 1, 6: 1 };
    var p = [];
    p.push('<svg viewBox="0 0 640 640" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="紫微斗数十二宫星盘" style="max-width:560px;width:100%;height:auto;display:block;margin:0 auto">');
    p.push('<circle cx="' + CX + '" cy="' + CY + '" r="312" fill="#faf7f2" stroke="#e6e9ee"/>');
    p.push('<circle cx="' + CX + '" cy="' + CY + '" r="120" fill="#fff" stroke="#e6e9ee"/>');
    p.push('<circle cx="' + CX + '" cy="' + CY + '" r="308" fill="none" stroke="#e6e9ee"/>');
    function pt(r, deg) { var t = deg * Math.PI / 180; return [CX + r * Math.cos(t), CY + r * Math.sin(t)]; }
    for (var i = 0; i < palaces.length; i++) {
      var deg = -90 + i * 30;
      var x2 = pt(R_DOT, deg); p.push('<line x1="' + CX + '" y1="' + CY + '" x2="' + x2[0].toFixed(1) + '" y2="' + x2[1].toFixed(1) + '" stroke="#e6e9ee"/>');
      var lx = pt(R_LABEL, deg), hl = !!sanfang[i];
      p.push('<text x="' + lx[0].toFixed(1) + '" y="' + lx[1].toFixed(1) + '" text-anchor="middle" font-size="13" font-weight="' + (hl ? "bold" : "normal") + '" fill="' + (hl ? "#8a5a2b" : "#1f2733") + '">' + palaces[i].palace + '</text>');
      var zx = pt(R_LABEL - 15, deg); p.push('<text x="' + zx[0].toFixed(1) + '" y="' + zx[1].toFixed(1) + '" text-anchor="middle" font-size="10" fill="#6b7785">' + palaces[i].zhi + '</text>');
      var dx = pt(R_DOT, deg); p.push('<circle cx="' + dx[0].toFixed(1) + '" cy="' + dx[1].toFixed(1) + '" r="4" fill="' + (hl ? "#8a5a2b" : "#cfd6dd") + '"/>');
      var mx = pt(R_DOT - 26, deg), stars = palaces[i].stars;
      if (stars.length) {
        p.push('<text x="' + mx[0].toFixed(1) + '" y="' + mx[1].toFixed(1) + '" text-anchor="middle" font-size="12" font-weight="bold" fill="#2b5a8a">' + stars.join(" ") + '</text>');
        var suf = stars.filter(function (s) { return sihua_map[s]; }).map(function (s) { return "(" + sihua_map[s] + ")"; }).join(" ");
        if (suf) { var sx = pt(R_DOT - 26, deg + 6); p.push('<text x="' + sx[0].toFixed(1) + '" y="' + sx[1].toFixed(1) + '" text-anchor="middle" font-size="9" fill="#c0392b">' + suf + '</text>'); }
      } else p.push('<text x="' + mx[0].toFixed(1) + '" y="' + mx[1].toFixed(1) + '" text-anchor="middle" font-size="11" fill="#9aa4af">空宫</text>');
      var fu = palaces[i].fu_stars;
      if (fu && fu.length) { var fx = pt(R_FU, deg); p.push('<text x="' + fx[0].toFixed(1) + '" y="' + fx[1].toFixed(1) + '" text-anchor="middle" font-size="9.5" fill="#6b7785">' + fu.join(" ") + '</text>'); }
    }
    p.push('<text x="' + CX + '" y="' + (CY - 44) + '" text-anchor="middle" font-size="13" font-weight="bold" fill="#8a5a2b">紫微斗数</text>');
    p.push('<text x="' + CX + '" y="' + (CY - 22) + '" text-anchor="middle" font-size="12" fill="#1f2733">命宫 ' + ziwei.mingong_gz + '</text>');
    p.push('<text x="' + CX + '" y="' + CY + '" text-anchor="middle" font-size="12" fill="#1f2733">' + ziwei.ju + '</text>');
    p.push('<text x="' + CX + '" y="' + (CY + 22) + '" text-anchor="middle" font-size="12" fill="#1f2733">紫微在 ' + ziwei.ziwei_zhi + '</text>');
    p.push('<text x="' + CX + '" y="' + (CY + 44) + '" text-anchor="middle" font-size="11" fill="#6b7785">命宫主星 ' + ziwei.main_star + '</text>');
    p.push('<text x="' + CX + '" y="600" text-anchor="middle" font-size="11" fill="#6b7785">○ 棕圈=三方四正（命/财/官/迁）｜ 蓝字=主星 灰字=辅星 红()=生年四化</text>');
    p.push('</svg>');
    return p.join("");
  }
  function fortune_trend_svg(liunian) {
    var rows = liunian.rows, n = rows.length, W = 760, H = 250, pad_l = 46, pad_r = 16, pad_t = 18, pad_b = 32;
    var plot_w = W - pad_l - pad_r, plot_h = H - pad_t - pad_b, SMIN = -3, SMAX = 3;
    function y_of(s) { s = Math.max(SMIN, Math.min(SMAX, s)); return pad_t + (1 - (s - SMIN) / (SMAX - SMIN)) * plot_h; }
    function x_of(i) { return n > 1 ? pad_l + plot_w * i / (n - 1) : pad_l + plot_w / 2; }
    var p = [];
    p.push('<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="十年运势走势" style="max-width:760px;width:100%;height:auto;display:block;margin:0 auto">');
    p.push('<line x1="' + pad_l + '" y1="' + pad_t + '" x2="' + pad_l + '" y2="' + (pad_t + plot_h) + '" stroke="#e6e9ee"/>');
    p.push('<line x1="' + pad_l + '" y1="' + (pad_t + plot_h) + '" x2="' + (pad_l + plot_w) + '" y2="' + (pad_t + plot_h) + '" stroke="#e6e9ee"/>');
    [-3, -2, -1, 1, 2, 3].forEach(function (s) { var yy = y_of(s); p.push('<line x1="' + pad_l + '" y1="' + yy.toFixed(1) + '" x2="' + (pad_l + plot_w) + '" y2="' + yy.toFixed(1) + '" stroke="#f0f2f5"/>'); p.push('<text x="' + (pad_l - 8) + '" y="' + (yy + 4).toFixed(1) + '" text-anchor="end" font-size="10" fill="#9aa4af">' + (s > 0 ? "+" : "") + s + '</text>'); });
    var y0 = y_of(0); p.push('<line x1="' + pad_l + '" y1="' + y0.toFixed(1) + '" x2="' + (pad_l + plot_w) + '" y2="' + y0.toFixed(1) + '" stroke="#cfd6dd" stroke-dasharray="4 3"/>');
    p.push('<text x="' + (pad_l - 8) + '" y="' + (y0 + 4).toFixed(1) + '" text-anchor="end" font-size="10" fill="#9aa4af">0</text>');
    var pts = rows.map(function (r, i) { return [x_of(i), y_of(r.score)]; });
    if (n > 1) { var d = "M " + pts.map(function (q) { return q[0].toFixed(1) + " " + q[1].toFixed(1); }).join(" L "); p.push('<path d="' + d + '" fill="none" stroke="#8a5a2b" stroke-width="2"/>'); }
    var cls_color = { "hi": "#1e7a3c", "mid": "#9a6b00", "lo": "#c0392b" };
    pts.forEach(function (q, i) { var r = rows[i], col = cls_color[r.cls] || "#9a6b00"; p.push('<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="4.5" fill="' + col + '"><title>' + r.year + " " + r.gz + "｜" + r.grade + "（评分 " + r.score + '）</title></circle>'); if (r.is_current) p.push('<text x="' + q[0].toFixed(1) + '" y="' + (q[1] - 11).toFixed(1) + '" text-anchor="middle" font-size="11" font-weight="bold" fill="#8a5a2b">今</text>'); });
    rows.forEach(function (r, i) { var x = x_of(i); p.push('<text x="' + x.toFixed(1) + '" y="' + (pad_t + plot_h + 16) + '" text-anchor="middle" font-size="10" fill="#6b7785">' + String(r.year).slice(2) + '</text>'); });
    p.push('<text x="' + (pad_l + plot_w) + '" y="' + (pad_t - 4) + '" text-anchor="end" font-size="10" fill="#9aa4af">绿=吉 黄=平 红=凶 · 数值=综合评分</text>');
    p.push('</svg>');
    return p.join("");
  }
  function radar_svg(labels, values, opts) {
    opts = opts || {};
    var N = labels.length, CX = 200, CY = 200, R = 150, W = 400, H = 400;
    var p = [];
    p.push('<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="' + (opts.title || "雷达图") + '" style="max-width:340px;width:100%;height:auto;display:block;margin:0 auto">');
    function pt(r, deg) { var t = (deg - 90) * Math.PI / 180; return [CX + r * Math.cos(t), CY + r * Math.sin(t)]; }
    var maxv = opts.max || Math.max.apply(null, values.concat([1]));
    for (var ring = 1; ring <= 4; ring++) {
      var rr = R * ring / 4, pts = [];
      for (var i = 0; i < N; i++) { var q = pt(rr, i * 360 / N); pts.push(q[0].toFixed(1) + "," + q[1].toFixed(1)); }
      p.push('<polygon points="' + pts.join(" ") + '" fill="none" stroke="#eef1f4"/>');
    }
    for (var j = 0; j < N; j++) { var a = pt(R, j * 360 / N); p.push('<line x1="' + CX + '" y1="' + CY + '" x2="' + a[0].toFixed(1) + '" y2="' + a[1].toFixed(1) + '" stroke="#eef1f4"/>'); }
    var dv = [];
    for (var k = 0; k < N; k++) { var v = values[k] / maxv * R; dv.push(pt(v, k * 360 / N)); }
    p.push('<polygon points="' + dv.map(function (q) { return q[0].toFixed(1) + "," + q[1].toFixed(1); }).join(" ") + '" fill="rgba(138,90,43,0.28)" stroke="#8a5a2b" stroke-width="2"/>');
    for (var m = 0; m < N; m++) {
      var lp = pt(R + 20, m * 360 / N);
      p.push('<text x="' + lp[0].toFixed(1) + '" y="' + lp[1].toFixed(1) + '" text-anchor="middle" font-size="11" fill="#1f2733">' + labels[m] + '</text>');
      var vp = pt(R + 20, m * 360 / N); // value near label
      p.push('<text x="' + vp[0].toFixed(1) + '" y="' + (vp[1] + 12).toFixed(1) + '" text-anchor="middle" font-size="9" fill="#9aa4af">' + values[m] + '</text>');
      var dp = pt(values[m] / maxv * R, m * 360 / N);
      p.push('<circle cx="' + dp[0].toFixed(1) + '" cy="' + dp[1].toFixed(1) + '" r="2.5" fill="#8a5a2b"/>');
    }
    p.push('</svg>');
    return p.join("");
  }
  function liunian_sihua_svg(liunian) {
    var rows = liunian.rows, n = rows.length;
    var W = 760, H = 150, pad_l = 60, pad_r = 16, cell = (W - pad_l - pad_r) / n;
    var p = [];
    p.push('<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="流年四化盘" style="max-width:760px;width:100%;height:auto;display:block;margin:0 auto">');
    var colors = { "禄": "#1e7a3c", "权": "#2b5a8a", "科": "#9a6b00", "忌": "#c0392b" };
    rows.forEach(function (r, i) {
      var x = pad_l + cell * i + cell / 2;
      var cur = r.is_current;
      p.push('<text x="' + x.toFixed(1) + '" y="18" text-anchor="middle" font-size="11" font-weight="' + (cur ? "bold" : "normal") + '" fill="' + (cur ? "#8a5a2b" : "#6b7785") + '">' + r.year + '</text>');
      p.push('<text x="' + x.toFixed(1) + '" y="34" text-anchor="middle" font-size="10" fill="#1f2733">' + r.gz + '</text>');
      p.push('<text x="' + x.toFixed(1) + '" y="50" text-anchor="middle" font-size="9" fill="#9aa4af">' + r.flow_palace + '</text>');
      var tags = ["禄", "权", "科", "忌"];
      var yy = 70;
      tags.forEach(function (t) {
        if (r.sihua[t]) {
          p.push('<circle cx="' + x.toFixed(1) + '" cy="' + yy + '" r="6" fill="' + colors[t] + '"><title>' + r.year + " " + t + r.sihua[t] + '</title></circle>');
          p.push('<text x="' + x.toFixed(1) + '" y="' + (yy + 3.2) + '" text-anchor="middle" font-size="8" fill="#fff">' + t + '</text>');
          yy += 18;
        }
      });
      if (!cur) p.push('<line x1="' + (pad_l + cell * i) + '" y1="10" x2="' + (pad_l + cell * i) + '" y2="' + (H - 10) + '" stroke="#f0f2f5"/>');
    });
    p.push('<text x="' + pad_l + '" y="' + (H - 2) + '" font-size="10" fill="#9aa4af">禄(绿)/权(蓝)/科(黄)/忌(红) 圆点表示该年流年四化落紫微流年命宫之星；纵列＝该年重点宫。</text>');
    p.push('</svg>');
    return p.join("");
  }

  // ============ 顶层分析 ============
  function analyze(y, mo, d, h, mi, gender, birthplace, meta) {
    var lon = CITY_LONGITUDE[birthplace] != null ? CITY_LONGITUDE[birthplace] : 120.0;
    var g = correct_to_solar(y, mo, d, h, mi, lon);
    var solar = g.solar;
    var sc_before = _hour_to_shichen(h), sc_after = _hour_to_shichen(solar.getHours());
    var geo = {
      birthplace: birthplace, longitude: lon, delta_h: Math.round(g.delta_h * 1000) / 1000, eot: Math.round(g.eot * 100) / 100,
      solar_birth: solar, shichen_before: ZHI[sc_before - 1] + "时", shichen_after: ZHI[sc_after - 1] + "时",
      shichen_changed: sc_before !== sc_after
    };
    var b = compute_bazi(solar.getFullYear(), solar.getMonth() + 1, solar.getDate(), solar.getHours(), solar.getMinutes(), gender);
    b.gender = gender;
    var z = compute_ziwei(solar.getFullYear(), solar.getMonth() + 1, solar.getDate(), solar.getHours(), solar.getMinutes(), gender);
    var yj = meihua_qigua(b.four_pillars);
    var tb = compute_tieban(b, z);
    var faceSig = (meta && meta.faceObs) ? face_signals(meta.faceObs, meta.facePx) : null;
    var palmSig = (meta && meta.palmObs) ? palm_signals(meta.palmObs, meta.palmPx) : null;
    var cv = cross_validate(b, z, yj, tb, faceSig, palmSig);
    var liu = compute_liunian(b, z, solar);
    var mingge = _mingge_zonglun(b, yj, cv);
    var yongshen = _yongshen_map(b, mingge);
    var dayun_detail = _dayun_detail(b, solar.getFullYear());
    var action_playbook = _action_playbook(b, cv, liu);
    var ziwei_svg = build_ziwei_svg(z);
    var fortune_svg = fortune_trend_svg(liu);
    var radar_wuxing = radar_svg(ELEMENTS, ELEMENTS.map(function (e) { return b.element_count[e]; }), { title: "五行分布", max: 8 });
    var ten_god_count = {}; TEN_GOD.forEach(function (t) { ten_god_count[t] = 0; });
    b.ten_gods.forEach(function (t) { ten_god_count[t]++; });
    var radar_shi_shen = radar_svg(TEN_GOD, TEN_GOD.map(function (t) { return ten_god_count[t]; }), { title: "十神分布", max: 4 });
    var liunian_sihua = liunian_sihua_svg(liu);
    var elem_data = ELEMENTS.map(function (e) { return { name: e, value: b.element_count[e], color: ELEMENT_COLOR[e] }; });
    return {
      birth_input: meta && meta.calendar
        ? {
            calendar: meta.calendar,
            year: y, month: mo, day: d, hour: h, minute: mi, gender: gender, birthplace: birthplace,
            ly: meta.ly, lmo: meta.lmo, ld: meta.ld, lleap: meta.lleap, lshichen: meta.lshichen,
            sy: meta.sy, smo: meta.smo, sd: meta.sd, sh: meta.sh, smi: meta.smi
          }
        : { calendar: "阳历", year: y, month: mo, day: d, hour: h, minute: mi, gender: gender, birthplace: birthplace },
      solar_birth: solar, gender: gender, geo: geo, bazi: b, ziwei: z, yijing: yj, tieban: tb, cv: cv,
      liunian: liu, ziwei_svg: ziwei_svg, fortune_svg: fortune_svg, radar_wuxing: radar_wuxing,
      radar_shi_shen: radar_shi_shen,       liunian_sihua: liunian_sihua, elem_data: elem_data,
      mingge: mingge, yongshen: yongshen, dayun_detail: dayun_detail, action_playbook: action_playbook,
      face: faceSig ? { signals: faceSig, obs: meta.faceObs, px: meta.facePx, img: meta.faceImg } : null,
      palm: palmSig ? { signals: palmSig, obs: meta.palmObs, px: meta.palmPx, img: meta.palmImg } : null
    };
  }

  return {
    C: { GAN: GAN, ZHI: ZHI, GZ60: GZ60, ELEMENTS: ELEMENTS, ELEMENT_COLOR: ELEMENT_COLOR, CITY_LONGITUDE: CITY_LONGITUDE, SIHUA: SIHUA, TEN_GOD: TEN_GOD, ZIWEI_PALACES: ZIWEI_PALACES },
    analyze: analyze, compute_bazi: compute_bazi, compute_ziwei: compute_ziwei, meihua_qigua: meihua_qigua,
    compute_tieban: compute_tieban, cross_validate: cross_validate, compute_liunian: compute_liunian, action_playbook: _action_playbook,
    face_signals: face_signals, palm_signals: palm_signals,
    build_ziwei_svg: build_ziwei_svg, fortune_trend_svg: fortune_trend_svg, radar_svg: radar_svg, liunian_sihua_svg: liunian_sihua_svg,
    correct_to_solar: correct_to_solar, nayin_name: nayin_name
  };
});
