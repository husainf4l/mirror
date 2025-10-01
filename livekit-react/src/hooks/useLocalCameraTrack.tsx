import { TrackReferenceOrPlaceholder, useLocalParticipant } from "@livekit/components-react";
import { Track } from "livekit-client";
import { useMemo } from "react";

export default function useLocalCameraTrack() {
  const { cameraTrack, localParticipant } = useLocalParticipant();

  const cameraTrackRef: TrackReferenceOrPlaceholder = useMemo(() => {
    if (cameraTrack) {
      return {
        participant: localParticipant,
        source: Track.Source.Camera,
        publication: cameraTrack,
      };
    } else {
      return {
        participant: localParticipant,
        source: Track.Source.Camera,
        publication: undefined,
      };
    }
  }, [localParticipant, cameraTrack]);

  return cameraTrackRef;
}
