"""
知乎API封装模块 - 离谱接线员项目专用
提供搜索、话题详情、问题回答等接口，带缓存机制

支持两种模式：
1. 模拟模式（默认）：基于话题关键词智能生成相关内容
2. 真实API模式：接入知乎开放平台API（需要配置ZHIHU_API_TOKEN）
"""

import requests
import time
import re
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime
import random

# ============================================================================
# API配置
# ============================================================================

ZHIHU_API_TOKEN = ""  # 知乎开放平台Token（可选）
ZHIHU_SEARCH_API = "https://www.zhihu.com/api/v4/search_v3"
ZHIHU_TOPIC_API = "https://www.zhihu.com/api/v4/topics"
ZHIHU_QUESTION_API = "https://www.zhihu.com/api/v4/questions"

# 缓存配置
DEFAULT_CACHE_TTL = 300  # 5分钟

# ============================================================================
# 缓存机制
# ============================================================================

class CacheManager:
    """简单的内存缓存，避免重复API调用"""
    
    def __init__(self, ttl_seconds: int = DEFAULT_CACHE_TTL):
        self._cache: Dict[str, tuple] = {}  # {key: (value, timestamp)}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存，如果过期返回None"""
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None
        return value
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys())
        }


# 全局缓存实例
_cache = CacheManager(ttl_seconds=DEFAULT_CACHE_TTL)


# ============================================================================
# 知乎内容模拟器 - 智能生成真实感的知乎内容
# ============================================================================

class ZhihuContentSimulator:
    """
    知乎内容模拟器
    
    基于话题关键词智能生成相关的知乎问题、回答摘要等内容。
    这些内容是结构化的，模拟真实知乎数据的格式，便于后续展示和处理。
    """
    
    # 知乎热门问题模板库
    QUESTION_TEMPLATES = [
        "{topic}是什么体验？",
        "如何看待{topic}？",
        "{topic}真的有用吗？",
        "如何正确理解{topic}？",
        "{topic}有哪些不为人知的秘密？",
        "为什么说{topic}被严重低估了？",
        "{topic}背后的底层逻辑是什么？",
        "普通人如何正确看待{topic}？",
        "{topic}的未来发展趋势是什么？",
        "你不知道的{topic}冷知识有哪些？",
    ]
    
    # 回答模板
    ANSWER_TEMPLATES = [
        "作为一个{topic}领域的从业者，我来分享一些真实的体验和看法。",
        "这个问题涉及到多个层面，让我从专业角度来解答。",
        "其实{topic}并没有大家想象的那么复杂，让我来帮你梳理一下。",
        "经过深入研究，我发现{topic}的本质其实很简单。",
        "关于{topic}，我想分享几个很少有人注意到的细节。",
    ]
    
    # 专业术语库（按领域）
    DOMAIN_TERMS = {
        "science": ["量子力学", "相对论", "弦理论", "暗物质", "量子纠缠", "熵增", "波粒二象性"],
        "tech": ["AI", "深度学习", "神经网络", "区块链", "元宇宙", "边缘计算", "量子计算"],
        "culture": ["哲学", "心理学", "社会学", "经济学", "历史", "文学", "艺术"],
        "life": ["健康", "饮食", "运动", "睡眠", "冥想", "习惯", "效率"],
        "business": ["创业", "投资", "管理", "营销", "品牌", "战略", "创新"],
    }
    
    @classmethod
    def generate_topic_context(cls, topic: str, num_questions: int = 3, num_answers: int = 2) -> Dict:
        """
        为话题生成模拟的知乎内容上下文
        
        Args:
            topic: 话题名称
            num_questions: 生成的问题数量
            num_answers: 每个问题的回答数量
        
        Returns:
            Dict: 包含话题信息和相关内容的字典
        """
        # 生成问题
        questions = []
        used_templates = set()
        
        for i in range(num_questions):
            template = random.choice([t for t in cls.QUESTION_TEMPLATES if t not in used_templates])
            used_templates.add(template)
            question_title = template.format(topic=topic)
            
            question = {
                "id": f"q_{hashlib.md5(f'{topic}_{i}'.encode()).hexdigest()[:8]}",
                "title": question_title,
                "url": f"https://www.zhihu.com/question/{random.randint(10000000, 99999999)}",
                "follower_count": random.randint(100, 50000),
                "answer_count": random.randint(5, 500),
                "created_time": int(time.time()) - random.randint(86400, 31536000),
                "updated_time": int(time.time()) - random.randint(0, 86400 * 30),
            }
            
            # 生成回答
            answers = []
            for j in range(num_answers):
                answer_author = random.choice([
                    "匿名用户", "知乎认证专家", "行业资深从业者", 
                    "热心知友", "相关领域研究者", "亲身经历者"
                ])
                
                # 生成回答摘要
                summary_template = random.choice(cls.ANSWER_TEMPLATES)
                key_term = random.choice(cls.DOMAIN_TERMS.get("culture", []))
                
                # 生成回答内容片段
                content_snippets = [
                    f"关于{topic}，我认为需要从多个维度来理解。首先，核心概念是...",
                    f"很多人对{topic}存在误解。实际上，它的关键在于...",
                    f"结合我自身的经验来看，{topic}最容易被忽视的一点是...",
                    f"从数据角度看，{topic}近年来呈现出以下趋势...",
                    f"有趣的发现：{topic}和{key_term}之间其实存在意想不到的联系...",
                ]
                
                answer = {
                    "id": f"a_{hashlib.md5(f'{topic}_{i}_{j}'.encode()).hexdigest()[:8]}",
                    "author_name": answer_author,
                    "author_follower_count": random.randint(50, 10000),
                    "voteup_count": random.randint(10, 5000),
                    "comment_count": random.randint(0, 200),
                    "excerpt": random.choice(content_snippets),
                    "content_length": random.randint(500, 3000),
                    "is_elite": random.random() > 0.7,  # 30%概率是精选回答
                    "created_time": int(time.time()) - random.randint(86400, 31536000 * 2),
                }
                answers.append(answer)
            
            # 按点赞数排序
            answers.sort(key=lambda x: x["voteup_count"], reverse=True)
            question["answers"] = answers
            question["top_answer"] = answers[0] if answers else None
            questions.append(question)
        
        # 生成话题详情
        topic_info = {
            "id": f"t_{hashlib.md5(topic.encode()).hexdigest()[:8]}",
            "name": topic,
            "url": f"https://www.zhihu.com/topic/{random.randint(10000000, 99999999)}",
            "followers_count": random.randint(1000, 500000),
            "questions_count": random.randint(5000, 200000),
            "description": f"关于{topic}的话题，汇聚了众多专业讨论和实践经验。",
            "related_topics": random.sample(
                [t for domain in cls.DOMAIN_TERMS.values() for t in domain if t != topic],
                min(5, 10)
            ),
        }
        
        return {
            "topic": topic_info,
            "questions": questions,
            "fetch_time": datetime.now().isoformat(),
            "source": "simulated",  # 标记为模拟数据
        }
    
    @classmethod
    def format_context_for_ai(cls, context: Dict, max_questions: int = 3, max_answer_length: int = 200) -> str:
        """
        将话题上下文格式化为AI可读的文本
        
        Args:
            context: 话题上下文
            max_questions: 最大问题数
            max_answer_length: 最大回答摘要长度
        
        Returns:
            str: 格式化后的文本
        """
        topic = context["topic"]
        questions = context["questions"][:max_questions]
        
        lines = [
            f"=== 话题信息 ===",
            f"话题名称：{topic['name']}",
            f"关注者数：{topic['followers_count']:,}",
            f"问题总数：{topic['questions_count']:,}",
            f"话题简介：{topic['description']}",
            "",
            f"=== 相关知乎讨论 ===",
        ]
        
        for i, q in enumerate(questions, 1):
            lines.append(f"\n【问题{i}】{q['title']}")
            lines.append(f"  关注者：{q['follower_count']:,} | 回答数：{q['answer_count']}")
            
            if q.get("top_answer"):
                ans = q["top_answer"]
                excerpt = ans["excerpt"]
                if len(excerpt) > max_answer_length:
                    excerpt = excerpt[:max_answer_length] + "..."
                lines.append(f"  热评摘要（{ans['voteup_count']}赞同 @{ans['author_name']}）：")
                lines.append(f"  {excerpt}")
        
        if topic.get("related_topics"):
            lines.append(f"\n=== 相关话题 ===")
            lines.append("、".join(topic["related_topics"]))
        
        return "\n".join(lines)


# ============================================================================
# API客户端类
# ============================================================================

class ZhihuAPIError(Exception):
    """知乎API错误"""
    pass


class ZhihuAPIClient:
    """
    知乎API客户端
    
    提供话题搜索、话题详情、问题回答等接口。
    优先使用真实API，失败时自动降级到模拟数据。
    """
    
    def __init__(self, api_token: str = None, use_simulator: bool = True):
        """
        初始化知乎API客户端
        
        Args:
            api_token: 知乎API Token（可选）
            use_simulator: 是否使用模拟器（默认True）
        """
        self.api_token = api_token or ZHIHU_API_TOKEN
        self.use_simulator = use_simulator
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
    
    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """发送API请求"""
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ZhihuAPIError(f"API请求失败: {e}")
    
    # -------------------------------------------------------------------------
    # 话题上下文获取（核心功能）
    # -------------------------------------------------------------------------
    
    def get_topic_context(self, topic: str, use_cache: bool = True) -> Dict:
        """
        获取话题的完整上下文（话题信息 + 相关问题 + 热门回答）
        
        这是项目的核心功能，将知乎内容组织成结构化的上下文供AI使用。
        
        Args:
            topic: 话题名称
            use_cache: 是否使用缓存
        
        Returns:
            Dict: 话题上下文
        """
        cache_key = f"topic_context_{topic}"
        
        # 检查缓存
        if use_cache:
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached
        
        # 尝试真实API
        context = None
        if self.api_token and not self.use_simulator:
            try:
                context = self._fetch_real_topic_context(topic)
            except ZhihuAPIError as e:
                print(f"真实API调用失败，降级到模拟数据: {e}")
        
        # 使用模拟数据
        if context is None:
            context = ZhihuContentSimulator.generate_topic_context(topic)
        
        # 存入缓存
        if use_cache:
            _cache.set(cache_key, context)
        
        return context
    
    def _fetch_real_topic_context(self, topic: str) -> Dict:
        """
        通过真实API获取话题上下文（需要知乎API Token）
        
        注意：知乎开放平台API需要申请，地址：https://open.zhihu.com
        """
        if not self.api_token:
            raise ZhihuAPIError("未配置知乎API Token")
        
        # 设置认证头
        headers = {
            "Authorization": f"Bearer {self.api_token}",
        }
        
        # 搜索话题
        search_url = f"{ZHIHU_SEARCH_API}"
        params = {
            "t": "general",
            "q": topic,
            "correction": 1,
            "offset": 0,
            "limit": 10,
        }
        
        response = self.session.get(search_url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            raise ZhihuAPIError(f"搜索API返回错误: {response.status_code}")
        
        data = response.json()
        questions = data.get("data", [])
        
        # TODO: 根据返回数据构建话题上下文
        # 这需要根据知乎开放平台的具体API来完善
        
        raise ZhihuAPIError("真实API对接功能开发中")
    
    # -------------------------------------------------------------------------
    # 话题详情
    # -------------------------------------------------------------------------
    
    def get_topic_info(self, topic_name: str, use_cache: bool = True) -> Dict:
        """
        获取话题详情
        
        Args:
            topic_name: 话题名称
            use_cache: 是否使用缓存
        
        Returns:
            Dict: 话题详情
        """
        context = self.get_topic_context(topic_name, use_cache)
        return context.get("topic", {})
    
    # -------------------------------------------------------------------------
    # 话题搜索
    # -------------------------------------------------------------------------
    
    def search_topics(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        搜索相关话题
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
        
        Returns:
            List[Dict]: 相关话题列表
        """
        cache_key = f"search_topics_{keyword}_{limit}"
        
        # 检查缓存
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached
        
        # 生成模拟搜索结果
        results = []
        for i in range(min(limit, 5)):
            term = random.choice(list(self.DOMAIN_TERMS.values())[0])
            results.append({
                "id": f"t_{hashlib.md5(f'{keyword}_{i}'.encode()).hexdigest()[:8]}",
                "name": f"{keyword} {term}" if i > 0 else keyword,
                "followers_count": random.randint(100, 100000),
                "match_score": 1.0 - (i * 0.15),  # 递减的匹配度
            })
        
        # 存入缓存
        _cache.set(cache_key, results)
        
        return results
    
    # -------------------------------------------------------------------------
    # 获取问题列表
    # -------------------------------------------------------------------------
    
    def get_topic_questions(self, topic_name: str, limit: int = 5) -> List[Dict]:
        """
        获取话题相关的问题
        
        Args:
            topic_name: 话题名称
            limit: 返回数量
        
        Returns:
            List[Dict]: 问题列表
        """
        context = self.get_topic_context(topic_name)
        questions = context.get("questions", [])
        return questions[:limit]
    
    # -------------------------------------------------------------------------
    # 获取回答摘要
    # -------------------------------------------------------------------------
    
    def get_question_answers(self, topic_name: str, question_index: int = 0, limit: int = 3) -> List[Dict]:
        """
        获取问题的回答摘要
        
        Args:
            topic_name: 话题名称
            question_index: 问题索引
            limit: 返回数量
        
        Returns:
            List[Dict]: 回答列表
        """
        context = self.get_topic_context(topic_name)
        questions = context.get("questions", [])
        
        if question_index < len(questions):
            answers = questions[question_index].get("answers", [])
            return answers[:limit]
        
        return []
    
    # -------------------------------------------------------------------------
    # 格式化输出
    # -------------------------------------------------------------------------
    
    def format_for_ai(self, topic_a: str, topic_b: str) -> str:
        """
        格式化两个话题的上下文，供AI生成脚本使用
        
        Args:
            topic_a: 第一个话题
            topic_b: 第二个话题
        
        Returns:
            str: 格式化的上下文文本
        """
        context_a = self.get_topic_context(topic_a)
        context_b = self.get_topic_context(topic_b)
        
        text_a = ZhihuContentSimulator.format_context_for_ai(context_a)
        text_b = ZhihuContentSimulator.format_context_for_ai(context_b)
        
        return f"""
{'='*60}
【话题A：{topic_a}】的知乎内容
{'='*60}
{text_a}

{'='*60}
【话题B：{topic_b}】的知乎内容
{'='*60}
{text_b}
"""
    
    def format_for_display(self, topic_a: str, topic_b: str) -> Dict[str, Any]:
        """
        格式化话题上下文，用于Streamlit界面展示
        
        Args:
            topic_a: 第一个话题
            topic_b: 第二个话题
        
        Returns:
            Dict: 包含展示所需数据的字典
        """
        context_a = self.get_topic_context(topic_a)
        context_b = self.get_topic_context(topic_b)
        
        return {
            "topic_a": {
                "name": topic_a,
                "info": context_a["topic"],
                "questions": context_a["questions"],
            },
            "topic_b": {
                "name": topic_b,
                "info": context_b["topic"],
                "questions": context_b["questions"],
            },
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    # -------------------------------------------------------------------------
    # 原有功能（保持兼容）
    # -------------------------------------------------------------------------
    
    def get_hot_list(self, category: str = "total", use_cache: bool = True) -> List[Dict]:
        """
        获取知乎热榜（带缓存）
        
        Args:
            category: 热榜类别
            use_cache: 是否使用缓存
        
        Returns:
            热榜话题列表
        """
        cache_key = f"hot_list_{category}"
        
        # 检查缓存
        if use_cache:
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached
        
        # 模拟热榜数据
        result = self._mock_hot_list()
        
        # 存入缓存
        if use_cache:
            _cache.set(cache_key, result)
        
        return result
    
    def _mock_hot_list(self) -> List[Dict]:
        """返回模拟热榜数据"""
        return [
            {"rank": 1, "title": "DeepSeek开源新模型对AI行业的影响", "heat": "5800万", "url": "#"},
            {"rank": 2, "title": "年轻人为什么开始拒绝无效社交？", "heat": "4200万", "url": "#"},
            {"rank": 3, "title": "AI时代哪些职业正在消失", "heat": "3500万", "url": "#"},
            {"rank": 4, "title": "2026年房价走势分析", "heat": "2900万", "url": "#"},
            {"rank": 5, "title": "考研还是就业？过来人怎么说", "heat": "2400万", "url": "#"},
            {"rank": 6, "title": "职场中如何优雅地拒绝加班", "heat": "2100万", "url": "#"},
            {"rank": 7, "title": "如何培养一个不焦虑的孩子", "heat": "1800万", "url": "#"},
            {"rank": 8, "title": "普通人如何抓住AI红利", "heat": "1600万", "url": "#"}
        ]


# ============================================================================
# 缓存管理函数
# ============================================================================

def clear_cache():
    """清除所有缓存"""
    _cache.clear()

def get_cache_stats() -> Dict:
    """获取缓存统计"""
    return _cache.get_stats()
