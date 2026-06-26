"""document 技能"""

from .document_skill import document_skill


def execute(params=None):
    if params is None:
        params = {}
    return document_skill().execute(params)
