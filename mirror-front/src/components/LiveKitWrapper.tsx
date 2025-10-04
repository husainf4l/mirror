'use client';

import React, { useEffect } from 'react';
import { LiveKitRoom, RoomAudioRenderer, useMaybeRoomContext } from '@livekit/components-react';
import { RoomEvent } from 'livekit-client';

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

interface LiveKitWrapperProps {
  token: string;
  serverUrl: string;
  enableAudio?: boolean;
  enableVideo?: boolean;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onTranscriptionReceived?: (segments: TranscriptSegment[]) => void;
}

function TranscriptionListener({ onTranscriptionReceived }: { onTranscriptionReceived?: (segments: any[]) => void }) {
  const room = useMaybeRoomContext();

  useEffect(() => {
    if (!room || !onTranscriptionReceived) {
      return;
    }

    const handleTranscription = (segments: any[]) => {
      console.log('🎙️ LiveKitWrapper: Transcription received:', segments);
      onTranscriptionReceived(segments);
    };

    room.on(RoomEvent.TranscriptionReceived, handleTranscription);

    return () => {
      room.off(RoomEvent.TranscriptionReceived, handleTranscription);
    };
  }, [room, onTranscriptionReceived]);

  return null;
}

export default function LiveKitWrapper({
  token,
  serverUrl,
  enableAudio = true,
  enableVideo = true,
  onConnected,
  onDisconnected,
  onTranscriptionReceived
}: LiveKitWrapperProps) {
  if (!token || !serverUrl) {
    return null;
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      onConnected={onConnected}
      onDisconnected={onDisconnected}
      audio={enableAudio}
      video={enableVideo}
      data-lk-theme="default"
    >
      <RoomAudioRenderer />
      <TranscriptionListener onTranscriptionReceived={onTranscriptionReceived} />
    </LiveKitRoom>
  );
}