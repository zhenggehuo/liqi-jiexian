"""
离谱接线员 - 知乎 Hackathon 2026「灵感引擎」赛道参赛项目

核心功能：用户输入两个看似无关的知乎话题，AI在知乎内容库中找它们的隐藏联系，
用"离谱小国"风格输出知识叙事脚本。

作者：Hackathon Team
日期：2026年
"""

import streamlit as st
import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from zhihu_api import ZhihuAPIClient

# =============================================================================
# 配置区域
# =============================================================================

# 加载 .env 文件中的环境变量
load_dotenv()

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Prompt文件路径（支持相对路径和绝对路径）
PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), "prompts", "connector.md")


# =============================================================================
# 辅助函数
# =============================================================================

def load_prompt_template() -> str:
    """
    加载核心Prompt模板
    
    Returns:
        str: prompt模板内容
    """
    try:
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Prompt模板文件未找到：{PROMPT_FILE_PATH}")
        return ""


def build_user_prompt(topic_a: str, topic_b: str, prompt_template: str) -> str:
    """
    构建用户请求的完整prompt
    
    Args:
        topic_a: 第一个话题
        topic_b: 第二个话题
        prompt_template: prompt模板
    
    Returns:
        str: 完整的用户prompt
    """
    user_prompt = f"""请发现以下两个话题之间的隐藏联系，并用"离谱小国"风格生成知识叙事脚本：

话题A：{topic_a}
话题B：{topic_b}

请严格按照以下格式输出：
1. 【脚本标题】
2. 【开场Hook】2-3句话，制造认知冲突
3. 【主体内容】发现联系的过程，300-500字，有梗有料
4. 【素材关键词】3-5个配图关键词
5. 【彩蛋】可选，一句延伸思考

{prompt_template}"""
    return user_prompt


def call_deepseek_api(topic_a: str, topic_b: str, temperature: float = 0.8) -> tuple[bool, str]:
    """
    调用DeepSeek API生成内容
    
    Args:
        topic_a: 第一个话题
        topic_b: 第二个话题
        temperature: 创意度参数（0.1-1.0）
    
    Returns:
        tuple: (是否成功, 返回内容或错误信息)
    """
    # 检查 API Key
    if not DEEPSEEK_API_KEY:
        return False, "❌ API密钥未配置。请检查 .env 文件中的 DEEPSEEK_API_KEY"
    
    if DEEPSEEK_API_KEY == "你的API密钥":
        return False, "❌ 请在 .env 文件中设置正确的 DeepSeek API Key"
    
    try:
        # 加载 Prompt 模板
        prompt_template = load_prompt_template()
        if not prompt_template:
            return False, "❌ 无法加载Prompt模板"
        
        # 构建完整 prompt
        full_prompt = build_user_prompt(topic_a, topic_b, prompt_template)
        
        # 调用 DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一位顶尖的「知识接线员」，擅长发现万事万物之间看似不可能、实则精妙的隐藏联系，用'离谱小国'风格讲述知识故事。"
                },
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 2000,
            "stream": False
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        
        # 检查响应状态
        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", "未知错误")
            return False, f"❌ API调用失败 ({response.status_code}): {error_msg}"
        
        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        return True, content
        
    except requests.exceptions.Timeout:
        return False, "❌ 请求超时，请检查网络连接后重试"
    except requests.exceptions.RequestException as e:
        return False, f"❌ 网络请求失败: {str(e)}"
    except KeyError as e:
        return False, f"❌ 响应解析失败: {str(e)}"
    except Exception as e:
        return False, f"❌ 发生未知错误: {str(e)}"


def validate_input(topic_a: str, topic_b: str) -> tuple[bool, str]:
    """
    验证用户输入的有效性
    
    Args:
        topic_a: 第一个话题
        topic_b: 第二个话题
    
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not topic_a or not topic_b:
        return False, "请输入两个话题"
    
    if len(topic_a) > 50 or len(topic_b) > 50:
        return False, "话题长度不能超过50个字符"
    
    if topic_a.strip() == topic_b.strip():
        return False, "请输入两个不同的话题"
    
    return True, ""


# =============================================================================
# 预设示例脚本（演示用）
# =============================================================================

EXAMPLE_SCRIPTS = {
    "量子力学+泡茶": """
**【泡茶的时候，你其实在经历一场量子物理实验】**

你有没有想过，为什么有些茶要洗，有些茶直接泡？很多人会说"第一泡是醒茶"，但今天我要告诉你一个离谱的事实：**你泡茶的方式，正在完美复刻量子力学最诡异的实验。**

先别急着划走，这不是民科。让我给你讲一个故事。

你泡龙井的时候，有没有注意到茶叶在水里"跳舞"的样子？它们一会儿沉下去，一会儿浮上来，最后才慢慢舒展开来。这个过程，看起来平平无奇对吧？

但如果我们把视角缩小到微观世界呢？

**一片茶叶进入热水的瞬间，就像一个量子比特被"观测"。** 在量子力学里，有个著名的现象叫"量子隧穿"——粒子有一定的概率穿过本不该穿过的能量屏障。你可以理解为，茶叶里的香气分子们，正在玩命地"穿墙"。

而更有意思的是"叠加态"。在量子世界里，一个粒子可以同时处于多个状态，直到被观测才"坍缩"成确定状态。**你杯子里正在舒展的茶叶，其实正在经历一场"叠加态"的表演——它是"卷曲的"也是"舒展的"，是"冷的"也是"热的"，直到你喝下它，这一切都"坍缩"成一个确定的味道。**

所以现在你知道了，为什么好茶需要"醒"，为什么水温要控制，为什么你永远泡不出和茶艺师一模一样的味道——

**因为你每一次倒水，都在扮演"观察者"的角色。你的动作，正在决定这杯茶的"量子态"。**

下次泡茶的时候，记得对杯子说一声："今天，让我们共同创造一杯薛定谔的茶。"

---

📚 **素材关键词**：
- 量子隧穿示意图
- 茶叶微观结构
- 泡茶慢动作
- 叠加态示意图
- 薛定谔的猫

💡 **彩蛋**：下次你可以试试用冷水泡茶——量子力学告诉你，冷泡茶的"隧穿效应"会更明显哦。
""",
    
    "明朝+直播带货": """
**【如果郑和活到现在，他可能是李佳琦最强的竞争对手】**

先别笑，我认真的。

你知道郑和下西洋花了多少钱吗？根据记载，每次远航要动用200多艘船、27000多人，烧掉的银子换算成现在大概是几十个亿。搁现在，这排面，比薇娅带货还夸张。

但问题来了——**郑和带货，带的什么货？**

答案是：**大明王朝的流量**。

你仔细品品这个逻辑。郑和每到一处，就"赏赐"当地国王大量金银丝绸。表面上看，这是天朝上国的面子工程。但你仔细想想，这不就是最早的"战略性亏损引流"吗？

**郑和的"GMV"，是那些藩属国的朝贡热情。** 他们发现，只要派个使团来中国，进贡几根香料、几头长颈鹿，就能换回一船一船的稀世珍宝。这ROI，高到离谱。

而直播带货呢？头部主播告诉你："今天这个价格，是我跟品牌方谈了三天的结果。"品牌方心里苦，但不敢说——因为主播手里有流量。**流量在手，价格我有。这套玩法，郑和500年前就玩明白了。**

更绝的是，明朝还有一套"差评危机公关"机制。

万历年间，有个叫徐光启的大臣上了一道奏折，说："郑和下西洋这种赔本买卖，不能再搞了。"结果呢？万历皇帝直接把奏折扔进了垃圾桶。为什么？因为**郑和带回来的不只是奇珍异宝，更重要的是——大明王朝的"品牌溢价"。**

就像现在的直播间，品牌宁可亏本也要上链接，只为换一个"被李佳琦/薇娅推荐过"的标签。

所以你现在明白了吗？为什么明朝能成为当时世界上最富有的国家？为什么郑和能七下西洋？

**因为他们早就参透了直播带货的终极奥义：流量为王，谁掌握了流量，谁就掌握了定价权。**

下次看直播的时候，请对屏幕里的主播保持敬畏——他可能正在复刻一段500年前的商业传奇。

---

📚 **素材关键词**：
- 郑和下西洋船队
- 明朝海上贸易
- 直播带货现场
- 古代朝贡体系
- GMV数据图

💡 **彩蛋**：如果郑和有朋友圈，他可能会发："今日下西洋，带货GMV突破百万两，新品预告：暹罗犀牛角，明晚八点直播间不见不散。"
""",
    
    "抑郁症+黑洞": """
**【抑郁症患者的大脑里，可能正在上演一场宇宙级别的灾难】**

我今天要讲一个有点沉重，但可能帮助很多人理解抑郁症的话题。

首先问一个问题：**你知道黑洞是什么吗？**

简单来说，黑洞是一个引力强到连光都逃不出去的区域。一旦越过某个边界——叫做"事件视界"——你就再也回不来了。你发射的所有信号，你发出的所有光，都会被黑洞永远吞噬。

听起来很可怕对吧？但我告诉你，**这可能是对抑郁症最精准的物理学隐喻。**

你有没有过这种感觉：脑子里有一万个声音在告诉你"你不行的"、"没人喜欢你"、"活着有什么意义"？你想逃，想换个思路，想开心起来，但——做不到。就像有一只无形的手，把你牢牢按在黑暗里。

**那就是你脑子里的"事件视界"。**

心理学上有个概念叫"反刍思维"，就是负面情绪像一头牛一样反复咀嚼同一件事，越嚼越苦。而在黑洞的逻辑里，这叫"引力势阱"——一旦掉进去，你的所有"思维能量"都会被这个深渊吞噬，越挣扎，陷得越深。

但这还不是最可怕的部分。

**黑洞会"蒸发"。** 霍金发现，黑洞并不是永恒的，它会通过一种叫"霍金辐射"的方式缓慢释放能量，直到最终蒸发殆尽。

这像不像抑郁症患者的状态？**你的生命力、你的热情、你对未来的期待，正在以你察觉不到的速度流失。** 也许今天你还能笑一下，明天就不行了，后天连假装都懒得装了——因为能量不够用了。

所以我想对正在经历抑郁症的朋友说一句话：

**你脑子里的那个黑洞，是真实存在的，但它不是你的全部。** 就像科学家不断研究如何观测黑洞、预测黑洞一样，现代心理学也在不断破解抑郁症的密码。治疗、药物、陪伴、专业的帮助——这些都是你对抗"事件视界"的武器。

你不是一个人在对抗引力。有人在帮你发光。

---

📚 **素材关键词**：
- 黑洞事件视界示意图
- 抑郁症脑成像对比
- 霍金辐射概念图
- 心理咨询场景
- 光与暗的对比

💡 **彩蛋**：霍金说过"即使把我关在果壳之中，我仍然自以为无限宇宙之王。"——送给每一个正在经历黑暗的人，你比你想象的更强大。
"""
}


# =============================================================================
# Streamlit UI 部分
# =============================================================================

def main():
    """主函数"""
    
    # 页面配置
    st.set_page_config(
        page_title="离谱接线员 | 知乎 Hackathon",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 自定义CSS
    st.markdown("""
    <style>
    /* 主标题样式 */
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    /* 副标题样式 */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* 输入框标签样式 */
    .topic-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #444;
        margin-bottom: 0.5rem;
    }
    
    /* 生成按钮样式 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 输出卡片样式 */
    .output-card {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* 关键词标签样式 */
    .keyword-tag {
        display: inline-block;
        background: #e9ecef;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        color: #495057;
    }
    
    /* 加载动画样式 */
    .loading-text {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 标题区域
    st.markdown('<h1 class="main-title">🔗 离谱接线员</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">输入两个话题，发现意想不到的联系</p>', unsafe_allow_html=True)
    
    # API Key 状态检查
    api_status = ""
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "你的API密钥":
        api_status = "⚠️ API未配置"
        st.warning("🔑 请在 `.env` 文件中配置 DeepSeek API Key，否则将使用演示模式")
    
    # 初始化知乎API客户端
    zhihu_client = ZhihuAPIClient()
    
    # 初始化session状态
    if "generated_script" not in st.session_state:
        st.session_state.generated_script = None
    if "current_topics" not in st.session_state:
        st.session_state.current_topics = ("", "")
    
    # 主内容区域 - 分为左右两栏
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📝 输入话题")
        st.markdown("输入两个看似无关的话题，AI帮你发现它们之间的隐藏联系")
        
        # 话题输入框
        topic_a = st.text_input(
            "话题 A",
            value=st.session_state.current_topics[0],
            placeholder="例如：量子力学",
            help="输入第一个话题"
        )
        
        topic_b = st.text_input(
            "话题 B",
            value=st.session_state.current_topics[1],
            placeholder="例如：泡茶",
            help="输入第二个话题"
        )
        
        # 今日热榜功能
        st.markdown("---")
        st.markdown("### 🔥 今日热榜")
        
        if "show_hot_list" not in st.session_state:
            st.session_state.show_hot_list = False
        
        col_hot_btn, col_refresh = st.columns([1, 1])
        with col_hot_btn:
            if st.button("📊 查看知乎热榜", use_container_width=True):
                st.session_state.show_hot_list = True
        
        if st.session_state.show_hot_list:
            with st.spinner("加载热榜中..."):
                hot_list = zhihu_client.get_hot_list()
            
            st.markdown("**点击话题快速填入：**")
            
            # 热榜话题展示 - 2列布局
            hot_cols = st.columns(2)
            for i, item in enumerate(hot_list[:8]):
                with hot_cols[i % 2]:
                    if st.button(f"#{item['rank']} {item['title']}", key=f"hot_{item['rank']}", use_container_width=True):
                        # 轮流填入话题A或话题B
                        if not st.session_state.current_topics[0]:
                            topic_a = item['title']
                            st.session_state.current_topics = (topic_a, st.session_state.current_topics[1])
                            st.rerun()
                        else:
                            topic_b = item['title']
                            st.session_state.current_topics = (st.session_state.current_topics[0], topic_b)
                            st.rerun()
        
        # 示例快捷按钮
        st.markdown("**💡 快速示例：**")
        example_cols = st.columns(3)
        
        examples = [
            ("量子力学", "泡茶"),
            ("明朝", "直播带货"),
            ("抑郁症", "黑洞")
        ]
        
        for i, (ex_a, ex_b) in enumerate(examples):
            with example_cols[i]:
                if st.button(f"{ex_a}\n+ {ex_b}", key=f"example_{i}", use_container_width=True):
                    topic_a = ex_a
                    topic_b = ex_b
        
        # 高级选项（折叠）
        with st.expander("⚙️ 高级选项"):
            temperature = st.slider("🎨 创意度", min_value=0.1, max_value=1.0, value=0.8, step=0.1)
            st.caption("💡 创意度越高，输出越离谱；建议保持在 0.7-0.9 之间")
        
        # 生成按钮
        st.markdown("---")
        generate_button = st.button("🚀 发现隐藏联系", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### ✨ 生成结果")
        
        if generate_button:
            # 验证输入
            is_valid, error_msg = validate_input(topic_a, topic_b)
            
            if not is_valid:
                st.error(error_msg)
            else:
                # 保存当前话题
                st.session_state.current_topics = (topic_a, topic_b)
                
                # 显示加载状态
                with st.spinner("🔍 AI正在发现隐藏联系，请稍候..."):
                    # 调用 DeepSeek API
                    success, result = call_deepseek_api(topic_a, topic_b, temperature)
                    
                    if success:
                        # 保存到session
                        st.session_state.generated_script = result
                        
                        # 显示结果
                        st.success("✅ 发现隐藏联系成功！")
                        st.markdown(result)
                        
                        # 下载按钮
                        st.download_button(
                            label="📥 下载脚本",
                            data=result,
                            file_name=f"离谱接线员_{topic_a}_{topic_b}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    else:
                        # API 调用失败，显示错误信息
                        st.error(result)
                        
                        # 如果用户想看效果，提供演示示例
                        st.info("💡 你可以点击左侧的【快速示例】按钮查看预设效果")
        
        # 显示历史结果
        elif st.session_state.generated_script:
            st.markdown(st.session_state.generated_script)
            st.download_button(
                label="📥 下载脚本",
                data=st.session_state.generated_script,
                file_name="离谱接线员_结果.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            # 空状态提示
            st.info("👆 在左侧输入两个话题，点击按钮开始发现隐藏联系")
            
            # 显示示例展示区
            st.markdown("---")
            st.markdown("### 📖 效果预览")
            
            with st.expander("🔬 示例：量子力学 + 泡茶", expanded=False):
                st.markdown(EXAMPLE_SCRIPTS.get("量子力学+泡茶", ""))
            
            with st.expander("🏛️ 示例：明朝 + 直播带货", expanded=False):
                st.markdown(EXAMPLE_SCRIPTS.get("明朝+直播带货", ""))
            
            with st.expander("🕳️ 示例：抑郁症 + 黑洞", expanded=False):
                st.markdown(EXAMPLE_SCRIPTS.get("抑郁症+黑洞", ""))
    
    # 底部信息
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #999; font-size: 0.9rem;">
            <p>🔗 离谱接线员 | 知乎 Hackathon 2026「灵感引擎」赛道</p>
            <p>Powered by DeepSeek API | 发现知识之间的隐藏联系</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =============================================================================
# 程序入口
# =============================================================================

if __name__ == "__main__":
    main()
