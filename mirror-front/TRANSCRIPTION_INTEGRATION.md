# Transcription Feature Integration

## Overview
The transcription feature has been successfully integrated from `transcription-frontend-groq` into `mirror-front`. This provides real-time voice-to-text transcription with a beautiful typewriter effect display.

## Files Added

### Hooks
- **`src/hooks/useTranscriber.ts`**: Manages LiveKit transcription segments via `RoomEvent.TranscriptionReceived`
- **`src/hooks/useTrackVolume.ts`**: Provides multiband audio volume visualization for microphone input

### Components
- **`src/components/Transcription/Typewriter.tsx`**: Displays transcriptions with character-by-character typing animation
- **`src/components/Transcription/MicrophoneButton.tsx`**: Interactive microphone control with volume visualization and spacebar hotkey support

### Pages
- **`src/app/(protected)/transcription/page.tsx`**: New transcription page with full UI (accessible at `/transcription`)

## Features

### 🎙️ Real-time Transcription
- Connects to Agent 2 (Standard Pipeline: Whisper → GPT-4o → TTS)
- Receives live transcription segments from LiveKit
- Displays transcriptions with smooth typewriter effect

### 🎨 Visual Feedback
- Multiband volume visualizer on microphone button
- Pulsing animation based on audio input level
- Connection state indicators (Connected/Connecting/Disconnected)
- Smooth transitions with Framer Motion animations

### ⌨️ Keyboard Controls
- **Space Bar**: Hold to talk (push-to-talk mode)
- Configurable via `isSpaceBarEnabled` prop

### 🔊 Audio Enhancement
- Krisp noise cancellation automatically applied when available
- Background noise reduction for clearer transcriptions

## Usage

### Accessing the Transcription Page
1. Navigate to `/transcription` (requires authentication)
2. Click "Start Voice Transcription" to connect
3. Grant microphone permissions when prompted
4. Start speaking - transcriptions will appear in real-time

### Integration in Other Pages
You can integrate transcription components anywhere in your app:

\`\`\`tsx
import { Typewriter } from '@/components/Transcription/Typewriter';
import { MicrophoneButton } from '@/components/Transcription/MicrophoneButton';
import { useTranscriber } from '@/hooks/useTranscriber';

function MyComponent() {
  const { transcriptions, state } = useTranscriber();
  
  return (
    <div>
      <Typewriter typingSpeed={30} />
      {/* Your other components */}
    </div>
  );
}
\`\`\`

## Backend Configuration

The transcription feature connects to your backend at:
- **API URL**: `https://raheva.com/api` (configurable via `NEXT_PUBLIC_API_URL`)
- **LiveKit WebSocket**: `wss://widdai-aphl2lb9.livekit.cloud` (configurable via `NEXT_PUBLIC_LIVEKIT_URL`)
- **Token Endpoint**: `POST /livekit/token`

### Token Request Format
\`\`\`json
{
  "room": "transcription-room-1234",
  "name": "guest-1234",
  "identity": "guest-1234"
}
\`\`\`

### Token Response Format
\`\`\`json
{
  "success": true,
  "token": "eyJhbGc...",
  "url": "wss://widdai-aphl2lb9.livekit.cloud",
  "room": "transcription-room-1234",
  "identity": "guest-1234"
}
\`\`\`

## Dependencies Added
- **framer-motion**: Smooth animations and transitions
- **@livekit/krisp-noise-filter**: Background noise cancellation

## Component Props

### Typewriter
\`\`\`tsx
interface TypewriterProps {
  typingSpeed?: number; // Character delay in ms (default: 50)
}
\`\`\`

### MicrophoneButton
\`\`\`tsx
interface MicrophoneButtonProps {
  localMultibandVolume: Float32Array; // Audio volume bands for visualization
  isSpaceBarEnabled?: boolean; // Enable push-to-talk mode (default: false)
}
\`\`\`

## Architecture

### Data Flow
1. User speaks into microphone
2. Audio sent to LiveKit room
3. Agent 2 (running on backend) processes audio:
   - Whisper: Speech → Text
   - GPT-4o: Generate response
   - OpenAI TTS: Text → Speech
4. Transcription segments broadcast via `RoomEvent.TranscriptionReceived`
5. `useTranscriber` hook captures segments
6. Typewriter component displays with animation

### State Management
- **Connection State**: Managed by LiveKit's `useConnectionState` hook
- **Transcription State**: Stored in `useTranscriber` hook as dictionary keyed by segment ID
- **Audio State**: Local microphone mute/unmute handled by LiveKit participant API

## Styling

The components use Tailwind CSS classes. Key styles:
- Dark theme (`bg-gray-900`, `text-white`)
- Blue accent colors for active states (`bg-blue-500`)
- Red accent for muted/disconnect states (`bg-red-500`)
- Smooth transitions and animations

## Troubleshooting

### No transcriptions appearing
- Check that Agent 2 is running (`agent2/agent.py`)
- Verify backend is accessible at `https://raheva.com/api`
- Check browser console for connection errors
- Ensure microphone permissions are granted

### Audio not working
- Verify microphone is not muted in browser
- Check that LocalParticipant has microphone track published
- Verify Krisp noise filter loaded successfully (check console)

### Connection failures
- Verify LiveKit token endpoint returns valid token
- Check LiveKit WebSocket URL is correct
- Ensure network allows WebSocket connections

## Next Steps

### Integration Options
1. **Existing LiveKit Page**: Add transcription display to `/livekit` page
2. **Mirror Page**: Show transcriptions during mirror interactions
3. **Admin Dashboard**: Monitor all transcriptions in real-time

### Example: Adding to LiveKit Page
\`\`\`tsx
// In /app/(protected)/livekit/page.tsx
import { Typewriter } from '@/components/Transcription/Typewriter';

export default function LiveKitPage() {
  return (
    <div>
      {/* Existing LiveKit viewer */}
      <LiveKitRoom>
        {/* ... */}
      </LiveKitRoom>
      
      {/* Add transcription display */}
      <div className="h-64 border-t border-gray-700">
        <Typewriter typingSpeed={30} />
      </div>
    </div>
  );
}
\`\`\`

## Testing

To test the transcription feature:
1. Start Agent 2: `cd agent2 && python agent.py dev`
2. Start React dev server: `cd mirror-front && npm start`
3. Navigate to `http://localhost:3000/transcription`
4. Click "Start Voice Transcription"
5. Speak into your microphone
6. Watch transcriptions appear with typewriter effect

## API Reference

### useTranscriber Hook
\`\`\`tsx
const { state, transcriptions } = useTranscriber();
// state: ConnectionState (Connected, Connecting, Disconnected)
// transcriptions: { [id: string]: TranscriptionSegment }
\`\`\`

### useMultibandTrackVolume Hook
\`\`\`tsx
const volumes = useMultibandTrackVolume(track, bands);
// track: LocalAudioTrack | undefined
// bands: number of frequency bands to analyze
// Returns: Float32Array of volume levels (0.0 - 1.0)
\`\`\`

## Performance Considerations

- Typewriter animation speed configurable for different use cases
- Volume visualization updates at ~60 FPS using requestAnimationFrame
- Transcription segments deduplicated by ID
- Auto-scroll to latest transcription with smooth behavior

## Security

- All connections use WSS (WebSocket Secure)
- Tokens generated server-side with expiration
- Microphone access requires explicit user permission
- Protected routes require authentication

---

For more information about the agents, see:
- `AGENT_REPORT.md` - Comprehensive agent architecture documentation
- `AGENTS_OVERVIEW.md` - Dual agent system overview
- `agent2/README.md` - Agent 2 specific documentation
