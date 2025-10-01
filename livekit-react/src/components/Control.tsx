import React, { useState } from 'react';
import './Control.css';

const apiUrl = process.env.REACT_APP_API_URL || '';

interface StatusType {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

const Control: React.FC = () => {
  const [customText, setCustomText] = useState<string>('');
  const [status, setStatus] = useState<StatusType>({ message: 'Ready to control the mirror ✨', type: 'info' });
  const [loading, setLoading] = useState<boolean>(false);

  // Predefined messages
  const messages = {
    welcome: '<span class="line fancy">Welcome</span><span class="line script">to the magical union of</span><span class="line fancy">Ibrahim & Zaina</span><span class="line script">Wedding</span>',
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

  return (
    <div className="control-page">
      <div className="container">
        <div className="header">
          <h1>🪞 Mirror Control Panel</h1>
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
              onClick={() => openWindow('/admin')}
              disabled={loading}
            >
              👥 Guest Management
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
