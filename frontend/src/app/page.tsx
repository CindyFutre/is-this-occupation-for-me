'use client';

import { useEffect, useState } from 'react';

interface HealthResponse {
  status: string;
}

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<string>('Loading...');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchHealthStatus = async () => {
      try {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8001';
        const response = await fetch(`${apiBaseUrl}/api/v1/health`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data: HealthResponse = await response.json();
        setHealthStatus(data.status);
      } catch (err) {
        console.error('Failed to fetch health status:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setHealthStatus('Error');
      }
    };

    fetchHealthStatus();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-8">Next.js Frontend</h1>
        <div className="text-xl">
          {error ? (
            <div className="text-red-500">
              <p>Error connecting to backend:</p>
              <p className="text-sm mt-2">{error}</p>
            </div>
          ) : (
            <p>Status: <span className="font-semibold text-green-400">{healthStatus}</span></p>
          )}
        </div>
      </div>
    </div>
  );
}