import { useEffect, useState } from 'react';
import AutoTradingToggle from './components/AutoTradingToggle.jsx';
import TradeHistory from './components/TradeHistory.jsx';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export default function App() {
  const [tradeLogs, setTradeLogs] = useState([]);
  const [status, setStatus] = useState('대기 중');

  const fetchLogs = async () => {
    const response = await fetch(`${API_BASE_URL}/api/trading/logs`);
    if (!response.ok) {
      throw new Error('거래 로그 조회 실패');
    }
    const data = await response.json();
    setTradeLogs(data);
  };

  const handleToggle = async (isRunning) => {
    const endpoint = isRunning ? 'start' : 'stop';
    const payload = isRunning
      ? { accountType: 'ISA', universe: ['360750', '461440', '385510'] }
      : {};

    const response = await fetch(`${API_BASE_URL}/api/trading/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('자동매매 상태 변경 실패');
    }

    setStatus(isRunning ? '운용 중' : '중지');
    await fetchLogs();
  };

  useEffect(() => {
    fetchLogs().catch(() => {
      setStatus('로그 조회 실패');
    });
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 px-6 py-6">
          <h1 className="text-2xl font-semibold">ISA/연금 ETF 로보어드바이저 대시보드</h1>
          <p className="text-sm text-slate-300">
            자동매매 상태: <span className="font-semibold text-emerald-400">{status}</span>
          </p>
        </div>
      </header>

      <main className="mx-auto grid max-w-5xl gap-6 px-6 py-10">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-lg font-semibold">자동매매 제어</h2>
              <p className="text-sm text-slate-400">
                KIS 실전 계좌 기반 ETF 스윙 전략을 실행하거나 중지합니다.
              </p>
            </div>
            <AutoTradingToggle onToggle={handleToggle} />
          </div>
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow">
          <TradeHistory logs={tradeLogs} />
        </section>
      </main>
    </div>
  );
}
