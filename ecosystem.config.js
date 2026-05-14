module.exports = {
  apps: [
    {
      name: 'web-server',
      script: 'python3',
      args: '-m http.server 8082 --directory web',
      cwd: '/mnt/d/clawsjoy',
      autorestart: true,
      watch: false,
      error_file: '/tmp/web-server-error.log',
      out_file: '/tmp/web-server-out.log'
    },
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
      watch: false,
      error_file: '/tmp/chat-api-error.log',
      out_file: '/tmp/chat-api-out.log'
    },
    {
      name: 'tts',
      script: 'bin/tts_server_stable.py',
      interpreter: 'python3',
      cwd: '/mnt/d/clawsjoy/bin',
      env: {
        PORT: 9000
      },
      autorestart: true,
      watch: false,
      error_file: '/tmp/tts-error.log',
      out_file: '/tmp/tts-out.log'
    },
    {
      name: 'joymate-api',
      script: 'bin/joymate_api.py',
      interpreter: 'python3',
      cwd: '/mnt/d/clawsjoy',
      env: {
        PORT: 8093
      },
      autorestart: true,
      watch: false,
      error_file: '/tmp/joymate-api-error.log',
      out_file: '/tmp/joymate-api-out.log'
    }
  ]
}
