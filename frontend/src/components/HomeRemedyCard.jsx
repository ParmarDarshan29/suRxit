import React from 'react';

/**
 * HomeRemedyCard
 * Shows a home remedy, description, and cautionary note for a drug.
 * Props: { drug, remedy, caution }
 */
export default function HomeRemedyCard({ drug, remedy, caution }) {
  return (
    <div className="border rounded shadow-sm p-4 bg-green-50 mb-4">
      <div className="font-bold text-lg text-green-800 mb-1">{drug}</div>
      <div className="text-gray-800 mb-2">{remedy}</div>
      {caution && (
        <div className="text-yellow-700 text-sm mt-2 flex items-center gap-1">
          <span className="font-semibold">Caution:</span> {caution}
        </div>
      )}
    </div>
  );
}
