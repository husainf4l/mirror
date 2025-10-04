'use client';

import React from 'react';
import LiveKitWrapper from '../LiveKitWrapper';
import './LiveKitConnection.css';

interface TranscriptSegment {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  final: boolean;
  language: string;
  participantIdentity?: string;
  timestamp?: number;
}

interface LiveKitConnectionProps {
  token: string;
  serverUrl: string;
  audioEnabled: boolean;
  videoEnabled: boolean;
  onConnected: () => void;
  onDisconnected: () => void;
  onTranscriptionReceived?: (segments: TranscriptSegment[]) => void;
}

const LiveKitConnection: React.FC<LiveKitConnectionProps> = ({
  token,
  serverUrl,
  audioEnabled,
  videoEnabled,
  onConnected,
  onDisconnected,
  onTranscriptionReceived,
}) => {
  console.log('🔗 LiveKitConnection rendering with transcription callback:', !!onTranscriptionReceived);
  
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
        onTranscriptionReceived={onTranscriptionReceived}
      />
    </div>
  );
};

export default LiveKitConnection;