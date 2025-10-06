import React, { useState } from 'react';

/**
 * DFIAccordion
 * Shows DFI cautions grouped by drug and food in an accordion.
 * Props: { dfi_cautions: [{ drug, food, advice }] }
 */
export default function DFIAccordion({ dfi_cautions = [] }) {
  const [openDrug, setOpenDrug] = useState(null);
  if (!dfi_cautions.length) return null;
  // Group by drug
  const grouped = dfi_cautions.reduce((acc, item) => {
    acc[item.drug] = acc[item.drug] || [];
    acc[item.drug].push(item);
    return acc;
  }, {});
  return (
    <div className="my-8">
      <h2 className="text-xl font-semibold mb-2">Drug–Food Interactions (DFI) Cautions</h2>
      <div className="border rounded divide-y">
        {Object.entries(grouped).map(([drug, items]) => (
          <div key={drug}>
            <button
              className="w-full text-left px-4 py-3 font-bold bg-gray-50 hover:bg-gray-100 focus:outline-none"
              onClick={() => setOpenDrug(openDrug === drug ? null : drug)}
              aria-expanded={openDrug === drug}
            >
              {drug}
            </button>
            {openDrug === drug && (
              <div className="bg-white px-6 py-3">
                <ul className="list-disc ml-6">
                  {items.map((item, i) => (
                    <li key={i} className="mb-2">
                      <span className="font-semibold text-blue-700">{item.food}:</span> {item.advice}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
