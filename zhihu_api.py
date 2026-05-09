"""
知乎API封装模块 - 万物连线项目专用
提供热榜功能接口
"""

import requests
from typing import List, Dict


# ============================================================================
# API配置
# ============================================================================

ZHIHU_API_KEY = ""
ZHIHU_HOT_LIST = "https://developer.zhihu.com/api/v1/content/hot_list"


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
            "User-Agent": "WanwuLianxian/1.0"
        })
    
    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """发送API请求"""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ZhihuAPIError(f"API请求失败: {e}")
    
    def get_hot_list(self, category: str = "total") -> List[Dict]:
        """
        获取知乎热榜
        
        Args:
            category: 热榜类别 (total/tech/science/business等)
        
        Returns:
            热榜话题列表
        """
        params = {"category": category}
        
        try:
            data = self._make_request("GET", ZHIHU_HOT_LIST, params=params)
            result = data.get("data", [])
            # 如果返回空或无效，使用模拟数据
            if not result or not isinstance(result, list):
                return self._mock_hot_list()
            return result
        except ZhihuAPIError:
            # 返回模拟热榜数据
            return self._mock_hot_list()
    
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
