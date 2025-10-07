import React from 'react';

/**
 * RiskGauge
 * Visualizes risk_score and level (LOW, MOD, HIGH, CRITICAL) as a gauge.
 * Props: { risk_score: number, level: string }
 */
const LEVEL_CONFIG = {
  LOW: {
    color: '#10b981', // emerald-500
    bgColor: 'bg-emerald-500',
    textColor: 'text-emerald-700',
    label: 'Low Risk'
  },
  MOD: {
    color: '#f59e0b', // amber-500
    bgColor: 'bg-amber-500',
    textColor: 'text-amber-700',
    label: 'Moderate Risk'
  },
  HIGH: {
    color: '#f97316', // orange-500
    bgColor: 'bg-orange-500',
    textColor: 'text-orange-700',
    label: 'High Risk'
  },
  CRITICAL: {
    color: '#ef4444', // red-500
    bgColor: 'bg-red-500',
    textColor: 'text-red-700',
    label: 'Critical Risk'
  }
};

export default function RiskGauge({ risk_score = 0, level = 'LOW' }) {
  // Clamp risk_score between 0 and 100
  const score = Math.max(0, Math.min(100, risk_score));
  const config = LEVEL_CONFIG[level] || LEVEL_CONFIG.LOW;
  
  // Calculate the stroke dash offset for the progress arc
  const radius = 80;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference * (1 - score / 100);

  return (
    <div className="flex flex-col items-center my-8 p-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Risk Assessment</h3>
      
      <div className="relative w-48 h-24 mb-6">
        <svg viewBox="0 0 200 120" className="w-full h-full">
          {/* Background arc */}
          <path
            d="M20,100 A80,80 0 0,1 180,100"
            fill="none"
            stroke="#f3f4f6"
            strokeWidth="12"
            strokeLinecap="round"
          />
          
          {/* Progress arc */}
          <path
            d="M20,100 A80,80 0 0,1 180,100"
            fill="none"
            stroke={config.color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
            style={{
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
            }}
          />
          
          {/* Center dot */}
          <circle
            cx="100"
            cy="100"
            r="4"
            fill={config.color}
            className="opacity-50"
          />
        </svg>
        
        {/* Score display - positioned below the gauge */}
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
          <div className="text-3xl font-bold text-gray-800 leading-none">
            {score}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            Risk Score
          </div>
        </div>
      </div>
      
      {/* Risk level badge */}
      <div className={`px-4 py-2 rounded-full ${config.bgColor} text-white font-medium text-sm shadow-md`}>
        {config.label}
      </div>
      
      {/* Risk level indicator bars */}
      <div className="flex items-center gap-1 mt-4">
        {Object.entries(LEVEL_CONFIG).map(([key, cfg]) => (
          <div
            key={key}
            className={`h-2 w-8 rounded-full transition-all duration-300 ${
              level === key 
                ? cfg.bgColor + ' scale-110' 
                : 'bg-gray-200'
            }`}
            title={cfg.label}
          />
        ))}
      </div>
    </div>
  );
}
