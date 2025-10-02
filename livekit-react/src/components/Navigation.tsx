import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navigation.css';

const Navigation: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Don't show navigation on login page
  if (location.pathname === '/login' || !isAuthenticated) {
    return null;
  }

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/mirror">🪞 Wedding Mirror</Link>
        </div>
        
        <div className="nav-links">
          <Link 
            to="/mirror" 
            className={location.pathname === '/mirror' ? 'active' : ''}
          >
            🪞 Mirror
          </Link>
          <Link 
            to="/control" 
            className={location.pathname === '/control' ? 'active' : ''}
          >
            ⚙️ Control
          </Link>
          <Link 
            to="/livekit" 
            className={location.pathname === '/livekit' ? 'active' : ''}
          >
            🎥 Video
          </Link>
          <Link 
            to="/guests" 
            className={location.pathname === '/guests' ? 'active' : ''}
          >
            👥 Guests
          </Link>
          <Link 
            to="/admin" 
            className={location.pathname === '/admin' ? 'active' : ''}
          >
            ⚙️ Admin
          </Link>
        </div>

        <button onClick={handleLogout} className="logout-btn">
          🚪 Logout
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
