// ============================================
// ClawsJoy 语音模块 - 后端 STT + TTS
// ============================================

const VOICE_CONFIG = {
    sttUrl: `http://${window.location.hostname}:8096/api/stt`,
    ttsUrl: `http://${window.location.hostname}:9000/api/tts`,
    recordingDuration: 5000,  // 最长录音 5 秒
    silenceTimeout: 1500      // 静音超时
};

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recordingTimer = null;
let silenceTimer = null;
let audioContext = null;

// 检查麦克风权限
async function checkMicrophone() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(t => t.stop());
        return true;
    } catch (e) {
        console.error('麦克风权限被拒绝:', e);
        return false;
    }
}

// 开始录音
async function startRecording() {
    if (isRecording) return;
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                audioChunks.push(e.data);
                resetSilenceTimer();
            }
        };
        
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendToSTT(blob);
            stream.getTracks().forEach(t => t.stop());
            isRecording = false;
            document.getElementById('micBtn')?.classList.remove('listening');
        };
        
        mediaRecorder.start(100);
        isRecording = true;
        document.getElementById('micBtn')?.classList.add('listening');
        
        // 设置最长录音时间
        recordingTimer = setTimeout(() => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                stopRecording();
            }
        }, VOICE_CONFIG.recordingDuration);
        
    } catch (e) {
        console.error('录音失败:', e);
        showToast('无法访问麦克风，请检查权限');
    }
}

// 停止录音
function stopRecording() {
    if (recordingTimer) clearTimeout(recordingTimer);
    if (silenceTimer) clearTimeout(silenceTimer);
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
}

// 重置静音计时器
function resetSilenceTimer() {
    if (silenceTimer) clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
        }
    }, VOICE_CONFIG.silenceTimeout);
}

// 发送音频到 STT 服务
async function sendToSTT(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.webm');
    
    showToast('🎤 识别中...');
    
    try {
        const response = await fetch(VOICE_CONFIG.sttUrl, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success && result.text) {
            const inputEl = document.getElementById('textInput');
            if (inputEl) {
                inputEl.value = result.text;
                sendMsg();
            }
        } else {
            showToast('未识别到语音，请重试');
        }
    } catch (e) {
        console.error('STT 错误:', e);
        showToast('语音识别失败');
    }
}

// TTS - 文字转语音
let currentAudio = null;
let isTTSPlaying = false;

async function speakText(text) {
    // 如果正在播放，先停止
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    
    // 检查本地 TTS 服务
    try {
        const response = await fetch(VOICE_CONFIG.ttsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            currentAudio = new Audio(audioUrl);
            currentAudio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                currentAudio = null;
                isTTSPlaying = false;
            };
            await currentAudio.play();
            isTTSPlaying = true;
            return;
        }
    } catch (e) {
        console.log('TTS 服务不可用，使用浏览器备用:', e);
    }
    
    // 备用：浏览器 TTS
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 0.9;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

// Toast 提示
function showToast(message, duration = 2000) {
    let toast = document.getElementById('voice-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'voice-toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 120px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: #0ff;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 10000;
            border: 1px solid #0ff;
        `;
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, duration);
}

// 导出函数
window.startVoice = startRecording;
window.stopVoice = stopRecording;
window.speakText = speakText;
window.checkMicrophone = checkMicrophone;
