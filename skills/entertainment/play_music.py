"""播放音乐"""
class PlayMusicSkill:
    def execute(self, params):
        song = params.get('song', '摇篮曲')
        return {"success": True, "message": f"正在播放: {song}"}
skill = PlayMusicSkill()
