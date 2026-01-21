import os
from datetime import datetime
from typing import List

import requests

from analysis.logger import TradeLogger, TradeLogEntry


class MonthlyReportGenerator:
    def __init__(self, trade_logger: TradeLogger) -> None:
        self.trade_logger = trade_logger
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_endpoint = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")

    def generate_monthly_report(self) -> str:
        logs = self.trade_logger.fetch_logs()
        prompt = self._build_prompt(logs)
        report_content = self._request_report(prompt)
        filename = f"analysis/reports/monthly-report-{datetime.utcnow().date()}.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as report_file:
            report_file.write(report_content)
        return filename

    def _build_prompt(self, logs: List[TradeLogEntry]) -> str:
        log_lines = "\n".join(
            f"{log.timestamp} | {log.symbol} | {log.side} | {log.quantity} @ {log.price} | {log.reasoning}"
            for log in logs
        )
        return (
            "너는 ISA/연금 ETF 포트폴리오를 운용하는 로보어드바이저다. "
            "아래 거래 로그를 바탕으로 월간 운용 보고서를 한국어로 작성하라. "
            "성과 요약, 리스크 관리, 다음 달 전략을 포함해라.\n\n"
            f"거래 로그:\n{log_lines}\n"
        )

    def _request_report(self, prompt: str) -> str:
        if not self.llm_api_key:
            return "LLM_API_KEY가 설정되지 않아 보고서를 생성하지 못했습니다."

        headers = {"Authorization": f"Bearer {self.llm_api_key}"}
        payload = {
            "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": "너는 전문 투자 리서치 애널리스트다."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }

        response = requests.post(self.llm_endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
