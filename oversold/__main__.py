"""Run with python3 -m oversold; no third-party packages or API keys needed."""

import argparse
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

from .app import SHANGHAI, build_report, closed_through, export_report, print_report
from .data import history


def main() -> int:
    parser = argparse.ArgumentParser(description="931743 收盘后超卖检查与近两年信号回溯")
    parser.add_argument("--as-of", type=date.fromisoformat, metavar="YYYY-MM-DD", help="历史回溯截止日；默认北京时间今天")
    parser.add_argument("--offline", action="store_true", help="显式离线分析缓存，不声称今日数据已更新")
    parser.add_argument("--db", type=Path, default=Path("data/931743.sqlite3"), help="SQLite 日线缓存路径")
    parser.add_argument("--output", type=Path, help="报告目录；默认 reports，历史回溯与离线报告自动放子目录")
    args = parser.parse_args()
    now = datetime.now(SHANGHAI)
    as_of = args.as_of or now.date()
    if as_of > now.date():
        parser.error("--as-of 不能晚于北京时间今天")
    destination = args.output or (Path("reports/offline") if args.offline else Path("reports") / str(as_of) if args.as_of else Path("reports"))
    try:
        candles = history(args.db, min(as_of, closed_through(now)), now, offline=args.offline)
        report = build_report(candles, as_of, now, offline=args.offline)
        export_report(report, destination)
        print_report(report, destination)
    except (ValueError, OSError, sqlite3.Error) as error:
        print(f"检查失败：{error}\n未生成新的收盘判断；原有报告不代表本次更新成功。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
