"""
知乎API封装模块 - 离谱接线员项目专用

支持两种模式：
1. 真实API模式（优先）：使用知乎开放平台API Key认证
2. 模拟模式（降级）：当真实API失败时使用结构化模拟数据

API Key配置：
- 环境变量：ZHIHU_API_KEY
- 默认Key：6gB7oguakanBSRXLT9alTXSlfkziabXs（用户提供的知乎开放平台Key）
"""

import requests
import time
import re
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime
import random
import os

# ============================================================================
# API配置
# ============================================================================

# 知乎开放平台API Key（优先从环境变量读取）
ZHIHU_API_KEY = os.getenv("ZHIHU_API_KEY", "6gB7oguakanBSRXLT9alTXSlfkziabXs")

# 知乎开放平台API端点（正确的热榜API）
ZHIHU_DEVELOPER_API = "https://developer.zhihu.com/api/v1/content/hot_list"

# 缓存配置
DEFAULT_CACHE_TTL = 300  # 5分钟

# ============================================================================
# 缓存机制
# ============================================================================

class CacheManager:
    """简单的内存缓存，避免重复API调用"""
    
    def __init__(self, ttl_seconds: int = DEFAULT_CACHE_TTL):
        self._cache: Dict[str, tuple] = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None
        return value
    
    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())
    
    def clear(self):
        self._cache.clear()
    
    def get_stats(self) -> Dict:
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys())
        }


_cache = CacheManager()


# ============================================================================
# 知乎API错误类
# ============================================================================

class ZhihuAPIError(Exception):
    """知乎API错误"""
    pass


# ============================================================================
# 知乎内容模拟器（降级备用）
# ============================================================================

class ZhihuContentSimulator:
    """知乎内容模拟器 - 当真实API不可用时使用"""
    
    QUESTION_TEMPLATES = [
        "{topic}是什么体验？",
        "如何看待{topic}？",
        "{topic}真的有用吗？",
        "如何正确理解{topic}？",
        "{topic}有哪些不为人知的秘密？",
        "为什么说{topic}被严重低估了？",
        "{topic}背后的底层逻辑是什么？",
        "普通人如何正确看待{topic}？",
    ]
    
    DOMAIN_TERMS = {
        "science": ["量子力学", "相对论", "暗物质", "量子纠缠"],
        "tech": ["AI", "深度学习", "神经网络", "区块链"],
        "culture": ["哲学", "心理学", "社会学", "经济学", "历史"],
        "life": ["健康", "饮食", "运动", "睡眠", "效率"],
        "business": ["创业", "投资", "管理", "营销", "创新"],
    }
    
    @classmethod
    def generate_topic_context(cls, topic: str, num_questions: int = 3) -> Dict:
        """为话题生成模拟的知乎内容上下文"""
        questions = []
        used_templates = set()
        
        for i in range(num_questions):
            template = random.choice([t for t in cls.QUESTION_TEMPLATES if t not in used_templates])
            used_templates.add(template)
            
            question = {
                "id": f"q_{hashlib.md5(f'{topic}_{i}'.encode()).hexdigest()[:8]}",
                "title": template.format(topic=topic),
                "url": f"https://www.zhihu.com/question/{random.randint(10000000, 99999999)}",
                "follower_count": random.randint(100, 50000),
                "answer_count": random.randint(5, 500),
                "top_answer": {
                    "author_name": random.choice(["知乎热心网友", "行业从业者", "研究者"]),
                    "voteup_count": random.randint(10, 5000),
                    "excerpt": f"关于{topic}，我认为需要从多个维度来理解..."
                }
            }
            questions.append(question)
        
        topic_info = {
            "id": f"t_{hashlib.md5(topic.encode()).hexdigest()[:8]}",
            "name": topic,
            "url": f"https://www.zhihu.com/topic/{random.randint(10000000, 99999999)}",
            "followers_count": random.randint(1000, 500000),
            "questions_count": random.randint(5000, 200000),
            "description": f"关于{topic}的话题，汇聚了众多专业讨论和实践经验。",
            "related_topics": [],
        }
        
        return {
            "topic": topic_info,
            "questions": questions,
            "fetch_time": datetime.now().isoformat(),
            "source": "simulated",
        }
    
    @classmethod
    def format_context_for_ai(cls, context: Dict, max_questions: int = 3) -> str:
        """将话题上下文格式化为AI可读的文本"""
        topic = context["topic"]
        questions = context["questions"][:max_questions]
        
        lines = [
            f"=== 话题信息 ===",
            f"话题名称：{topic['name']}",
            f"关注者数：{topic['followers_count']:,}",
            f"问题总数：{topic['questions_count']:,}",
            "",
            f"=== 相关知乎讨论 ===",
        ]
        
        for i, q in enumerate(questions, 1):
            lines.append(f"\n【问题{i}】{q['title']}")
            if q.get("top_answer"):
                ans = q["top_answer"]
                lines.append(f"  热评摘要（{ans['voteup_count']}赞同）：{ans['excerpt']}")
        
        return "\n".join(lines)


# ============================================================================
# 真实知乎API客户端
# ============================================================================

class ZhihuAPIClient:
    """
    知乎API客户端
    
    优先使用真实API：
    1. 热榜数据 - 使用知乎开放平台热榜API
    2. 话题数据 - 使用话题API
    
    当真实API不可用时，自动降级到模拟数据
    """
    
    def __init__(self, api_key: str = None):
        """
        初始化知乎API客户端
        
        Args:
            api_key: 知乎开放平台API Key，默认使用配置的Key
        """
        self.api_key = api_key or ZHIHU_API_KEY
        self.session = requests.Session()
        self._setup_headers()
        self._api_status = None  # None=未检测, True=可用, False=不可用
    
    def _setup_headers(self):
        """设置请求头"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.zhihu.com/",
        })
    
    def _get_auth_headers(self) -> Dict:
        """获取认证头（符合知乎开放平台API规范）"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Request-Timestamp": str(int(time.time())),
            "Content-Type": "application/json",
        }
    
    def _check_api_availability(self) -> bool:
        """检查API是否可用（使用热榜API检测）"""
        if self._api_status is not None:
            return self._api_status
        
        try:
            # 使用热榜API做检测（Limit=1即可）
            headers = self._get_auth_headers()
            response = self.session.get(
                ZHIHU_DEVELOPER_API,
                headers=headers,
                params={"Limit": 1},  # 注意：大写L
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # 检查返回的Code是否为0（成功）
                code = data.get("Code", -1)
                if code == 0:
                    self._api_status = True
                    print(f"✅ 知乎API验证成功: {self.api_key[:10]}...")
                    return True
                else:
                    self._api_status = False
                    self._print_api_error(code, data.get("Message", "未知错误"))
                    return False
            else:
                self._api_status = False
                print(f"⚠️ 知乎API返回HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            self._api_status = False
            print(f"❌ 知乎API不可用: {e}")
            return False
    
    def _print_api_error(self, code: int, message: str):
        """打印API错误信息"""
        error_messages = {
            20001: "鉴权失败，请检查API Key是否正确",
            30001: "频率限制，请稍后重试",
            90001: "知乎内部错误，请稍后重试",
        }
        msg = error_messages.get(code, message)
        print(f"⚠️ 知乎API错误 [{code}]: {msg}")
    
    def get_hot_list(self, limit: int = 10) -> List[Dict]:
        """
        获取知乎热榜 - 优先使用真实API，失败时降级到mock数据
        
        Args:
            limit: 返回数量
        
        Returns:
            List[Dict]: 热榜列表，永远不会返回None
        """
        try:
            cache_key = f"hot_list_{limit}"
            cached = _cache.get(cache_key)
            if cached is not None and isinstance(cached, list):
                return cached
            
            hot_list = []
            
            # 使用知乎开放平台热榜API
            if self._check_api_availability():
                try:
                    headers = self._get_auth_headers()
                    response = self.session.get(
                        ZHIHU_DEVELOPER_API,
                        headers=headers,
                        params={"Limit": limit},  # 注意：大写L
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        code = data.get("Code", -1)
                        if code == 0:
                            hot_list = self._parse_developer_hot_response(data, limit)
                        else:
                            self._print_api_error(code, data.get("Message", "未知错误"))
                    else:
                        print(f"⚠️ 知乎热榜API返回HTTP: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ 知乎热榜API调用失败: {e}")
            
            # 确保返回列表（降级到模拟数据）
            if not isinstance(hot_list, list) or not hot_list:
                hot_list = self._generate_mock_hot_list(limit)
            
            _cache.set(cache_key, hot_list)
            return hot_list
            
        except Exception as e:
            print(f"❌ get_hot_list异常: {e}")
            # 永远返回mock数据，不让应用崩溃
            return self._generate_mock_hot_list(limit)
    
    def _parse_developer_hot_response(self, data: Dict, limit: int) -> List[Dict]:
        """
        解析知乎开放平台热榜响应
        
        响应格式：
        {
            "Code": 0,
            "Message": "success",
            "Data": {
                "Total": 2,
                "Items": [
                    {
                        "Title": "问题标题",
                        "Url": "https://www.zhihu.com/question/123456789",
                        "ThumbnailUrl": "https://...",
                        "Summary": "摘要内容"
                    }
                ]
            }
        }
        """
        hot_list = []
        try:
            items = data.get("Data", {}).get("Items", [])
            for i, item in enumerate(items[:limit], 1):
                hot_list.append({
                    "rank": i,
                    "title": item.get("Title", ""),
                    "url": item.get("Url", ""),
                    "id": self._extract_question_id(item.get("Url", "")),
                    "hot_value": "",  # 该API没有热度值字段
                    "excerpt": item.get("Summary", ""),
                    "answer_count": 0,  # 该API没有回答数字段
                    "thumbnail": item.get("ThumbnailUrl", ""),
                })
        except Exception as e:
            print(f"解析热榜响应失败: {e}")
        return hot_list
    
    def _extract_question_id(self, url: str) -> str:
        """从知乎URL中提取问题ID"""
        if not url:
            return ""
        # URL格式: https://www.zhihu.com/question/123456789
        match = re.search(r'/question/(\d+)', url)
        if match:
            return match.group(1)
        return ""
    
    def _generate_mock_hot_list(self, limit: int = 10) -> List[Dict]:
        """生成模拟热榜（当真实API不可用时）"""
        # 使用更真实的热榜话题格式
        mock_titles = [
            "DeepSeek发布新模型对AI行业格局的影响",
            "年轻人为什么开始迷上玄学？",
            "为什么说2024是AI应用元年",
            "特斯拉FSD进入中国意味着什么",
            "拼多多市值超越阿里说明了什么",
            "为什么现在年轻人不愿意卷了",
            "新能源车渗透率超过50%意味着什么",
            "人口负增长对普通人意味着什么",
            "为什么大厂纷纷开始降本增效",
            "ChatGPT对教育行业的影响有多大"
        ]
        
        return [
            {
                "rank": i + 1,
                "title": mock_titles[i % len(mock_titles)],
                "url": f"https://www.zhihu.com/question/{10000000 + i}",
                "id": str(10000000 + i),
                "hot_value": "",
                "excerpt": "相关讨论正在进行中...",
                "answer_count": random.randint(100, 2000),
            }
            for i in range(min(limit, len(mock_titles)))
        ]
    
    def get_topic_context(self, topic: str, use_cache: bool = True) -> Dict:
        """
        获取话题的完整上下文
        
        优先使用真实API，失败后降级到模拟数据
        """
        cache_key = f"topic_context_{topic}"
        
        if use_cache:
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached
        
        context = None
        
        # 尝试从热榜中查找相关话题
        if self._check_api_availability():
            try:
                context = self._fetch_topic_from_api(topic)
            except Exception as e:
                print(f"获取话题上下文失败: {e}")
        
        # 如果没有获取到，使用模拟数据
        if context is None:
            context = ZhihuContentSimulator.generate_topic_context(topic)
        
        if use_cache:
            _cache.set(cache_key, context)
        
        return context
    
    def _fetch_topic_from_api(self, topic: str) -> Optional[Dict]:
        """从知乎API获取话题数据"""
        # 注意：当前API Key可能没有话题搜索权限，这里作为预留方法
        # 如果需要完整的话题功能，可能需要申请额外的API权限
        print(f"⚠️ 话题API需要额外权限，当前使用模拟数据")
        return None
    
    def format_for_ai(self, topic_a: str, topic_b: str) -> str:
        """格式化两个话题的上下文，供AI生成脚本使用"""
        context_a = self.get_topic_context(topic_a)
        context_b = self.get_topic_context(topic_b)
        
        text_a = ZhihuContentSimulator.format_context_for_ai(context_a)
        text_b = ZhihuContentSimulator.format_context_for_ai(context_b)
        
        source_a = "（来自知乎真实数据）" if context_a.get("source") == "zhihu_api" else "（基于话题内容生成）"
        source_b = "（来自知乎真实数据）" if context_b.get("source") == "zhihu_api" else "（基于话题内容生成）"
        
        return f"""
{'='*60}
【话题A：{topic_a}】的知乎内容{source_a}
{'='*60}
{text_a}

{'='*60}
【话题B：{topic_b}】的知乎内容{source_b}
{'='*60}
{text_b}
"""
    
    def format_for_display(self, topic_a: str, topic_b: str) -> Dict:
        """格式化两个话题的数据用于展示"""
        context_a = self.get_topic_context(topic_a)
        context_b = self.get_topic_context(topic_b)
        
        return {
            "topic_a": context_a,
            "topic_b": context_b,
            "fetch_time": datetime.now().isoformat(),
        }


# ============================================================================
# 缓存统计函数
# ============================================================================

def get_cache_stats() -> Dict:
    """获取缓存统计"""
    return _cache.get_stats()

def clear_cache():
    """清除缓存"""
    _cache.clear()


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("知乎API测试")
    print("=" * 50)
    print(f"API Key: {ZHIHU_API_KEY[:15]}...")
    
    client = ZhihuAPIClient()
    
    # 测试热榜
    print("\n📊 测试获取热榜...")
    hot_list = client.get_hot_list(limit=5)
    print(f"获取到 {len(hot_list)} 条热榜")
    for item in hot_list[:3]:
        print(f"  {item['rank']}. {item['title'][:40]}...")
        print(f"     URL: {item['url']}")
    
    # 测试话题
    print("\n📝 测试获取话题上下文...")
    context = client.get_topic_context("人工智能")
    print(f"话题: {context['topic']['name']}")
    print(f"关注者: {context['topic']['followers_count']:,}")
    print(f"数据来源: {context.get('source', 'unknown')}")
    
    print("\n✅ 测试完成!")
