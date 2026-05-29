---
name: my-calculator
description: 自定义计算器技能，支持加减乘除四则运算
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: []
    emoji: "🧮"
    homepage: ""
    os: []
    always: true
    envVars: []
---

# 我的计算器

## 功能描述
执行数学计算，支持加法、减法、乘法、除法运算。

## 参数说明
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| a | number | 是 | 第一个数字 |
| b | number | 是 | 第二个数字 |
| op | string | 是 | 运算类型: add/sub/mul/div |

## 返回格式
```json
{
  "result": 15,
  "skill": "my-calculator"
}
