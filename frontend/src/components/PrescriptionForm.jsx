import React, { useRef, useState } from 'react';

/**
 * Unified Intake Form for prescription analysis
 * - Text input
 * - File upload (PDF/JPG/PNG)
 * - Optional allergy/condition checkboxes
 */
export default function PrescriptionForm({ onSubmit, loading }) {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [allergies, setAllergies] = useState([]);
  const fileInputRef = useRef();

  const allergyOptions = [
    'Penicillin',
    'Sulfa',
    'Aspirin',
    'NSAIDs',
    'Latex',
    'Other',
  ];

  function handleFileChange(e) {
    setFile(e.target.files[0] || null);
  }

  function handleAllergyChange(e) {
    const { value, checked } = e.target;
    setAllergies((prev) =>
      checked ? [...prev, value] : prev.filter((a) => a !== value)
    );
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!text && !file) return;
    const formData = new FormData();
    formData.append('text', text);
    if (file) formData.append('file', file);
    formData.append('allergies', JSON.stringify(allergies));
    onSubmit?.(formData);
  }

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <label className="block font-medium mb-1">Prescription / Symptoms</label>
        <textarea
          className="w-full border rounded p-2 min-h-[80px]"
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Paste prescription text or describe symptoms..."
        />
      </div>
      <div>
        <label className="block font-medium mb-1">Upload File (PDF, JPG, PNG)</label>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileChange}
          className="block w-full border rounded p-2"
        />
        {file && <div className="text-xs mt-1">Selected: {file.name}</div>}
      </div>
      <div>
        <label className="block font-medium mb-1">Known Allergies / Conditions</label>
        <div className="flex flex-wrap gap-3">
          {allergyOptions.map(opt => (
            <label key={opt} className="flex items-center gap-1">
              <input
                type="checkbox"
                value={opt}
                checked={allergies.includes(opt)}
                onChange={handleAllergyChange}
              />
              {opt}
            </label>
          ))}
        </div>
      </div>
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Analyze Prescription'}
      </button>
    </form>
  );
}
