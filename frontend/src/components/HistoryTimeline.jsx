import React from 'react';

/**
 * HistoryTimeline
 * Shows a timeline of all previous assessments for a patient.
 * Props: { history: array of { date, summary, risk_score, level } }
 */
export default function HistoryTimeline({ history = [] }) {
  if (!history.length) return null;
  return (
    <div className="my-8">
      <h2 className="text-xl font-semibold mb-2">Assessment History</h2>
      <ol className="relative border-l-2 border-blue-300 ml-4">
        {history.map((item, i) => (
          <li key={i} className="mb-6 ml-4">
            <div className="absolute w-3 h-3 bg-blue-500 rounded-full -left-1.5 border border-white"></div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">{new Date(item.date).toLocaleString()}</span>
              <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                item.level === 'CRITICAL' ? 'bg-red-600 text-white' :
                item.level === 'HIGH' ? 'bg-orange-500 text-white' :
                item.level === 'MOD' ? 'bg-yellow-400 text-black' :
                'bg-green-500 text-white'
              }`}>
                {item.level}
              </span>
              <span className="text-xs text-gray-700">Score: {item.risk_score}</span>
            </div>
            <div className="mt-1 text-sm">{item.summary}</div>
          </li>
        ))}
      </ol>
    </div>
  );
}
