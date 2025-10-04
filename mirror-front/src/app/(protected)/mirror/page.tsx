'use client';

import dynamic from 'next/dynamic';

// Dynamically import Mirror component to avoid SSR issues with LiveKit
const Mirror = dynamic(() => import('@/components/Mirror'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center min-h-screen bg-black text-white">
      <div className="text-lg">Loading Mirror...</div>
    </div>
  ),
});

export default function MirrorPage() {
  return <Mirror />;
}