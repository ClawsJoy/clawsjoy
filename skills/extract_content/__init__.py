"""extract_content 技能"""

from .extract_content_skill import extract_content


def execute(params=None):
    if params is None:
        params = {}
    return extract_content().execute(params)
