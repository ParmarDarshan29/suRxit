import React from 'react';

/**
 * RiskGauge
 * Visualizes risk_score and level (LOW, MOD, HIGH, CRITICAL) as a gauge.
 * Props: { risk_score: number, level: string }
 */
const LEVEL_COLORS = {
  LOW: 'bg-green-500',
  MOD: 'bg-yellow-400',
  HIGH: 'bg-orange-500',
  CRITICAL: 'bg-red-600',
};

function getLabel(level) {
  switch (level) {
    case 'LOW': return 'Low';
    case 'MOD': return 'Moderate';
    case 'HIGH': return 'High';
    case 'CRITICAL': return 'Critical';
    default: return level;
  }
}

export default function RiskGauge({ risk_score = 0, level = 'LOW' }) {
  // Clamp risk_score between 0 and 100
  const score = Math.max(0, Math.min(100, risk_score));
  const color = LEVEL_COLORS[level] || 'bg-gray-400';
  return (
    <div className="flex flex-col items-center my-6">
      <div className="relative w-40 h-20">
        <svg viewBox="0 0 200 100" className="w-full h-full">
          <path
            d="M10,100 A90,90 0 0,1 190,100"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
          />
          <path
            d="M10,100 A90,90 0 0,1 190,100"
            fill="none"
            stroke="currentColor"
            strokeWidth="20"
            strokeDasharray={Math.PI * 90}
            strokeDashoffset={Math.PI * 90 * (1 - score / 100)}
            className={color}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold">{score}</span>
          <span className={`mt-1 text-lg font-semibold ${color} text-white px-2 rounded`}>{getLabel(level)}</span>
        </div>
      </div>
    </div>
  );
}
