"""
docker 技能模块
"""

from .docker_skill import DockerExecutor


def execute(params=None):
    """统一执行入口"""
    skill = DockerExecutor()
    return skill.execute(params)
