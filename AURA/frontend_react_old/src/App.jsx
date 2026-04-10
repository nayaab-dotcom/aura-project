import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DroneView from './pages/DroneView';
import Analysis from './pages/Analysis';
import Login from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/drone/:id" element={<DroneView />} />
        <Route path="/analysis" element={<Analysis />} />
        {/* Keep /report for compatibility; render combined page */}
        <Route path="/report" element={<Analysis />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
