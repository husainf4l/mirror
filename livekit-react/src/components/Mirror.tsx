import React, { useState, useEffect, useRef } from 'react';
import './Mirror.css';
import LiveKitWrapper from '../LiveKitWrapper';
import { useDevicePermissions } from '../hooks/useDevicePermissions';

const apiUrl = process.env.REACT_APP_API_URL || '';
const serverUrl = process.env.REACT_APP_LIVEKIT_URL || 'wss://mirror-je9mbmgp.livekit.cloud';

interface SSEMessage {
  type: string;
  text?: string;
  new_text?: string;
  current_text?: string;
  message?: string;
  timestamp?: number;
}

interface TokenResponse {
  success: boolean;
  token?: string;
  url?: string;
  error?: string;
}

const Mirror: React.FC = () => {
  const [mirrorText, setMirrorText] = useState<string>(
    '<span class="line fancy">Welcome to</span><span class="line fancy">x & y</span><span class="line fancy">Wedding</span><span class="line script">Say Mirror Mirror to begin</span>'
  );
  const [connected, setConnected] = useState<boolean>(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // LiveKit states
  const [token, setToken] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [roomName, setRoomName] = useState<string>('wedding-mirror-guest');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [showVideoControls, setShowVideoControls] = useState<boolean>(false);
  const hasAutoConnected = useRef<boolean>(false);

  // Audio and video enable states
  const [audioEnabled, setAudioEnabled] = useState<boolean>(false);
  const [videoEnabled, setVideoEnabled] = useState<boolean>(false);

  // Use device permissions hook
  const {
    permissions,
    devices,
    requestPermissions,
    loading: permissionLoading,
    error: permissionError,
  } = useDevicePermissions();

  // Enable audio and video when permissions are granted
  useEffect(() => {
    if (permissions.microphone === 'granted' && !audioEnabled) {
      console.log('🎤 Microphone permissions granted - enabling audio');
      setAudioEnabled(true);
    }
    if (permissions.camera === 'granted' && !videoEnabled) {
      console.log('📹 Camera permissions granted - enabling video');
      setVideoEnabled(true);
    }
  }, [permissions.microphone, permissions.camera, audioEnabled, videoEnabled]);
  const getToken = async (room: string, name: string): Promise<string> => {
    setLoading(true);
    setError('');
    
    try {
      console.log('🌐 Requesting token from:', `${apiUrl}/api/livekit/token`);
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

      console.log('📡 Token API response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: TokenResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to get token');
      }

      console.log('✅ Token API response successful');
      return data.token || '';
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // SSE Connection Effect (runs once)
  useEffect(() => {
    // Connect to Server-Sent Events
    const connectSSE = () => {
      console.log('🔗 Connecting to Mirror SSE stream...');
      
      const eventSource = new EventSource(`${apiUrl}/api/events`, {
        withCredentials: true
      });
      
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data: SSEMessage = JSON.parse(event.data);
          console.log('📡 SSE Message received:', data);

          switch (data.type) {
            case 'text_update':
              console.log('📝 Processing text update...');
              if (data.text) {
                setMirrorText(data.text);
              }
              break;
              
            case 'reset':
              console.log('🔄 Processing reset event...');
              if (data.new_text) {
                setMirrorText(data.new_text);
              }
              break;
              
            case 'connected':
              console.log('🔗 Connected to mirror SSE stream');
              setConnected(true);
              if (data.current_text) {
                console.log('📝 Setting initial text from connection');
                setMirrorText(data.current_text);
              }
              break;
              
            case 'ping':
              // Ignore ping messages - just for keepalive
              break;
              
            default:
              console.log('❓ Unknown message type:', data.type);
          }
        } catch (error) {
          console.log('❌ Error parsing SSE data:', error);
          console.log('Raw event data:', event.data);
        }
      };

      eventSource.onerror = (event) => {
        console.log('❌ SSE Error:', event);
        setConnected(false);
        
        // Reconnect after 5 seconds
        setTimeout(() => {
          if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
            connectSSE();
          }
        }, 5000);
      };

      eventSource.onopen = () => {
        console.log('✅ SSE Connection opened');
        setConnected(true);
      };
    };

    connectSSE();

    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        console.log('🔌 Closing SSE connection');
        eventSourceRef.current.close();
      }
    };
  }, []); // Empty dependency array - runs once on mount

  // Auto-permission and connect effect
  useEffect(() => {
    const autoConnect = async () => {
      if (hasAutoConnected.current || isConnected) {
        console.log('🔄 Auto-connect skipped - already attempted or connected', {
          hasAutoConnected: hasAutoConnected.current,
          isConnected
        });
        return;
      }

      hasAutoConnected.current = true;
      console.log('🎤 Starting auto-connect process for wedding mirror...');

      try {
        // Request permissions automatically
        console.log('🔒 Requesting device permissions...');
        await requestPermissions();
        console.log('✅ Permission request completed');

        // Wait for permissions to be processed
        setTimeout(async () => {
          console.log('📊 Checking permissions after delay:', {
            camera: permissions.camera,
            microphone: permissions.microphone
          });

          // For now, let's try to connect even if permissions aren't granted
          // The LiveKit components will handle permission requests
          if (!isConnected) {
            console.log('🎭 Auto-connecting to wedding mirror (permissions may be requested later)...');

            // Generate random room and guest name for auto-connect
            const randomRoom = `mirror-${Date.now()}`;
            const randomGuest = `Guest-${Date.now()}`;
            setRoomName(randomRoom);
            setUserName(randomGuest);

            try {
              const roomToken = await getToken(randomRoom, randomGuest);
              console.log('🎫 Token received, connecting to room...', roomToken ? 'Token OK' : 'Token failed');
              setToken(roomToken);
              setIsConnected(true);
              console.log('✨ Wedding mirror connection established!');
            } catch (error) {
              console.error('❌ Auto-connect failed:', error);
              hasAutoConnected.current = false; // Allow retry on error
            }
          } else {
            console.log('ℹ️ Already connected, skipping auto-connect');
          }
        }, 1000); // Reduced to 1 second
      } catch (error) {
        console.error('❌ Permission request failed:', error);
        hasAutoConnected.current = false; // Allow retry on error
      }
    };

    // Start auto-connect process
    autoConnect();
  }, [requestPermissions, isConnected]); // Simplified dependencies

  const handleConnect = async () => {
    try {
      // Generate random room and guest name
      const randomRoom = `mirror-${Date.now()}`;
      const randomGuest = `Guest-${Date.now()}`;

      console.log('🎭 Connecting to mirror with random credentials...');
      setRoomName(randomRoom);
      setUserName(randomGuest);

      const roomToken = await getToken(randomRoom, randomGuest);
      setToken(roomToken);
      setIsConnected(true);
      setShowVideoControls(false);
      console.log('✨ Connected to wedding mirror!');
    } catch (error) {
      console.error('Failed to connect:', error);
      setError('Connection failed. Please try again.');
    }
  };

  const handleDisconnect = () => {
    setToken('');
    setIsConnected(false);
    setError('');
    setShowVideoControls(false);
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

  return (
    <div className="mirror-page">
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

      <div className="mirror-container">
        <div 
          className="mirror-text" 
          dangerouslySetInnerHTML={{ __html: mirrorText }}
        />
      </div>

      {/* Hidden LiveKit Integration - Auto-connects, Agent Can See */}
      {isConnected && token && (
        <div className="hidden-livekit">
          <LiveKitWrapper
            token={token}
            serverUrl={serverUrl}
            enableAudio={audioEnabled}
            enableVideo={videoEnabled}
            onConnected={() => {
              console.log('✨ Wedding mirror connected to room - agent can now see and hear you!');
            }}
            onDisconnected={() => {
              console.log('❌ Wedding mirror disconnected from room');
              handleDisconnect();
            }}
          />
        </div>
      )}

      {/* Manual Connection Controls - Show if auto-connect fails */}
      {(!isConnected || !token) && (
        <div className="video-join-overlay">
          <button 
            className="join-video-btn"
            onClick={() => setShowVideoControls(!showVideoControls)}
          >
            � Talk to Mirror
          </button>
          
          {showVideoControls && (
            <div className="video-join-card">
              <h3>� Connect to Wedding Mirror</h3>
              
              {/* Permission Status */}
              <div className="permission-status-compact">
                <div className={`permission-item ${(permissions.camera as string) === 'granted' ? 'granted' : 'denied'}`}>
                  {(permissions.camera as string) === 'granted' ? '✅' : '❌'} Camera
                </div>
                <div className={`permission-item ${(permissions.microphone as string) === 'granted' ? 'granted' : 'denied'}`}>
                  {(permissions.microphone as string) === 'granted' ? '✅' : '❌'} Microphone
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
                onClick={handleConnect}
                disabled={loading || isConnected}
                className="connect-btn-compact"
              >
                {loading ? '🔄 Connecting...' : isConnected ? '🎭 Connected' : '🎭 Talk to Mirror'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Connection Status Indicator */}
      <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
        {connected ? '🔗' : '⚠️'}
      </div>
    </div>
  );
};

export default Mirror;
