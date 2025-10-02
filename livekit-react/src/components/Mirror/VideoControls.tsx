import React from 'react';
import './VideoControls.css';

interface VideoControlsProps {
  isConnected: boolean;
  showControls: boolean;
  loading: boolean;
  error: string;
  permissionError: string;
  permissions: {
    camera: string;
    microphone: string;
  };
  onToggleControls: () => void;
  onConnect: () => void;
}

const VideoControls: React.FC<VideoControlsProps> = ({
  isConnected,
  showControls,
  loading,
  error,
  permissionError,
  permissions,
  onToggleControls,
  onConnect,
}) => {
  // Only show if not connected or no token
  if (isConnected) return null;

  return (
    <div className="video-join-overlay">
      <button 
        className="join-video-btn"
        onClick={onToggleControls}
      >
        🎭 Talk to Mirror
      </button>
      
      {showControls && (
        <div className="video-join-card">
          <h3>🎭 Connect to Wedding Mirror</h3>
          
          {/* Permission Status */}
          <div className="permission-status-compact">
            <div className={`permission-item ${permissions.camera === 'granted' ? 'granted' : 'denied'}`}>
              {permissions.camera === 'granted' ? '✅' : '❌'} Camera
            </div>
            <div className={`permission-item ${permissions.microphone === 'granted' ? 'granted' : 'denied'}`}>
              {permissions.microphone === 'granted' ? '✅' : '❌'} Microphone
            </div>
          </div>

          {/* Error Display */}
          {(error || permissionError) && (
            <div className="error-message-compact">
              ❌ {error || permissionError}
            </div>
          )}
          
          {/* Connect Button */}
          <button 
            onClick={onConnect}
            disabled={loading || isConnected}
            className="connect-btn-compact"
          >
            {loading ? '🔄 Connecting...' : isConnected ? '🎭 Connected' : '🎭 Talk to Mirror'}
          </button>
        </div>
      )}
    </div>
  );
};

export default VideoControls;
