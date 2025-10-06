import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                suRxit
              </Link>
              <span className="ml-2 text-sm text-gray-500">AI-Powered Medication Safety</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                to="/dashboard" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md font-medium"
              >
                Doctor Dashboard
              </Link>
              <Link 
                to="/patient" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md font-medium"
              >
                Patient Portal
              </Link>
            </div>
          </div>
        </div>
      </nav>
    </div>
  );
}