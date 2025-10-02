import React, { useState, useRef, useCallback } from 'react';
import { useLocalParticipant, useRoomContext } from '@livekit/components-react';
import './BrowserRecorder.css';

interface BrowserRecorderProps {
  onRecordingComplete: (blob: Blob) => void;
}

export const BrowserRecorder: React.FC<BrowserRecorderProps> = ({ onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const room = useRoomContext();
  const { localParticipant } = useLocalParticipant();

  const startRecording = useCallback(async () => {
    try {
      // Get user media stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9'
      });

      chunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        onRecordingComplete(blob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Clear timer
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      console.log('🎥 Browser recording started');
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Could not start recording. Please allow camera/microphone access.');
    }
  }, [onRecordingComplete]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      console.log('🛑 Browser recording stopped');
    }
  }, [isRecording]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="browser-recorder">
      <div className="recording-controls">
        {!isRecording ? (
          <button 
            onClick={startRecording}
            className="btn primary"
          >
            🎬 Start Browser Recording
          </button>
        ) : (
          <div className="recording-active">
            <button 
              onClick={stopRecording}
              className="btn danger"
            >
              ⏹️ Stop Recording
            </button>
            <div className="recording-timer">
              🔴 REC {formatTime(recordingTime)}
            </div>
          </div>
        )}
      </div>

    </div>
  );
};
