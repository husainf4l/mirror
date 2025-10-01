import { useState, useEffect, useCallback } from 'react';
import { createLocalAudioTrack, createLocalVideoTrack, LocalAudioTrack, LocalVideoTrack } from 'livekit-client';

export interface DevicePermissions {
  camera: PermissionState;
  microphone: PermissionState;
}

export interface MediaDevices {
  audioInputs: MediaDeviceInfo[];
  videoInputs: MediaDeviceInfo[];
  audioOutputs: MediaDeviceInfo[];
}

export interface UseDevicePermissionsReturn {
  permissions: DevicePermissions;
  devices: MediaDevices;
  requestPermissions: () => Promise<void>;
  checkPermissions: () => Promise<void>;
  loading: boolean;
  error: string | null;
  localTracks: {
    audioTrack: LocalAudioTrack | null;
    videoTrack: LocalVideoTrack | null;
  };
}

export function useDevicePermissions(): UseDevicePermissionsReturn {
  const [permissions, setPermissions] = useState<DevicePermissions>({
    camera: 'prompt',
    microphone: 'prompt',
  });
  
  const [devices, setDevices] = useState<MediaDevices>({
    audioInputs: [],
    videoInputs: [],
    audioOutputs: [],
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localTracks, setLocalTracks] = useState<{
    audioTrack: LocalAudioTrack | null;
    videoTrack: LocalVideoTrack | null;
  }>({
    audioTrack: null,
    videoTrack: null,
  });

  const checkPermissions = useCallback(async () => {
    try {
      if (navigator.permissions) {
        const [cameraPermission, microphonePermission] = await Promise.all([
          navigator.permissions.query({ name: 'camera' as PermissionName }),
          navigator.permissions.query({ name: 'microphone' as PermissionName }),
        ]);

        setPermissions({
          camera: cameraPermission.state,
          microphone: microphonePermission.state,
        });
      }
    } catch (error) {
      console.warn('Permission API not supported:', error);
    }
  }, []);

  const enumerateDevices = useCallback(async () => {
    try {
      const deviceInfos = await navigator.mediaDevices.enumerateDevices();
      
      setDevices({
        audioInputs: deviceInfos.filter(device => device.kind === 'audioinput'),
        videoInputs: deviceInfos.filter(device => device.kind === 'videoinput'),
        audioOutputs: deviceInfos.filter(device => device.kind === 'audiooutput'),
      });
    } catch (error) {
      console.error('Error enumerating devices:', error);
      setError('Failed to enumerate media devices');
    }
  }, []);

  const requestPermissions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Clean up existing tracks
      if (localTracks.audioTrack) {
        localTracks.audioTrack.stop();
      }
      if (localTracks.videoTrack) {
        localTracks.videoTrack.stop();
      }

      // Request permissions by creating tracks
      const [audioTrack, videoTrack] = await Promise.all([
        createLocalAudioTrack({
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }).catch((err) => {
          console.warn('Audio track creation failed:', err);
          return null;
        }),
        createLocalVideoTrack({
          resolution: {
            width: 1280,
            height: 720,
          },
          facingMode: 'user',
        }).catch((err) => {
          console.warn('Video track creation failed:', err);
          return null;
        }),
      ]);

      setLocalTracks({
        audioTrack,
        videoTrack,
      });

      // Update permissions based on track creation success
      await checkPermissions();
      await enumerateDevices();

    } catch (error: any) {
      console.error('Permission request failed:', error);
      setError(error.message || 'Failed to access media devices');
    } finally {
      setLoading(false);
    }
  }, [checkPermissions, enumerateDevices, localTracks]);

  useEffect(() => {
    // Initial check
    checkPermissions();
    enumerateDevices();

    // Listen for device changes
    const handleDeviceChange = () => {
      enumerateDevices();
    };

    navigator.mediaDevices.addEventListener('devicechange', handleDeviceChange);

    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', handleDeviceChange);
      
      // Clean up tracks on unmount
      if (localTracks.audioTrack) {
        localTracks.audioTrack.stop();
      }
      if (localTracks.videoTrack) {
        localTracks.videoTrack.stop();
      }
    };
  }, [checkPermissions, enumerateDevices]);

  return {
    permissions,
    devices,
    requestPermissions,
    checkPermissions,
    loading,
    error,
    localTracks,
  };
}
