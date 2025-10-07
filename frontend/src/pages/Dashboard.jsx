
import React, { useState } from 'react';
import { useAPI } from '../providers/APIProvider';
import { useAuth } from '../hooks/useAuth';
import PrescriptionForm from '../components/PrescriptionForm';
import RiskGauge from '../components/RiskGauge';
import DDITable from '../components/DDITable';
import DFIAccordion from '../components/DFIAccordion';
import HomeRemedyCard from '../components/HomeRemedyCard';
import EvidenceModal from '../components/EvidenceModal';
import HistoryTimeline from '../components/HistoryTimeline';
import AlertsBanner from '../components/AlertsBanner';
import ChatbotWidget from '../components/ChatbotWidget';


const Dashboard = () => {
  const api = useAPI();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleAnalyze(formData) {
    setLoading(true);
    setError(null);
    setResult(null);
    
    // Check if mock data is enabled
    const useMockData = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true';
    
    // extract simple drug list from the entered text (comma/semicolon/newline separated)
    const submittedText = formData.get('text') || '';
    const extractedDrugs = (submittedText || '')
      .split(/[,;\n]/)
      .map(s => s.trim())
      .filter(Boolean);

    if (useMockData) {
      // Mock data for development/demo
      setTimeout(() => {
        const mockResult = {
          risk_score: 75,
          level: 'HIGH',
          ddi_summary: [
            { drug1: 'Warfarin', drug2: 'Aspirin', interaction: 'Increased bleeding risk', severity: 'HIGH' },
            { drug1: 'Metformin', drug2: 'Ibuprofen', interaction: 'Kidney function impact', severity: 'MOD' }
          ],
          adr_flags: ['Gastrointestinal bleeding', 'Hypoglycemia risk'],
          dfi_cautions: [
            { drug: 'Warfarin', food: 'Leafy greens', advice: 'Maintain consistent vitamin K intake' },
            { drug: 'Metformin', food: 'Alcohol', advice: 'Avoid excessive alcohol consumption' }
          ],
          home_remedies: [
            { drug: 'Metformin', remedy: 'Take with meals to reduce stomach upset', caution: 'Monitor blood sugar levels regularly' },
            { drug: 'Warfarin', remedy: 'Maintain consistent diet', caution: 'Watch for unusual bleeding or bruising' }
          ],
          evidence_paths: [
            'Drug interaction database → Warfarin + Aspirin → Bleeding risk studies',
            'Clinical trials → Metformin + NSAIDs → Renal function data'
          ],
          contributors: [
            'Patient age: 65+ (higher risk)',
            'Multiple medications (polypharmacy)',
            'History of GI issues'
          ],
          history: [
            { date: '2024-01-15', summary: 'Initial prescription analysis', risk_score: 45, level: 'MOD' },
            { date: '2024-02-20', summary: 'Added blood pressure medication', risk_score: 60, level: 'HIGH' },
            { date: '2024-03-10', summary: 'Adjusted dosages', risk_score: 75, level: 'HIGH' }
          ]
        };
        // attach extracted submitted drugs so UI can show drug-specific remedies
        setResult({ ...mockResult, _submittedDrugs: extractedDrugs });
        setLoading(false);
      }, 1500);
    } else {
      // Real API integration
      try {
        console.log('=== PRESCRIPTION ANALYSIS DEBUG ===');
        console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL);
        console.log('Full URL will be:', `${import.meta.env.VITE_API_BASE_URL}/analyze/prescription`);
        console.log('FormData contents:');
        for (let [key, value] of formData.entries()) {
          console.log(`  ${key}:`, value);
        }
        
        const { data } = await api.post('/analyze/prescription', formData, {
          // Don't set Content-Type for FormData - let axios handle it
          timeout: 15000, // Increased timeout for AI processing
        });
        
        console.log('✅ API Success! Response:', data);
        // attach submitted drugs so components can render drug-specific content
        setResult({ ...data, _submittedDrugs: extractedDrugs });
      } catch (err) {
        console.error('❌ API Error Full Details:', err);
        console.error('Error name:', err.name);
        console.error('Error message:', err.message);
        console.error('Error code:', err.code);
        console.error('Error config:', err.config);
        console.error('Error request:', err.request);
        console.error('Error response:', err.response);
        
        if (err.response) {
          console.error('Response status:', err.response.status);
          console.error('Response headers:', err.response.headers);
          console.error('Response data:', err.response.data);
        }
        
        if (err.response?.status === 401) {
          setError('Authentication required. Please log in.');
        } else if (err.response?.status === 429) {
          setError('Too many requests. Please try again later.');
        } else if (err.code === 'ECONNABORTED') {
          setError('Request timeout. The analysis is taking longer than expected.');
        } else {
          setError(err?.response?.data?.message || 'Failed to analyze prescription. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    }
  }

  return (
    <>
      <AlertsBanner />
      <div className="max-w-2xl mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Analyze Prescription</h1>
      <PrescriptionForm onSubmit={handleAnalyze} loading={loading} />
      {error && <div className="text-red-600 mt-4">{error}</div>}
      {result && (
        <>
          <RiskGauge risk_score={result.risk_score} level={result.level} />
          <DDITable ddi_summary={result.ddi_summary} adr_flags={result.adr_flags} />
          <DFIAccordion dfi_cautions={result.dfi_cautions} />
          {console.log('Home remedies check:', {
            isArray: Array.isArray(result.home_remedies),
            length: result.home_remedies?.length,
            data: result.home_remedies
          })}
          {Array.isArray(result.home_remedies) && result.home_remedies.length > 0 && (
            <div className="my-8 p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-green-800">Home Remedies & Self-Care</h2>
              </div>
              <p className="text-green-700 text-sm mb-6 italic">
                Natural approaches and lifestyle recommendations to complement your medication regimen
              </p>
              {result.home_remedies.map((rem, i) => {
                console.log('Home remedy item:', rem);
                return (
                  <HomeRemedyCard
                    key={i}
                    {...rem}
                    submittedDrugs={result._submittedDrugs || []}
                  />
                );
              })}
            </div>
          )}
          <EvidenceModal evidence_paths={result.evidence_paths} contributors={result.contributors} />
          {Array.isArray(result.history) && result.history.length > 0 && (
            <HistoryTimeline history={result.history} />
          )}
          <pre className="mt-6 bg-gray-100 p-4 rounded text-xs overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
        </>
      )}
      </div>
      <ChatbotWidget />
    </>
  );
};

export default Dashboard;
