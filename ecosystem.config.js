module.exports = {
  apps: [
    {
      name: 'chat-api',
      script: '/mnt/d/clawsjoy/bin/chat_api_agent.py',
      interpreter: 'python3',
      cwd: '/mnt/d/clawsjoy/bin',
      env: {
        PORT: 8101
      },
      autorestart: true,
      watch: false
    },
    {
      name: 'tts',
      script: '/mnt/d/clawsjoy/bin/tts_server_stable.py',
      interpreter: 'python3',
      cwd: '/mnt/d/clawsjoy/bin',
      autorestart: true,
      watch: false
    },
    {
      name: 'ollama',
      script: 'ollama',
      args: 'serve',
      interpreter: 'none',
      autorestart: true,
      watch: false
    }
  ]
}
