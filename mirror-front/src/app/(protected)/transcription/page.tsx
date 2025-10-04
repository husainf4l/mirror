'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Room, RoomEvent, Track, LocalAudioTrack, ConnectionState } from 'livekit-client';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useConnectionState,
  useLocalParticipant,
} from '@livekit/components-react';
import { AnimatePresence, motion } from 'framer-motion';
import { Typewriter } from '@/components/Transcription/Typewriter';
import { MicrophoneButton } from '@/components/Transcription/MicrophoneButton';
import { useMultibandTrackVolume } from '@/hooks/useTrackVolume';

const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || 'wss://widdai-aphl2lb9.livekit.cloud';
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://raheva.com/api';

function TranscriptionPlayground({ onConnect }: { onConnect: (connect: boolean) => void }) {
  const { localParticipant } = useLocalParticipant();
  const roomState = useConnectionState();

  useEffect(() => {
    if (roomState === ConnectionState.Connected) {
      localParticipant.setMicrophoneEnabled(true);
    }
  }, [localParticipant, roomState]);

  // Get microphone track for volume visualization
  const micTrack = localParticipant.getTrackPublication(Track.Source.Microphone);
  const localMultibandVolume = useMultibandTrackVolume(
    micTrack?.track as LocalAudioTrack | undefined,
    9
  );

  const isLoading = roomState === ConnectionState.Connecting;
  const isActive = !isLoading && roomState !== ConnectionState.Disconnected;

  return (
    <div className="flex flex-col h-full w-full">
      {/* Transcription Display */}
      <div className="flex-1 bg-gray-900 text-white overflow-hidden">
        <Typewriter typingSpeed={30} />
      </div>

      {/* Control Panel */}
      <div className="relative bg-gray-800 py-8">
        <div className="w-full">
          <AnimatePresence>
            {!isActive ? (
              <motion.div
                className="flex justify-center"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                transition={{
                  type: 'spring',
                  stiffness: 260,
                  damping: 20,
                }}
              >
                <button
                  className={`px-8 py-4 text-lg font-semibold rounded-lg transition-all ${
                    isLoading
                      ? 'bg-gray-600 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                  onClick={() => onConnect(roomState === ConnectionState.Disconnected)}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Connecting...
                    </div>
                  ) : (
                    'Start Voice Transcription'
                  )}
                </button>
              </motion.div>
            ) : (
              <motion.div
                className="flex justify-center gap-4"
                initial={{ opacity: 0, y: 25 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 25 }}
                transition={{
                  type: 'spring',
                  stiffness: 260,
                  damping: 20,
                }}
              >
                <MicrophoneButton
                  localMultibandVolume={localMultibandVolume}
                  isSpaceBarEnabled={true}
                />
                <button
                  className="flex items-center justify-center w-16 h-16 bg-red-500 hover:bg-red-600 rounded-full text-white transition-all"
                  onClick={() => onConnect(false)}
                  title="Disconnect"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M3 3l18 18M6 6L18 18" />
                  </svg>
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default function TranscriptionPage() {
  const router = useRouter();
  const [shouldConnect, setShouldConnect] = useState(false);
  const [connectionDetails, setConnectionDetails] = useState<{
    wsUrl: string;
    token: string;
  }>({ wsUrl: '', token: '' });

  const handleConnect = useCallback(async (connect: boolean) => {
    if (connect) {
      try {
        // Generate random room and participant names
        const roomName = `transcription-room-${Math.floor(Math.random() * 10000)}`;
        const participantName = `guest-${Math.floor(Math.random() * 10000)}`;

        // Get token from backend
        const response = await fetch(`${apiUrl}/livekit/token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            room: roomName,
            name: participantName,
            identity: participantName,
          }),
        });

        const data = await response.json();

        if (!data.success) {
          throw new Error(data.error || 'Failed to get token');
        }

        setConnectionDetails({
          wsUrl: data.url || serverUrl,
          token: data.token,
        });
        setShouldConnect(true);
      } catch (error) {
        console.error('Failed to connect:', error);
        alert('Failed to connect. Please check your backend is running.');
      }
    } else {
      setShouldConnect(false);
    }
  }, []);

  const room = useMemo(() => {
    const r = new Room();
    r.on(RoomEvent.LocalTrackPublished, async (trackPublication) => {
      if (
        trackPublication.source === Track.Source.Microphone &&
        trackPublication.track instanceof LocalAudioTrack
      ) {
        try {
          const { KrispNoiseFilter, isKrispNoiseFilterSupported } = await import(
            '@livekit/krisp-noise-filter'
          );
          if (isKrispNoiseFilterSupported()) {
            await trackPublication.track?.setProcessor(KrispNoiseFilter());
          }
        } catch (e) {
          console.warn('Background noise reduction could not be enabled');
        }
      }
    });
    return r;
  }, []);

  return (
    <div className="h-screen w-full bg-gray-900">
      <div className="absolute top-4 right-4 z-10">
        <button
          onClick={() => router.push('/admin')}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          Back to Admin
        </button>
      </div>
      
      <LiveKitRoom
        className="h-full w-full"
        serverUrl={connectionDetails.wsUrl}
        token={connectionDetails.token}
        room={room}
        connect={shouldConnect}
        onError={console.error}
      >
        <TranscriptionPlayground onConnect={handleConnect} />
        <RoomAudioRenderer />
      </LiveKitRoom>
    </div>
  );
}
