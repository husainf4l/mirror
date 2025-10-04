# Mirror Transcription Feature

## Overview
Live transcriptions are now displayed below the main mirror text, showing what guests are saying in real-time.

## What Was Changed

### 1. LiveKitWrapper Component (`src/components/LiveKitWrapper.tsx`)
**Added:**
- `TranscriptionListener` component that listens to `RoomEvent.TranscriptionReceived`
- Automatic forwarding of transcription segments to parent component
- Console logging for debugging transcription events

**How it works:**
```tsx
room.on(RoomEvent.TranscriptionReceived, handleTranscription);
```

### 2. Mirror Component (`src/components/Mirror/index.tsx`)
**Added:**
- `transcriptions` state: Stores transcription segments as a dictionary `{[id: string]: segment}`
- `handleTranscriptionReceived()`: Callback that receives and stores new transcription segments
- `getTranscriptionText()`: Sorts and concatenates transcription segments into readable text
- Transcription display box: Shows below main mirror text with blur effect
- Toggle button: Shows/hides transcriptions (appears only when transcriptions exist)

**State Management:**
```tsx
const [showTranscript, setShowTranscript] = useState<boolean>(true);
const [transcriptions, setTranscriptions] = useState<{[id: string]: any}>({});
```

## Features

### 🎙️ Real-time Transcription Display
- Transcriptions appear automatically as Agent 2 processes speech
- Text displays below the main mirror message
- Sorted chronologically by `firstReceivedTime`

### 🎨 Beautiful Styling
- Black/60 opacity background with backdrop blur
- White border with 20% opacity
- Rounded corners (2xl)
- Shadow effects for depth
- Responsive text sizing (lg → xl → 2xl)
- Centered on screen
- Positioned at `bottom-32` to avoid controls

### 🔘 Toggle Control
- New button appears next to fullscreen button (right side)
- Icons: `fa-comment` (shown) / `fa-comment-slash` (hidden)
- Button only visible when transcriptions exist
- Smooth transitions and hover effects
- Same styling as fullscreen button

### 🧹 Auto-cleanup
- Transcriptions cleared on new connection
- No transcriptions persist between sessions

## UI Layout

```
┌─────────────────────────────────────────────────┐
│                                                 │
│              ✨ Main Mirror Text ✨             │
│        (Welcome message, guest name, etc.)      │
│                                                 │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │  💬 Live Transcription Display            │ │
│  │                                           │ │
│  │  "Hello, my name is Sarah and I'm so    │ │
│  │   excited to celebrate with you today!"  │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
                                    [💬] [⭐]
                              (transcript)(fullscreen)
```

## How It Works

### 1. Agent 2 Processing
```
Guest speaks → Whisper STT → Text transcription
                                    ↓
                        GPT-4o processes text
                                    ↓
                        OpenAI TTS generates response
                                    ↓
                        Transcription sent via LiveKit
```

### 2. Frontend Flow
```
LiveKit Room → TranscriptionReceived event
                        ↓
            handleTranscriptionReceived()
                        ↓
            Updates transcriptions state
                        ↓
            getTranscriptionText() sorts & joins
                        ↓
            Renders in transcription box
```

### 3. Data Structure
```typescript
// Transcription segment from LiveKit
{
  id: "seg_12345",
  text: "Hello everyone",
  firstReceivedTime: 1696435200000,
  final: true,
  language: "en"
}

// Stored in state as:
transcriptions = {
  "seg_12345": { /* segment data */ },
  "seg_12346": { /* segment data */ },
  // ...
}
```

## Testing

### Manual Test Steps
1. **Start Agent 2**: `cd agent2 && python agent.py dev`
2. **Start Frontend**: `cd mirror-front && npm start`
3. **Open Mirror**: Navigate to `/mirror` route
4. **Speak**: Say "Mirror mirror"
5. **Watch**: Transcription appears below main text
6. **Toggle**: Click 💬 button to hide/show

### Expected Behavior
- ✅ Transcriptions appear after ~2-3 seconds of speaking
- ✅ Text updates in real-time as more speech is processed
- ✅ Multiple sentences accumulate (space-separated)
- ✅ Toggle button appears when transcriptions exist
- ✅ Toggle button hides/shows transcription box
- ✅ New connection clears old transcriptions

### Console Logs to Watch For
```
🎙️ LiveKitWrapper: Transcription received: [...]
📝 Transcription segments received: [...]
```

## Customization

### Change Transcription Position
```tsx
// In Mirror/index.tsx
<div className="fixed bottom-32 left-1/2 ...">
//                    ↑
//              Change this value
```

### Change Box Styling
```tsx
<div className="bg-black/60 backdrop-blur-md border border-white/20 ...">
//               ↑ opacity      ↑ blur amount   ↑ border opacity
```

### Change Text Styling
```tsx
<div className="text-white/90 text-lg md:text-xl lg:text-2xl ...">
//               ↑ opacity     ↑ responsive sizing
```

### Hide Toggle Button
```tsx
// Remove or comment out the transcript toggle button section
{/* Transcript toggle button */}
```

### Always Show Transcriptions (No Toggle)
```tsx
// Change showTranscript condition
{Object.keys(transcriptions).length > 0 && (
  // Remove: showTranscript &&
```

## Troubleshooting

### Transcriptions Not Appearing
1. **Check Agent 2 is running**
   ```bash
   cd agent2 && python agent.py dev
   ```
2. **Verify connection logs**
   - Look for: "Agent 2 starting, connecting to room"
   - Check: "registered worker AW_..."

3. **Check browser console**
   - Should see: "🎙️ LiveKitWrapper: Transcription received"
   - If missing, Agent 2 may not be sending transcriptions

4. **Verify LiveKit connection**
   - Look for: "✨ Wedding mirror connected to room"
   - Check token generation succeeded

### Transcriptions Delayed
- Normal latency is 2-3 seconds for:
  - Speech detection (VAD)
  - Whisper processing
  - Network transmission
  - LLM response generation

### Toggle Button Not Showing
- Button only appears when `Object.keys(transcriptions).length > 0`
- Speak for a few seconds to generate transcriptions
- Check console for transcription received events

### Old Transcriptions Persisting
- Should clear automatically on new connection
- Manually clear by disconnecting and reconnecting
- Check `setTranscriptions({})` is called in `onConnected`

## Future Enhancements

### Potential Improvements
1. **Typewriter Effect**: Animate character-by-character
2. **Fade In/Out**: Smooth appearance of new segments
3. **Auto-hide**: Hide after X seconds of silence
4. **Highlight Latest**: Different styling for most recent segment
5. **Export**: Save transcription to file
6. **Search**: Filter/search through transcriptions
7. **Language Detection**: Show detected language badge
8. **Speaker Labels**: Show who is speaking (if available)

### Performance Optimizations
1. **Limit Storage**: Keep only last N segments
2. **Virtual Scrolling**: If many segments
3. **Debounce Updates**: Reduce re-renders
4. **Memoization**: Cache sorted text

## Related Files

- `/src/components/LiveKitWrapper.tsx` - Transcription listener
- `/src/components/Mirror/index.tsx` - Main integration
- `/src/components/Mirror/LiveKitConnection.tsx` - LiveKit connection wrapper
- `/agent2/agent.py` - Agent 2 that generates transcriptions
- `/src/hooks/useTranscriber.ts` - Reusable transcription hook (alternative approach)

## Technical Notes

### Why Dictionary Instead of Array?
```typescript
// Dictionary: O(1) lookups and updates
transcriptions[segment.id] = segment;

// Array: O(n) to find and update
const index = transcriptions.findIndex(t => t.id === segment.id);
```

### Why firstReceivedTime?
- Segments may arrive out of order
- Need chronological sorting for readable text
- `firstReceivedTime` provides stable ordering

### Why Separate Toggle State?
- User preference persists during session
- Can hide temporarily without losing data
- Cleaner UX than destroying/recreating box

---

## Summary

✅ **Live transcriptions now display below mirror text**
✅ **Toggle button to show/hide transcriptions**
✅ **Automatic cleanup on new connection**
✅ **Beautiful blur effect styling**
✅ **Real-time updates as speech is processed**

The transcription feature seamlessly integrates with the existing mirror display, providing guests and operators with live visibility into what the AI agent is hearing and responding to.
