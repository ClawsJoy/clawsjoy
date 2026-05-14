class SearchSkill:
    name = "search"
    description = "信息搜索"
    version = "1.0.0"
    category = "search"

    KNOWLEDGE_BASE = {
        "高才通": "高才通全称「高端人才通行证计划」，2022年12月28日推出，分为A/B/C三类。A类：年收入250万港币以上；B类：全球百强大学学士+3年工作经验；C类：全球百强大学学士+工作经验不足3年（每年限额1万人）。审批周期约4周。",
        "高端人才": "高端人才通行证计划（高才通）是香港2022年底推出的新人才引进政策。A类：年收入250万港币以上；B类：全球百强大学学士+3年工作经验；C类：全球百强大学学士+工作经验不足3年。",
        "优才计划": "香港优秀人才入境计划（优才计划）是香港2006年推出的人才引进政策，2024年11月改革后采用12项评核准则，需满足其中6项。",
        "香港优才": "香港优秀人才入境计划，2006年推出，2024年11月重大改革，综合计分制改为12项评核准则。",
    }

    def execute(self, params):
        query = params.get("query", "")
        if not query:
            return {"error": "query required"}
        
        for key, value in self.KNOWLEDGE_BASE.items():
            if key in query or query in key:
                return {"success": True, "query": query, "answer": value, "source": "本地知识库"}
        
        if "人才" in query or "通行证" in query:
            return {"success": True, "query": query, "answer": self.KNOWLEDGE_BASE.get("高才通", ""), "source": "关键词映射"}
        
        return {"success": True, "query": query, "answer": f"未找到「{query}」的信息。建议搜索：高才通、优才计划"}

skill = SearchSkill()
