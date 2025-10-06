import React, { createContext, useContext, useMemo } from 'react';
import axios from 'axios';

const APIContext = createContext();

export function useAPI() {
  return useContext(APIContext);
}

export function APIProvider({ children }) {
  const api = useMemo(() => {
    const instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 5000,
    });
    instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('jwt');
        if (token) config.headers.Authorization = `Bearer ${token}`;
        return config;
      },
      (error) => Promise.reject(error)
    );
    instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
    return instance;
  }, []);

  return (
    <APIContext.Provider value={api}>
      {children}
    </APIContext.Provider>
  );
}
