// Script de test pour diagnostiquer les erreurs API
import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Paper, Alert } from '@mui/material';

const ApiTestPage = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const testEndpoints = [
    { name: 'Members API', url: '/api/v1/members/members/' },
    { name: 'Inventory API', url: '/api/v1/inventory/products/' },
    { name: 'Sales API', url: '/api/v1/sales/sales/' },
  ];

  const testApi = async (endpoint) => {
    setLoading(true);
    const baseUrl = 'http://127.0.0.1:8000';
    
    try {
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      console.log(`Testing ${endpoint.name} at ${baseUrl}${endpoint.url}`);
      
      const response = await fetch(`${baseUrl}${endpoint.url}`, {
        method: 'GET',
        headers,
      });

      const data = await response.text(); // Obtenir la réponse brute d'abord
      
      let result = {
        endpoint: endpoint.name,
        status: response.status,
        success: response.ok,
        rawData: data,
        error: null,
      };

      try {
        result.jsonData = JSON.parse(data);
      } catch (parseError) {
        result.parseError = parseError.message;
      }

      setResults(prev => [...prev, result]);
      
    } catch (error) {
      console.error(`Error testing ${endpoint.name}:`, error);
      setResults(prev => [...prev, {
        endpoint: endpoint.name,
        status: 'Network Error',
        success: false,
        error: error.message,
        stack: error.stack,
      }]);
    }
    
    setLoading(false);
  };

  const testAll = async () => {
    setResults([]);
    for (const endpoint of testEndpoints) {
      await testApi(endpoint);
      await new Promise(resolve => setTimeout(resolve, 500)); // Pause entre les tests
    }
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        API Test & Debug
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Button 
          variant="contained" 
          onClick={testAll} 
          disabled={loading}
          sx={{ mr: 2 }}
        >
          Test All APIs
        </Button>
        <Button variant="outlined" onClick={clearResults}>
          Clear Results
        </Button>
      </Box>

      {results.map((result, index) => (
        <Paper key={index} sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            {result.endpoint}
          </Typography>
          
          <Alert severity={result.success ? 'success' : 'error'} sx={{ mb: 2 }}>
            Status: {result.status} - {result.success ? 'Success' : 'Failed'}
          </Alert>

          {result.error && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="error">Error:</Typography>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', bgcolor: '#f5f5f5', p: 1 }}>
                {result.error}
              </Typography>
            </Box>
          )}

          {result.rawData && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Raw Response:</Typography>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', bgcolor: '#f5f5f5', p: 1, maxHeight: 200, overflow: 'auto' }}>
                {result.rawData.substring(0, 1000)}{result.rawData.length > 1000 ? '...' : ''}
              </Typography>
            </Box>
          )}

          {result.jsonData && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">JSON Data:</Typography>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', bgcolor: '#f0f0f0', p: 1, maxHeight: 200, overflow: 'auto' }}>
                {JSON.stringify(result.jsonData, null, 2)}
              </Typography>
            </Box>
          )}

          {result.parseError && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="warning.main">Parse Error:</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'warning.main' }}>
                {result.parseError}
              </Typography>
            </Box>
          )}
        </Paper>
      ))}
    </Box>
  );
};

export default ApiTestPage;