"""expression_switcher 技能"""

from .expression_switcher import ExpressionSwitcher


def execute(params=None):
    if params is None:
        params = {}
    return ExpressionSwitcher().execute(params)
