import re

file_path = "core/agents/wisdom/wisdom_factory.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 v4_agents 字典中添加 comic_writer_agent
old_v4_agents = '''            "director_agent": ("agents.director_agent.agent_v4", "DirectorAgentV4"),
        }'''

new_v4_agents = '''            "director_agent": ("agents.director_agent.agent_v4", "DirectorAgentV4"),
            "comic_writer_agent": ("agents.comic_writer_agent.agent_v4", "ComicWriterAgentV4"),
        }'''

content = content.replace(old_v4_agents, new_v4_agents)

# 在 v4_agent_names 列表中添加 comic_writer_agent
old_names = '''            "video_indexer_agent", "proactive_agent","director_agent"
        ]'''

new_names = '''            "video_indexer_agent", "proactive_agent","director_agent",
            "comic_writer_agent"
        ]'''

content = content.replace(old_names, new_names)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ comic_writer_agent 已注册到 wisdom_factory")
