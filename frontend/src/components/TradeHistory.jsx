export default function TradeHistory({ logs }) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">매매 기록</h2>
        <p className="text-sm text-slate-400">매수/매도 판단 근거와 지표를 타임라인으로 확인합니다.</p>
      </div>

      <div className="space-y-4">
        {logs.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 p-6 text-center text-slate-400">
            아직 기록된 거래가 없습니다.
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 shadow"
            >
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="text-sm text-slate-400">{new Date(log.timestamp).toLocaleString()}</p>
                  <h3 className="text-lg font-semibold">
                    {log.symbol} · {log.side} {log.quantity}주
                  </h3>
                </div>
                <div className="text-sm text-slate-300">실행가: {log.price.toLocaleString()}원</div>
              </div>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div className="rounded-lg bg-slate-900 p-3 text-sm">
                  <p className="text-slate-400">지표</p>
                  <ul className="mt-1 space-y-1 text-slate-200">
                    <li>단기 이동평균: {log.indicators.short_ma.toFixed(2)}</li>
                    <li>장기 이동평균: {log.indicators.long_ma.toFixed(2)}</li>
                    <li>RSI: {log.indicators.rsi.toFixed(2)}</li>
                  </ul>
                </div>
                <div className="rounded-lg bg-slate-900 p-3 text-sm">
                  <p className="text-slate-400">판단 근거</p>
                  <p className="mt-1 text-slate-200">{log.reasoning}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
