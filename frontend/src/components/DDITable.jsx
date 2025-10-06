import React from 'react';

/**
 * DDITable
 * Visualizes DDI summary and ADR flags in a color-coded table.
 * Props: { ddi_summary: array, adr_flags: array }
 */
export default function DDITable({ ddi_summary = [], adr_flags = [] }) {
  if (!ddi_summary.length && !adr_flags.length) return null;
  return (
    <div className="my-8">
      <h2 className="text-xl font-semibold mb-2">Drug–Drug Interactions (DDI) & Adverse Drug Reactions (ADR)</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full border text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-3 py-2 border">Drug 1</th>
              <th className="px-3 py-2 border">Drug 2</th>
              <th className="px-3 py-2 border">Interaction</th>
              <th className="px-3 py-2 border">Severity</th>
            </tr>
          </thead>
          <tbody>
            {ddi_summary.map((ddi, i) => (
              <tr key={i} className={
                ddi.severity === 'CRITICAL' ? 'bg-red-100' :
                ddi.severity === 'HIGH' ? 'bg-orange-100' :
                ddi.severity === 'MOD' ? 'bg-yellow-100' :
                'bg-green-50'}>
                <td className="px-3 py-2 border">{ddi.drug1}</td>
                <td className="px-3 py-2 border">{ddi.drug2}</td>
                <td className="px-3 py-2 border">{ddi.interaction}</td>
                <td className="px-3 py-2 border font-bold">{ddi.severity}</td>
              </tr>
            ))}
            {adr_flags.length > 0 && (
              <tr className="bg-pink-100">
                <td colSpan={4} className="px-3 py-2 border text-red-700 font-semibold">
                  ADR Flags: {adr_flags.join(', ')}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
