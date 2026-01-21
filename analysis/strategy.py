from __future__ import annotations

from dataclasses import dataclass
from typing import List

from analysis.kis_api import KISClient
from analysis.logger import TradeLogger


@dataclass
class IndicatorSnapshot:
    symbol: str
    last_price: float
    short_ma: float
    long_ma: float
    rsi: float


class TradingStrategy:
    def __init__(self, kis_client: KISClient, trade_logger: TradeLogger) -> None:
        self.kis = kis_client
        self.trade_logger = trade_logger
        self._running = False

    def stop(self) -> None:
        self._running = False

    def run_once(self, account_type: str, universe: List[str]) -> None:
        self._running = True
        etf_universe = [symbol for symbol in universe if not symbol.endswith("L")]

        for symbol in etf_universe:
            if not self._running:
                break
            indicators = self._calculate_indicators(symbol)
            if indicators is None:
                continue
            self._evaluate_trade(account_type, indicators)

    def _calculate_indicators(self, symbol: str) -> IndicatorSnapshot | None:
        candles = self.kis.get_candles(symbol)
        if len(candles) < 50:
            return None
        closes = [float(candle.get("stck_clpr", 0)) for candle in candles]
        short_ma = sum(closes[:20]) / 20
        long_ma = sum(closes[:50]) / 50
        rsi = self._calculate_rsi(closes[:14])
        last_price = closes[0]
        return IndicatorSnapshot(
            symbol=symbol,
            last_price=last_price,
            short_ma=short_ma,
            long_ma=long_ma,
            rsi=rsi,
        )

    def _calculate_rsi(self, closes: List[float]) -> float:
        gains = []
        losses = []
        for i in range(1, len(closes)):
            delta = closes[i - 1] - closes[i]
            if delta > 0:
                gains.append(delta)
            else:
                losses.append(abs(delta))
        avg_gain = sum(gains) / len(closes) if gains else 0
        avg_loss = sum(losses) / len(closes) if losses else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _evaluate_trade(self, account_type: str, indicators: IndicatorSnapshot) -> None:
        reason = []
        action = None
        quantity = 0

        if indicators.short_ma > indicators.long_ma and indicators.rsi < 35:
            action = "BUY"
            quantity = 10
            reason.append("20일선이 50일선을 상향 돌파")
            reason.append("RSI 과매도 구간")
        elif indicators.short_ma < indicators.long_ma and indicators.rsi > 70:
            action = "SELL"
            quantity = 10
            reason.append("20일선이 50일선을 하향 돌파")
            reason.append("RSI 과매수 구간")

        if action:
            execution = self.kis.place_order(
                indicators.symbol, action, quantity, indicators.last_price
            )
            self.trade_logger.log_trade(
                symbol=indicators.symbol,
                side=action,
                quantity=quantity,
                price=indicators.last_price,
                indicators={
                    "short_ma": indicators.short_ma,
                    "long_ma": indicators.long_ma,
                    "rsi": indicators.rsi,
                },
                reasoning="; ".join(reason),
                account_type=account_type,
                execution_metadata=execution,
            )
