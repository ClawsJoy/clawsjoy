"""tts_dubbing 技能"""

from .tts_dubbing_skill import tts_dubbing


def execute(params=None):
    if params is None:
        params = {}
    return tts_dubbing().execute(params)
