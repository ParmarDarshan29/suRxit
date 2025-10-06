
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
        setResult(mockResult);
        setLoading(false);
      }, 1500);
    } else {
      // Real API integration
      try {
        const { data } = await api.post('/analyze/prescription', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 15000, // Increased timeout for AI processing
        });
        setResult(data);
      } catch (err) {
        console.error('API Error:', err);
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
          {Array.isArray(result.home_remedies) && result.home_remedies.length > 0 && (
            <div className="my-8">
              <h2 className="text-xl font-semibold mb-2">Home Remedies & Self-Care</h2>
              {result.home_remedies.map((rem, i) => (
                <HomeRemedyCard key={i} {...rem} />
              ))}
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
