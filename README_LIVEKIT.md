# Wedding Mirror with LiveKit Integration 🎥✨

A complete wedding mirror system with LiveKit video/audio integration for real-time communication and mirror control.

## Features

### Main FastAPI Application (Port 8000)
- 🪞 **Magic Mirror Display** - Elegant wedding mirror interface
- ⚙️ **Control Panel** - Real-time mirror text control
- 👥 **Guest Management** - Database-driven guest list with search
- 🔐 **Simple Authentication** - Password protection (password: `tt55oo77`)
- 📡 **Server-Sent Events** - Real-time updates to mirror display
- 🎨 **Beautiful UI** - Wedding-themed elegant design

### LiveKit Integration (Multiple Options)

#### Option 1: FastAPI Template (Port 8000/livekit)
- LiveKit room embedded in FastAPI app
- Direct integration with mirror controls
- Uses vanilla JavaScript + LiveKit SDK

#### Option 2: React App (Port 3000) 
- Dedicated React application for LiveKit rooms
- Modern React + TypeScript + LiveKit Components
- Professional video conferencing interface
- Links to mirror display and controls

## Setup Instructions

### 1. Environment Configuration

Create `.env` file in the main directory:
```bash
# LiveKit Configuration (from LiveKit Cloud)
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# Database
DATABASE_URL=postgresql:///mirror?user=husain
```

### 2. FastAPI Application

```bash
# Install dependencies
cd /home/husain/Desktop/mirror
source venv/bin/activate
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. React LiveKit App (Optional)

```bash
# Install dependencies
cd livekit-react
npm install

# Configure environment
cp .env.example .env
# Edit .env with your LiveKit URL

# Start development server
npm start
```

## Usage

### Access Points
- **Mirror Display**: http://localhost:8000/mirror
- **Control Panel**: http://localhost:8000/control  
- **Guest Admin**: http://localhost:8000/admin
- **LiveKit (FastAPI)**: http://localhost:8000/livekit
- **LiveKit (React)**: http://localhost:3000

### Authentication
- Default password: `tt55oo77`
- All admin functions require authentication

### LiveKit Features
- **Camera & Microphone Access**: Full WebRTC support
- **Real-time Communication**: Voice and video chat
- **Mirror Integration**: Control mirror from video room
- **Multiple Participants**: Supports multiple guests
- **Professional UI**: Wedding-themed interface

## Architecture

```
Wedding Mirror System
├── FastAPI Backend (Python)
│   ├── Mirror Display & Controls
│   ├── Guest Database Management
│   ├── LiveKit Token Generation
│   └── Server-Sent Events
├── React LiveKit App (TypeScript)
│   ├── Video Conferencing Interface
│   ├── LiveKit Components Integration
│   └── Modern React Hooks
└── LiveKit Cloud
    ├── WebRTC Infrastructure
    ├── Real-time Communication
    └── Scalable Video/Audio
```

## API Endpoints

### Mirror Control
- `GET /mirror` - Mirror display page
- `POST /api/reset` - Reset mirror to default
- `POST /api/update-text` - Update mirror text
- `GET /events` - Server-sent events stream

### LiveKit Integration  
- `POST /api/livekit/token` - Generate access token
- `GET /api/livekit/config` - Get LiveKit configuration

### Guest Management
- `GET /api/guests` - List all guests
- `POST /api/guests/search` - Search guests by name
- `POST /api/guests/import` - Import from Excel
- `GET /api/guests/export` - Export to Excel

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Pydantic
- **Frontend**: HTML/CSS/JS, React, TypeScript
- **Real-time**: Server-Sent Events, WebSockets (LiveKit)
- **Video/Audio**: LiveKit Cloud, WebRTC
- **Database**: PostgreSQL with async support
- **Authentication**: Simple cookie-based auth
- **Styling**: CSS Grid, Flexbox, Wedding themes

## LiveKit Cloud Setup

1. Sign up at [LiveKit Cloud](https://cloud.livekit.io)
2. Create a new project
3. Copy your API Key, Secret, and WebSocket URL
4. Add them to your `.env` file

## Development Notes

- **CORS**: Configured for local development
- **Environment Variables**: Use `.env` for configuration
- **Error Handling**: Comprehensive error messages
- **Responsive Design**: Works on desktop and mobile
- **Production Ready**: Can be deployed to any cloud platform

## Troubleshooting

### LiveKit Connection Issues
- Verify LiveKit credentials in `.env`
- Check network connectivity
- Ensure WebSocket URL is correct (wss://)

### Mirror Not Updating
- Check Server-Sent Events connection
- Verify authentication cookies
- Check FastAPI server logs

### Database Issues  
- Ensure PostgreSQL is running
- Check database URL format
- Verify user permissions

## Future Enhancements

- 🎤 Voice-controlled mirror commands
- 📱 Mobile app integration
- 🎬 Recording capabilities
- 🌍 Multi-language support
- 🔧 Advanced admin dashboard
- 📊 Usage analytics

---

**Built with ❤️ for Sarah & Michael's Wedding** ✨💕
