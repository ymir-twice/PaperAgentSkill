#!/usr/bin/env python3
"""
AI领域新闻检索与推送脚本
使用Tavily API检索VLA和世界模型领域的最新进展，并自动推送到飞书群

授权方式: ApiKey
凭证Key: COZE_TAVILY_SEARCH_7617706585846235199
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# 必须从 coze_workload_identity 导入 requests
from coze_workload_identity import requests


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认为 references/config.json
        """
        if config_path is None:
            # 默认配置文件路径（相对于脚本位置）
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / "references" / "config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @property
    def webhook_url(self) -> str:
        """获取飞书Webhook URL"""
        return self.config.get("feishu_webhook_url", "")
    
    @property
    def topics(self) -> List[str]:
        """获取搜索主题列表"""
        return self.config.get("search_config", {}).get("topics", ["VLA", "world model"])
    
    @property
    def days(self) -> int:
        """获取搜索时间范围（天）"""
        return self.config.get("search_config", {}).get("days", 1)
    
    @property
    def max_results_per_topic(self) -> int:
        """获取每个主题的最大结果数"""
        return self.config.get("search_config", {}).get("max_results_per_topic", 20)
    
    @property
    def max_articles_to_push(self) -> int:
        """获取推送的最大文章数"""
        return self.config.get("search_config", {}).get("max_articles_to_push", 8)


class TavilySearcher:
    """Tavily搜索客户端"""
    
    def __init__(self):
        """初始化搜索客户端"""
        # 获取凭证
        self.api_key = os.getenv("COZE_TAVILY_SEARCH_7617706585846235199")
        
        if not self.api_key:
            raise ValueError(
                "缺少Tavily API凭证。请确保已配置环境变量 COZE_TAVILY_SEARCH_7617706585846235199"
            )
        
        self.base_url = "https://api.tavily.com/search"
    
    def search(
        self,
        query: str,
        days: int = 1,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            days: 搜索最近几天的内容
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": max_results,
            "include_domains": [
                "arxiv.org",
                "github.com",
                "medium.com",
                "openai.com",
                "deepmind.google",
                "anthropic.com",
                "huggingface.co",
                "paperswithcode.com"
            ],
            "exclude_domains": [],
            "topic": "news"
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查HTTP状态码
            if response.status_code >= 400:
                raise Exception(
                    f"HTTP请求失败: 状态码 {response.status_code}, "
                    f"响应内容: {response.text}"
                )
            
            data = response.json()
            
            # 检查API错误
            if "error" in data:
                raise Exception(f"Tavily API错误: {data['error']}")
            
            results = data.get("results", [])
            
            # 过滤时间范围
            filtered_results = []
            for item in results:
                published_date = item.get("published_date")
                if published_date:
                    try:
                        pub_date = datetime.fromisoformat(
                            published_date.replace("Z", "+00:00")
                        )
                        if pub_date >= start_date:
                            filtered_results.append(item)
                    except:
                        # 如果日期解析失败，保留该结果
                        filtered_results.append(item)
                else:
                    # 没有发布日期的，也保留
                    filtered_results.append(item)
            
            return filtered_results
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")


def calculate_credibility_score(result: Dict[str, Any]) -> float:
    """
    计算来源可信度评分
    
    Args:
        result: 搜索结果项
        
    Returns:
        可信度评分 (0-10)
    """
    url = result.get("url", "").lower()
    score = 5.0  # 基础分
    
    # 学术来源加分
    if "arxiv.org" in url:
        score += 3.0
    elif "paperswithcode.com" in url:
        score += 2.5
    elif "huggingface.co" in url:
        score += 2.0
    
    # 知名机构加分
    if any(domain in url for domain in [
        "openai.com", "deepmind", "anthropic.com",
        "google.com", "meta.com", "microsoft.com"
    ]):
        score += 2.0
    
    # GitHub项目
    if "github.com" in url:
        score += 1.5
    
    # 技术博客
    if "medium.com" in url:
        score += 1.0
    
    return min(score, 10.0)


def format_article_for_display(article: Dict[str, Any]) -> Dict[str, str]:
    """
    格式化单篇文章用于展示
    
    Args:
        article: 文章数据
        
    Returns:
        格式化后的文章信息
    """
    return {
        "title": article.get("title", "无标题"),
        "url": article.get("url", ""),
        "source": article.get("url", "").split("/")[2] if "/" in article.get("url", "") else "未知",
        "published_date": article.get("published_date", "未知"),
        "content": article.get("content", ""),
        "credibility_score": round(calculate_credibility_score(article), 1)
    }


def build_feishu_card(articles: List[Dict[str, Any]], max_articles: int = 8) -> Dict[str, Any]:
    """
    构建飞书卡片消息
    
    Args:
        articles: 文章列表
        max_articles: 最大文章数
        
    Returns:
        飞书卡片消息结构
    """
    # 限制文章数量
    articles = articles[:max_articles]
    
    # 构建文章元素列表
    article_elements = []
    
    for idx, article in enumerate(articles, 1):
        formatted = format_article_for_display(article)
        
        # 构建文章卡片
        article_text = (
            f"**{idx}. [{formatted['title'][:50]}{'...' if len(formatted['title']) > 50 else ''}]({formatted['url']})**\n"
            f"来源：{formatted['source']} | 发布时间：{formatted['published_date'][:10] if formatted['published_date'] != '未知' else '未知'}\n"
            f"📝 摘要：{formatted['content'][:100]}{'...' if len(formatted['content']) > 100 else ''}\n"
            f"🔥 可信度：{formatted['credibility_score']}/10"
        )
        
        article_elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": article_text
            }
        })
        
        # 添加分隔线（最后一篇不加）
        if idx < len(articles):
            article_elements.append({"tag": "hr"})
    
    # 构建完整卡片
    card = {
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
                        "content": "**📦 今日主题：VLA & 世界模型最新进展**"
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
    
    return card


def push_to_feishu(webhook_url: str, card: Dict[str, Any]) -> bool:
    """
    推送消息到飞书群
    
    Args:
        webhook_url: 飞书Webhook URL
        card: 卡片消息结构
        
    Returns:
        是否推送成功
    """
    try:
        response = requests.post(
            webhook_url,
            json=card,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code >= 400:
            print(f"推送失败: HTTP {response.status_code}", file=sys.stderr)
            return False
        
        result = response.json()
        
        # 飞书返回 StatusCode 为 0 表示成功
        if result.get("StatusCode") == 0 or result.get("code") == 0:
            return True
        else:
            print(f"推送失败: {result}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"推送异常: {str(e)}", file=sys.stderr)
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="检索AI领域最新进展并推送到飞书群"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="配置文件路径（默认使用 references/config.json）"
    )
    parser.add_argument(
        "--topics",
        type=str,
        default=None,
        help="搜索主题，多个主题用逗号分隔（覆盖配置文件）"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="搜索最近几天的内容（覆盖配置文件）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅搜索不推送，用于测试"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "text"],
        default="json",
        help="输出格式（仅 dry-run 模式有效）"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = Config(args.config)
    
    # 命令行参数覆盖配置文件
    topics = args.topics.split(",") if args.topics else config.topics
    days = args.days if args.days else config.days
    max_results = config.max_results_per_topic
    
    # 初始化搜索器
    searcher = TavilySearcher()
    
    all_results = []
    
    # 对每个主题执行搜索
    for topic in topics:
        print(f"正在检索主题: {topic}", file=sys.stderr)
        
        try:
            results = searcher.search(
                query=f"{topic.strip()} AI research latest",
                days=days,
                max_results=max_results
            )
            
            all_results.extend(results)
            print(f"  找到 {len(results)} 篇相关文章", file=sys.stderr)
            
        except Exception as e:
            print(f"  搜索失败: {str(e)}", file=sys.stderr)
    
    # 去重（基于URL）
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    # 按可信度排序
    unique_results.sort(
        key=lambda x: calculate_credibility_score(x),
        reverse=True
    )
    
    print(f"\n共找到 {len(unique_results)} 篇不重复文章", file=sys.stderr)
    
    # 干运行模式：仅输出结果
    if args.dry_run:
        formatted_results = [
            format_article_for_display(article)
            for article in unique_results[:config.max_articles_to_push]
        ]
        
        if args.output == "json":
            print(json.dumps(formatted_results, ensure_ascii=False, indent=2))
        else:
            for idx, article in enumerate(formatted_results, 1):
                print(f"\n{idx}. {article['title']}")
                print(f"   来源: {article['source']}")
                print(f"   链接: {article['url']}")
                print(f"   摘要: {article['content'][:100]}...")
        
        return
    
    # 构建飞书卡片
    card = build_feishu_card(unique_results, config.max_articles_to_push)
    
    # 推送到飞书
    webhook_url = config.webhook_url
    if not webhook_url:
        print("错误: 未配置飞书Webhook URL", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n正在推送到飞书群...", file=sys.stderr)
    
    if push_to_feishu(webhook_url, card):
        print(f"✓ 推送成功！共推送 {min(len(unique_results), config.max_articles_to_push)} 篇文章", file=sys.stderr)
    else:
        print("✗ 推送失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
