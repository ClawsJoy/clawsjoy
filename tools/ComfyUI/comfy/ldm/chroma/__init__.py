# 临时模块 - 绕过导入错误
import sys
import types

class DummyModule(types.ModuleType):
    pass

# 创建一个假的模型
def dummy(*args, **kwargs):
    return None

sys.modules['comfy.ldm.chroma.model'] = DummyModule('comfy.ldm.chroma.model')
