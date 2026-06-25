"""video-description 技能实现 - 用 llava 逐帧描述视频并生成日志"""

import subprocess, base64, requests, json, tempfile, shutil
from pathlib import Path
from datetime import datetime


class VideoDescription:
    name = "video-description"
    description = "用视觉模型逐帧描述视频内容并生成分析日志"
    version = "2.0.0"
    
    LOG_FILE = Path("data/assets/novels/AI觉醒/video_analysis_log.jsonl")

    def execute(self, params):
        video_path = params.get("video_path", "")
        if not video_path:
            return {"success": False, "error": "请提供视频文件路径"}
        
        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}
        
        fps = params.get("fps", 1)
        question = params.get("question", "描述：角色形象一致吗？场景一致吗？画面流畅吗？有什么问题？一句话。")
        version = params.get("version", path.stem)
        
        # 提取帧
        tmp_dir = tempfile.mkdtemp(prefix="video_frames_")
        subprocess.run([
            'ffmpeg', '-y', '-i', str(path),
            '-vf', f'fps={fps}',
            f'{tmp_dir}/frame_%03d.png'
        ], capture_output=True)
        
        frames = sorted(Path(tmp_dir).glob("frame_*.png"))
        if not frames:
            shutil.rmtree(tmp_dir)
            return {"success": False, "error": "未能提取视频帧"}
        
        # llava 逐帧描述
        descriptions = []
        issues = []
        for f in frames:
            with open(f, 'rb') as fp:
                img = base64.b64encode(fp.read()).decode()
            r = requests.post('http://localhost:11434/api/generate', json={
                'model': 'llava:latest',
                'prompt': question,
                'images': [img],
                'stream': False
            }, timeout=60)
            desc = r.json().get('response', '无描述')[:300]
            descriptions.append({"frame": f.stem, "description": desc})
            
            # 自动标记问题
            if any(kw in desc for kw in ["不一致", "不同", "空白", "占位", "无内容", "移除"]):
                issues.append(f"{f.stem}: {desc[:100]}")
        
        shutil.rmtree(tmp_dir)
        
        # 生成日志
        log = {
            "time": datetime.now().isoformat(),
            "video": str(path),
            "version": version,
            "frame_count": len(frames),
            "descriptions": descriptions,
            "issues": issues,
            "summary": f"共{len(frames)}帧，{len(issues)}个问题"
        }
        
        # 写入日志文件
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.LOG_FILE, 'a') as f:
            f.write(json.dumps(log, ensure_ascii=False) + '\n')
        
        return {"success": True, "log": log}


video_description = VideoDescription()
