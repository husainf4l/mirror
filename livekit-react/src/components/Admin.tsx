import React from 'react';
import './Admin.css';

const Admin: React.FC = () => {
  return (
    <div className="admin-page">
      <div className="container">
        <div className="header">
          <h1>👥 Guest Management</h1>
          <p>Admin panel for managing wedding guests and data</p>
        </div>

        <div className="admin-grid">
          <div className="admin-section">
            <h3 className="section-title">Guest Analytics</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">0</div>
                <div className="stat-label">Total Visitors</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">0</div>
                <div className="stat-label">Active Sessions</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">0</div>
                <div className="stat-label">Messages Sent</div>
              </div>
            </div>
          </div>

          <div className="admin-section">
            <h3 className="section-title">Quick Actions</h3>
            <div className="actions-grid">
              <button className="admin-btn primary">
                📊 View Reports
              </button>
              <button className="admin-btn">
                📋 Export Data
              </button>
              <button className="admin-btn">
                🔄 Refresh Stats
              </button>
              <button className="admin-btn warning">
                ⚙️ System Settings
              </button>
            </div>
          </div>

          <div className="admin-section full-width">
            <h3 className="section-title">Recent Activity</h3>
            <div className="activity-log">
              <div className="activity-item">
                <span className="activity-time">Coming soon...</span>
                <span className="activity-text">Guest activity logging will be implemented here</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Admin;
