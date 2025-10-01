import React, { useState } from 'react';
import LiveKitWrapper from '../LiveKitWrapper';
import { useDevicePermissions } from '../hooks/useDevicePermissions';
import './LiveKitRoom.css';

const serverUrl = process.env.REACT_APP_LIVEKIT_URL || 'wss://mirror-je9mbmgp.livekit.cloud';
const apiUrl = process.env.REACT_APP_API_URL || '';

interface TokenResponse {
  success: boolean;
  token?: string;
  url?: string;
  error?: string;
}

const LiveKitRoom: React.FC = () => {
  const [token, setToken] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [roomName, setRoomName] = useState<string>('mirror-room');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [selectedCamera, setSelectedCamera] = useState<string>('');
  const [selectedMicrophone, setSelectedMicrophone] = useState<string>('');

  // Use our custom device permissions hook
  const {
    permissions,
    devices,
    requestPermissions,
    loading: permissionLoading,
    error: permissionError,
  } = useDevicePermissions();

  const getToken = async (room: string, name: string): Promise<string> => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${apiUrl}/api/livekit/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          room: room,
          name: name,
          identity: `${name}-${Date.now()}`
        })
      });

      const data: TokenResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to get token');
      }

      return data.token || '';
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userName.trim()) {
      setError('Please enter your name');
      return;
    }

    // Check if we have necessary permissions
    const needsCamera = permissions.camera !== 'granted';
    const needsMic = permissions.microphone !== 'granted';
    
    if (needsCamera || needsMic) {
      setError('Camera and microphone permissions are required');
      return;
    }

    try {
      const roomToken = await getToken(roomName, userName);
      setToken(roomToken);
      setIsConnected(true);
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  };

  const handleDisconnect = () => {
    setToken('');
    setIsConnected(false);
    setError('');
  };

  const resetMirror = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/reset`, {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        console.log('✅ Mirror reset successfully');
      }
    } catch (error) {
      console.error('❌ Failed to reset mirror:', error);
    }
  };

  const openWindow = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  // If connected and have token, show the LiveKit room
  if (isConnected && token) {
    return (
      <div className="livekit-page">
        <div className="room-header">
          <h1>🎥 Wedding Mirror - Video Room</h1>
          <div className="room-info">
            <span>Room: {roomName}</span>
            <span>User: {userName}</span>
            <div className="header-buttons">
              <button onClick={resetMirror} className="mirror-btn">
                🪞 Reset Mirror
              </button>
              <button onClick={() => openWindow('/control')} className="control-btn">
                ⚙️ Control Panel
              </button>
              <button onClick={handleDisconnect} className="disconnect-btn">
                🚪 Leave Room
              </button>
            </div>
          </div>
        </div>
        
        <LiveKitWrapper
          token={token}
          serverUrl={serverUrl}
          onConnected={() => console.log('Connected to room')}
          onDisconnected={() => {
            console.log('Disconnected from room');
            handleDisconnect();
          }}
        />
      </div>
    );
  }

  // Show connection form
  return (
    <div className="livekit-page">
      <div className="connection-container">
        <div className="connection-card">
          <h1>🎥 Join Wedding Video Room</h1>
          <p>Connect with camera and microphone access</p>
          
          {/* Device Permission Status */}
          <div className="permission-status">
            <h3>Device Permissions</h3>
            <div className="permission-grid">
              <div className={`permission-item ${permissions.camera === 'granted' ? 'granted' : 'denied'}`}>
                <span className="permission-icon">
                  {permissions.camera === 'granted' ? '✅' : '❌'}
                </span>
                <span>Camera: {permissions.camera === 'granted' ? 'Granted' : 'Denied'}</span>
              </div>
              <div className={`permission-item ${permissions.microphone === 'granted' ? 'granted' : 'denied'}`}>
                <span className="permission-icon">
                  {permissions.microphone === 'granted' ? '✅' : '❌'}
                </span>
                <span>Microphone: {permissions.microphone === 'granted' ? 'Granted' : 'Denied'}</span>
              </div>
            </div>
            
            {(permissions.camera !== 'granted' || permissions.microphone !== 'granted') && (
              <button 
                onClick={requestPermissions}
                disabled={permissionLoading}
                className="permission-btn"
              >
                {permissionLoading ? '🔄 Requesting...' : '🔒 Request Permissions'}
              </button>
            )}
          </div>

          {/* Device Selection */}
          {permissions.camera === 'granted' && permissions.microphone === 'granted' && (
            <div className="device-selection">
              <div className="form-group">
                <label htmlFor="cameraSelect">Camera:</label>
                <select
                  id="cameraSelect"
                  value={selectedCamera}
                  onChange={(e) => setSelectedCamera(e.target.value)}
                >
                  <option value="">Select Camera</option>
                  {devices.videoInputs.map((device) => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label || `Camera ${device.deviceId.slice(0, 8)}...`}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="microphoneSelect">Microphone:</label>
                <select
                  id="microphoneSelect"
                  value={selectedMicrophone}
                  onChange={(e) => setSelectedMicrophone(e.target.value)}
                >
                  <option value="">Select Microphone</option>
                  {devices.audioInputs.map((device) => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label || `Microphone ${device.deviceId.slice(0, 8)}...`}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Error Messages */}
          {(error || permissionError) && (
            <div className="error-message">
              ❌ {error || permissionError}
            </div>
          )}
          
          {/* Connection Form */}
          <form onSubmit={handleConnect} className="connection-form">
            <div className="form-group">
              <label htmlFor="userName">Your Name:</label>
              <input
                type="text"
                id="userName"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your name"
                required
                disabled={loading}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="roomName">Room Name:</label>
              <input
                type="text"
                id="roomName"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                placeholder="Room name"
                required
                disabled={loading}
              />
            </div>
            
            <button 
              type="submit" 
              disabled={
                loading || 
                permissions.camera !== 'granted' || 
                permissions.microphone !== 'granted'
              } 
              className="connect-btn"
            >
              {loading ? '🔄 Connecting...' : '🎬 Join Room'}
            </button>
          </form>
          
          <div className="links">
            <button onClick={() => openWindow('/mirror')} className="link-btn">
              🪞 View Mirror Display
            </button>
            <button onClick={() => openWindow('/control')} className="link-btn">
              ⚙️ Mirror Control Panel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveKitRoom;
