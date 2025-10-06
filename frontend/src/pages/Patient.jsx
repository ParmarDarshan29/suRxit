import React, { useState, useEffect } from 'react';
import { useAPI } from '../providers/APIProvider';
import RiskGauge from '../components/RiskGauge';
import DFIAccordion from '../components/DFIAccordion';
import HomeRemedyCard from '../components/HomeRemedyCard';
import AlertsBanner from '../components/AlertsBanner';
import ChatbotWidget from '../components/ChatbotWidget';

const Patient = () => {
  const api = useAPI();
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if mock data is enabled
    const useMockData = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true';
    
    if (useMockData) {
      // Mock patient data for development/demo
      setTimeout(() => {
        const mockData = {
          patient_name: 'John Doe',
          risk_score: 65,
          level: 'MOD',
          prescription_summary: 'Metformin 500mg twice daily, Lisinopril 10mg once daily',
          dfi_cautions: [
            { drug: 'Metformin', food: 'Alcohol', advice: 'Limit alcohol intake to prevent lactic acidosis risk' },
            { drug: 'Lisinopril', food: 'High potassium foods', advice: 'Monitor potassium levels, avoid salt substitutes' }
          ],
          home_remedies: [
            { drug: 'Metformin', remedy: 'Take with meals to reduce stomach upset', caution: 'Monitor blood sugar regularly' },
            { drug: 'Lisinopril', remedy: 'Take at same time daily for best effect', caution: 'Stand up slowly to prevent dizziness' }
          ],
          alerts: [
            { type: 'warning', message: 'Remember to take evening Metformin dose' },
            { type: 'info', message: 'Blood pressure check due next week' }
          ]
        };
        setPatientData(mockData);
        setLoading(false);
      }, 1000);
    } else {
      // Real API integration
      const fetchPatientData = async () => {
        try {
          const { data } = await api.get('/patient/dashboard', {
            timeout: 10000,
          });
          setPatientData(data);
        } catch (err) {
          console.error('Patient API Error:', err);
          // Fallback to basic data structure on error
          setPatientData({
            patient_name: 'Patient',
            risk_score: 0,
            level: 'LOW',
            prescription_summary: 'No current prescriptions',
            dfi_cautions: [],
            home_remedies: [],
            alerts: [{ type: 'info', message: 'Unable to load prescription data. Please contact your healthcare provider.' }]
          });
        } finally {
          setLoading(false);
        }
      };
      
      fetchPatientData();
    }
  }, [api]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading your prescription information...</div>
      </div>
    );
  }

  return (
    <>
      <AlertsBanner />
      <div className="max-w-4xl mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold mb-2 text-center">Your Medication Dashboard</h1>
        <p className="text-gray-600 text-center mb-8">Welcome back, {patientData.patient_name}</p>
        
        {/* Current Risk Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Current Risk Assessment</h2>
          <RiskGauge risk_score={patientData.risk_score} level={patientData.level} />
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <h3 className="font-semibold mb-2">Current Prescription:</h3>
            <p className="text-gray-700">{patientData.prescription_summary}</p>
          </div>
        </div>

        {/* Alerts Section */}
        {patientData.alerts && patientData.alerts.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Important Alerts</h2>
            {patientData.alerts.map((alert, i) => (
              <div key={i} className={`p-3 rounded mb-2 ${
                alert.type === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
              }`}>
                <span className="font-semibold">{alert.type === 'warning' ? '⚠️' : 'ℹ️'}</span> {alert.message}
              </div>
            ))}
          </div>
        )}

        {/* Food Interactions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Foods to Watch</h2>
          <DFIAccordion dfi_cautions={patientData.dfi_cautions} />
        </div>

        {/* Self-Care Recommendations */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Self-Care Tips</h2>
          {patientData.home_remedies.map((remedy, i) => (
            <HomeRemedyCard key={i} {...remedy} />
          ))}
        </div>

        {/* Educational Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Why These Recommendations?</h2>
          <div className="space-y-4">
            <details className="border rounded p-4">
              <summary className="font-semibold cursor-pointer">Why monitor food interactions?</summary>
              <p className="mt-2 text-gray-700">
                Certain foods can affect how your medications work. Some may increase or decrease the medication's effectiveness, 
                while others may increase the risk of side effects.
              </p>
            </details>
            <details className="border rounded p-4">
              <summary className="font-semibold cursor-pointer">When to contact your doctor?</summary>
              <p className="mt-2 text-gray-700">
                Contact your healthcare provider if you experience unusual symptoms, side effects, or if you have questions 
                about your medications. Never stop taking prescribed medications without consulting your doctor.
              </p>
            </details>
          </div>
        </div>
      </div>
      <ChatbotWidget />
    </>
  );
};

export default Patient;
