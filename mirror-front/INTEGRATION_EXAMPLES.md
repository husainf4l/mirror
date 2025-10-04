/**
 * Transcription Feature - Quick Integration Guide
 * 
 * This file provides examples for integrating transcription features
 * into existing pages in the mirror-front application.
 */

// =============================================================================
// EXAMPLE 1: Add Transcription Display to Existing LiveKit Page
// =============================================================================

/*
// File: mirror-front/src/app/(protected)/livekit/page.tsx

'use client';

import { useState } from 'react';
import { LiveKitRoom, GridLayout, ParticipantTile, ControlBar } from '@livekit/components-react';
import { Typewriter } from '@/components/Transcription/Typewriter';

export default function LiveKitPage() {
  const [token, setToken] = useState('');
  
  return (
    <div className="h-screen flex flex-col">
      {/* Video Display Area - 70% */}
      <div className="flex-[7] bg-gray-900">
        <LiveKitRoom
          serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
          token={token}
          connect={!!token}
        >
          <GridLayout>
            <ParticipantTile />
          </GridLayout>
          <ControlBar />
        </LiveKitRoom>
      </div>
      
      {/* Transcription Display Area - 30% */}
      <div className="flex-[3] bg-gray-800 border-t border-gray-700">
        <div className="h-full">
          <div className="px-4 py-2 border-b border-gray-700">
            <h2 className="text-white font-semibold">Live Transcription</h2>
          </div>
          <div className="h-[calc(100%-48px)]">
            <Typewriter typingSpeed={30} />
          </div>
        </div>
      </div>
    </div>
  );
}
*/

// =============================================================================
// EXAMPLE 2: Add Transcription to Mirror Page
// =============================================================================

/*
// File: mirror-front/src/app/(protected)/mirror/page.tsx

'use client';

import { LiveKitRoom } from '@livekit/components-react';
import { Typewriter } from '@/components/Transcription/Typewriter';
import { MirrorDisplay } from '@/components/Mirror';

export default function MirrorPage() {
  return (
    <div className="h-screen grid grid-cols-2">
      {/* Left Side - Mirror Display */}
      <div className="bg-black">
        <MirrorDisplay />
      </div>
      
      {/* Right Side - Transcription Display */}
      <div className="bg-gray-900">
        <LiveKitRoom
          serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
          token={token}
          connect={!!token}
        >
          <div className="h-full flex flex-col">
            <div className="flex-1">
              <Typewriter typingSpeed={30} />
            </div>
          </div>
        </LiveKitRoom>
      </div>
    </div>
  );
}
*/

// =============================================================================
// EXAMPLE 3: Floating Transcription Overlay
// =============================================================================

/*
// File: mirror-front/src/components/TranscriptionOverlay.tsx

'use client';

import { useState } from 'react';
import { Typewriter } from '@/components/Transcription/Typewriter';

export function TranscriptionOverlay() {
  const [isMinimized, setIsMinimized] = useState(false);
  
  return (
    <div className={`
      fixed bottom-4 right-4 bg-gray-900 border border-gray-700 rounded-lg shadow-2xl
      transition-all duration-300
      ${isMinimized ? 'w-64 h-12' : 'w-96 h-64'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <h3 className="text-white font-semibold">Transcription</h3>
        <button
          onClick={() => setIsMinimized(!isMinimized)}
          className="text-gray-400 hover:text-white"
        >
          {isMinimized ? '▲' : '▼'}
        </button>
      </div>
      
      {/* Content */}
      {!isMinimized && (
        <div className="h-[calc(100%-44px)]">
          <Typewriter typingSpeed={30} />
        </div>
      )}
    </div>
  );
}
*/

// =============================================================================
// EXAMPLE 4: Custom Transcription Hook Usage
// =============================================================================

/*
// File: mirror-front/src/app/(protected)/custom/page.tsx

'use client';

import { useTranscriber } from '@/hooks/useTranscriber';
import { ConnectionState } from 'livekit-client';

export default function CustomPage() {
  const { state, transcriptions } = useTranscriber();
  
  // Access individual transcription segments
  const segments = Object.values(transcriptions);
  const fullText = segments
    .sort((a, b) => a.firstReceivedTime - b.firstReceivedTime)
    .map(s => s.text)
    .join(' ');
  
  return (
    <div>
      <div>Status: {state}</div>
      <div>Transcriptions: {segments.length}</div>
      <div>Full Text: {fullText}</div>
    </div>
  );
}
*/

// =============================================================================
// EXAMPLE 5: Transcription with Microphone Control
// =============================================================================

/*
// File: mirror-front/src/components/TranscriptionPanel.tsx

'use client';

import { useLocalParticipant } from '@livekit/components-react';
import { Track, LocalAudioTrack } from 'livekit-client';
import { Typewriter } from '@/components/Transcription/Typewriter';
import { MicrophoneButton } from '@/components/Transcription/MicrophoneButton';
import { useMultibandTrackVolume } from '@/hooks/useTrackVolume';

export function TranscriptionPanel() {
  const { localParticipant } = useLocalParticipant();
  
  // Get microphone track for volume visualization
  const micTrack = localParticipant.getTrackPublication(Track.Source.Microphone);
  const localMultibandVolume = useMultibandTrackVolume(
    micTrack?.track as LocalAudioTrack | undefined,
    9
  );
  
  return (
    <div className="flex flex-col h-full">
      {/* Transcription Display */}
      <div className="flex-1 overflow-hidden">
        <Typewriter typingSpeed={30} />
      </div>
      
      {/* Controls */}
      <div className="p-4 border-t border-gray-700 flex justify-center">
        <MicrophoneButton
          localMultibandVolume={localMultibandVolume}
          isSpaceBarEnabled={true}
        />
      </div>
    </div>
  );
}
*/

// =============================================================================
// EXAMPLE 6: Save Transcriptions to Database
// =============================================================================

/*
// File: mirror-front/src/hooks/useSaveTranscription.ts

import { useEffect } from 'react';
import { useTranscriber } from '@/hooks/useTranscriber';

export function useSaveTranscription(roomId: string) {
  const { transcriptions } = useTranscriber();
  
  useEffect(() => {
    // Save transcriptions to backend every 5 seconds
    const interval = setInterval(() => {
      if (Object.keys(transcriptions).length > 0) {
        fetch('/api/save-transcription', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            roomId,
            transcriptions: Object.values(transcriptions),
            timestamp: Date.now()
          })
        });
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [transcriptions, roomId]);
}

// Usage in component:
// useSaveTranscription('mirror-room-123');
*/

// =============================================================================
// EXAMPLE 7: Transcription Search and Filter
// =============================================================================

/*
// File: mirror-front/src/components/TranscriptionSearch.tsx

'use client';

import { useState, useMemo } from 'react';
import { useTranscriber } from '@/hooks/useTranscriber';

export function TranscriptionSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const { transcriptions } = useTranscriber();
  
  const filteredTranscriptions = useMemo(() => {
    if (!searchQuery) return Object.values(transcriptions);
    
    return Object.values(transcriptions).filter(segment =>
      segment.text.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [transcriptions, searchQuery]);
  
  return (
    <div>
      <input
        type="text"
        placeholder="Search transcriptions..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-4 py-2 bg-gray-800 text-white rounded"
      />
      
      <div className="mt-4">
        {filteredTranscriptions.map(segment => (
          <div key={segment.id} className="p-2 border-b border-gray-700">
            <div className="text-sm text-gray-400">
              {new Date(segment.firstReceivedTime).toLocaleTimeString()}
            </div>
            <div className="text-white">{segment.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
*/

// =============================================================================
// EXAMPLE 8: Export Transcriptions
// =============================================================================

/*
// File: mirror-front/src/utils/exportTranscriptions.ts

import { TranscriptionSegment } from 'livekit-client';

export function exportTranscriptionsAsText(
  transcriptions: { [id: string]: TranscriptionSegment },
  roomName: string
): void {
  const segments = Object.values(transcriptions)
    .sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
  
  const text = segments
    .map(s => `[${new Date(s.firstReceivedTime).toISOString()}] ${s.text}`)
    .join('\n');
  
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `transcription-${roomName}-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

export function exportTranscriptionsAsJSON(
  transcriptions: { [id: string]: TranscriptionSegment },
  roomName: string
): void {
  const data = {
    room: roomName,
    exportedAt: new Date().toISOString(),
    segments: Object.values(transcriptions).sort(
      (a, b) => a.firstReceivedTime - b.firstReceivedTime
    )
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json'
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `transcription-${roomName}-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
*/

// =============================================================================
// INTEGRATION CHECKLIST
// =============================================================================

/*
✅ Prerequisites:
- [ ] Agent 2 is running (cd agent2 && python agent.py dev)
- [ ] Backend is accessible at https://raheva.com/api
- [ ] LiveKit token endpoint working (POST /livekit/token)
- [ ] Environment variables configured

✅ Basic Integration:
- [ ] Import Typewriter component
- [ ] Wrap page in LiveKitRoom
- [ ] Add transcription display area
- [ ] Test connection and transcription

✅ Advanced Features:
- [ ] Add MicrophoneButton for control
- [ ] Implement volume visualization
- [ ] Add save/export functionality
- [ ] Style to match your design

✅ Testing:
- [ ] Test microphone permissions
- [ ] Verify transcriptions appear
- [ ] Check typewriter animation
- [ ] Test on mobile devices
- [ ] Verify performance
*/

export {};
