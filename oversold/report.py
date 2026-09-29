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
<meta name="theme-color" content="#f5f6f1">
<title>超卖观察 · 931743</title>
<style>
:root {
  --paper:#f5f6f1; --surface:#fff; --ink:#25372e; --muted:#70796e; --line:#e2e6dc;
  --olive:#40563b; --olive-light:#edf1e7; --amber:#996622; --amber-light:#faf3e5;
  --red:#bc554d; --green:#347e68;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif;
  color:var(--ink); background:var(--paper); line-height:1.6; font-variant-numeric:tabular-nums;
}
*{box-sizing:border-box} [hidden]{display:none!important} html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0} a{color:inherit;text-decoration:none} button{font:inherit;cursor:pointer}
h1,h2,h3,p{margin:0} h2{font-size:18px;letter-spacing:-.025em} h3{font-size:14px}
button,a,summary{touch-action:manipulation}
:focus-visible{outline:3px solid #a17c35;outline-offset:4px}
::selection{background:#dfe8cc} .wrap{max-width:1480px;margin:auto;padding:0 48px}
.icon{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex:none}
.eyebrow{font-size:10px;font-weight:600;letter-spacing:.18em;color:var(--muted)}
.muted{color:var(--muted)} .up{color:var(--red)} .down{color:var(--green)} .accent{color:var(--amber)}
.topbar{height:88px;display:flex;align-items:center;justify-content:space-between;gap:24px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:12px;flex:none}
.brand-mark{width:38px;height:38px;padding:9px;background:var(--olive);border-radius:11px;color:#fff}
.brand strong{display:block;font-size:17px;letter-spacing:.08em;line-height:1.4}
.brand small{font-size:9px;letter-spacing:.16em;color:var(--muted)}
.nav{display:flex;gap:32px;font-size:13px;color:var(--muted)} .nav a:hover{color:var(--olive)}
.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:40px;padding:8px 15px;border:1px solid var(--line);border-radius:9px;background:#fff;font-size:12px;font-weight:600;transition:background .15s,border-color .15s}
.button:hover{background:var(--olive-light);border-color:#bac6ae}
.hero{display:flex;align-items:center;justify-content:space-between;gap:28px;padding:38px 0 29px}
.hero .eyebrow{margin-bottom:12px;color:var(--olive)}
.hero-title{display:flex;align-items:baseline;gap:15px;flex-wrap:wrap}
h1{font-size:clamp(24px,2.5vw,36px);font-weight:650;line-height:1.4;letter-spacing:-.045em}
.index-code{font-size:12px;letter-spacing:.08em;color:var(--muted);border:1px solid #d9dfd0;border-radius:5px;padding:2px 7px}
.subtitle{font-size:13px;color:var(--muted);margin-top:11px}
.snapshot-date{text-align:right;flex:none;border-left:1px solid var(--line);padding-left:32px}
.snapshot-date small{display:block;color:var(--muted);font-size:11px}
.snapshot-date strong{font-size:30px;font-weight:500;letter-spacing:-.04em}
.snapshot-date span{font-size:12px;color:var(--muted);margin-left:9px}
.status{display:flex;gap:12px;align-items:flex-start;background:var(--olive-light);border:1px solid #dfe6d5;border-radius:10px;padding:12px 16px;font-size:12px;color:var(--olive)}
.status .icon{margin-top:1px} .status strong{font-weight:650;margin-right:10px;white-space:nowrap}
.status p{display:inline} .status.warn{color:#886027;background:#fbf6eb;border-color:#ece1c9}
.warnings{margin:6px 0 0;padding-left:18px} .status-meta{font-size:11px;opacity:.85;margin-top:3px}
.metrics{display:grid;grid-template-columns:1.22fr 1fr 1fr 1.12fr;gap:16px;margin:22px 0 26px}
.metric{min-width:0;position:relative;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 23px 19px}
.metric-label{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:12px;color:var(--muted)}
.metric-label .icon{width:16px;height:16px;opacity:.7}
.metric-value{display:block;font-size:32px;font-weight:550;line-height:1.2;letter-spacing:-.045em;margin-top:15px}
.metric-note{font-size:11px;color:var(--muted);margin-top:12px;min-height:18px}
.metric-price{background:var(--olive);border-color:var(--olive);color:#fff;overflow:hidden}
.metric-price .metric-label,.metric-price .metric-note{color:#d4ddca}
.price-bottom{display:flex;align-items:flex-end;justify-content:space-between;gap:8px;margin-top:12px}
.price-change{font-size:12px;white-space:nowrap} .metric-price .up{color:#ffd1ba}.metric-price .down{color:#c0e6c9}
.sparkline{width:105px;height:28px;opacity:.75;flex-shrink:1}
.meter{position:relative;height:4px;margin-top:20px;border-radius:9px;background:linear-gradient(to right,#dfcda5 30%,#e9ede3 30%)}
.meter::after{content:"";position:absolute;left:30%;top:-3px;height:10px;border-left:1px solid #b09158}
.meter-dot{position:absolute;top:-3px;width:10px;height:10px;border-radius:50%;background:var(--olive);border:2px solid #fff;box-shadow:0 0 0 1px var(--olive);transform:translateX(-50%)}
.meter-labels{display:flex;justify-content:space-between;color:var(--muted);font-size:10px;margin-top:7px}
.metric-state .metric-value{font-size:25px;margin-top:18px;display:flex;align-items:center;gap:9px}
.state-dot{width:8px;height:8px;border-radius:50%;background:#8e9c7f;box-shadow:0 0 0 5px var(--olive-light);flex:none}
.metric-state.triggered .state-dot{background:var(--amber);box-shadow:0 0 0 5px var(--amber-light)}
.metric-state.triggered .metric-value{color:var(--amber)}
.workspace{display:grid;grid-template-columns:minmax(0,1fr) 286px;gap:22px;align-items:start}
.panel{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:16px}
.panel-head{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:25px 26px 17px}
.section-tag{font-size:10px;letter-spacing:.13em;color:var(--muted);margin-bottom:4px}
.panel-subtitle{font-size:11px;color:var(--muted);margin-top:5px}
.segmented{display:flex;gap:3px;background:#f3f5ef;border:1px solid #e8ebe2;padding:3px;border-radius:8px;flex:none}
.segmented button{background:transparent;border:0;border-radius:5px;min-height:34px;padding:6px 13px;font-size:12px;color:var(--muted);white-space:nowrap}
.segmented button:hover{color:var(--olive);background:#e8eddf}
.segmented button[aria-pressed="true"]{background:#fff;color:var(--olive);box-shadow:0 1px 4px #25372e12;font-weight:650}
.legend{display:flex;flex-wrap:wrap;align-items:center;gap:9px 17px;padding:0 26px 18px;font-size:10px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:5px}.swatch{display:inline-block;width:13px;height:2px;background:currentColor}
.swatch.candle{width:5px;height:9px;border-radius:1px}.swatch.dot{width:6px;height:6px;border-radius:50%;background:var(--amber)}
.band-key{color:#8093a0}.rsi-key{color:#75844e}
.chart-scroll{overflow:auto hidden;margin:0 16px;scrollbar-width:thin;scrollbar-color:#ced6c6 transparent;overscroll-behavior-x:contain}
.chart-scroll svg{display:block;font-family:inherit}.candle-hit:focus{outline:none}
.candle-hit:focus-visible{stroke:#8b773e;stroke-width:1;stroke-dasharray:3 4}
.inspect{margin:4px 26px 0;border-top:1px solid var(--line);padding:14px 0 0}
.inspect-head{display:flex;justify-content:space-between;gap:10px;font-size:11px;margin-bottom:10px}
.inspect-head strong{font-size:12px;font-weight:600}.inspect-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.inspect-grid small{display:block;color:var(--muted);font-size:10px;margin-bottom:2px}.inspect-grid span{font-size:13px;font-weight:550}
.inspect-bands{font-size:10px;color:var(--muted);margin-top:10px}
.chart-note{font-size:10px;color:var(--muted);padding:12px 26px 20px}
.sidebar{display:grid;gap:18px}.window-card{padding:24px;background:#ecf0e5;border:1px solid #dce3d1;border-radius:16px}
.window-card .section-tag{color:#66765a}.window-dates{font-size:11px;color:#697960;margin-top:10px}
.window-stats{display:grid;grid-template-columns:1fr 1fr;margin:22px 0;padding-bottom:20px;border-bottom:1px solid #d4dccb}
.window-stats div+div{border-left:1px solid #d4dccb;padding-left:22px}
.window-stats strong{display:block;font-size:38px;line-height:1.2;font-weight:500;letter-spacing:-.05em}
.window-stats small{display:block;font-size:11px;color:#657459;margin-top:7px}
.last-signal small{display:block;font-size:11px;color:#657459}.last-signal strong{display:block;font-size:17px;font-weight:550;margin:5px 0}
.last-signal p{font-size:11px;color:#657459}.window-link{display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-top:22px;font-weight:600}
.window-link:hover{text-decoration:underline;text-underline-offset:4px}
.rule-card{padding:22px 24px}.rule-intro{font-size:11px;color:var(--muted);margin-top:5px}
.rule-item{display:flex;gap:11px;padding-top:20px}.rule-number{width:25px;height:25px;display:grid;place-items:center;border:1px solid var(--line);border-radius:50%;font-size:10px;color:var(--muted);flex:none}
.rule-item strong{font-size:12px;font-weight:550}.rule-item p{font-size:11px;color:var(--muted);margin-top:3px}
.rule-result{font-size:10px;display:inline-block;background:var(--olive-light);color:var(--olive);padding:1px 7px;border-radius:4px;margin-top:6px}
.rule-result.met{background:var(--amber-light);color:var(--amber)}
.rule-footnote{font-size:10px;color:var(--muted);border-top:1px solid var(--line);margin-top:18px;padding-top:13px}
.signals-panel{margin-top:26px;overflow:hidden}.count-pill{display:inline-block;vertical-align:middle;font-size:11px;font-weight:500;background:var(--olive-light);color:var(--olive);padding:1px 9px;margin-left:8px;border-radius:5px}
.table-context{padding:0 26px 18px;font-size:11px;color:var(--muted)}.table-wrap{overflow-x:auto;scrollbar-width:thin}
table{border-collapse:collapse;width:100%;min-width:720px;text-align:left;font-size:12px}
th{color:var(--muted);font-size:11px;font-weight:500;background:#f8f9f5;padding:12px 24px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:15px 24px;border-bottom:1px solid #eef0e9;white-space:nowrap}.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:last-child td{border-bottom:0}tbody tr:hover{background:#f7f9f3}.date-cell{font-weight:550;color:#40503e}
.reason{display:inline-block;font-size:10px;color:#74715b;border:1px solid #e8e6d9;border-radius:4px;padding:2px 7px;margin-right:5px;background:#fcfbf7}
.badge{display:inline-flex;align-items:center;gap:5px;border-radius:5px;font-size:10px;padding:3px 8px;background:#f0f2ed;color:#6c7764}
.badge.entry{background:#f5eddb;color:#956922}.badge::before{content:"";width:4px;height:4px;border-radius:50%;background:currentColor}
.empty{padding:40px 26px;color:var(--muted);font-size:13px}.mobile-hint{display:none}
.bottom-grid{display:grid;grid-template-columns:minmax(0,1fr) 350px;gap:28px;margin:28px 0}
.notes{padding:22px 0;font-size:12px;color:var(--muted)}.notes h2{color:var(--ink);font-size:14px;margin-bottom:10px}
.notes p{line-height:1.9}.notes details{margin-top:15px}.notes summary{width:fit-content;cursor:pointer;color:var(--olive);font-size:11px;min-height:30px;padding:3px 0}
.notes details p{font-size:11px;margin-top:9px}.risk{border-left:2px solid #cbd3be;padding-left:13px;margin-top:12px}
.exports{background:#eef1e8;border:1px solid var(--line);border-radius:12px;padding:21px 23px;align-self:start}
.export-heading{display:flex;justify-content:space-between;align-items:center}.exports h2{font-size:14px}.exports p{font-size:10px;color:var(--muted);margin-top:4px}
.export-links{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}.export-links a{font-size:11px;background:#fff;border:1px solid #dce2d3;border-radius:6px;padding:9px 10px;display:flex;justify-content:space-between;gap:5px}
.export-links a:hover{border-color:#97a784;color:var(--olive)}.export-links span{color:#859277}
footer{border-top:1px solid var(--line);padding:21px 0 30px;color:var(--muted);font-size:10px;display:flex;align-items:flex-start;justify-content:space-between;gap:22px}
.footer-brand{white-space:nowrap;letter-spacing:.08em;color:var(--olive);font-weight:600}.provenance{text-align:right;max-width:80%;overflow-wrap:anywhere}.provenance p+p{margin-top:4px}
.skip-link{position:absolute;top:-60px;left:20px;z-index:10;padding:10px 18px;background:var(--ink);color:#fff;border-radius:7px}.skip-link:focus{top:12px}
noscript p{padding:20px;background:var(--amber-light);color:var(--amber)}
@media(min-width:1600px){.wrap{padding:0 56px}.hero{padding-top:44px;padding-bottom:33px}}
@media(max-width:1150px){
  .wrap{padding:0 28px}.metrics{gap:12px}.metric{padding:20px 17px}.metric-value{font-size:28px}
  .workspace{grid-template-columns:minmax(0,1fr) 248px;gap:18px}.panel-head{padding:22px 20px 17px;flex-wrap:wrap}
  .rule-card,.window-card{padding:21px}.legend{padding-left:20px;padding-right:20px}.segmented button{padding:6px 11px}
  .inspect{margin-left:20px;margin-right:20px}.chart-note{padding-left:20px;padding-right:20px}.nav{gap:24px}
}
@media(max-width:900px){
  .workspace{grid-template-columns:minmax(0,1fr)}.sidebar{grid-template-columns:1fr 1fr;align-items:stretch}
  .metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.metric{padding:21px 23px}.metric-value{font-size:32px}
  .metric-state .metric-value{font-size:27px}.bottom-grid{grid-template-columns:minmax(0,1fr) 300px;gap:22px}
  .hero-title{gap:8px}.snapshot-date{padding-left:22px}.hero{gap:20px}.nav{gap:20px;font-size:12px}
}
@media(max-width:600px){
  .wrap{padding:0 18px}.topbar{height:74px;gap:14px}.brand{gap:9px}.brand strong{font-size:15px}.brand small{font-size:8px}
  .brand-mark{width:33px;height:33px;padding:8px;border-radius:9px}.nav{display:none}.topbar .button{font-size:11px;padding:8px 11px}
  .hero{padding:27px 0 23px}.hero .eyebrow{font-size:8px;letter-spacing:.12em;margin-bottom:10px}
  h1{font-size:25px}.hero-title{gap:7px}.index-code{font-size:10px}.subtitle{font-size:11px;line-height:1.8}.snapshot-date{display:none}
  .status{padding:12px;font-size:11px;gap:9px}.status strong{display:block;margin-bottom:4px}.status-meta{font-size:10px;margin-top:6px}
  .metrics{gap:10px;margin:17px 0 20px}.metric{padding:17px 15px;border-radius:12px}.metric-label{font-size:10px}.metric-label .icon{display:none}
  .metric-value{font-size:27px;margin-top:14px}.metric-note{font-size:10px;line-height:1.7}.metric-state .metric-value{font-size:21px}
  .price-bottom{gap:4px}.price-change{font-size:10px}.sparkline{width:54px;height:25px}.meter-labels{font-size:9px}
  .panel{border-radius:13px}.panel-head{padding:20px 17px 15px;gap:15px}.section-tag{font-size:9px}h2{font-size:17px}
  .chart-panel .panel-head{display:block}.chart-panel .segmented{margin-top:16px;width:fit-content}
  .legend{padding:0 17px 15px;gap:9px 13px;font-size:9px}.chart-scroll{margin:0 9px}.chart-note{padding:11px 17px 17px;line-height:1.8}
  .inspect{margin:4px 17px 0}.inspect-head{flex-wrap:wrap;gap:5px}.inspect-grid{gap:6px}.inspect-grid span{font-size:11px}.inspect-grid small{font-size:9px}.inspect-bands{font-size:9px}
  .sidebar{gap:13px;grid-template-columns:minmax(0,1fr)}.window-card{padding:22px}.window-stats{margin:17px 0}.window-stats div+div{padding-left:27px}
  .rule-card{padding:22px}.rule-item{padding-top:16px}.signals-panel{margin-top:20px}.signals-panel .panel-head{display:block}.signals-panel .segmented{margin-top:15px;width:fit-content}
  .table-context{padding:0 17px 15px}.mobile-hint{display:block;margin-top:5px;color:#8c927f}
  th,td{padding:13px 17px}.table-wrap th:first-child,.table-wrap td:first-child{position:sticky;left:0;background:#fff;border-right:1px solid var(--line)}
  .table-wrap th:first-child{background:#f8f9f5}.table-wrap tr:hover td:first-child{background:#f7f9f3}
  .bottom-grid{grid-template-columns:minmax(0,1fr);gap:8px;margin:18px 0 24px}.notes{padding:16px 2px}.exports{padding:20px}
  footer{display:block;font-size:9px}.provenance{text-align:left;max-width:none;margin-top:10px}.provenance p+p{margin-top:7px}
}
@media(max-width:360px){.wrap{padding:0 12px}.metric{padding:16px 12px}.metric-value{font-size:24px}.metric-state .metric-value{font-size:19px}.hero .eyebrow{letter-spacing:.07em}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.button{transition:none}}
</style>
</head>
<body>
<a href="#overview" class="skip-link">跳转到行情概览</a>
<div class="wrap">
  <header class="topbar">
    <a class="brand" href="#overview" aria-label="超卖观察，返回行情概览">
      <svg class="brand-mark" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 17V11M9 20V6M14 15V3M19 18V8" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
      <span><strong>超卖观察</strong><small>MARKET OBSERVATORY</small></span>
    </a>
    <nav class="nav" aria-label="页面导航"><a href="#overview">行情概览</a><a href="#chart-section">走势分析</a><a href="#signals-section">信号记录</a></nav>
    <a class="button" href="#exports"><svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m-4-4 4 4 4-4M5 16v4h14v-4"/></svg>下载数据</a>
  </header>
  <main id="overview">
    <section class="hero" aria-labelledby="title">
      <div><p class="eyebrow">A-SHARE RESEARCH / SEMICONDUCTOR</p><div class="hero-title"><h1 id="title">中证半导体材料设备主题指数</h1><span class="index-code" id="index-code">931743</span></div><p class="subtitle">追踪价格与动量，记录规则触发。<span id="identity"></span></p></div>
      <div class="snapshot-date"><small>最新已记录交易日</small><strong id="snapshot-day">—</strong><span id="snapshot-year"></span></div>
    </section>
    <section id="status" class="status" aria-live="polite">
      <svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
      <div><strong id="status-title"></strong><p id="status-message"></p><div class="status-meta" id="status-context"></div><ul id="warnings" class="warnings" hidden></ul></div>
    </section>
    <section class="metrics" aria-label="最新已记录行情">
      <article class="metric metric-price"><div class="metric-label">最新收盘 · 指数点<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m3 16 6-6 4 4 8-10M15 4h6v6"/></svg></div><strong class="metric-value" id="close">—</strong><div class="price-bottom"><span class="price-change" id="price-change">—</span><svg id="sparkline" class="sparkline" viewBox="0 0 110 30" aria-hidden="true"></svg></div><p class="metric-note" id="latest-date"></p></article>
      <article class="metric"><div class="metric-label">相对强弱 · RSI(14)<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h4l3-7 4 14 3-7h4"/></svg></div><strong class="metric-value" id="rsi">—</strong><div class="meter" aria-hidden="true"><i class="meter-dot" id="rsi-marker" hidden></i></div><div class="meter-labels"><span>0</span><span>30 · 超卖阈值</span><span>100</span></div><p class="metric-note">Wilder 平滑 · 14 个交易日</p></article>
      <article class="metric"><div class="metric-label">布林带下轨 · 指数点<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></div><strong class="metric-value" id="lower">—</strong><p class="metric-note" id="band-distance"></p><p class="metric-note">20 日均线 · 2 倍总体标准差</p></article>
      <article class="metric metric-state" id="state-card"><div class="metric-label">最新交易日信号<span class="eyebrow">SIGNAL</span></div><div class="metric-value"><i class="state-dot" aria-hidden="true"></i><strong id="state">—</strong></div><p class="metric-note" id="state-reason"></p><p class="metric-note" id="state-note"></p></article>
    </section>
    <div class="workspace">
      <section class="panel chart-panel" id="chart-section" aria-labelledby="chart-heading">
        <div class="panel-head"><div><p class="section-tag">PRICE &amp; MOMENTUM</p><h2 id="chart-heading">行情与动量</h2><p class="panel-subtitle" id="chart-range"></p></div><div class="segmented" role="group" aria-label="图表显示区间" id="ranges"><button type="button" data-months="3" aria-pressed="true">近 3 个月</button><button type="button" data-months="12" aria-pressed="false">近 1 年</button><button type="button" data-months="24" aria-pressed="false">近 2 年</button></div></div>
        <div class="legend" aria-label="图例"><span class="up"><i class="swatch candle"></i>上涨</span><span class="down"><i class="swatch candle"></i>下跌</span><span class="band-key"><i class="swatch"></i>布林带 (20, 2)</span><span class="rsi-key"><i class="swatch"></i>RSI (14)</span><span><i class="swatch dot"></i>超卖日</span></div>
        <div class="chart-scroll" id="chart-scroll" tabindex="0" role="region" aria-label="可横向滚动的日线图"><svg id="chart" role="group" aria-label="日 K 线、布林带与 RSI 图；Tab 进入，左右方向键选择交易日，Home 和 End 跳转首尾"></svg></div>
        <div id="inspect" class="inspect" role="status" aria-live="polite" aria-atomic="true"><div class="inspect-head"><strong id="inspect-date">选择交易日查看数据</strong><span id="inspect-state" class="muted"></span></div><div class="inspect-grid"><div><small>开盘</small><span id="inspect-open">—</span></div><div><small>最高</small><span id="inspect-high">—</span></div><div><small>最低</small><span id="inspect-low">—</span></div><div><small>收盘</small><span id="inspect-close">—</span></div><div><small>RSI(14)</small><span id="inspect-rsi">—</span></div></div><p id="inspect-bands" class="inspect-bands"></p></div>
        <p class="chart-note">悬停或轻触 K 线查看详情；键盘 Tab 进入后用 ← → 切换。长区间可横向滚动；指标预热期不连线。</p>
      </section>
      <aside class="sidebar" aria-label="观察窗口与判定逻辑">
        <section class="window-card" aria-labelledby="window-heading"><p class="section-tag">THE BIG PICTURE</p><h2 id="window-heading">两年观察窗口</h2><p class="window-dates" id="window-dates"></p><div class="window-stats"><div><strong id="total-signals">—</strong><small>超卖交易日</small></div><div><strong id="total-entries">—</strong><small>新触发日</small></div></div><div class="last-signal"><small>窗口内最近一次新触发</small><strong id="last-entry-date">—</strong><p id="last-entry-reason"></p></div><a href="#signals-section" class="window-link">查看完整信号记录 <span aria-hidden="true">→</span></a></section>
        <section class="panel rule-card" aria-labelledby="rule-heading"><p class="section-tag">SIGNAL LOGIC</p><h2 id="rule-heading">任一满足，即为超卖</h2><p class="rule-intro">两个指标均完成预热后判定</p><div class="rule-item"><span class="rule-number">01</span><div><strong>RSI(14) &lt; 30</strong><p>相对强弱进入超卖区间</p><span class="rule-result" id="rsi-condition">—</span></div></div><div class="rule-item"><span class="rule-number">02</span><div><strong>收盘价 &lt; 布林带下轨</strong><p>严格跌破，不含等于下轨</p><span class="rule-result" id="band-condition">—</span></div></div><p class="rule-footnote" id="condition-date"></p></section>
      </aside>
    </div>
    <section class="panel signals-panel" id="signals-section" aria-labelledby="signals-heading">
      <div class="panel-head"><div><p class="section-tag">SIGNAL HISTORY</p><h2 id="signals-heading">历史信号记录 <span id="signal-count" class="count-pill"></span></h2></div><div class="segmented" role="group" aria-label="日期表筛选" id="filters"><button type="button" data-view="signals" aria-pressed="true">全部超卖日</button><button type="button" data-view="entries" aria-pressed="false">仅新触发日</button></div></div>
      <div class="table-context"><p id="table-context"></p><span class="mobile-hint">左右滑动查看完整指标 · 日期列固定</span></div>
      <div class="table-wrap" tabindex="0" role="region" aria-label="超卖日期与指标明细，可横向滚动"><table><thead><tr><th scope="col">交易日期</th><th scope="col" class="num">收盘 · 点</th><th scope="col" class="num">RSI(14)</th><th scope="col" class="num">下轨 · 点</th><th scope="col">触发原因</th><th scope="col">信号状态</th></tr></thead><tbody id="signal-rows"></tbody></table></div><p id="empty" class="empty" hidden></p>
    </section>
    <div class="bottom-grid">
      <section class="notes" aria-labelledby="notes-heading"><h2 id="notes-heading">读懂信号，而不是预测市场</h2><p id="rule"></p><p class="risk">超卖不等于低估，也不意味着买点。本页仅记录历史行情与机械规则，不构成投资建议；更频繁的信号不代表更高胜率。指数并非可直接交易的证券。</p><details><summary>指标口径与数据限制</summary><p>RSI 使用 Wilder 平滑；布林带采用最近 20 个收盘价的总体标准差（ddof=0）。两个指标均完成预热后才判定，使用未四舍五入的原始值。仅使用当日及此前数据；“新触发”是相对前一个已记录交易日从非超卖转为超卖，连续超卖日标为“持续”。</p><p>全部日期按北京时间（Asia/Shanghai）。15:30 前排除当日日线；缺少今日日线不代表今日未超卖。数据可能延迟、缺失或修订，请同时核对顶部数据状态与原始来源。</p></details></section>
      <section class="exports" id="exports" aria-labelledby="export-heading"><div class="export-heading"><h2 id="export-heading">把数据带走</h2><svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m-4-4 4 4 4-4M5 16v4h14v-4"/></svg></div><p>同一份报告快照 · CSV / JSON</p><div class="export-links"><a href="daily.csv" download>每日行情 <span>CSV ↓</span></a><a href="signals.csv" download>超卖日期 <span>CSV ↓</span></a><a href="entries.csv" download>新触发日 <span>CSV ↓</span></a><a href="summary.json" download>完整报告 <span>JSON ↓</span></a></div></section>
    </div>
  </main>
  <footer><span class="footer-brand">超卖观察 / 931743</span><div class="provenance"><p id="footer"></p><p id="source"></p></div></footer>
  <noscript><p>请启用 JavaScript 查看交互图表；也可直接打开同目录的 CSV 与 JSON 数据文件。</p></noscript>
</div>
<script id="report-data" type="application/json">__REPORT_DATA__</script>
<script>
'use strict';
const report = JSON.parse(document.getElementById('report-data').textContent);
const $ = id => document.getElementById(id);
const finite = x => typeof x === 'number' && Number.isFinite(x);
const number = (x, digits = 2) => finite(x) ? x.toLocaleString('zh-CN', {minimumFractionDigits:digits, maximumFractionDigits:digits}) : '—';
const text = (id, value) => { $(id).textContent = value; };
const rows = report.rows || [];
const latest = report.latest || null;
const allSignals = report.signals || [];
const entries = report.entries || [];
const current = report.status === 'current';
const ready = row => finite(row?.rsi) && finite(row?.bb_lower);
const signalLabel = row => !row ? '暂无记录' : !ready(row) ? '指标预热中' : row.oversold ? (row.entry ? '超卖 · 新触发' : '超卖 · 持续') : '未触发超卖';
const generated = (report.generated_at || '').replace('T', ' ').replace(/\+08:00$/, '（北京时间）');
text('title', report.index?.name || '指数超卖观察');
text('index-code', report.index?.code || '—');
text('identity', '日线观察 / 非实时行情');
text('snapshot-day', latest?.date ? latest.date.slice(5).replace('-', '.') : '—');
text('snapshot-year', latest?.date?.slice(0, 4) || '');
text('status-title', ({current:'收盘数据已更新', awaiting_close:'等待当日收盘', no_current_bar:'尚无最新日线', historical:'历史数据快照', offline:'离线缓存快照'})[report.status] || '数据状态待核对');
text('status-message', report.status_message || '请核对原始数据。');
text('status-context', current ? `生成于 ${generated} · 以下信号仅对应最近已确认交易日。` : `生成于 ${generated} · 未确认当前交易日数据，不能据此判断今天是否出现信号。`);
$('status').classList.toggle('warn', !current);
const warnings = report.warnings || [];
if (warnings.length) {
  $('warnings').hidden = false;
  for (const item of warnings) { const li = document.createElement('li'); li.textContent = item; $('warnings').append(li); }
}
text('close', number(latest?.close));
text('rsi', number(latest?.rsi));
text('lower', number(latest?.bb_lower));
text('latest-date', latest?.date ? `${latest.date} · 已记录` : '暂无交易日数据');
const previous = rows.length > 1 ? rows[rows.length - 2] : null;
const change = finite(latest?.close) && finite(previous?.close) && previous.close !== 0 ? (latest.close / previous.close - 1) * 100 : null;
text('price-change', finite(change) ? `${change > 0 ? '+' : ''}${number(change)}% 较前一交易日` : '暂无前日对比');
if (finite(change) && change !== 0) $('price-change').classList.add(change > 0 ? 'up' : 'down');
if (finite(latest?.rsi)) {
  $('rsi-marker').hidden = false;
  $('rsi-marker').style.left = `${Math.max(0, Math.min(100, latest.rsi))}%`;
  $('rsi').classList.toggle('accent', latest.rsi < report.rule.rsi_threshold);
}
const distance = finite(latest?.close) && finite(latest?.bb_lower) && latest.bb_lower > 0 ? (latest.close / latest.bb_lower - 1) * 100 : null;
text('band-distance', finite(distance) ? (distance === 0 ? '当前收盘等于下轨' : `当前收盘${distance > 0 ? '高于' : '低于'}下轨 ${number(Math.abs(distance))}%`) : '指标尚未形成');
text('state', signalLabel(latest));
text('state-reason', latest?.trigger_reason || (ready(latest) ? 'RSI 与布林条件均未满足' : '等待完整指标数据'));
text('state-note', latest?.date ? `仅对应 ${latest.date}，非实时信号` : '请核对顶部数据状态');
$('state-card').classList.toggle('triggered', !!latest?.oversold);
text('window-dates', `${report.window_start} — ${report.as_of}`);
text('total-signals', allSignals.length);
text('total-entries', entries.length);
const lastEntry = entries.at(-1);
text('last-entry-date', lastEntry?.date || '窗口内暂无新触发');
text('last-entry-reason', lastEntry?.trigger_reason || '没有记录不代表未来不会发生。');
for (const [id, value, threshold] of [['rsi-condition', latest?.rsi, report.rule.rsi_threshold], ['band-condition', latest?.close, latest?.bb_lower]]) {
  const known = finite(value) && finite(threshold);
  text(id, known ? (value < threshold ? '已满足' : '未满足') : '未就绪');
  $(id).classList.toggle('met', known && value < threshold);
}
text('condition-date', latest?.date ? `条件状态对应 ${latest.date}；仅为机械筛选，不是交易建议。` : '暂无可判断的交易日。');
text('rule', `判定规则：${report.rule.description}。任一条件满足即可触发，日期表列明原因。`);
text('footer', `数据覆盖 ${report.data_start} — ${report.data_end} · 生成于 ${generated}`);
text('source', `来源：${report.index?.source || '未标明'}${report.index?.source_url ? ' · ' + report.index.source_url : ''}`);

let tableView = 'signals';
function renderTable() {
  const selection = tableView === 'entries' ? entries : allSignals;
  text('signal-count', `${selection.length} 日`);
  text('table-context', `${tableView === 'entries' ? '仅新触发日' : '全部超卖日'} · ${selection.length} 条记录 · 按交易日期从近到远排列；连续超卖只在首日标记“新触发”。`);
  $('signal-rows').replaceChildren();
  for (const row of selection.slice().reverse()) {
    const tr = document.createElement('tr');
    const cells = [row.date, number(row.close), number(row.rsi), number(row.bb_lower)];
    cells.forEach((value, index) => {
      const td = document.createElement('td'); td.textContent = value;
      td.className = index === 0 ? 'date-cell' : 'num';
      if (index === 2 && finite(row.rsi) && row.rsi < report.rule.rsi_threshold) td.classList.add('accent');
      tr.append(td);
    });
    const reasons = document.createElement('td');
    for (const reason of (row.trigger_reason || '—').split(' + ')) {
      const tag = document.createElement('span'); tag.className = 'reason'; tag.textContent = reason; reasons.append(tag);
    }
    tr.append(reasons);
    const state = document.createElement('td'), badge = document.createElement('span');
    badge.className = 'badge' + (row.entry ? ' entry' : ''); badge.textContent = row.entry ? '新触发' : '持续';
    state.append(badge); tr.append(state); $('signal-rows').append(tr);
  }
  $('empty').hidden = !!selection.length;
  text('empty', tableView === 'entries' ? '这个观察窗口内，没有新的超卖触发。' : '这个观察窗口内，没有符合规则的超卖交易日。');
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
const sparkRows = rows.slice(-24).filter(row => finite(row.close));
if (sparkRows.length > 1) {
  const values = sparkRows.map(row => row.close), lo = Math.min(...values), span = Math.max(...values) - lo;
  const points = values.map((value, i) => `${2 + i / (values.length - 1) * 106},${span ? 27 - (value - lo) / span * 24 : 15}`);
  $('sparkline').append(svgNode('polyline', {points:points.join(' '), fill:'none', stroke:'#d3e1b7', 'stroke-width':1.7, 'stroke-linecap':'round', 'stroke-linejoin':'round'}));
}
function showCandle(row) {
  text('inspect-date', row?.date || '所选区间暂无数据');
  for (const key of ['open', 'high', 'low', 'close', 'rsi']) text(`inspect-${key}`, number(row?.[key]));
  text('inspect-state', `${signalLabel(row)}${row?.trigger_reason ? ' · ' + row.trigger_reason : ''}`);
  $('inspect-state').classList.toggle('accent', !!row?.oversold);
  text('inspect-bands', row ? `布林带 · 上轨 ${number(row.bb_upper)} / 中轨 ${number(row.bb_middle)} / 下轨 ${number(row.bb_lower)}` : '切换显示区间，或核对数据覆盖范围。');
}
function monthStart(dateString, months) {
  const [year, month, day] = dateString.slice(0, 10).split('-').map(Number);
  const monthIndex = year * 12 + month - 1 - months;
  const y = Math.floor(monthIndex / 12), m = monthIndex - y * 12 + 1;
  const d = Math.min(day, new Date(y, m, 0).getDate());
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}
let chartMonths = 3;
function renderChart() {
  const chart = $('chart'), scroll = $('chart-scroll'); chart.replaceChildren();
  const endDate = report.as_of || rows.at(-1)?.date;
  const selected = endDate ? rows.filter(row => row.date >= monthStart(endDate, chartMonths) && row.date <= endDate) : [];
  const x0 = 58, right = 24, available = Math.max(650, scroll.clientWidth);
  const step = Math.max(6.5, (available - x0 - right) / Math.max(selected.length, 1));
  const width = Math.max(available, x0 + selected.length * step + right);
  const top = 24, priceBottom = 244, rsiTop = 294, rsiBottom = 376, axisBottom = 414;
  chart.setAttribute('viewBox', `0 0 ${width} ${axisBottom}`);
  chart.setAttribute('width', width); chart.setAttribute('height', axisBottom);
  text('chart-range', selected.length ? `${selected[0].date} — ${selected.at(-1).date} · ${selected.length} 个交易日` : '所选区间暂无交易日数据');
  if (!selected.length) {
    chart.append(svgNode('text', {x:width / 2, y:205, 'text-anchor':'middle', fill:'#70796e', 'font-size':13}, '所选区间暂无交易日数据'));
    showCandle(null); return;
  }
  const values = selected.flatMap(row => [row.low, row.high, row.bb_lower, row.bb_upper]).filter(finite);
  let lo = Math.min(...values), hi = Math.max(...values);
  const pad = (hi - lo || Math.max(Math.abs(hi) * .02, 1)) * .09; lo -= pad; hi += pad;
  const py = value => priceBottom - (value - lo) / (hi - lo) * (priceBottom - top);
  const ry = value => rsiBottom - Math.max(0, Math.min(100, value)) / 100 * (rsiBottom - rsiTop);
  const cx = i => x0 + i * step + step / 2;
  const grid = svgNode('g', {'aria-hidden':'true'}), bands = svgNode('g', {'aria-hidden':'true'});
  const candles = svgNode('g', {'aria-hidden':'true'}), hits = svgNode('g');
  const crosshair = svgNode('line', {y1:top, y2:rsiBottom, stroke:'#839277', 'stroke-dasharray':'3 4', 'pointer-events':'none', 'aria-hidden':'true'});
  chart.append(grid, bands, candles, crosshair, hits);
  grid.append(svgNode('rect', {x:x0, y:ry(30), width:width-x0-right, height:rsiBottom-ry(30), fill:'#faf6eb'}));
  for (let i = 0; i <= 4; i++) {
    const y = top + (priceBottom - top) * i / 4;
    grid.append(svgNode('line', {x1:x0, y1:y, x2:width-right, y2:y, stroke:'#edf0e8', 'stroke-dasharray':'3 4'}));
    grid.append(svgNode('text', {x:x0-10, y:y+4, 'text-anchor':'end', fill:'#87907f', 'font-size':10}, number(hi - (hi-lo)*i/4, 0)));
  }
  for (const level of [0, 30, 70, 100]) {
    const y = ry(level);
    grid.append(svgNode('line', {x1:x0, y1:y, x2:width-right, y2:y, stroke:level===30?'#c9ad71':'#edf0e8', 'stroke-dasharray':level===30?'4 5':'2 4'}));
    grid.append(svgNode('text', {x:x0-10, y:y+3, 'text-anchor':'end', fill:level===30?'#a17d36':'#87907f', 'font-size':9}, String(level)));
  }
  grid.append(svgNode('text', {x:4, y:11, fill:'#70796e', 'font-size':10}, '指数点'));
  grid.append(svgNode('text', {x:4, y:rsiTop-12, fill:'#70796e', 'font-size':10}, 'RSI(14)'));
  grid.append(svgNode('text', {x:width-right, y:rsiTop-12, 'text-anchor':'end', fill:'#9b814d', 'font-size':9}, '虚线 / 超卖阈值 30'));
  let bandRun = [];
  function fillBand() {
    if (bandRun.length > 1) {
      const upper = bandRun.map(([row, i]) => `${cx(i)},${py(row.bb_upper)}`);
      const lower = bandRun.slice().reverse().map(([row, i]) => `${cx(i)},${py(row.bb_lower)}`);
      bands.append(svgNode('polygon', {points:upper.concat(lower).join(' '), fill:'#eef2f3', opacity:.65}));
    }
    bandRun = [];
  }
  selected.forEach((row, i) => { if (finite(row.bb_upper) && finite(row.bb_lower)) bandRun.push([row, i]); else fillBand(); });
  fillBand();
  function drawLine(key, scale, color, dash, lineWidth = 1.3) {
    let points = [];
    function flush() {
      if (points.length > 1) bands.append(svgNode('polyline', {points:points.join(' '), fill:'none', stroke:color, 'stroke-width':lineWidth, 'stroke-dasharray':dash || 'none', 'stroke-linejoin':'round'}));
      points = [];
    }
    selected.forEach((row, index) => { if (finite(row[key])) points.push(`${cx(index)},${scale(row[key])}`); else flush(); }); flush();
    // Preserve isolated values without bridging missing or warming-up indicators.
    selected.forEach((row, index) => {
      if (finite(row[key]) && !finite(selected[index-1]?.[key]) && !finite(selected[index+1]?.[key])) bands.append(svgNode('circle', {cx:cx(index), cy:scale(row[key]), r:2.5, fill:color}));
    });
  }
  drawLine('bb_upper', py, '#b8c4ca', '4 4');
  drawLine('bb_middle', py, '#a4b1b8', '3 4');
  drawLine('bb_lower', py, '#8197a3', '', 1.6);
  drawLine('rsi', ry, '#75844e', '', 1.8);
  const targets = [];
  let activeIndex = -1;
  function selectCandle(index) {
    if (activeIndex >= 0) targets[activeIndex].setAttribute('tabindex', '-1');
    activeIndex = index; targets[index].setAttribute('tabindex', '0');
    crosshair.setAttribute('x1', cx(index)); crosshair.setAttribute('x2', cx(index));
    showCandle(selected[index]);
  }
  selected.forEach((row, index) => {
    const x = cx(index), color = row.close >= row.open ? '#bc554d' : '#347e68';
    if ([row.open, row.high, row.low, row.close].every(finite)) {
      candles.append(svgNode('line', {x1:x, y1:py(row.high), x2:x, y2:py(row.low), stroke:color, 'stroke-width':1.2}));
      const bodyWidth = Math.min(10, Math.max(3, step * .55));
      candles.append(svgNode('rect', {x:x-bodyWidth/2, y:Math.min(py(row.open), py(row.close)), width:bodyWidth, height:Math.max(1.4, Math.abs(py(row.open)-py(row.close))), fill:color, rx:.7}));
      if (row.oversold) candles.append(svgNode('circle', {class:'signal-dot', cx:x, cy:Math.min(priceBottom-4, py(row.low)+10), r:3.6, fill:'#b28b40', stroke:'#fff', 'stroke-width':1.3}));
    }
    const hit = svgNode('rect', {x:x-step/2, y:top, width:step, height:rsiBottom-top, fill:'transparent', class:'candle-hit', tabindex:'-1', role:'button', 'aria-label':`${row.date}，收盘 ${number(row.close)}，RSI ${number(row.rsi)}，${signalLabel(row)}`});
    targets.push(hit);
    hit.addEventListener('pointerenter', () => selectCandle(index));
    hit.addEventListener('focus', () => selectCandle(index));
    hit.addEventListener('click', () => selectCandle(index));
    hit.addEventListener('keydown', event => {
      let next = index;
      if (event.key === 'ArrowLeft') next = Math.max(0, index - 1);
      else if (event.key === 'ArrowRight') next = Math.min(selected.length - 1, index + 1);
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = selected.length - 1;
      else if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault(); selectCandle(next); targets[next].focus({preventScroll:true});
      if (cx(next) < scroll.scrollLeft + x0 || cx(next) > scroll.scrollLeft + scroll.clientWidth - right) scroll.scrollLeft = cx(next) - scroll.clientWidth / 2;
    });
    hits.append(hit);
  });
  const stride = Math.max(1, Math.ceil(selected.length / Math.max(4, width / 110)));
  for (let index = 0; index < selected.length; index += stride) grid.append(svgNode('text', {x:cx(index), y:axisBottom-13, 'text-anchor':'middle', fill:'#87907f', 'font-size':10}, selected[index].date.slice(2)));
  selectCandle(selected.length - 1);
  scroll.scrollLeft = scroll.scrollWidth;
}
$('ranges').addEventListener('click', event => {
  const button = event.target.closest('button[data-months]'); if (!button) return;
  for (const item of $('ranges').querySelectorAll('button')) item.setAttribute('aria-pressed', String(item === button));
  chartMonths = Number(button.dataset.months); renderChart();
});
let chartWidth = $('chart-scroll').clientWidth;
renderChart();
new ResizeObserver(() => {
  const width = $('chart-scroll').clientWidth;
  if (width !== chartWidth) { chartWidth = width; renderChart(); }
}).observe($('chart-scroll'));
</script>
</body>
</html>
'''
