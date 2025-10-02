import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Control.css';

// Do not add any redirect to mirror in this component. The ProtectedRoute handles authentication.

const apiUrl = process.env.REACT_APP_API_URL || '';

interface StatusType {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

interface RoomsResponse {
  success: boolean;
  rooms: string[];
  count: number;
  error?: string;
}

interface DeleteRoomsResponse {
  success: boolean;
  deleted_count: number;
  total_rooms?: number;
  message: string;
  error?: string;
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

interface VideosResponse {
  success: boolean;
  recordings: VideoRecording[];
  total: number;
  error?: string;
}

const Control: React.FC = () => {
  const navigate = useNavigate();
  const [customText, setCustomText] = useState<string>('');
  const [status, setStatus] = useState<StatusType>({ message: 'Ready to control the mirror ✨', type: 'info' });
  const [loading, setLoading] = useState<boolean>(false);
  const [rooms, setRooms] = useState<string[]>([]);
  const [roomsLoading, setRoomsLoading] = useState<boolean>(false);
  const [videos, setVideos] = useState<VideoRecording[]>([]);
  const [videosLoading, setVideosLoading] = useState<boolean>(false);
  const [showVideoDetails, setShowVideoDetails] = useState<boolean>(false);

  // Predefined messages
  const messages = {
    welcome: '<span class="line fancy">Welcome</span><span class="line script">to the magical union of</span><span class="line fancy">x & y</span><span class="line script">Wedding</span>',
    compliment: '<span class="line script">You look</span><span class="line fancy">Absolutely Radiant</span><span class="line script">tonight</span>',
    love: '<span class="line script">Two hearts</span><span class="line fancy">One Love</span><span class="line script">Forever Bound</span>',
    ceremony: '<span class="line fancy">The Ceremony</span><span class="line script">begins soon</span><span class="line fancy">Please be seated</span>',
    reception: '<span class="line fancy">Reception</span><span class="line script">Let the celebration</span><span class="line fancy">Begin!</span>',
    photos: '<span class="line fancy">Smile!</span><span class="line script">You are</span><span class="line fancy">Picture Perfect</span>',
    dancing: '<span class="line script">The dance floor</span><span class="line fancy">Awaits You</span><span class="line script">Let\'s celebrate!</span>'
  };

  const updateStatus = (message: string, type: StatusType['type']) => {
    setStatus({ message, type });
    
    // Auto-clear after 3 seconds
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
        await response.json(); // Response processed but not used
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

  const openWindow = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
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
        const data: RoomsResponse = await response.json();
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
        const data: DeleteRoomsResponse = await response.json();
        if (data.success) {
          updateStatus(`✅ ${data.message}`, 'success');
          setRooms([]); // Clear the rooms list
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
        const data: VideosResponse = await response.json();
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
          // Refresh the video list
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
          // Open the LiveKit room in viewer mode
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

  return (
    <div className="control-page">
      <div className="container">
        <div className="header">
          <h1>⚙️ Control Panel</h1>
          <p>Wedding Mirror Management System</p>
        </div>

        <div className="control-grid">
          {/* Navigation */}
          <div className="control-section">
            <h3 className="section-title">Navigation</h3>
            <button 
              className="btn primary" 
              onClick={() => openWindow('/livekit')}
              disabled={loading}
            >
              🎥 LiveKit Video Room
            </button>
            <button 
              className="btn" 
              onClick={() => openWindow('/mirror')}
              disabled={loading}
            >
              🪞 View Mirror Display
            </button>
            <button 
              className="btn" 
              onClick={() => navigate('/guests')}
              disabled={loading}
            >
              👥 Guest Management
            </button>
            <button 
              className="btn" 
              onClick={() => openWindow('/admin')}
              disabled={loading}
            >
              ⚙️ Admin Panel
            </button>
          </div>

          {/* Quick Actions */}
          <div className="control-section">
            <h3 className="section-title">Quick Actions</h3>
            <button 
              className="btn primary" 
              onClick={() => sendCommand('reset')}
              disabled={loading}
            >
              🔄 Reset to Default
            </button>
            <button 
              className="btn warning" 
              onClick={() => sendCommand('welcome')}
              disabled={loading}
            >
              👋 Wedding Welcome
            </button>
            <button 
              className="btn" 
              onClick={() => sendCommand('compliment')}
              disabled={loading}
            >
              ✨ Guest Compliment
            </button>
            <button 
              className="btn" 
              onClick={() => sendCommand('love')}
              disabled={loading}
            >
              💕 Love Message
            </button>
          </div>

          {/* Wedding Messages */}
          <div className="control-section">
            <h3 className="section-title">Wedding Messages</h3>
            <button 
              className="btn" 
              onClick={() => sendCommand('ceremony')}
              disabled={loading}
            >
              💒 Ceremony Welcome
            </button>
            <button 
              className="btn" 
              onClick={() => sendCommand('reception')}
              disabled={loading}
            >
              🎉 Reception Time
            </button>
            <button 
              className="btn" 
              onClick={() => sendCommand('photos')}
              disabled={loading}
            >
              📸 Photo Booth Mode
            </button>
            <button 
              className="btn" 
              onClick={() => sendCommand('dancing')}
              disabled={loading}
            >
              💃 Dance Floor
            </button>
          </div>

          {/* LiveKit Room Management */}
          <div className="control-section">
            <h3 className="section-title">LiveKit Room Management</h3>
            <button 
              className="btn" 
              onClick={listRooms}
              disabled={roomsLoading || loading}
            >
              🔍 List Active Rooms
            </button>
            <button 
              className="btn warning" 
              onClick={deleteAllRooms}
              disabled={loading || roomsLoading}
            >
              🗑️ Delete All Rooms
            </button>
            
            {rooms.length > 0 && (
              <div className="rooms-list">
                <strong>Active Rooms ({rooms.length})</strong>
                <div style={{ 
                  marginTop: '12px', 
                  maxHeight: '300px', 
                  overflowY: 'auto',
                  overflowX: 'hidden',
                  paddingRight: '8px' 
                }}>
                  {rooms.map((room, index) => (
                    <div key={index} className="room-card" style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      padding: '12px',
                      marginBottom: '8px',
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <span>🏠 {room}</span>
                      <button 
                        className="btn small primary"
                        onClick={() => viewRoom(room)}
                        disabled={loading}
                      >
                        👁️ View Room
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {rooms.length === 0 && !roomsLoading && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#6e6e73', fontSize: '0.9rem' }}>
                No active rooms found
              </div>
            )}
          </div>

          {/* Video Recording Management */}
          <div className="control-section">
            <h3 className="section-title">🎥 Video Recordings</h3>
            <button 
              className="btn primary" 
              onClick={listVideos}
              disabled={videosLoading || loading}
            >
              {videosLoading ? '🔄 Loading...' : '🎥 Load Recordings'}
            </button>
            
            {videos.length > 0 && (
              <button 
                className={`btn toggle ${showVideoDetails ? 'active' : ''}`}
                onClick={() => setShowVideoDetails(!showVideoDetails)}
              >
                {showVideoDetails ? '📋 Hide Details' : '📋 Show Details'}
              </button>
            )}
            
            {videos.length > 0 && (
              <div className="videos-list">
                <strong>Video Recordings ({videos.length})</strong>
                {showVideoDetails ? (
                  <div style={{ 
                    marginTop: '12px', 
                    maxHeight: '400px', 
                    overflowY: 'auto',
                    overflowX: 'hidden',
                    paddingRight: '8px' 
                  }}>
                    {videos.map((video) => (
                      <div key={video.id} className="video-card">
                        <div className="video-header">
                          <div className="video-title">
                            {video.guest_name ? (
                              <>👤 {video.guest_name}</>
                            ) : (
                              <>🏠 {video.room_id}</>
                            )}
                          </div>
                          <span className={`status-badge ${video.processing_status}`}>
                            {video.processing_status}
                          </span>
                        </div>
                        
                        <div className="video-meta">
                          📅 {new Date(video.created_at).toLocaleString()}
                        </div>
                        
                        {video.guest_relation && (
                          <div className="video-meta">
                            👥 {video.guest_relation}
                          </div>
                        )}
                        
                        <div className="video-meta">
                          ⏱️ {formatDuration(video.duration_seconds)} • 
                          📁 {formatFileSize(video.file_size_bytes)}
                        </div>
                        
                        <div className="video-actions">
                          {video.video_url && (
                            <button 
                              className="btn small primary"
                              onClick={() => window.open(video.video_url, '_blank')}
                            >
                              🔗 Direct Link
                            </button>
                          )}
                          {video.presigned_url && (
                            <button 
                              className="btn small"
                              onClick={() => window.open(video.presigned_url!, '_blank')}
                            >
                              ⏰ Presigned Link
                            </button>
                          )}
                          <button 
                            className="btn small"
                            onClick={() => refreshPresignedUrl(video.id)}
                            disabled={loading}
                          >
                            🔄 Refresh
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ul className="simple-list">
                    {videos.map((video) => (
                      <li key={video.id}>
                        <strong>{video.guest_name || video.room_id}</strong> • 
                        {new Date(video.created_at).toLocaleDateString()} • 
                        <span className={`status-badge ${video.processing_status}`} style={{marginLeft: '8px'}}>
                          {video.processing_status}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            
            {videos.length === 0 && !videosLoading && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#6e6e73', fontSize: '0.9rem' }}>
                No video recordings found
              </div>
            )}
          </div>

          {/* Custom Message */}
          <div className="control-section">
            <h3 className="section-title">Custom Message</h3>
            <div className="custom-message">
              <textarea
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Enter your custom mirror message here...&#10;&#10;Use line breaks to separate lines.&#10;&#10;Example:&#10;Welcome Beautiful Guest&#10;You look stunning tonight&#10;Enjoy the celebration"
                disabled={loading}
              />
            </div>
            <button 
              className="btn primary" 
              onClick={sendCustomMessage}
              disabled={loading || !customText.trim()}
            >
              📝 Send Custom Message
            </button>
          </div>
        </div>

        {/* Status Bar */}
        <div className="status-bar">
          <div className={`status-message ${status.type}`}>
            {status.message}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Control;
