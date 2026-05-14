#!/bin/bash
echo "检查Python..."
python3 --version
echo "检查Ollama..."
curl -s http://127.0.0.1:11434/api/tags > /dev/null && echo "Ollama OK" || echo "Ollama 未运行"
echo "检查目录..."
mkdir -p output/bg output/characters logs data
