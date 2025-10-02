import React from 'react';

interface LiveKitWrapperProps {
  token: string;
  serverUrl: string;
  enableVideo?: boolean;
  enableAudio?: boolean;
  selectedCamera?: string;
  selectedMicrophone?: string;
  viewerMode?: boolean;
  onConnected?: () => void;
  onDisconnected?: () => void;
}

const LiveKitWrapper: React.FC<LiveKitWrapperProps> = ({ 
  token, 
  serverUrl,
  enableVideo = false,  // Start with video disabled
  enableAudio = false,  // Start with audio disabled
  selectedCamera,
  selectedMicrophone,
  viewerMode = false,
  onConnected, 
  onDisconnected 
}) => {
  // Import components dynamically
  const [components, setComponents] = React.useState<any>(null);

  React.useEffect(() => {
    const loadComponents = async () => {
      try {
        const livekit = await import('@livekit/components-react');
        setComponents({
          LiveKitRoom: livekit.LiveKitRoom,
          VideoConference: livekit.VideoConference
        });
      } catch (error) {
        console.error('Failed to load LiveKit components:', error);
      }
    };
    loadComponents();
  }, []);

  if (!components) {
    return <div>Loading LiveKit components...</div>;
  }

  const { LiveKitRoom: Room, VideoConference: Conference } = components;

  // Prepare room options with device constraints
  const roomOptions = {
    video: viewerMode ? false : (enableVideo ? {
      deviceId: selectedCamera || undefined
    } : false),
    audio: viewerMode ? false : (enableAudio ? {
      deviceId: selectedMicrophone || undefined
    } : false),
    token: token,
    serverUrl: serverUrl,
    'data-lk-theme': 'default',
    style: { height: 'calc(100vh - 100px)' },
    onConnected: onConnected,
    onDisconnected: onDisconnected,
    connectOptions: viewerMode ? {
      autoSubscribe: true,  // Subscribe to other participants
      publishAudio: false,  // Don't publish audio in viewer mode
      publishVideo: false   // Don't publish video in viewer mode
    } : undefined
  };

  return React.createElement(
    Room,
    roomOptions,
    React.createElement(Conference)
  );
};

export default LiveKitWrapper;
