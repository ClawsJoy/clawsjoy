import subprocess
def execute(params):
    script = params.get("script")
    out = params.get("output_path")
    if not script or not out:
        return {"success": False, "error": "Missing script or output_path"}
    try:
        cmd = f'edge-tts --text "{script}" --voice zh-CN-XiaoxiaoNeural --write-media {out}'
        subprocess.run(cmd, shell=True, check=True, timeout=30)
        return {"success": True, "audio_path": out}
    except Exception as e:
        return {"success": False, "error": str(e)}
