# Mirror Component Refactoring

## Overview
The Mirror page has been refactored from a single large component into multiple smaller, manageable components for better organization and maintainability.

## New Component Structure

```
livekit-react/src/components/Mirror/
├── index.tsx                    # Main Mirror component (orchestrator)
├── Mirror.css                   # Main page styles
├── MirrorDisplay.tsx           # Text display and stars
├── MirrorDisplay.css
├── ConnectionStatus.tsx        # Connection indicator (🔗/⚠️)
├── ConnectionStatus.css
├── RotationControl.tsx         # Rotation button (🔄)
├── RotationControl.css
├── VideoControls.tsx           # Manual connection overlay
├── VideoControls.css
├── LiveKitConnection.tsx       # Hidden LiveKit wrapper
└── LiveKitConnection.css
```

## Component Responsibilities

### 1. **index.tsx** (Main Orchestrator)
- **Purpose:** Main component that manages all state and logic
- **Responsibilities:**
  - SSE connection management
  - LiveKit token management
  - Auto-connect logic
  - Permission handling
  - State management for all child components
- **Props:** None (root component)

### 2. **MirrorDisplay.tsx**
- **Purpose:** Display the mirror text and twinkling stars
- **Responsibilities:**
  - Render mirror text with HTML formatting
  - Display 8 animated stars
- **Props:**
  - `mirrorText: string` - HTML formatted text to display

### 3. **ConnectionStatus.tsx**
- **Purpose:** Show SSE connection status indicator
- **Responsibilities:**
  - Display connection icon (🔗 or ⚠️)
  - Pulse animation when disconnected
- **Props:**
  - `connected: boolean` - Connection status

### 4. **RotationControl.tsx**
- **Purpose:** Button to rotate the entire display
- **Responsibilities:**
  - Render rotation button
  - Handle rotation click
  - Show current rotation in tooltip
- **Props:**
  - `rotation: number` - Current rotation angle (0, 90, 180, 270)
  - `onRotate: () => void` - Callback when button clicked

### 5. **VideoControls.tsx**
- **Purpose:** Manual connection controls overlay
- **Responsibilities:**
  - Show/hide connection card
  - Display permission status
  - Show error messages
  - Connect button
- **Props:**
  - `isConnected: boolean`
  - `showControls: boolean`
  - `loading: boolean`
  - `error: string`
  - `permissionError: string`
  - `permissions: { camera: string, microphone: string }`
  - `onToggleControls: () => void`
  - `onConnect: () => void`

### 6. **LiveKitConnection.tsx**
- **Purpose:** Hidden LiveKit wrapper for agent connection
- **Responsibilities:**
  - Wrap LiveKitWrapper component
  - Hide video from user (agent can see)
  - Handle connection callbacks
- **Props:**
  - `token: string`
  - `serverUrl: string`
  - `audioEnabled: boolean`
  - `videoEnabled: boolean`
  - `onConnected: () => void`
  - `onDisconnected: () => void`

## Benefits of Refactoring

### 1. **Better Organization**
- Each component has a single responsibility
- Easy to find and modify specific functionality
- Clear separation of concerns

### 2. **Improved Maintainability**
- Changes to one component don't affect others
- Easier to debug issues
- Simpler unit testing

### 3. **Code Reusability**
- Components can be reused in other parts of the app
- Easier to share components across projects

### 4. **Better Performance**
- Components only re-render when their props change
- More granular control over updates

### 5. **Easier Collaboration**
- Multiple developers can work on different components
- Clear interfaces between components
- Less merge conflicts

## Usage Example

```tsx
import Mirror from './components/Mirror';

// In your route
<Route path="/mirror" element={<Mirror />} />
```

The new structure is backward compatible - you use it exactly the same way as before!

## File Locations

### Old Structure (Single File)
```
livekit-react/src/components/
├── Mirror.tsx (400+ lines)
└── Mirror.css (500+ lines)
```

### New Structure (Multiple Files)
```
livekit-react/src/components/Mirror/
├── index.tsx (250 lines - main logic)
├── Mirror.css (20 lines - page layout)
├── MirrorDisplay.tsx (30 lines)
├── MirrorDisplay.css (80 lines)
├── ConnectionStatus.tsx (15 lines)
├── ConnectionStatus.css (25 lines)
├── RotationControl.tsx (20 lines)
├── RotationControl.css (45 lines)
├── VideoControls.tsx (70 lines)
├── VideoControls.css (80 lines)
├── LiveKitConnection.tsx (30 lines)
└── LiveKitConnection.css (10 lines)
```

## Migration Notes

✅ **No changes needed in App.tsx** - Import path `'./components/Mirror'` works automatically with the new `index.tsx`

✅ **All functionality preserved** - SSE, LiveKit, rotation, permissions all work the same

✅ **Styling maintained** - All CSS extracted to component-specific files

## Next Steps

You can now:
1. Easily modify individual components without affecting others
2. Add new features by creating new components
3. Test components independently
4. Share components across different pages if needed

## Example: Adding a New Feature

Want to add a volume control? Just create:
```tsx
// VolumeControl.tsx
interface VolumeControlProps {
  volume: number;
  onVolumeChange: (volume: number) => void;
}

const VolumeControl: React.FC<VolumeControlProps> = ({ volume, onVolumeChange }) => {
  // Component implementation
};
```

Then import and use in `index.tsx`:
```tsx
import VolumeControl from './VolumeControl';

// In the component
<VolumeControl volume={volume} onVolumeChange={setVolume} />
```

Much easier than modifying a 400+ line file! 🎉
