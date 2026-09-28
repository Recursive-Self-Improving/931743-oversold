"""Render an offline, dependency-free interactive report for daily index signals."""

from __future__ import annotations

import json
from pathlib import Path


def render_html(report: dict, destination: Path) -> None:
    """Write a self-contained Chinese HTML report using the supplied report snapshot."""
    # Escape HTML-sensitive characters even inside the inert JSON script element:
    # HTML parsers recognize </script> regardless of the script's MIME type.
    payload = json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    for character, escape in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        payload = payload.replace(character, escape)

    html = _PAGE.replace("__REPORT_DATA__", payload)
    destination.write_text(html, encoding="utf-8")


_PAGE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>超卖观察 · 931743</title>
<style>
:root{font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:#1b3041;background:#f3f6f6;font-variant-numeric:tabular-nums;line-height:1.55}
*{box-sizing:border-box}body{margin:0}.wrap{max-width:1320px;margin:auto;padding:32px 28px 64px}
h1,h2,p{margin-top:0}h1{font-size:clamp(1.65rem,3.5vw,2.6rem);line-height:1.25;margin-bottom:8px;letter-spacing:-.025em}h2{font-size:1.18rem;margin-bottom:15px}
.kicker{color:#04747a;font-size:.78rem;letter-spacing:.14em;font-weight:800;margin-bottom:10px}.subtitle,.muted{color:#58717b}.subtitle{margin-bottom:22px}
.panel{background:#fff;border:1px solid #dce7e6;border-radius:17px;box-shadow:0 6px 24px rgba(25,54,65,.04);padding:23px;margin:18px 0}
.status{border-left:5px solid #13777c}.status.warn{border-left-color:#a55d17;background:#fffcf5}.status strong{display:block;margin-bottom:3px}.status p{margin:0;color:#455f69}.warnings{padding-left:20px;margin:9px 0 0;color:#8d491e}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}.metric{background:#fff;border:1px solid #dce7e6;border-radius:15px;padding:17px 18px;min-width:0}.metric small{color:#58717b;display:block;margin-bottom:7px}.metric strong{font-size:clamp(1.2rem,2.2vw,1.8rem);line-height:1.3;overflow-wrap:anywhere}.metric .sub{display:block;color:#637983;font-size:.77rem;margin-top:5px}.up{color:#b13837}.down{color:#13806b}.accent{color:#a45a1a}
.rowhead{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px}.segmented{display:flex;flex-wrap:wrap;gap:6px}.segmented button{border:1px solid #cbdcdb;background:#f4f8f7;color:#234754;border-radius:9px;padding:7px 13px;min-height:40px;font:inherit;cursor:pointer}.segmented button[aria-pressed="true"]{background:#125e66;color:#fff;border-color:#125e66}.segmented button:focus-visible,a:focus-visible,.candle-hit:focus-visible{outline:3px solid #dc832f;outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:8px 17px;font-size:.82rem;color:#516b76;margin:8px 0 15px}.swatch{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:baseline;background:currentColor}.legend .up,.legend .down{font-weight:700}
.chart-scroll{overflow-x:auto;overflow-y:hidden;border:1px solid #e7eeee;border-radius:10px;background:#fbfdfd}.chart-scroll svg{display:block}.chart-scroll:focus-visible{outline:3px solid #dc832f}
.chart-note{color:#657a82;font-size:.8rem;margin:12px 0 0}.inspect{margin:11px 0 0;min-height:48px;padding:10px 13px;border-radius:9px;background:#f0f6f5;color:#204751;font-size:.87rem}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.9rem;min-width:570px}th{text-align:left;color:#56707b;font-weight:600;border-bottom:1px solid #d9e5e4;padding:10px 12px}td{padding:11px 12px;border-bottom:1px solid #edf1f1}tbody tr:hover{background:#f6f9f8}td.num{text-align:right}th.num{text-align:right}.badge{display:inline-block;border-radius:20px;padding:2px 10px;background:#eff3f3;color:#43616a}.badge.entry{background:#fff0dc;color:#865015;font-weight:700}.empty{padding:28px 5px;color:#58717b}
.notes{font-size:.88rem;color:#49636d}.notes p{margin:9px 0}.export{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:16px}.export a{color:#075f69;text-underline-offset:3px}
footer{color:#637983;font-size:.79rem;margin-top:24px}
@media(max-width:780px){.wrap{padding:20px 14px 40px}.panel{padding:17px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.metric{padding:13px}.metric strong{font-size:1.28rem}}
@media(max-width:390px){.metric strong{font-size:1.05rem}.segmented button{padding:7px 9px}}
</style>
</head>
<body>
<main class="wrap">
<header><div class="kicker">A-SHARE · INDEX WATCH</div><h1 id="title">超卖观察</h1><p class="subtitle" id="identity"></p></header>
<section id="status" class="panel status" aria-live="polite"><strong id="status-title"></strong><p id="status-message"></p><ul id="warnings" class="warnings" hidden></ul></section>
<section class="metrics" aria-label="最新已记录行情"><div class="metric"><small>最新收盘 · 点</small><strong id="close">—</strong><span class="sub" id="latest-date"></span></div><div class="metric"><small>RSI(14)</small><strong id="rsi">—</strong><span class="sub">Wilder 平滑 · 超卖阈值 30</span></div><div class="metric"><small>布林带下轨 · 点</small><strong id="lower">—</strong><span class="sub">20 日 · 2 倍总体标准差</span></div><div class="metric"><small>最新交易日状态</small><strong id="state">—</strong><span class="sub" id="state-note"></span></div></section>
<section class="panel" aria-labelledby="chart-heading"><div class="rowhead"><h2 id="chart-heading">日线与指标</h2><div class="segmented" role="group" aria-label="图表显示区间" id="ranges"><button type="button" data-months="3" aria-pressed="true">近 3 个月</button><button type="button" data-months="12" aria-pressed="false">近 1 年</button><button type="button" data-months="24" aria-pressed="false">近 2 年</button></div></div>
<div class="legend" aria-label="图例"><span class="up"><i class="swatch"></i>上涨（红）</span><span class="down"><i class="swatch"></i>下跌（绿）</span><span style="color:#647d9d"><i class="swatch"></i>布林带上 / 中 / 下轨</span><span class="accent"><i class="swatch" style="border-radius:50%"></i>超卖日</span><span style="color:#99763c">- - RSI 30</span></div>
<div class="chart-scroll" id="chart-scroll" tabindex="0" aria-label="可水平滚动的日线图，按 Tab 键聚焦 K 线查看数值"><svg id="chart" role="img" aria-label="日 K 线、布林带、超卖标记及 RSI 指标图"></svg></div><div id="inspect" class="inspect" role="status" aria-live="polite">将鼠标移至 K 线，或用 Tab 键选择 K 线，查看当日行情与指标。</div><p class="chart-note">图表按实际交易日绘制；横向滚动可查看完整区间。预热期未形成的指标不连线。</p></section>
<section class="panel" aria-labelledby="signals-heading"><div class="rowhead"><h2 id="signals-heading">超卖日期 <span id="signal-count" class="muted"></span></h2><div class="segmented" role="group" aria-label="日期表筛选" id="filters"><button type="button" data-view="signals" aria-pressed="true">全部超卖日</button><button type="button" data-view="entries" aria-pressed="false">仅新触发日</button></div></div><p class="muted" id="table-context"></p><div class="table-wrap"><table><thead><tr><th scope="col">交易日期</th><th scope="col" class="num">收盘 · 点</th><th scope="col" class="num">RSI(14)</th><th scope="col" class="num">下轨 · 点</th><th scope="col">状态</th></tr></thead><tbody id="signal-rows"></tbody></table></div><p id="empty" class="empty" hidden></p></section>
<section class="panel notes" aria-labelledby="notes-heading"><h2 id="notes-heading">判定方式与风险提示</h2><p id="rule"></p><p>RSI 使用 Wilder 平滑；布林带采用最近 20 个收盘价的总体标准差（ddof=0）。仅用当日及此前数据计算；“新触发”是相对前一个已记录交易日从非超卖转为超卖，连续超卖日标为“持续”。指标预热期间不作超卖判定。</p><p>本页仅描述历史指数行情与机械规则，不预测未来表现，不构成买卖建议。指数不是可直接交易的证券；数据可能延迟、缺失或被修订，请核对数据状态与原始来源。</p><div class="export" aria-label="下载同目录数据"><a href="daily.csv" download>每日数据 CSV</a><a href="signals.csv" download>超卖日期 CSV</a><a href="entries.csv" download>新触发日期 CSV</a><a href="summary.json" download>完整报告 JSON</a></div></section>
<footer id="footer"></footer>
</main>
<script id="report-data" type="application/json">__REPORT_DATA__</script>
<script>
'use strict';
const report = JSON.parse(document.getElementById('report-data').textContent);
const $ = id => document.getElementById(id);
const finite = x => typeof x === 'number' && Number.isFinite(x);
const number = (x, digits = 2) => finite(x) ? x.toLocaleString('zh-CN', {minimumFractionDigits: digits, maximumFractionDigits: digits}) : '—';
const text = (id, value) => { $(id).textContent = value; };
const rows = report.rows || [];
const latest = report.latest || null;
const allSignals = report.signals || [];
const entries = report.entries || [];
const current = report.status === 'current';
text('title', (report.index?.name || '指数') + ' · 超卖观察');
text('identity', `指数代码 ${report.index?.code || '—'} · 观察窗口 ${report.window_start} — ${report.as_of} · 生成于 ${report.generated_at}`);
text('status-title', ({current:'数据已更新', awaiting_close:'等待当日收盘', no_current_bar:'尚无最新日线', historical:'历史数据快照', offline:'离线缓存快照'})[report.status] || '数据状态待核对');
text('status-message', (report.status_message || '') + (current ? ' · 以下状态以最新已记录交易日为准。' : ' · 数据未确认更新至当前交易日，不能据此判断今天是否出现信号。'));
$('status').classList.toggle('warn', !current);
const warnings = report.warnings || [];
if (warnings.length) { $('warnings').hidden = false; for (const item of warnings) { const li = document.createElement('li'); li.textContent = item; $('warnings').append(li); } }
text('close', number(latest?.close));
text('rsi', number(latest?.rsi));
text('lower', number(latest?.bb_lower));
text('latest-date', latest?.date ? `${latest.date} · 最新已记录交易日` : '暂无交易日数据');
text('state', latest ? (latest.oversold ? (latest.entry ? '超卖 · 新触发' : '超卖 · 持续') : '未超卖') : '暂无记录');
$('state').classList.toggle('accent', !!latest?.oversold);
text('state-note', current ? '仅表示最近已确认交易日' : '非当前实时判断 · 请查看数据状态');
text('rule', `规则：${report.rule?.description || 'RSI(14) < 30 且收盘价 ≤ 布林带下轨(20, 2)'}。两个条件需在同一交易日同时满足；使用未四舍五入的原始计算值判定。`);
text('footer', `数据区间 ${report.data_start} — ${report.data_end} · 来源：${report.index?.source || '未标明'}${report.index?.source_url ? ' · ' + report.index.source_url : ''} · 生成时间 ${report.generated_at}`);

let tableView = 'signals';
function renderTable() {
  const selection = tableView === 'entries' ? entries : allSignals;
  text('signal-count', `${allSignals.length} 个超卖交易日 · ${entries.length} 个新触发日`);
  text('table-context', `当前：${tableView === 'entries' ? '仅新触发日' : '全部超卖日'}（${selection.length} 条）；日期按交易日升序，列出观察窗口内所有符合条件的日期。`);
  $('signal-rows').replaceChildren();
  for (const row of selection) {
    const tr = document.createElement('tr');
    const cells = [row.date, number(row.close), number(row.rsi), number(row.bb_lower)];
    cells.forEach((value, index) => { const td = document.createElement('td'); td.textContent = value; if (index > 0) td.className = 'num'; tr.append(td); });
    const state = document.createElement('td'); const badge = document.createElement('span');
    badge.className = 'badge' + (row.entry ? ' entry' : ''); badge.textContent = row.entry ? '新触发' : '持续'; state.append(badge); tr.append(state);
    $('signal-rows').append(tr);
  }
  $('empty').hidden = !!selection.length;
  text('empty', tableView === 'entries' ? '观察窗口内没有新触发日。' : '观察窗口内没有超卖交易日。');
}
$('filters').addEventListener('click', event => {
  const button = event.target.closest('button[data-view]'); if (!button) return;
  tableView = button.dataset.view;
  for (const item of $('filters').querySelectorAll('button')) item.setAttribute('aria-pressed', String(item === button));
  renderTable();
});
renderTable();

const NS = 'http://www.w3.org/2000/svg';
function svgNode(tag, attributes = {}, content) {
  const node = document.createElementNS(NS, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, String(value));
  if (content !== undefined) node.textContent = content;
  return node;
}
function showCandle(row) {
  text('inspect', `${row.date} · 开 ${number(row.open)}  高 ${number(row.high)}  低 ${number(row.low)}  收 ${number(row.close)} · RSI ${number(row.rsi)} · 布林上轨 ${number(row.bb_upper)} / 中轨 ${number(row.bb_middle)} / 下轨 ${number(row.bb_lower)} · ${row.oversold ? (row.entry ? '超卖 · 新触发' : '超卖 · 持续') : '未超卖'}`);
}
function monthStart(dateString, months) {
  const [year, month, day] = dateString.slice(0, 10).split('-').map(Number);
  const monthIndex = year * 12 + month - 1 - months;
  const y = Math.floor(monthIndex / 12), m = monthIndex - y * 12 + 1;
  const d = Math.min(day, new Date(y, m, 0).getDate());
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}
function renderChart(months) {
  const chart = $('chart'); chart.replaceChildren();
  const endDate = report.as_of || rows.at(-1)?.date;
  const selected = endDate ? rows.filter(row => row.date >= monthStart(endDate, months) && row.date <= endDate) : [];
  const x0 = 72, step = Math.max(7, Math.min(15, 780 / Math.max(selected.length, 1))), width = Math.max(720, x0 + selected.length * step + 34);
  const top = 27, priceBottom = 292, rsiTop = 354, rsiBottom = 458, axisBottom = 505;
  chart.setAttribute('viewBox', `0 0 ${width} ${axisBottom}`);
  chart.setAttribute('width', width); chart.setAttribute('height', axisBottom);
  if (!selected.length) { chart.append(svgNode('text', {x:width / 2,y:230,'text-anchor':'middle',fill:'#59737c'}, '所选区间暂无交易日数据')); return; }
  const values = selected.flatMap(row => [row.low, row.high, row.bb_lower, row.bb_upper]).filter(finite);
  let lo = Math.min(...values), hi = Math.max(...values);
  const pad = (hi - lo || Math.max(Math.abs(hi) * .02, 1)) * .08; lo -= pad; hi += pad;
  const py = value => priceBottom - (value - lo) / (hi - lo) * (priceBottom - top);
  const ry = value => rsiBottom - Math.max(0, Math.min(100, value)) / 100 * (rsiBottom - rsiTop);
  const cx = i => x0 + i * step + step / 2;
  const grid = svgNode('g', {'aria-hidden':'true'}), bands = svgNode('g', {'aria-hidden':'true'}), candles = svgNode('g');
  chart.append(grid, bands, candles);
  for (let i = 0; i <= 4; i++) {
    const y = top + (priceBottom - top) * i / 4;
    grid.append(svgNode('line', {x1:x0,y1:y,x2:width-20,y2:y,stroke:'#e8eeee'}));
    grid.append(svgNode('text', {x:x0-9,y:y+4,'text-anchor':'end',fill:'#617984','font-size':11}, number(hi - (hi-lo)*i/4, 0)));
  }
  for (const level of [0, 30, 50, 100]) {
    const y = ry(level);
    grid.append(svgNode('line', {x1:x0,y1:y,x2:width-20,y2:y,stroke:level===30?'#b1955a':'#e8eeee','stroke-dasharray':level===30?'5 5':'none'}));
    grid.append(svgNode('text', {x:x0-9,y:y+4,'text-anchor':'end',fill:'#617984','font-size':11}, String(level)));
  }
  grid.append(svgNode('text', {x:8,y:16,fill:'#516e79','font-size':12}, '价格 · 点'));
  grid.append(svgNode('text', {x:8,y:rsiTop-12,fill:'#516e79','font-size':12}, 'RSI(14)'));
  function drawLine(key, scale, color, dash, parent, lineWidth = 1.4) {
    let points = [];
    function flush() { if (points.length > 1) parent.append(svgNode('polyline', {points:points.join(' '),fill:'none',stroke:color,'stroke-width':lineWidth,'stroke-dasharray':dash || 'none','vector-effect':'non-scaling-stroke'})); points = []; }
    selected.forEach((row, index) => { if (finite(row[key])) points.push(`${cx(index)},${scale(row[key])}`); else flush(); }); flush();
    // A single valid observation still matters: show a point, not an invisible line.
    selected.forEach((row,index) => { if (finite(row[key]) && !finite(selected[index-1]?.[key]) && !finite(selected[index+1]?.[key])) parent.append(svgNode('circle',{cx:cx(index),cy:scale(row[key]),r:2.5,fill:color})); });
  }
  drawLine('bb_upper', py, '#9eb1c2', '4 4', bands);
  drawLine('bb_middle', py, '#7a98b0', '', bands);
  drawLine('bb_lower', py, '#476c9b', '', bands, 2);
  drawLine('rsi', ry, '#8a59a5', '', bands, 1.8);
  selected.forEach((row, index) => {
    const x = cx(index), positive = row.close >= row.open, color = positive ? '#b13837' : '#13806b';
    if (![row.open,row.high,row.low,row.close].every(finite)) return;
    candles.append(svgNode('line', {x1:x,y1:py(row.high),x2:x,y2:py(row.low),stroke:color,'stroke-width':1.3}));
    const bodyTop = Math.min(py(row.open),py(row.close));
    candles.append(svgNode('rect', {x:x-Math.max(2,step*.3),y:bodyTop,width:Math.max(4,step*.6),height:Math.max(1.6,Math.abs(py(row.open)-py(row.close))),fill:color}));
    if (row.oversold) candles.append(svgNode('circle', {cx:x,cy:Math.min(priceBottom-5,py(row.low)+10),r:3.5,fill:'#d79027',stroke:'#fff','stroke-width':1.2}));
    const hit = svgNode('rect', {x:x-step/2,y:top,width:step,height:rsiBottom-top,fill:'transparent',class:'candle-hit',tabindex:'0',role:'button','aria-label':`${row.date}，收盘 ${number(row.close)}，RSI ${number(row.rsi)}，${row.oversold?'超卖':'未超卖'}`});
    hit.addEventListener('pointerenter', () => showCandle(row));
    hit.addEventListener('focus', () => showCandle(row));
    hit.addEventListener('click', () => showCandle(row));
    hit.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); showCandle(row); } });
    candles.append(hit);
  });
  const stride = Math.max(1, Math.ceil(selected.length / Math.max(4, width / 130)));
  for (let index = 0; index < selected.length; index += stride) grid.append(svgNode('text', {x:cx(index),y:axisBottom-21,'text-anchor':'middle',fill:'#617984','font-size':11}, selected[index].date.slice(2)));
  $('chart-scroll').scrollLeft = $('chart-scroll').scrollWidth;
}
$('ranges').addEventListener('click', event => {
  const button = event.target.closest('button[data-months]'); if (!button) return;
  for (const item of $('ranges').querySelectorAll('button')) item.setAttribute('aria-pressed', String(item === button));
  renderChart(Number(button.dataset.months));
});
renderChart(3);
</script>
</body>
</html>
'''
