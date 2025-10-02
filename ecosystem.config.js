module.exports = {
  apps: [
    {
      name: 'fastapi-server',
      script: 'bash',
      args: ['-c', 'source venv/bin/activate && PYTHONPATH=/home/husain/Desktop/mirror uvicorn backend.app.main:app --host 0.0.0.0 --port 8000'],
      cwd: '/home/husain/Desktop/mirror',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development'
      }
    },
    {
      name: 'livekit-agent',
      script: 'bash',
      args: ['-c', 'source /home/husain/Desktop/mirror/venv/bin/activate && PYTHONPATH=/home/husain/Desktop/mirror python agent.py dev'],
      cwd: '/home/husain/Desktop/mirror/agent',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development'
      }
    },
    {
      name: 'react-dev-server',
      script: 'npm',
      args: 'start',
      cwd: '/home/husain/Desktop/mirror/livekit-react',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development'
      }
    }
  ]
};