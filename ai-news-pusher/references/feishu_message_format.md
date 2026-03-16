# 飞书消息格式规范

## 概览
本文档定义了AI新闻推送到飞书群的消息格式规范，确保消息呈现美观、信息清晰。

## 消息类型
使用飞书自定义机器人的 **交互式卡片消息**（Interactive Card）

## 消息结构

### 完整示例

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "🤖 AI前沿速递 - 2024年XX月XX日"
      },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**📦 今日主题：VLA & 世界模型最新进展**"
        }
      },
      {
        "tag": "hr"
      },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**1. [文章标题](文章链接)**\n来源：arXiv | 发布时间：2024-XX-XX\n📝 摘要：文章核心观点和创新点概述...\n🔥 亮点：关键技术点或创新之处"
        }
      },
      {
        "tag": "hr"
      },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**2. [第二篇文章标题](链接)**\n来源：GitHub | 发布时间：2024-XX-XX\n📝 摘要：文章核心观点...\n🔥 亮点：关键技术点"
        }
      },
      {
        "tag": "hr"
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "查看完整报告"
            },
            "url": "报告链接（可选）",
            "type": "primary"
          }
        ]
      },
      {
        "tag": "note",
        "elements": [
          {
            "tag": "plain_text",
            "content": "由 AI News Pusher 自动推送 | 共筛选出 5 篇高质量文章"
          }
        ]
      }
    ]
  }
}
```

## 格式规范详解

### 1. 消息头部（Header）
```json
{
  "header": {
    "title": {
      "tag": "plain_text",
      "content": "🤖 AI前沿速递 - {日期}"
    },
    "template": "blue"
  }
}
```
- 标题格式：`🤖 AI前沿速递 - YYYY年MM月DD日`
- 颜色主题：`blue`（蓝色，专业感）

### 2. 主题说明
```json
{
  "tag": "div",
  "text": {
    "tag": "lark_md",
    "content": "**📦 今日主题：{主题名称}**"
  }
}
```
- 使用加粗和图标突出主题
- 主题名称示例：`VLA & 世界模型最新进展`

### 3. 文章条目格式
每篇文章使用以下格式：

```json
{
  "tag": "div",
  "text": {
    "tag": "lark_md",
    "content": "**{序号}. [{标题}]({链接})**\n来源：{来源} | 发布时间：{日期}\n📝 摘要：{摘要内容}\n🔥 亮点：{关键亮点}"
  }
}
```

**字段说明**：
- **序号**：从1开始递增
- **标题**：文章原标题（可适当截断，不超过50字）
- **链接**：文章原文URL
- **来源**：域名或机构名（如：arXiv、GitHub、OpenAI）
- **日期**：发布日期（格式：YYYY-MM-DD）
- **摘要**：50-100字的核心观点概述
- **亮点**：关键技术点或创新之处（可选）

### 4. 分隔线
每篇文章之间使用水平分隔线：
```json
{
  "tag": "hr"
}
```

### 5. 底部操作区（可选）
```json
{
  "tag": "action",
  "actions": [
    {
      "tag": "button",
      "text": {
        "tag": "plain_text",
        "content": "查看完整报告"
      },
      "url": "{报告链接}",
      "type": "primary"
    }
  ]
}
```

### 6. 底部备注
```json
{
  "tag": "note",
  "elements": [
    {
      "tag": "plain_text",
      "content": "由 AI News Pusher 自动推送 | 共筛选出 {数量} 篇高质量文章"
    }
  ]
}
```

## 内容组织建议

### 文章排序规则
1. **第一优先级**：来源可信度（arXiv > GitHub > 技术博客 > 新闻媒体）
2. **第二优先级**：时效性（发布时间倒序）
3. **第三优先级**：相关性（与主题的匹配程度）

### 文章数量控制
- 推荐：5-8篇文章
- 最多：不超过10篇
- 如果文章过多，只保留质量最高的

### 摘要撰写原则
- 突出核心贡献或创新点
- 使用简洁的技术语言
- 避免营销性描述
- 长度控制在50-100字

## Markdown语法支持

飞书卡片支持以下Markdown语法：
- **加粗**：`**文本**`
- *斜体*：`*文本*`
- 链接：`[显示文本](URL)`
- 代码：`` `代码` ``
- 列表：`- 项目` 或 `1. 项目`

## 消息推送示例

### 示例1：单篇文章推送
```json
{
  "tag": "div",
  "text": {
    "tag": "lark_md",
    "content": "**1. [Scaling Vision-Language-Action Models for Robot Learning](https://arxiv.org/abs/xxx)**\n来源：arXiv | 发布时间：2024-01-15\n📝 摘要：本文提出了一种大规模视觉-语言-行动模型的训练方法，在机器人操作任务上取得了显著提升。\n🔥 亮点：模型参数达到10B，在真实机器人上实现了零样本泛化"
  }
}
```

### 示例2：多篇文章推送（完整消息）
见上方"完整示例"部分。

## 注意事项

1. **链接有效性**：确保所有URL可访问
2. **时间准确性**：使用实际发布时间，不要使用爬取时间
3. **内容真实性**：摘要必须准确反映文章内容，禁止杜撰
4. **格式一致性**：所有文章条目使用统一格式
5. **长度控制**：单条消息总长度不超过4096字符

## 推送脚本示例

```python
import requests

def push_to_feishu(webhook_url: str, articles: list):
    """推送消息到飞书群"""
    
    # 构建文章列表
    article_elements = []
    for idx, article in enumerate(articles, 1):
        article_elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{idx}. [{article['title']}]({article['url']})**\n"
                          f"来源：{article['source']} | 发布时间：{article['date']}\n"
                          f"📝 摘要：{article['summary']}\n"
                          f"🔥 亮点：{article['highlight']}"
            }
        })
        article_elements.append({"tag": "hr"})
    
    # 移除最后一个分隔线
    if article_elements and article_elements[-1]["tag"] == "hr":
        article_elements.pop()
    
    # 构建完整消息
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🤖 AI前沿速递 - {datetime.now().strftime('%Y年%m月%d日')}"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📦 今日主题：VLA & 世界模型最新进展**"
                    }
                },
                {"tag": "hr"},
                *article_elements,
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"由 AI News Pusher 自动推送 | 共筛选出 {len(articles)} 篇高质量文章"
                        }
                    ]
                }
            ]
        }
    }
    
    # 发送请求
    response = requests.post(webhook_url, json=message)
    return response.status_code == 200
```
