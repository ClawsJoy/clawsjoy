"""tts-dubbing 技能"""
from .tts_dubbing_skill import tts_dubbing

def execute(params):
    skill = tts_dubbing()
    return skill.execute(params)
