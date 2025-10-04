'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useDevicePermissions } from '../../hooks/useDevicePermissions';
import MirrorDisplay from './MirrorDisplay';
import ConnectionStatus from './ConnectionStatus';
import             const randomRoom = `mirror-${Date.now()}`;
            const randomGuest = `Guest-${Date.now()}`;

            try {
              const roomToken = await getToken(randomRoom, randomGuest);ntrols from './VideoControls';
import LiveKitConnection from './LiveKitConnection';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || 'wss://widdai-aphl2lb9.livekit.cloud';

interface SSEMessage {
  type: string;
  text?: string;
  new_text?: string;
  current_text?: string;
  message?: string;
  timestamp?: number;
  audio_file?: string;
  action?: string;
}

interface TokenResponse {
  success: boolean;
  token?: string;
  url?: string;
  error?: string;
}

interface TranscriptionSegment {
  id: string;
  text: string;
  firstReceivedTime: number;
  final: boolean;
}

const Mirror: React.FC = () => {
  // Mirror state
  const [mirrorText, setMirrorText] = useState<string>(
    '<span class="line welcome fancy">Welcome to</span><span class="line names fancy">Rakan & Farah Wedding</span><span class="line script">Say Mirror Mirror to begin</span>'
  );
  const [connected, setConnected] = useState<boolean>(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // LiveKit states
  const [token, setToken] = useState<string>('');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [showVideoControls, setShowVideoControls] = useState<boolean>(false);
  const hasAutoConnected = useRef<boolean>(false);

  // Audio and video enable states
  const [audioEnabled, setAudioEnabled] = useState<boolean>(false);
  
  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [videoEnabled, setVideoEnabled] = useState<boolean>(false);
  
  // Transcript state
  const [showTranscript, setShowTranscript] = useState<boolean>(true);
  const [transcriptions, setTranscriptions] = useState<{[id: string]: TranscriptionSegment}>({});

  // Audio playback function
  const playMirrorActivationSound = () => {
    try {
      console.log('🔊 Playing mirror activation sound...');
      // Create audio element and play the sound
      const audio = new Audio('/mirror.wav'); // Audio file should be in public folder
      audio.volume = 0.8;
      audio.play().then(() => {
        console.log('✅ Mirror activation sound played successfully');
      }).catch((error) => {
        console.log('❌ Failed to play mirror activation sound:', error);
        // Fallback: try different audio file or path
        try {
          const fallbackAudio = new Audio('/audio/mirror-activation.wav');
          fallbackAudio.volume = 0.8;
          fallbackAudio.play();
        } catch (fallbackError) {
          console.log('❌ Fallback audio also failed:', fallbackError);
        }
      });
    } catch (error) {
      console.log('❌ Error creating audio element:', error);
    }
  };

  // Use device permissions hook
  const {
    permissions,
    requestPermissions,
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

  // SSE Connection Effect
  useEffect(() => {
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
              
            case 'audio_play':
              console.log('🔊 Processing audio play event...');
              if (data.action === 'play_mirror_sound') {
                playMirrorActivationSound();
              }
              break;
              
            case 'ping':
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

    return () => {
      if (eventSourceRef.current) {
        console.log('🔌 Closing SSE connection');
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Auto-permission and connect effect
  useEffect(() => {
    const autoConnect = async () => {
      if (hasAutoConnected.current || isConnected) {
        console.log('🔄 Auto-connect skipped - already attempted or connected');
        return;
      }

      hasAutoConnected.current = true;
      console.log('🎤 Starting auto-connect process for wedding mirror...');

      try {
        console.log('🔒 Requesting device permissions...');
        await requestPermissions();
        console.log('✅ Permission request completed');

        setTimeout(async () => {
          if (!isConnected) {
            console.log('🎭 Auto-connecting to wedding mirror...');

            const randomRoom = `mirror-${Date.now()}`;
            const randomGuest = `Guest-${Date.now()}`;
            setRoomName(randomRoom);
            setUserName(randomGuest);

            try {
              const roomToken = await getToken(randomRoom, randomGuest);
              console.log('🎫 Token received, connecting to room...');
              setToken(roomToken);
              setIsConnected(true);
              console.log('✨ Wedding mirror connection established!');
            } catch (error) {
              console.error('❌ Auto-connect failed:', error);
              hasAutoConnected.current = false;
            }
          }
        }, 1000);
      } catch (error) {
        console.error('❌ Permission request failed:', error);
        hasAutoConnected.current = false;
      }
    };

    autoConnect();
  }, [requestPermissions, isConnected]);

  const handleConnect = async () => {
    try {
      const randomRoom = `mirror-${Date.now()}`;
      const randomGuest = `Guest-${Date.now()}`;

      console.log('🎭 Connecting to mirror with random credentials...');

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

  // Fullscreen functionality
  const enterFullscreen = async () => {
    try {
      if (document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
        setIsFullscreen(true);
      }
    } catch (error) {
      console.error('Failed to enter fullscreen:', error);
    }
  };

  const exitFullscreen = async () => {
    try {
      if (document.fullscreenElement && document.exitFullscreen) {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (error) {
      console.error('Failed to exit fullscreen:', error);
    }
  };

  const toggleFullscreen = () => {
    if (isFullscreen) {
      exitFullscreen();
    } else {
      enterFullscreen();
    }
  };

  // Transcript toggle function
  const toggleTranscript = () => {
    setShowTranscript(!showTranscript);
  };

  // Handle transcription received from LiveKit
  const handleTranscriptionReceived = (segments: TranscriptionSegment[]) => {
    console.log('📝 Transcription segments received:', segments);
    setTranscriptions((prev) => {
      const newTranscriptions = { ...prev };
      for (const segment of segments) {
        newTranscriptions[segment.id] = segment;
      }
      return newTranscriptions;
    });
  };

  // Get sorted transcription text (limited to last 3 words)
  const getTranscriptionText = () => {
    const segments = Object.values(transcriptions);
    if (segments.length === 0) return '';
    
    const fullText = segments
      .sort((a: TranscriptionSegment, b: TranscriptionSegment) => (a.firstReceivedTime || 0) - (b.firstReceivedTime || 0))
      .map((s: TranscriptionSegment) => s.text)
      .join(' ');
    
    // Split by whitespace and get last 3 words
    const words = fullText.trim().split(/\s+/);
    const lastThreeWords = words.slice(-3).join(' ');
    
    return lastThreeWords;
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  return (
    <>
      {/* Black background that covers entire viewport */}
      <div className="fixed inset-0 bg-black h-screen w-screen overflow-hidden -z-10" />
      
      <div 
        className="fixed inset-0 bg-black text-white flex flex-col items-center justify-start pt-16 z-10 overflow-y-auto"
        style={{ 
          fontFamily: 'Cinzel, serif'
        }}
      >
        <div className="flex flex-col items-center w-full max-w-full pb-32">
          {/* Transcription Display - Above main text */}
          {showTranscript && Object.keys(transcriptions).length > 0 && (
            <div className="mb-10 max-w-4xl w-full px-8">
              <div className="text-white text-4xl md:text-5xl lg:text-6xl text-center leading-tight font-light tracking-wide">
                {getTranscriptionText()}
              </div>
            </div>
          )}

          <MirrorDisplay mirrorText={mirrorText} />
        </div>

        <LiveKitConnection
          token={token}
          serverUrl={serverUrl}
          audioEnabled={audioEnabled}
          videoEnabled={videoEnabled}
          onConnected={() => {
            console.log('✨ Wedding mirror connected to room - agent can now see and hear you!');
            setTranscriptions({}); // Clear transcriptions on new connection
          }}
          onDisconnected={() => {
            console.log('❌ Wedding mirror disconnected from room');
            handleDisconnect();
          }}
          onTranscriptionReceived={handleTranscriptionReceived}
        />

        <VideoControls
          isConnected={isConnected && !!token}
          showControls={showVideoControls}
          loading={loading}
          error={error}
          permissionError={permissionError || ''}
          permissions={{
            camera: permissions.camera as string,
            microphone: permissions.microphone as string,
          }}
          onToggleControls={() => setShowVideoControls(!showVideoControls)}
          onConnect={handleConnect}
        />

        <ConnectionStatus connected={connected} />
      </div>
 
      {/* Fullscreen control */}
      <button 
        className="fixed bottom-5 right-5 w-9 h-9 text-base bg-white/10 backdrop-blur-sm border border-white/20 
                   rounded-full text-white/80 cursor-pointer z-[999999] transition-all duration-300 ease-out
                   flex items-center justify-center shadow-lg opacity-70 visible pointer-events-auto
                   hover:bg-white/20 hover:border-white/40 hover:text-white hover:opacity-100 hover:scale-110 hover:shadow-xl
                   active:scale-90 active:rotate-[72deg] active:shadow-sm active:bg-white/30
                   md:w-[30px] md:h-[30px] md:text-sm md:bottom-4 md:right-4"
        onClick={toggleFullscreen}
        title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
      >
        <i className="fas fa-star"></i>
      </button>

      {/* Transcript toggle button */}
      {Object.keys(transcriptions).length > 0 && (
        <button 
          className="fixed bottom-5 right-16 w-9 h-9 text-base bg-white/10 backdrop-blur-sm border border-white/20 
                     rounded-full text-white/80 cursor-pointer z-[999999] transition-all duration-300 ease-out
                     flex items-center justify-center shadow-lg opacity-70 visible pointer-events-auto
                     hover:bg-white/20 hover:border-white/40 hover:text-white hover:opacity-100 hover:scale-110 hover:shadow-xl
                     active:scale-90 active:shadow-sm active:bg-white/30
                     md:w-[30px] md:h-[30px] md:text-sm md:bottom-4 md:right-14"
          onClick={toggleTranscript}
          title={showTranscript ? "Hide Transcript" : "Show Transcript"}
        >
          <i className={`fas ${showTranscript ? 'fa-comment' : 'fa-comment-slash'}`}></i>
        </button>
      )}
    </>
  );
};

export default Mirror;