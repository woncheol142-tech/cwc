import { useState } from 'react';

export default function AutoTradingToggle({ onToggle }) {
  const [enabled, setEnabled] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    const nextValue = !enabled;
    setLoading(true);
    try {
      await onToggle(nextValue);
      setEnabled(nextValue);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex items-center gap-3 rounded-full px-6 py-2 text-sm font-semibold transition ${
        enabled ? 'bg-emerald-500 text-slate-900' : 'bg-slate-700 text-slate-100'
      } ${loading ? 'opacity-60' : 'hover:opacity-90'}`}
      disabled={loading}
    >
      <span className={`h-3 w-3 rounded-full ${enabled ? 'bg-emerald-900' : 'bg-slate-200'}`} />
      {loading ? '처리 중...' : enabled ? '자동매매 중지' : '자동매매 시작'}
    </button>
  );
}
