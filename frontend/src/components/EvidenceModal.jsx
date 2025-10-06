import React, { useState } from 'react';

/**
 * EvidenceModal
 * Shows knowledge graph paths and SHAP factors for a given assessment.
 * Props: { evidence_paths: array, contributors: array }
 */
export default function EvidenceModal({ evidence_paths = [], contributors = [] }) {
  const [open, setOpen] = useState(false);
  if (!evidence_paths.length && !contributors.length) return null;
  return (
    <>
      <button
        className="mt-4 px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800"
        onClick={() => setOpen(true)}
      >
        Show Evidence
      </button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-lg w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
              onClick={() => setOpen(false)}
              aria-label="Close"
            >
              ×
            </button>
            <h3 className="text-xl font-bold mb-4">Evidence & Explanation</h3>
            {evidence_paths.length > 0 && (
              <div className="mb-4">
                <div className="font-semibold mb-1">Knowledge Graph Paths:</div>
                <ul className="list-disc ml-6 text-sm">
                  {evidence_paths.map((path, i) => (
                    <li key={i}>{path}</li>
                  ))}
                </ul>
              </div>
            )}
            {contributors.length > 0 && (
              <div>
                <div className="font-semibold mb-1">SHAP Contributors:</div>
                <ul className="list-disc ml-6 text-sm">
                  {contributors.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
