import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import '@livekit/components-styles';
import './App.css';

// Components
import Login from './components/Login';
import Mirror from './components/Mirror';
import Control from './components/Control';
import Admin from './components/Admin';
import LiveKitRoom from './components/LiveKitRoom';
import GuestManagement from './components/GuestManagement';
// Context
import { AuthProvider, useAuth } from './context/AuthContext';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>; // Or a proper loading component
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/mirror" element={<ProtectedRoute><Mirror /></ProtectedRoute>} />
            <Route path="/control" element={<ProtectedRoute><Control /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
            <Route path="/guests" element={<ProtectedRoute><GuestManagement /></ProtectedRoute>} />
            <Route path="/livekit" element={<ProtectedRoute><LiveKitRoom /></ProtectedRoute>} />
            <Route path="/" element={<Navigate to="/control" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
