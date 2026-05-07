---
name: url-collector
description: URL采集和内容提取技能
version: 1.0.0
parameters:
  - name: action
    type: string
    required: true
    enum: ["crawl", "search", "add"]
  - name: url
    type: string
    required: false
  - name: category
    type: string
    required: false
  - name: name
    type: string
    required: false
---

# URL 采集技能

## 使用示例

采集单个URL:
execute_skill("url-collector", {"action": "crawl", "url": "https://example.com"})

按分类查找采集源:
execute_skill("url-collector", {"action": "search", "category": "移民"})

添加新采集源:
execute_skill("url-collector", {
    "action": "add",
    "name": "香港房屋署",
    "url": "https://www.housingauthority.gov.hk/",
    "category": "住房"
})
