import React from 'react';
import LiveKitWrapper from '../../LiveKitWrapper';
import './LiveKitConnection.css';

interface LiveKitConnectionProps {
  token: string;
  serverUrl: string;
  audioEnabled: boolean;
  videoEnabled: boolean;
  onConnected: () => void;
  onDisconnected: () => void;
}

const LiveKitConnection: React.FC<LiveKitConnectionProps> = ({
  token,
  serverUrl,
  audioEnabled,
  videoEnabled,
  onConnected,
  onDisconnected,
}) => {
  if (!token) return null;

  return (
    <div className="hidden-livekit">
      <LiveKitWrapper
        token={token}
        serverUrl={serverUrl}
        enableAudio={audioEnabled}
        enableVideo={videoEnabled}
        onConnected={onConnected}
        onDisconnected={onDisconnected}
      />
    </div>
  );
};

export default LiveKitConnection;
