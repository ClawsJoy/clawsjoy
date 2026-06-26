actions: []
name: my_calculator
version: 1.0.0
description: '自定义计算器技能 支持加减乘除四则运算 数学计算 加法 减法 乘法 除法'
author: ClawsJoy
security_grade: 🟢 A
use_when: 数学计算, 数值运算, 加减乘除
not_for: 文本处理
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
  "skill": "my_calculator"
}
