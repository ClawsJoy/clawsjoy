module.exports = {
  apps: [
    {
      name: 'chat-api',
      script: 'bin/chat_api_agent.py',
      interpreter: 'python3',
      cwd: '/mnt/d/clawsjoy',
      env: {
        PORT: 8101,
        OLLAMA_HOST: 'http://localhost:11434',
        NO_PROXY: 'localhost,127.0.0.1'
      },
      autorestart: true,
      watch: false
    },
    {
      name: 'tts-api',
      script: 'bin/tts_server_stable.py',
      interpreter: 'python3',
      cwd: '/mnt/d/clawsjoy/bin',
      env: { PORT: 9000 },
      autorestart: true,
      watch: false
    }
  ]
}
