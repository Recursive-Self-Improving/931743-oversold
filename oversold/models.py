"""Shared, dependency-free contracts for daily index analysis."""

from dataclasses import dataclass
from datetime import date

INDEX_CODE = "931743"
INDEX_NAME = "中证半导体材料设备主题指数"
TIMEZONE = "Asia/Shanghai"
RULE_DESCRIPTION = "RSI(14) < 30 且收盘价 ≤ 布林带下轨(20, 2)"


@dataclass(frozen=True, slots=True)
class Candle:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float


@dataclass(frozen=True, slots=True)
class Signal:
    candle: Candle
    rsi: float | None
    bb_middle: float | None
    bb_upper: float | None
    bb_lower: float | None
    oversold: bool
    entry: bool

    def as_dict(self) -> dict:
        return {
            "date": self.candle.date.isoformat(),
            "open": self.candle.open,
            "high": self.candle.high,
            "low": self.candle.low,
            "close": self.candle.close,
            "volume": self.candle.volume,
            "amount": self.candle.amount,
            "rsi": self.rsi,
            "bb_middle": self.bb_middle,
            "bb_upper": self.bb_upper,
            "bb_lower": self.bb_lower,
            "oversold": self.oversold,
            "entry": self.entry,
        }
