import { useAPI } from '../providers/APIProvider';

export function usePatientAPI() {
  const api = useAPI();

  const getPatientDashboard = async (patientId) => {
    const { data } = await api.get(`/patient/${patientId}/dashboard`);
    return data;
  };

  const getPatientHistory = async (patientId) => {
    const { data } = await api.get(`/patient/${patientId}/history`);
    return data;
  };

  const updatePatientProfile = async (patientId, profileData) => {
    const { data } = await api.put(`/patient/${patientId}/profile`, profileData);
    return data;
  };

  return {
    getPatientDashboard,
    getPatientHistory,
    updatePatientProfile,
  };
}

export function usePrescriptionAPI() {
  const api = useAPI();

  const analyzePrescription = async (formData) => {
    const { data } = await api.post('/analyze/prescription', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 15000,
    });
    return data;
  };

  const getRiskAssessment = async (patientId) => {
    const { data } = await api.get(`/risk/${patientId}`);
    return data;
  };

  const getInteractions = async (drugList) => {
    const { data } = await api.post('/interactions/check', { drugs: drugList });
    return data;
  };

  const getAlternatives = async (drugName) => {
    const { data } = await api.get(`/drugs/${drugName}/alternatives`);
    return data;
  };

  return {
    analyzePrescription,
    getRiskAssessment,
    getInteractions,
    getAlternatives,
  };
}

export function useChatAPI() {
  const api = useAPI();

  const sendMessage = async (messages, context = 'medication_safety') => {
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/chat/session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('jwt')}`,
      },
      body: JSON.stringify({ messages, context }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response;
  };

  const getChatHistory = async (sessionId) => {
    const { data } = await api.get(`/chat/${sessionId}/history`);
    return data;
  };

  return {
    sendMessage,
    getChatHistory,
  };
}