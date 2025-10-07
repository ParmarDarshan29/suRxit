import React from 'react';

/**
 * HomeRemedyCard
 * Shows a home remedy, description, and cautionary note for a drug.
 * Props: { drug, remedy, caution } OR { name, indication, preparation, precautions, evidence_level }
 */
export default function HomeRemedyCard({ drug, remedy, caution, name, indication, preparation, precautions, evidence_level, submittedDrugs = [] }) {
  // normalize and log
  // submittedDrugs is an array of drug strings from the user's input
  console.log('HomeRemedyCard props:', { drug, remedy, caution, name, indication, preparation, precautions, evidence_level, submittedDrugs });

  // Handle both data structures - mock data format and API format
  const displayDrug = drug || name || 'Unknown Drug';
  const displayRemedy = remedy || preparation || 'No remedy information available';
  const displayCaution = caution || precautions || null;
  const displayEvidence = evidence_level || null;

  // Determine relevance: check if any submitted drug matches words in name/precautions/indication
  const lowerName = (displayDrug || '').toLowerCase();
  const searchableText = [
    lowerName,
    (displayCaution || '').toLowerCase(),
    (indication || '').toLowerCase(),
  ].join(' ');

  const matched = (submittedDrugs || []).filter(s => {
    if (!s) return false;
    const token = s.toLowerCase();
    return searchableText.includes(token) || lowerName.includes(token);
  });

  const isRelevant = matched.length > 0;
  
  return (
  <div className={`bg-white border rounded-xl shadow-lg p-6 mb-4 hover:shadow-xl transition-shadow duration-300 ${isRelevant ? 'border-green-500 ring-1 ring-green-100' : 'border-green-200'}`}>
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        
        <div className="flex-1">
          {/* Drug name */}
          <div className="flex items-center gap-2 mb-3">
            <h3 className={`font-bold text-lg ${isRelevant ? 'text-green-900' : 'text-green-800'}`}>{displayDrug}</h3>
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
              Home Remedy
            </span>
            {displayEvidence && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                {displayEvidence}
              </span>
            )}
            {isRelevant && (
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                Relevant to: {matched.join(', ')}
              </span>
            )}
          </div>
          
          {/* Indication (if available from API) */}
          {indication && preparation && (
            <div className="text-gray-700 text-sm leading-relaxed mb-3">
              <div className="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-300 mb-3">
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <span className="font-medium text-blue-800">Indication:</span>
                    <p className="mt-1">{indication}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Remedy description */}
          <div className="text-gray-700 text-sm leading-relaxed mb-3 bg-green-50 p-3 rounded-lg border-l-4 border-green-300">
            <div className="flex items-start gap-2">
              <svg className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <div>
                <span className="font-medium text-green-800">
                  {preparation ? 'Preparation:' : 'Recommendation:'}
                </span>
                <p className="mt-1">{displayRemedy}</p>
              </div>
            </div>
          </div>
          
          {/* Caution */}
          {displayCaution && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <span className="font-semibold text-amber-800 text-sm">Caution:</span>
                  <p className="text-amber-700 text-sm mt-1">{displayCaution}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
