"use client";

import { useEffect, useState } from "react";
import { useLocalParticipant } from "@livekit/components-react";

interface MicrophoneButtonProps {
  localMultibandVolume: Float32Array;
  isSpaceBarEnabled?: boolean;
}

export function MicrophoneButton({
  localMultibandVolume,
  isSpaceBarEnabled = false,
}: MicrophoneButtonProps) {
  const { localParticipant } = useLocalParticipant();
  const [isMuted, setIsMuted] = useState(false);
  const [isSpacePressed, setIsSpacePressed] = useState(false);

  useEffect(() => {
    if (!isSpaceBarEnabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" && !isSpacePressed) {
        e.preventDefault();
        setIsSpacePressed(true);
        localParticipant.setMicrophoneEnabled(true);
        setIsMuted(false);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        setIsSpacePressed(false);
        localParticipant.setMicrophoneEnabled(false);
        setIsMuted(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, [isSpaceBarEnabled, isSpacePressed, localParticipant]);

  const toggleMicrophone = async () => {
    const newMutedState = !isMuted;
    await localParticipant.setMicrophoneEnabled(!newMutedState);
    setIsMuted(newMutedState);
  };

  // Calculate average volume for visualization
  const avgVolume = localMultibandVolume.reduce((a, b) => a + b, 0) / localMultibandVolume.length;

  return (
    <button
      onClick={toggleMicrophone}
      className={`relative flex items-center justify-center w-16 h-16 rounded-full transition-all ${
        isMuted
          ? "bg-red-500 hover:bg-red-600"
          : "bg-blue-500 hover:bg-blue-600"
      }`}
      title={isMuted ? "Unmute microphone" : "Mute microphone"}
    >
      <div
        className="absolute inset-0 rounded-full bg-white opacity-20"
        style={{
          transform: `scale(${1 + avgVolume * 0.5})`,
          transition: "transform 0.1s ease-out",
        }}
      />
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-white relative z-10"
      >
        {isMuted ? (
          <>
            <line x1="1" y1="1" x2="23" y2="23" />
            <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6" />
            <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </>
        ) : (
          <>
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </>
        )}
      </svg>
      {isSpaceBarEnabled && (
        <div className="absolute -bottom-8 text-xs text-gray-400">
          Hold Space
        </div>
      )}
    </button>
  );
}
