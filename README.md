# PaperAgentSkill

# AI领域新闻推送

## 任务目标
- 本 Skill 用于：检索VLA（Vision-Language-Action）和世界模型领域的最新进展，筛选高质量文章并推送到飞书群
- 能力包含：智能搜索、内容筛选、质量评估、自动推送、定时任务
- 触发条件：用户请求获取AI领域最新动态、追踪前沿研究、推送技术文章

## 前置准备

### 依赖说明
```
requests==2.31.0
```

### 配置文件
配置文件位于 `references/config.json`，包含：
- **飞书Webhook URL**：已配置
- **搜索主题**：VLA、world model（可自定义）
- **时间范围**：最近1天
- **推送数量**：最多8篇文章
- **定时推送**：每天10:00（Asia/Shanghai时区）

如需修改配置，请编辑 `references/config.json` 文件。

## 操作步骤

### 方式一：立即推送（推荐）

直接调用脚本执行搜索和推送：
```bash
python scripts/search_and_push.py
```

脚本将自动完成：
1. 检索VLA和世界模型领域的最新文章
2. 按可信度排序并筛选高质量文章
3. 构建飞书卡片消息
4. 自动推送到配置的飞书群

### 方式二：测试模式（不推送）

仅搜索不推送，用于验证搜索结果：
```bash
# JSON格式输出
python scripts/search_and_push.py --dry-run

# 文本格式输出
python scripts/search_and_push.py --dry-run --output text
```

### 方式三：自定义参数

覆盖配置文件中的默认参数：
```bash
# 指定主题和时间范围
python scripts/search_and_push.py --topics "VLA,world model,embodied AI" --days 3

# 指定自定义配置文件
python scripts/search_and_push.py --config /path/to/custom_config.json
```

## 定时任务设置

### 方案一：使用系统定时任务（Linux/Mac）

如果Skill运行在Linux或Mac服务器上，使用cron设置定时任务：

1. 编辑crontab：
```bash
crontab -e
```

2. 添加定时任务（每天10:00执行）：
```bash
0 10 * * * cd /workspace/projects/ai-news-pusher && python scripts/search_and_push.py >> logs/push.log 2>&1
```

3. 创建日志目录：
```bash
mkdir -p /workspace/projects/ai-news-pusher/logs
```

### 方案二：使用系统定时任务（Windows）

如果运行在Windows系统上，使用任务计划程序：

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器：每天10:00
4. 设置操作：启动程序
   - 程序：`python`
   - 参数：`scripts/search_and_push.py`
   - 起始位置：`/workspace/projects/ai-news-pusher`

### 方案三：通过智能体定期调用

如果Skill运行在支持定时调用的智能体平台上，可以：
1. 配置智能体的定时触发器
2. 每天10:00自动执行"推送今天的AI新闻"指令
3. 智能体调用本Skill完成推送

## 工作流程详解

### 步骤1：智能搜索
调用 `scripts/search_and_push.py` 使用Tavily API执行搜索：
- 搜索范围：arXiv、GitHub、知名实验室/公司官网
- 时间范围：最近24小时
- 搜索深度：高级搜索

### 步骤2：质量筛选
自动按以下标准筛选：
- **来源可信度**：arXiv > Papers with Code > HuggingFace > GitHub > 技术博客
- **时效性**：优先最近发布的文章
- **相关性**：确保内容与VLA或世界模型高度相关

### 步骤3：内容整理
- 每篇文章自动生成摘要（前100字）
- 提取来源、发布时间、原文链接
- 按可信度评分排序

### 步骤4：自动推送
- 构建飞书交互式卡片
- 包含标题、摘要、链接、可信度评分
- 自动推送到配置的飞书群

## 资源索引
- 主脚本：见 [scripts/search_and_push.py](scripts/search_and_push.py)（搜索与推送一体化）
- 配置文件：见 [references/config.json](references/config.json)（Webhook URL、搜索参数）
- 消息格式：见 [references/feishu_message_format.md](references/feishu_message_format.md)（飞书卡片格式规范）

## 配置修改指南

### 修改搜索主题
编辑 `references/config.json`：
```json
{
  "search_config": {
    "topics": ["VLA", "world model", "embodied AI"],
    "days": 1,
    "max_articles_to_push": 10
  }
}
```

### 修改推送时间
编辑 `references/config.json`：
```json
{
  "schedule": {
    "enabled": true,
    "time": "09:00",
    "timezone": "Asia/Shanghai"
  }
}
```

### 更换飞书群
编辑 `references/config.json`：
```json
{
  "feishu_webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_NEW_WEBHOOK"
}
```

## 注意事项
- 搜索结果可能包含大量文章，已自动筛选保证推送质量
- Webhook URL已集成到配置文件，无需每次提供
- 如需推送其他AI领域，修改配置文件中的topics字段
- 建议使用定时任务实现每日自动推送
- 测试时使用 `--dry-run` 参数，避免重复推送

## 使用示例

### 示例1：每日定时推送
**场景**：每天早上10点自动推送最新进展

**执行流程**：
1. 定时任务触发脚本执行
2. 自动检索并筛选文章
3. 推送到飞书群

**设置命令**：
```bash
# 添加到crontab
0 10 * * * cd /workspace/projects/ai-news-pusher && python scripts/search_and_push.py
```

### 示例2：测试搜索结果
**场景**：查看今天的搜索结果，暂不推送

**执行命令**：
```bash
python scripts/search_and_push.py --dry-run --output text
```

### 示例3：紧急推送特定主题
**场景**：需要推送最近3天的具身智能相关文章

**执行命令**：
```bash
python scripts/search_and_push.py --topics "embodied AI" --days 3
```
