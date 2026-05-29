"""白噪音/背景音"""
class WhiteNoiseSkill:
    def execute(self, params):
        sound = params.get('sound', 'rain')
        sounds = {
            "rain": "🌧️ 雨声",
            "wave": "🌊 海浪声",
            "forest": "🌲 森林鸟鸣",
            "piano": "🎹 钢琴曲"
        }
        return {"success": True, "playing": sounds.get(sound, sounds["rain"]), "message": f"正在播放{sound}声"}
skill = WhiteNoiseSkill()
