'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useState } from 'react';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StatusType {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

interface VideoRecording {
  id: number;
  room_id: string;
  video_url: string;
  presigned_url?: string;
  guest_name?: string;
  guest_relation?: string;
  processing_status: string;
  created_at: string;
  duration_seconds?: number;
  file_size_bytes?: number;
}

export default function AdminPage() {
  const { logout } = useAuth();
  const [customText, setCustomText] = useState<string>('');
  const [status, setStatus] = useState<StatusType>({ message: 'Ready to control the mirror ✨', type: 'info' });
  const [loading, setLoading] = useState<boolean>(false);
  const [rooms, setRooms] = useState<string[]>([]);
  const [roomsLoading, setRoomsLoading] = useState<boolean>(false);
  const [videos, setVideos] = useState<VideoRecording[]>([]);
  const [videosLoading, setVideosLoading] = useState<boolean>(false);
  const [showVideoDetails, setShowVideoDetails] = useState<boolean>(false);

  const messages = {
    welcome: '<span class="line fancy">Welcome</span><span class="line script">to the magical union of</span><span class="line fancy">Motasem & Hala</span><span class="line script">Wedding</span>',
    compliment: '<span class="line script">You look</span><span class="line fancy">Absolutely Radiant</span><span class="line script">tonight</span>',
    love: '<span class="line script">Two hearts</span><span class="line fancy">One Love</span><span class="line script">Forever Bound</span>',
    ceremony: '<span class="line fancy">The Ceremony</span><span class="line script">begins soon</span><span class="line fancy">Please be seated</span>',
    reception: '<span class="line fancy">Reception</span><span class="line script">Let the celebration</span><span class="line fancy">Begin!</span>',
    photos: '<span class="line fancy">Smile!</span><span class="line script">You are</span><span class="line fancy">Picture Perfect</span>',
    dancing: '<span class="line script">The dance floor</span><span class="line fancy">Awaits You</span><span class="line script">Let\'s celebrate!</span>'
  };

  const updateStatus = (message: string, type: StatusType['type']) => {
    setStatus({ message, type });
    setTimeout(() => {
      setStatus({ message: 'Ready to control the mirror ✨', type: 'info' });
    }, 3000);
  };

  const sendCommand = async (command: keyof typeof messages | 'reset') => {
    try {
      setLoading(true);
      updateStatus('Sending command...', 'info');
      
      let response: Response;
      
      if (command === 'reset') {
        response = await fetch(`${apiUrl}/api/reset`, {
          method: 'POST',
          credentials: 'include'
        });
      } else {
        response = await fetch(`${apiUrl}/api/update-text`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            text: messages[command]
          })
        });
      }
      
      if (response.ok) {
        updateStatus('✅ Command sent successfully!', 'success');
      } else {
        throw new Error('Failed to send command');
      }
    } catch (error) {
      updateStatus('❌ Error sending command', 'error');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendCustomMessage = async () => {
    if (!customText.trim()) {
      updateStatus('⚠️ Please enter a custom message', 'warning');
      return;
    }

    try {
      setLoading(true);
      updateStatus('Sending custom message...', 'info');
      
      const response = await fetch(`${apiUrl}/api/update-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          text: customText
        })
      });
      
      if (response.ok) {
        updateStatus('✅ Custom message sent!', 'success');
        setCustomText('');
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      updateStatus('❌ Error sending message', 'error');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const listRooms = async () => {
    try {
      setRoomsLoading(true);
      updateStatus('Loading rooms...', 'info');
      
      const response = await fetch(`${apiUrl}/api/rooms`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setRooms(data.rooms);
          updateStatus(`✅ Found ${data.count} active rooms`, 'success');
        } else {
          throw new Error(data.error || 'Failed to fetch rooms');
        }
      } else {
        throw new Error('Failed to fetch rooms');
      }
    } catch (error) {
      updateStatus('❌ Error loading rooms', 'error');
      console.error('Error:', error);
      setRooms([]);
    } finally {
      setRoomsLoading(false);
    }
  };

  const deleteAllRooms = async () => {
    if (!window.confirm('Are you sure you want to delete ALL LiveKit rooms? This action cannot be undone.')) {
      return;
    }

    try {
      setLoading(true);
      updateStatus('Deleting all rooms...', 'warning');
      
      const response = await fetch(`${apiUrl}/api/rooms`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          updateStatus(`✅ ${data.message}`, 'success');
          setRooms([]);
        } else {
          throw new Error(data.error || 'Failed to delete rooms');
        }
      } else {
        throw new Error('Failed to delete rooms');
      }
    } catch (error) {
      updateStatus('❌ Error deleting rooms', 'error');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const listVideos = async () => {
    try {
      setVideosLoading(true);
      updateStatus('Loading video recordings...', 'info');
      
      const response = await fetch(`${apiUrl}/api/videos`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setVideos(data.recordings);
          updateStatus(`✅ Found ${data.total} video recordings`, 'success');
        } else {
          throw new Error(data.error || 'Failed to fetch videos');
        }
      } else {
        throw new Error('Failed to fetch videos');
      }
    } catch (error) {
      updateStatus('❌ Error loading videos', 'error');
      console.error('Error:', error);
      setVideos([]);
    } finally {
      setVideosLoading(false);
    }
  };

  const refreshPresignedUrl = async (videoId: number) => {
    try {
      updateStatus('Refreshing video link...', 'info');
      
      const response = await fetch(`${apiUrl}/api/videos/${videoId}/refresh`, {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          updateStatus('✅ Video link refreshed', 'success');
          await listVideos();
        } else {
          throw new Error(data.error || 'Failed to refresh video link');
        }
      } else {
        throw new Error('Failed to refresh video link');
      }
    } catch (error) {
      updateStatus('❌ Error refreshing video link', 'error');
      console.error('Error:', error);
    }
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return 'Unknown';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return 'Unknown';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const viewRoom = async (roomName: string) => {
    try {
      updateStatus('Getting viewer access...', 'info');
      
      // Get viewer token for the room
      const response = await fetch(`${apiUrl}/api/livekit/viewer-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          room: roomName,
          name: 'Admin Viewer',
          identity: `admin-viewer-${Date.now()}`
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Navigate to the LiveKit viewer page (zoom-style) instead of mirror
          const viewerUrl = `/livekit?token=${encodeURIComponent(data.token)}&room=${encodeURIComponent(roomName)}&viewer=true`;
          window.open(viewerUrl, '_blank', 'noopener,noreferrer');
          updateStatus('✅ Viewer room opened!', 'success');
        } else {
          throw new Error(data.error || 'Failed to get viewer token');
        }
      } else {
        throw new Error('Failed to get viewer access');
      }
    } catch (error) {
      updateStatus('❌ Error accessing room', 'error');
      console.error('Error:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-6 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">⚙️ Admin Control Panel</h1>
              <p className="text-gray-600 mt-1">Wedding Mirror Management System</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Status Bar */}
        <div className="mb-6">
          <div className={`p-4 rounded-lg ${
            status.type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
            status.type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
            status.type === 'warning' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
            'bg-blue-100 text-blue-800 border border-blue-200'
          }`}>
            {status.message}
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button 
                onClick={() => sendCommand('reset')}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🔄 Reset to Default
              </button>
              <button 
                onClick={() => sendCommand('welcome')}
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                👋 Wedding Welcome
              </button>
              <button 
                onClick={() => sendCommand('compliment')}
                disabled={loading}
                className="w-full bg-pink-600 hover:bg-pink-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                ✨ Guest Compliment
              </button>
              <button 
                onClick={() => sendCommand('love')}
                disabled={loading}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                💕 Love Message
              </button>
            </div>
          </div>

          {/* Wedding Messages */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Wedding Messages</h3>
            <div className="space-y-2">
              <button 
                onClick={() => sendCommand('ceremony')}
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                💒 Ceremony Welcome
              </button>
              <button 
                onClick={() => sendCommand('reception')}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🎉 Reception Time
              </button>
              <button 
                onClick={() => sendCommand('photos')}
                disabled={loading}
                className="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                📸 Photo Booth Mode
              </button>
              <button 
                onClick={() => sendCommand('dancing')}
                disabled={loading}
                className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                💃 Dance Floor
              </button>
            </div>
          </div>

          {/* Custom Message */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Custom Message</h3>
            <textarea
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder="Enter your custom mirror message here...&#10;&#10;Use line breaks to separate lines."
              disabled={loading}
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <button 
              onClick={sendCustomMessage}
              disabled={loading || !customText.trim()}
              className="w-full mt-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              📝 Send Custom Message
            </button>
          </div>

          {/* LiveKit Room Management */}
          <div className="bg-white shadow rounded-lg p-6 md:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🏠 LiveKit Room Management</h3>
            <div className="flex gap-2 mb-4">
              <button 
                onClick={listRooms}
                disabled={roomsLoading || loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🔍 List Active Rooms
              </button>
              <button 
                onClick={deleteAllRooms}
                disabled={loading || roomsLoading}
                className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🗑️ Delete All Rooms
              </button>
            </div>
            
            {rooms.length > 0 && (
              <div className="border border-gray-200 rounded-lg p-4 max-h-64 overflow-y-auto">
                <strong className="text-gray-700">Active Rooms ({rooms.length})</strong>
                <div className="mt-3 space-y-2">
                  {rooms.map((room, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <span className="text-gray-700">🏠 {room}</span>
                      <button 
                        onClick={() => viewRoom(room)}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-xs font-medium transition-colors"
                      >
                        👁️ View Room
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {rooms.length === 0 && !roomsLoading && (
              <div className="text-center py-8 text-gray-500">
                No active rooms found
              </div>
            )}
          </div>

          {/* Video Recording Management */}
          <div className="bg-white shadow rounded-lg p-6 lg:col-span-3">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🎥 Video Recordings</h3>
            <div className="flex gap-2 mb-4">
              <button 
                onClick={listVideos}
                disabled={videosLoading || loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                {videosLoading ? '🔄 Loading...' : '🎥 Load Recordings'}
              </button>
              
              {videos.length > 0 && (
                <button 
                  onClick={() => setShowVideoDetails(!showVideoDetails)}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {showVideoDetails ? '📋 Hide Details' : '📋 Show Details'}
                </button>
              )}
            </div>
            
            {videos.length > 0 && (
              <div className="border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                <strong className="text-gray-700">Video Recordings ({videos.length})</strong>
                {showVideoDetails ? (
                  <div className="mt-3 space-y-3">
                    {videos.map((video) => (
                      <div key={video.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                        <div className="flex items-start justify-between mb-2">
                          <div className="font-semibold text-gray-900">
                            {video.guest_name ? `👤 ${video.guest_name}` : `🏠 ${video.room_id}`}
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            video.processing_status === 'completed' ? 'bg-green-100 text-green-800' :
                            video.processing_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {video.processing_status}
                          </span>
                        </div>
                        
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>📅 {new Date(video.created_at).toLocaleString()}</div>
                          {video.guest_relation && <div>👥 {video.guest_relation}</div>}
                          <div>⏱️ {formatDuration(video.duration_seconds)} • 📁 {formatFileSize(video.file_size_bytes)}</div>
                        </div>
                        
                        <div className="flex gap-2 mt-3">
                          {video.video_url && (
                            <button 
                              onClick={() => window.open(video.video_url, '_blank')}
                              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium transition-colors"
                            >
                              🔗 Direct Link
                            </button>
                          )}
                          {video.presigned_url && (
                            <button 
                              onClick={() => window.open(video.presigned_url!, '_blank')}
                              className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-xs font-medium transition-colors"
                            >
                              ⏰ Presigned Link
                            </button>
                          )}
                          <button 
                            onClick={() => refreshPresignedUrl(video.id)}
                            disabled={loading}
                            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-xs font-medium transition-colors"
                          >
                            🔄 Refresh
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ul className="mt-3 space-y-2">
                    {videos.map((video) => (
                      <li key={video.id} className="text-sm text-gray-700 py-2 border-b border-gray-200 last:border-b-0">
                        <strong>{video.guest_name || video.room_id}</strong> • 
                        {new Date(video.created_at).toLocaleDateString()} • 
                        <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                          video.processing_status === 'completed' ? 'bg-green-100 text-green-800' :
                          video.processing_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {video.processing_status}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            
            {videos.length === 0 && !videosLoading && (
              <div className="text-center py-8 text-gray-500">
                No video recordings found
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}