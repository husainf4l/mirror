import { useEffect, useState, useRef } from "react";
import { AudioTrack } from "livekit-client";

export function useMultibandTrackVolume(
  track: AudioTrack | undefined,
  bands: number
): Float32Array {
  const [volumes, setVolumes] = useState<Float32Array>(
    new Float32Array(bands)
  );
  const animationFrameRef = useRef<number | undefined>(undefined);
  const analyserRef = useRef<AnalyserNode | undefined>(undefined);
  const dataArrayRef = useRef<Uint8Array | undefined>(undefined);

  useEffect(() => {
    if (!track) {
      setVolumes(new Float32Array(bands));
      return;
    }

    const mediaStream = new MediaStream([track.mediaStreamTrack]);
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const microphone = audioContext.createMediaStreamSource(mediaStream);

    analyser.smoothingTimeConstant = 0.8;
    analyser.fftSize = 1024;

    microphone.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    analyserRef.current = analyser;
    dataArrayRef.current = dataArray;

    const updateVolume = () => {
      if (!analyserRef.current || !dataArrayRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArrayRef.current as any);

      const bufferLength = dataArrayRef.current.length;
      const bandWidth = Math.floor(bufferLength / bands);
      const newVolumes = new Float32Array(bands);

      for (let i = 0; i < bands; i++) {
        let sum = 0;
        const start = i * bandWidth;
        const end = start + bandWidth;

        for (let j = start; j < end; j++) {
          sum += dataArrayRef.current[j];
        }

        newVolumes[i] = sum / bandWidth / 255;
      }

      setVolumes(newVolumes);
      animationFrameRef.current = requestAnimationFrame(updateVolume);
    };

    updateVolume();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      microphone.disconnect();
      analyser.disconnect();
      audioContext.close();
    };
  }, [track, bands]);

  return volumes;
}
