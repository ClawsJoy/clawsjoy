import subprocess, os
def execute(params):
    script = params.get("script")
    out = params.get("output_path")
    if not script or not out:
        return {"success": False, "error": "Missing script or output_path"}
    model = os.environ.get("CLAWSJOY_PIPER_MODEL", "/mnt/d/clawsjoy/piper_models/zh_CN-medium.onnx")
    wav = out.replace(".mp3", ".wav")
    try:
        cmd = f'echo "{script}" | piper --model {model} --output_file {wav}'
        subprocess.run(cmd, shell=True, check=True, timeout=30)
        subprocess.run(['ffmpeg', '-y', '-i', wav, '-c:a', 'libmp3lame', '-q:a', '4', out],
                       check=True, timeout=10, stderr=subprocess.DEVNULL)
        os.remove(wav)
        return {"success": True, "audio_path": out}
    except Exception as e:
        return {"success": False, "error": str(e)}
