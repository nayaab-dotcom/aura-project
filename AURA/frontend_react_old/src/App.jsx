import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DroneView from './pages/DroneView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/drone/:id" element={<DroneView />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
