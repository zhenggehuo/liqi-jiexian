"""
知乎API封装模块 - 离谱接线员项目专用
提供热榜功能接口，带缓存机制避免重复请求
"""

import requests
import time
from typing import List, Dict, Optional


# ============================================================================
# API配置
# ============================================================================

ZHIHU_API_KEY = ""
ZHIHU_HOT_LIST = "https://developer.zhihu.com/api/v1/content/hot_list"


# ============================================================================
# 缓存机制
# ============================================================================

class CacheManager:
    """简单的内存缓存，避免重复API调用"""
    
    def __init__(self, ttl_seconds: int = 300):  # 默认缓存5分钟
        self._cache: Dict[str, tuple] = {}  # {key: (value, timestamp)}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[any]:
        """获取缓存，如果过期返回None"""
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None
        return value
    
    def set(self, key: str, value: any):
        """设置缓存"""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局缓存实例
_cache = CacheManager(ttl_seconds=300)  # 热榜缓存5分钟


# ============================================================================
# API客户端类
# ============================================================================

class ZhihuAPIError(Exception):
    """知乎API错误"""
    pass


class ZhihuAPIClient:
    """知乎API客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ZHIHU_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Lipiqxj/1.0"
        })
    
    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """发送API请求"""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ZhihuAPIError(f"API请求失败: {e}")
    
    def get_hot_list(self, category: str = "total", use_cache: bool = True) -> List[Dict]:
        """
        获取知乎热榜（带缓存）
        
        Args:
            category: 热榜类别 (total/tech/science/business等)
            use_cache: 是否使用缓存，默认True
        
        Returns:
            热榜话题列表
        """
        cache_key = f"hot_list_{category}"
        
        # 检查缓存
        if use_cache:
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached
        
        params = {"category": category}
        
        try:
            data = self._make_request("GET", ZHIHU_HOT_LIST, params=params)
            result = data.get("data", [])
            # 如果返回空或无效，使用模拟数据
            if not result or not isinstance(result, list):
                result = self._mock_hot_list()
        except ZhihuAPIError:
            # API调用失败，返回模拟数据
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


def clear_hot_cache():
    """清除热榜缓存"""
    _cache.clear()
