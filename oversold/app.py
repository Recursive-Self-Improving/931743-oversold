"""Close-of-day policy and reproducible two-calendar-year report snapshots."""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

from .data import DataError, SOURCE_NAME, SOURCE_URL
from .indicators import analyze, two_year_start
from .models import Candle, INDEX_CODE, INDEX_NAME, RULE_DESCRIPTION, TIMEZONE
from .report import render_html

SHANGHAI = ZoneInfo(TIMEZONE)
# Do not evaluate the live intraday bar; allow 30 minutes after the 15:00 close.
FINAL_BAR_TIME = time(15, 30)
CSV_FIELDS = ["date", "open", "high", "low", "close", "volume", "amount", "rsi", "bb_middle", "bb_upper", "bb_lower", "oversold", "entry"]


def closed_through(now: datetime) -> date:
    local = now.astimezone(SHANGHAI)
    return local.date() if local.time() >= FINAL_BAR_TIME else local.date() - timedelta(days=1)


def build_report(candles: list[Candle], as_of: date, now: datetime, *, offline: bool = False) -> dict:
    local = now.astimezone(SHANGHAI)
    if as_of > local.date():
        raise DataError("不能对未来日期作收盘判断。")
    end = min(as_of, closed_through(local))
    finalized = [candle for candle in candles if candle.date <= end]
    if len(finalized) < 20:
        raise DataError("已收盘日线不足 20 根，无法完成 RSI 与布林带预热。")
    analyzed = analyze(finalized)
    window_start = two_year_start(as_of)
    rows = [signal.as_dict() for signal in analyzed if window_start <= signal.candle.date <= as_of]
    if not rows:
        raise DataError("查询窗口内没有已收盘日线。")
    latest = rows[-1]
    warnings = []
    if sum(candle.date < window_start for candle in finalized) < 20:
        warnings.append(f"完整 OHLC 从 {finalized[0].date} 开始；此窗口的历史覆盖或预热不足，不能视作完整两年信号清单。")
    if offline:
        status = "offline"
        message = f"离线缓存回溯，最新已记录日期 {latest['date']}；未联网确认，不作为今日收盘判断。"
    elif as_of < local.date():
        status = "historical"
        message = f"历史回溯截至 {as_of}，最近可用日线 {latest['date']}；未使用截止日之后的日线。"
    elif local.time() < FINAL_BAR_TIME:
        status = "awaiting_close"
        message = f"北京时间尚未到 15:30，已排除今日未确认日线；仅展示 {latest['date']} 的状态。"
    elif latest["date"] != as_of.isoformat():
        status = "no_current_bar"
        message = f"未获取 {as_of} 的收盘日线（可能休市或源数据未发布）；最新为 {latest['date']}，不能判断今天是否超卖。"
    else:
        status = "current"
        message = f"已获取 {as_of} 收盘日线，按北京时间 15:30 后口径计算。"
    return {
        "index": {"code": INDEX_CODE, "name": INDEX_NAME, "source": SOURCE_NAME, "source_url": SOURCE_URL},
        "rule": {"description": RULE_DESCRIPTION, "rsi_period": 14, "rsi_threshold": 30, "bb_period": 20, "bb_std": 2, "rsi_method": "Wilder", "std_ddof": 0},
        "generated_at": local.isoformat(timespec="seconds"),
        "as_of": as_of.isoformat(), "window_start": window_start.isoformat(),
        "data_start": finalized[0].date.isoformat(), "data_end": latest["date"],
        "mode": "offline" if offline else "live", "status": status, "status_message": message,
        "warnings": warnings, "latest": latest, "rows": rows,
        "signals": [row for row in rows if row["oversold"]],
        "entries": [row for row in rows if row["entry"]],
        "units": {"prices": "指数点", "volume": "股", "amount": "元；源数据精确到 0.01 亿元"},
    }


def export_report(report: dict, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    # Render everything first; publish HTML last, never leave a half-written file.
    with TemporaryDirectory(prefix=".oversold-", dir=destination) as temporary:
        staging = Path(temporary)
        for filename, key in (("daily.csv", "rows"), ("signals.csv", "signals"), ("entries.csv", "entries")):
            with (staging / filename).open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(report[key])
        (staging / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        render_html(report, staging / "index.html")
        for filename in ("daily.csv", "signals.csv", "entries.csv", "summary.json", "index.html"):
            (staging / filename).replace(destination / filename)


def print_report(report: dict, destination: Path) -> None:
    print(f"{INDEX_NAME}（{INDEX_CODE}）")
    print(f"规则：{RULE_DESCRIPTION}")
    print(report["status_message"])
    for warning in report["warnings"]:
        print(f"警告：{warning}")
    row = report["latest"]
    state = ("超卖 / 新触发" if row["entry"] else "超卖 / 持续") if row["oversold"] else "未超卖"
    print(f"{row['date']}  收盘 {row['close']:.2f}  RSI {row['rsi']:.4f}  下轨 {row['bb_lower']:.4f}  {state}")
    print(f"\n回溯窗口：{report['window_start']} — {report['as_of']}（两端含）")
    print(f"超卖交易日 {len(report['signals'])} 个；新触发日 {len(report['entries'])} 个")
    print("日期          收盘点位      RSI(14)      布林下轨  状态")
    for signal in report["signals"]:
        print(f"{signal['date']}  {signal['close']:10.2f}  {signal['rsi']:10.4f}  {signal['bb_lower']:12.4f}  {'新触发' if signal['entry'] else '持续'}")
    if not report["signals"]:
        print("此规则下，观察窗口内没有超卖日。")
    print(f"\nHTML 报告：{destination.resolve() / 'index.html'}")
    print("CSV：daily.csv / signals.csv / entries.csv；机器可读结果：summary.json")
    print("超卖不代表低估或买点。本项目不自动交易。")
