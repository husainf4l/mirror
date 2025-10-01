# Static Files

This directory contains static assets served by the FastAPI application.

## Directory Structure

```
static/
├── audio/           # Audio files
│   └── mirror.wav   # Magic mirror sound effect
├── css/             # CSS stylesheets
├── js/              # JavaScript files
└── images/          # Image assets
```

## Usage

### Audio Files
- **Mirror Sound Effect**: `/static/audio/mirror.wav`
  - Accessible at: `http://localhost:8000/static/audio/mirror.wav`
  - Type: WAV audio file
  - Usage: Magic mirror activation sound

### Test Pages
- **Audio Test**: `/test-audio`
  - Test page for audio playback functionality
  - Includes audio controls and direct links

### API Endpoints
- **Audio Info**: `/audio/mirror`
  - Returns JSON with audio file information

## Adding New Static Files

1. Place files in appropriate subdirectory:
   - CSS files → `static/css/`
   - JavaScript files → `static/js/`
   - Images → `static/images/`
   - Audio → `static/audio/`

2. Access via URL: `http://localhost:8000/static/[subdirectory]/[filename]`

## Examples

```html
<!-- Audio -->
<audio controls>
    <source src="/static/audio/mirror.wav" type="audio/wav">
</audio>

<!-- CSS -->
<link rel="stylesheet" href="/static/css/style.css">

<!-- JavaScript -->
<script src="/static/js/app.js"></script>

<!-- Images -->
<img src="/static/images/logo.png" alt="Logo">
```
