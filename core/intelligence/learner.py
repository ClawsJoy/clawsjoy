#!/usr/bin/env python3
"""Learner - Learner 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import json
from datetime import datetime
from pathlib import Path


class Learner:
    VERSION = "4.0.0"

    def __init__(self):
        self.learning_file = (
            Path(__file__).parent.parent / "data" / "learning_results.json"
        )
        self._load()

    def _load(self):
        if self.learning_file.exists():
            try:
                with open(self.learning_file, "r") as f:
                    self.data = json.load(f)
            except Exception as e:
                self.data = {"patterns": [], "count": 0}
        else:
            self.data = {"patterns": [], "count": 0}

    def _save(self):
        with open(self.learning_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def learn(self, pattern: str, outcome: str) -> bool:
        self.data["patterns"].append(
            {
                "pattern": pattern,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.data["count"] += 1
        self._save()
        return True

    def get_stats(self):
        return {"version": self.VERSION, "learned_count": self.data["count"]}


learner = Learner()
