#!/usr/bin/env python3
import os, importlib.util, json

SKILLS_DIR = "/home/flybo/clawsjoy/skills"

def load_skill(skill_name):
    skill_path = os.path.join(SKILLS_DIR, skill_name, "main.py")
    if not os.path.exists(skill_path):
        return None
    spec = importlib.util.spec_from_file_location(skill_name, skill_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def list_skills():
    skills = []
    for d in os.listdir(SKILLS_DIR):
        meta = os.path.join(SKILLS_DIR, d, "skill.json")
        if os.path.exists(meta):
            with open(meta) as f:
                skills.append(json.load(f))
    return skills
