from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List

from analysis.kis_api import KISClient
from analysis.logger import TradeLogger, TradeLogEntry
from analysis.strategy import TradingStrategy
from analysis.reporting import MonthlyReportGenerator

app = FastAPI(title="ISA Robo Advisor Engine")

kis_client = KISClient()
trade_logger = TradeLogger()
strategy = TradingStrategy(kis_client, trade_logger)
report_generator = MonthlyReportGenerator(trade_logger)


class TradingCommand(BaseModel):
    accountType: str
    universe: List[str]


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/trading/start")
async def start_trading(command: TradingCommand, background_tasks: BackgroundTasks):
    background_tasks.add_task(strategy.run_once, command.accountType, command.universe)
    return {"status": "started", "accountType": command.accountType}


@app.post("/trading/stop")
async def stop_trading():
    strategy.stop()
    return {"status": "stopped"}


@app.get("/trading/logs", response_model=List[TradeLogEntry])
async def get_logs():
    return trade_logger.fetch_logs()


@app.post("/reports/monthly")
async def generate_monthly_report():
    report_path = report_generator.generate_monthly_report()
    return {"status": "generated", "path": report_path}
