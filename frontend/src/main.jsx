
import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './providers/AuthProvider';
import { APIProvider } from './providers/APIProvider';
import Navigation from './components/Navigation';
import './index.css';
import Dashboard from './pages/Dashboard';
import Patient from './pages/Patient';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient();

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <APIProvider>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <div className="min-h-screen bg-gray-50">
              {/* Navigation Header */}
              <nav className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                  <div className="flex justify-between h-16">
                    <div className="flex items-center">
                      <a href="/" className="text-2xl font-bold text-blue-600">
                        suRxit
                      </a>
                      <span className="ml-2 text-sm text-gray-500">AI-Powered Medication Safety</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <a 
                        href="/dashboard" 
                        className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md font-medium"
                      >
                        Doctor Dashboard
                      </a>
                      <a 
                        href="/patient" 
                        className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md font-medium"
                      >
                        Patient Portal
                      </a>
                    </div>
                  </div>
                </div>
              </nav>
              
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard/*" element={<Dashboard />} />
                <Route path="/patient/*" element={<Patient />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </BrowserRouter>
        </QueryClientProvider>
      </APIProvider>
    </AuthProvider>
  </React.StrictMode>
);
