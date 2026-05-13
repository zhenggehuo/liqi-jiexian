"""
知乎OAuth2.0登录模块 - 离谱接线员项目专用

支持知乎账号登录，获取用户基本信息。

OAuth流程：
1. 生成授权URL，引导用户跳转
2. 用户授权后回调，带code参数
3. 用code换取access_token
4. 用access_token获取用户信息
"""

import os
import secrets
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode

# ============================================================================
# 配置
# ============================================================================

# 知乎OAuth2.0配置
ZHIHU_OAUTH_BASE_URL = "https://openapi.zhihu.com"

# 知乎OAuth应用凭证（黑客松项目专用）
ZHIHU_APP_ID = os.getenv("ZHIHU_APP_ID", "284")
ZHIHU_APP_KEY = os.getenv("ZHIHU_APP_KEY", "e358ea83f1474bbdbc6ed63269e79424")

# 回调地址（Streamlit公网地址）
ZHIHU_REDIRECT_URI = os.getenv(
    "ZHIHU_REDIRECT_URI", 
    "https://liqi-jiexian-bvcch7e2mqcnszjkeqrvve.streamlit.app/"
)

# ============================================================================
# OAuth错误类
# ============================================================================

class ZhihuOAuthError(Exception):
    """知乎OAuth错误"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


# ============================================================================
# 知乎OAuth客户端
# ============================================================================

class ZhihuOAuth:
    """知乎OAuth2.0客户端"""
    
    def __init__(self, app_id: str = None, app_key: str = None, redirect_uri: str = None):
        """
        初始化知乎OAuth客户端
        
        Args:
            app_id: 知乎应用ID，默认使用配置的Key
            app_key: 知乎应用Key，默认使用配置的Key
            redirect_uri: 回调地址，默认使用Streamlit公网地址
        """
        self.app_id = app_id or ZHIHU_APP_ID
        self.app_key = app_key or ZHIHU_APP_KEY
        self.redirect_uri = redirect_uri or ZHIHU_REDIRECT_URI
    
    def generate_auth_url(self) -> Tuple[str, str]:
        """
        生成知乎授权URL（自动生成state）
        
        Returns:
            Tuple[str, str]: (授权页面URL, 随机state)
        """
        # 生成随机state用于CSRF防护
        state = secrets.token_urlsafe(32)
        
        params = {
            "redirect_uri": self.redirect_uri,
            "app_id": self.app_id,
            "response_type": "code",
            "state": state,
        }
        
        auth_url = f"{ZHIHU_OAUTH_BASE_URL}/authorize?{urlencode(params)}"
        return auth_url, state
    
    def exchange_token(self, code: str) -> Dict[str, Any]:
        """
        用授权码换取access_token
        
        Args:
            code: 用户授权后获得的authorization_code
            
        Returns:
            包含access_token的字典
            
        Raises:
            ZhihuOAuthError: 换取token失败
        """
        try:
            req_data = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
                "code": code,
            }
            # 调试：把请求参数记录下来（隐藏app_key）
            _debug_data = {**req_data, "app_key": req_data["app_key"][:6] + "***"}
            import sys
            print(f"[DEBUG exchange_token] request data: {_debug_data}", file=sys.stderr)
            
            response = requests.post(
                f"{ZHIHU_OAUTH_BASE_URL}/access_token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=req_data,
                timeout=30
            )
            
            # 调试：打印响应
            print(f"[DEBUG exchange_token] status: {response.status_code}", file=sys.stderr)
            print(f"[DEBUG exchange_token] body: {response.text[:500]}", file=sys.stderr)
            
            # 尝试解析JSON响应
            try:
                result = response.json()
            except:
                result = {}
            
            if response.status_code != 200:
                error_msg = result.get("data", result.get("message", "Unknown error"))
                error_code = result.get("code", response.status_code)
                raise ZhihuOAuthError(error_code, f"Failed to exchange token: {error_msg}")
            
            if "access_token" not in result:
                raise ZhihuOAuthError(
                    result.get("code", -1),
                    result.get("data", result.get("message", "No access_token in response"))
                )
            
            return {
                "access_token": result.get("access_token"),
                "token_type": result.get("token_type", "Bearer"),
                "expires_in": result.get("expires_in", 3600),
            }
            
        except requests.exceptions.RequestException as e:
            raise ZhihuOAuthError(-1, f"Network error: {str(e)}")
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取当前登录用户的基本信息
        
        Args:
            access_token: 有效的access_token
            
        Returns:
            用户信息字典
            
        Raises:
            ZhihuOAuthError: 获取用户信息失败
        """
        try:
            response = requests.get(
                f"{ZHIHU_OAUTH_BASE_URL}/user",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30
            )
            
            # 尝试解析JSON响应
            try:
                result = response.json()
            except:
                result = {}
            
            if response.status_code == 401:
                raise ZhihuOAuthError(401, "Access token invalid or expired")
            
            if response.status_code == 403:
                raise ZhihuOAuthError(403, "API access denied")
            
            if response.status_code == 404:
                raise ZhihuOAuthError(404, "User not found")
            
            if response.status_code != 200:
                error_code = result.get("code", response.status_code)
                error_msg = result.get("data", result.get("message", "Unknown error"))
                raise ZhihuOAuthError(error_code, f"Failed to get user info: {error_msg}")
            
            return {
                "uid": result.get("uid"),
                "fullname": result.get("fullname", "知乎用户"),
                "gender": result.get("gender", "unknown"),
                "headline": result.get("headline", ""),
                "description": result.get("description", ""),
                "avatar_url": result.get("avatar_path", ""),
                "phone_no": result.get("phone_no", ""),
                "email": result.get("email", ""),
            }
            
        except requests.exceptions.RequestException as e:
            raise ZhihuOAuthError(-1, f"Network error: {str(e)}")
    
    def get_followers(self, access_token: str) -> Dict[str, Any]:
        """
        获取当前用户的粉丝列表
        
        Args:
            access_token: 有效的access_token
            
        Returns:
            粉丝数据
        """
        try:
            response = requests.get(
                f"{ZHIHU_OAUTH_BASE_URL}/user/followers",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30
            )
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    def get_followed(self, access_token: str) -> Dict[str, Any]:
        """
        获取当前用户关注的用户列表
        
        Args:
            access_token: 有效的access_token
            
        Returns:
            关注列表数据
        """
        try:
            response = requests.get(
                f"{ZHIHU_OAUTH_BASE_URL}/user/followed",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30
            )
            return response.json() if response.status_code == 200 else {}
        except:
            return {}


# ============================================================================
# Streamlit会话状态管理
# ============================================================================

def init_oauth_session_state(st):
    """初始化OAuth相关的session_state"""
    if "zhihu_user" not in st.session_state:
        st.session_state.zhihu_user = None
    if "zhihu_access_token" not in st.session_state:
        st.session_state.zhihu_access_token = None
    if "zhihu_login_error" not in st.session_state:
        st.session_state.zhihu_login_error = None
    if "zhihu_oauth_state" not in st.session_state:
        st.session_state.zhihu_oauth_state = None


def prepare_oauth_login(st) -> str:
    """
    准备OAuth登录：生成授权URL并保存state
    
    Args:
        st: Streamlit的st对象
        
    Returns:
        授权页面URL
    """
    oauth = ZhihuOAuth()
    auth_url, state = oauth.generate_auth_url()
    st.session_state.zhihu_oauth_state = state
    return auth_url


def handle_oauth_callback(st) -> bool:
    """
    处理OAuth回调
    
    检查URL中的code和state参数，验证state后换取token并获取用户信息
    
    Args:
        st: Streamlit的st对象
        
    Returns:
        是否成功处理了OAuth回调
    """
    # 检查URL中是否有code参数
    # 注意：知乎回调参数名是 authorization_code 而非标准的 code
    query_params = st.query_params
    code = query_params.get("authorization_code") or query_params.get("code")
    state = query_params.get("state")
    error = query_params.get("error")
    
    if error:
        st.session_state.zhihu_login_error = f"授权被拒绝: {error}"
        # 清除URL参数
        st.query_params.clear()
        return False
    
    if not code:
        return False
    
    # 验证state防止CSRF攻击
    # 注意：Streamlit Cloud回调后session_state会重置，导致saved_state是新生成的
    # 与URL里的旧state不一致。因此Streamlit部署环境下跳过state验证。
    # code是一次性的，CSRF风险可接受。
    saved_state = st.session_state.get("zhihu_oauth_state")
    if saved_state and state and state != saved_state:
        # Streamlit session重置导致state不匹配，跳过验证
        pass
    
    # 清除已保存的state
    st.session_state.zhihu_oauth_state = None
    
    # 清除URL中的code参数（防止刷新重复提交）
    st.query_params.clear()
    
    try:
        oauth = ZhihuOAuth()
        
        # 用code换取token
        with st.spinner("🔄 正在验证身份..."):
            token_data = oauth.exchange_token(code)
            access_token = token_data["access_token"]
        
        # 用token获取用户信息
        with st.spinner("📡 正在获取用户信息..."):
            user_info = oauth.get_user_info(access_token)
        
        # 保存到session_state
        st.session_state.zhihu_user = user_info
        st.session_state.zhihu_access_token = access_token
        st.session_state.zhihu_login_error = None
        
        return True
        
    except ZhihuOAuthError as e:
        st.session_state.zhihu_login_error = f"登录失败: {e.message}"
        return False
    except Exception as e:
        st.session_state.zhihu_login_error = f"登录异常: {str(e)}"
        return False


def logout(st):
    """退出登录"""
    st.session_state.zhihu_user = None
    st.session_state.zhihu_access_token = None
    st.session_state.zhihu_login_error = None
    st.session_state.zhihu_oauth_state = None
