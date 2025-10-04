'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Room } from 'livekit-client';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  ControlBar,
  GridLayout,
  ParticipantTile,
  useTracks,
} from '@livekit/components-react';
import { Track } from 'livekit-client';
import '@livekit/components-styles';

const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || 'wss://widdai-aphl2lb9.livekit.cloud';
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LiveKitViewerPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [token, setToken] = useState<string>('');
  const [roomName, setRoomName] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [isViewerMode, setIsViewerMode] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const viewerToken = searchParams.get('token');
    const roomParam = searchParams.get('room');
    const viewerMode = searchParams.get('viewer') === 'true';

    if (viewerToken && roomParam) {
      setToken(viewerToken);
      setRoomName(roomParam);
      setUserName('Admin Viewer');
      setIsViewerMode(viewerMode);
    } else {
      setError('Missing required parameters (token or room)');
    }
  }, [searchParams]);

  const handleDisconnect = () => {
    router.push('/admin');
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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="bg-red-900 text-white p-6 rounded-lg max-w-md">
          <h2 className="text-xl font-bold mb-2">Error</h2>
          <p>{error}</p>
          <button
            onClick={() => router.push('/admin')}
            className="mt-4 bg-red-700 hover:bg-red-600 px-4 py-2 rounded"
          >
            Back to Admin
          </button>
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading room...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-white">
              {isViewerMode ? '👁️ Room Viewer' : '🎥 LiveKit Room'}
            </h1>
            <div className="flex items-center gap-3 text-sm text-gray-300">
              <span className="bg-gray-700 px-3 py-1 rounded-full">
                Room: {roomName}
              </span>
              <span className="bg-gray-700 px-3 py-1 rounded-full">
                User: {userName}
              </span>
              {isViewerMode && (
                <span className="bg-blue-600 text-white px-3 py-1 rounded-full font-semibold">
                  👁️ Viewer Mode
                </span>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {!isViewerMode && (
              <button
                onClick={resetMirror}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🪞 Reset Mirror
              </button>
            )}
            <button
              onClick={() => router.push('/admin')}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              ⚙️ Admin Panel
              </button>
            <button
              onClick={handleDisconnect}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              🚪 Leave Room
            </button>
          </div>
        </div>
      </div>

      {/* LiveKit Room */}
      <div className="h-[calc(100vh-80px)]">
        <LiveKitRoom
          token={token}
          serverUrl={serverUrl}
          connect={true}
          audio={!isViewerMode}
          video={!isViewerMode}
          onDisconnected={handleDisconnect}
          style={{ height: '100%' }}
        >
          <RoomContent isViewerMode={isViewerMode} />
        </LiveKitRoom>
      </div>
    </div>
  );
}

function RoomContent({ isViewerMode }: { isViewerMode: boolean }) {
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: true },
      { source: Track.Source.ScreenShare, withPlaceholder: false },
    ],
    { onlySubscribed: false }
  );

  return (
    <div className="h-full flex flex-col">
      {/* Participants Grid */}
      <div className="flex-1 overflow-hidden">
        <GridLayout tracks={tracks} style={{ height: '100%' }}>
          <ParticipantTile />
        </GridLayout>
      </div>

      {/* Audio Renderer */}
      <RoomAudioRenderer />

      {/* Control Bar - Only show if not in viewer mode */}
      {!isViewerMode && (
        <div className="bg-gray-800 border-t border-gray-700">
          <ControlBar />
        </div>
      )}

      {/* Viewer Mode Indicator */}
      {isViewerMode && (
        <div className="bg-gray-800 border-t border-gray-700 px-6 py-3">
          <div className="max-w-7xl mx-auto text-center text-gray-300 text-sm">
            👁️ You are viewing this room silently. Participants cannot see or hear you.
          </div>
        </div>
      )}
    </div>
  );
}
