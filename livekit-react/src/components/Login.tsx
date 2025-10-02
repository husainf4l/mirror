import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login: React.FC = () => {
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/control');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!password.trim()) {
      setError('Please enter a password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const success = await login(password);
      if (success) {
        navigate('/control');
      } else {
        setError('Invalid password. Please try again.');
      }
    } catch (error) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-focus password field
  useEffect(() => {
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
      passwordInput.focus();
    }
  }, []);

  return (
    <div className="login-page">
      <div className="stars">
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
        <i className="star fas fa-star"></i>
      </div>

      <div className="login-container">
        <h1 className="login-title">Mirror Access</h1>
        <p className="login-subtitle">Enter the secret phrase to continue</p>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password..."
              required
              disabled={loading}
            />
          </div>
          
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Entering...' : 'Enter Mirror'}
          </button>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default Login;
