"""
离谱接线员 - 知乎 Hackathon 2026「灵感引擎」赛道参赛项目

核心功能：用户输入两个看似无关的知乎话题，AI发现它们之间的隐藏联系，
用"离谱小国"风格输出知识叙事脚本。

路演优化版：
- 预置精品案例（防翻车）
- 知乎蓝主题UI
- 轮播加载动画
- 知乎真实API接入
- 一键复制功能

作者：Hackathon Team
日期：2026年5月
"""

import streamlit as st
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from zhihu_api import ZhihuAPIClient, ZhihuContentSimulator, get_cache_stats, clear_cache

# =============================================================================
# 配置
# =============================================================================

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), "prompts", "connector.md")


# =============================================================================
# 预置精品案例（路演防翻车专用）
# =============================================================================

PREMIUM_EXAMPLES = {
    "始皇帝 × AI时代": {
        "topic_a": "秦始皇",
        "topic_b": "AI时代",
        "script": """**【如果秦始皇活在AI时代，他可能是最牛的产品经理】**

你有没有想过一个问题——

**秦始皇焚书坑儒的时候，有没有想过自己正在做一件很AI的事？**

等等别划走，我知道你在想什么：秦始皇？AI？这俩能有什么关系？

但你仔细想想——

**秦始皇这辈子干的最牛的事是什么？**

不是修长城，不是建阿房宫，而是——**统一**。

统一文字，所有人写同一种字；统一度量衡，所有人用同一把尺；统一货币，所有人花同一种钱。

这叫什么？

**这叫「数据标准化」！**

---

现在问题来了——

秦始皇统一六国之后，发现一个很离谱的问题：

*「我去，六国的文字居然有八种写法！」*

就像现在AI工程师的噩梦：**数据格式不统一**。

一个用户数据，这边写"北京朝阳区"，那边写"北京市-朝阳区"，那边写"BJ-Chaoyang"，你说AI怎么跑？

所以秦始皇干的第一件事，就是**强制数据清洗**。

李斯造了小篆，相当于古代的UTF-8编码——所有系统必须统一接入。

这波操作，搁现在就是——

**「强制迁移到云端，统一API接口，不迁移就封号！」**

---

然后你猜秦始皇还干了什么？

**他修了两条「数据高速公路」——秦直道。**

以咸阳为中心，修了几条超宽的马路，宽度足够三十辆马车并排跑。

这像什么？

**像现代的骨干网！**

想象一下，如果古代有互联网，秦始皇一定是那个建基站的。

而且他建的基站，还必须是「国家电网」——私人不许建，建了就是谋反。

就问你离谱不离谱。

---

但最绝的还在后头。

秦始皇死后，赵高搞了个「指鹿为马」。

一个很明显是鹿的东西，硬说成是马。

你知道这在AI领域叫什么吗？

**这叫「对抗样本攻击」！**

给AI看一张猫的照片，标注成狗，AI就会学坏。

秦始皇好不容易统一的数据标准，被赵高这一波操作搞得稀碎。

所以后来秦朝凉了——

**你品，这是不是一次经典的「数据污染导致的系统崩溃」？**

---

📚 **素材关键词**：
- 秦朝小篆/统一度量衡文物
- 秦直道遗址/古代高速公路
- 指鹿为马插画
- AI数据中心/服务器机房
- 数据流可视化图

💡 **彩蛋**：如果秦始皇有微信，他一定会发一条朋友圈：*「今日完成六国数据迁移，感谢李斯的996。」*
""",
        "emoji": "👑",
        "tags": ["历史", "科技", "格局炸裂"]
    },
    
    "相亲市场 × 推荐算法": {
        "topic_a": "相亲市场",
        "topic_b": "推荐算法",
        "script": """**【你为什么总遇不到对的人？】**

你有没有发现一个诡异的现象——

你在抖音刷到的每个视频都精准踩中你的xp（癖好）；
你在某宝看到的每件商品都是你想买的；
你在某红书刷到的每条笔记都像是「另一个你」发的。

**算法比你亲妈还懂你。**

但奇怪的是——

**为什么相亲软件给你推的人，你一个都看不上？**

这个问题，我研究了一下午，然后发现了一个人类终极困惑：

**算法推荐和相亲匹配，为什么差距这么大？**

---

先说抖音是怎么「懂你」的。

你刷到一个视频，停留了3秒，算法记下了：*「此人喜欢此类内容」*。

你又刷到一个，点了个赞，算法更新：*「此人极度喜欢此类内容，权重提升10倍」*。

**整个过程，就一个核心逻辑——**

**「你过去的行为，是你未来偏好的最好预测。」**

---

好了，现在把这个逻辑套到相亲上——

某相亲App的算法工程师小李，信心满满地写了一套「用户匹配系统」。

逻辑很简单：

*「用户A过去喜欢的人，B也喜欢类似的，所以A和B应该匹配。」*

**听起来没问题对吧？**

但问题是——

**你在抖音上刷到一个不喜欢的视频，你会立刻划走。**

**你在相亲市场上遇到一个不合适的人，你会礼貌地吃完那顿饭。**

**你不会给相亲对象「点踩」。**

**你只会微笑着「下次再约」，然后再也不约。**

---

所以算法的数据从哪来？

**从「成功匹配」的用户来。**

谁成功了？

那些第一次约会就干柴烈火的、那些双方都立刻确认心意的。

但问题是——

**这些人根本不需要相亲软件啊！**

他们在酒吧认识、在公司认识、在朋友圈认识——早就脱单了。

留下来的用户是什么？

**是一群嘴上说「我要认真找对象」，实际上连「要不要继续聊」都要纠结三天的——**

**选择困难症患者！**

---

更绝的来了——

算法为了提高「匹配成功率」，会给你推**你大概率会右滑的人**。

什么是「你大概率会右滑的人」？

**和你前任长得像的。**

**和你crush风格相似的。**

**和你「理想型画像」重合度最高的。**

然后你就陷入了一个死循环：

*前任是渣 → 我喜欢渣 → 算法推渣 → 我继续被渣 → 我单身*

**推荐算法不是在帮你脱单，**

**它是在帮你强化你的「择偶偏见」。**

---

📚 **素材关键词**：
- 相亲角/人民公园相亲角
- 算法推荐流程图
- 手机滑动匹配界面
- 抖音推荐机制示意图

💡 **彩蛋**：故意去刷那些你「绝对不会喜欢」的内容，让算法以为你口味变了——这不是作弊，这是**数据攻防战**。
""",
        "emoji": "💕",
        "tags": ["职场", "共鸣", "扎心"]
    },
    
    "WiFi信号 × 玄学": {
        "topic_a": "WiFi信号",
        "topic_b": "玄学风水",
        "script": """**【你家的WiFi信号差，可能跟风水有关——物理学家沉默了】**

说出来你可能不信，**WiFi信号的传播模型，其实跟道家"气"的运行逻辑一毛一样**。

你敢信？一个用麦克斯韦方程组算出来的现代科技，一个拿罗盘测了几千年的玄学，居然能对上号——但这不是玄学，是物理。

你想想，为什么你家路由器放在客厅，卧室信号就弱？

因为你家**墙角、承重墙、金属家具**就是风水里的"煞气"啊。

"煞"的本质是气场被打断、被阻隔，WiFi电磁波撞上钢筋混凝土，直接反射、折射、衰减——这不就是"气运受阻"吗？

物理学叫"多径效应"，玄学叫"穿堂煞"，名字不同，底层逻辑一模一样。

---

更有意思的是，WiFi的天线朝向、摆放位置，跟风水学里的"藏风聚气"异曲同工。

风水讲究"前低后高、左青龙右白虎"，本质上是在寻找最优的能量通道；

而WiFi工程师告诉你，天线要垂直地面、远离墙角、避开金属反射面——

**一个是给"气"找路，一个是给"电磁波"找路**，人类对"看不见的能量"的直觉，跨越千年还是那套思维模式。

---

所以下次你妈说"路由器别放西南角，那个方位'火煞'太重"，你别急着笑——

**因为西南角通常是厨房，电磁炉、微波炉一开，2.4GHz频段直接干扰你WiFi**

她说的火煞，是真实的电磁干扰。

你敢说这是迷信？

---

📚 **素材关键词**：
- 路由器被卡在墙角的搞笑插画
- 风水罗盘和WiFi信号热力图对比
- 承重墙内钢筋和电磁波反射示意图
- 穿堂煞与信号衰减的知乎体对比图

💡 **彩蛋**：下期聊聊"为什么你在厕所刷手机信号最好"——不是玄学，是尿急产生的生物磁场（不是）。
""",
        "emoji": "📶",
        "tags": ["生活", "有趣", "破防"]
    },
    
    "量子力学 × 泡茶": {
        "topic_a": "量子力学",
        "topic_b": "泡茶",
        "script": """**【泡茶的时候，你其实在经历一场量子物理实验】**

你有没有想过，为什么有些茶要洗，有些茶直接泡？

很多人会说"第一泡是醒茶"，但今天我要告诉你一个离谱的事实：

**你泡茶的方式，正在完美复刻量子力学最诡异的实验。**

先别急着划走，这不是民科。让我给你讲一个故事。

你泡龙井的时候，有没有注意到茶叶在水里"跳舞"的样子？

它们一会儿沉下去，一会儿浮上来，最后才慢慢舒展开来。

这个过程，看起来平平无奇对吧？

但如果我们把视角缩小到微观世界呢？

---

**一片茶叶进入热水的瞬间，就像一个量子比特被"观测"。**

在量子力学里，有个著名的现象叫"量子隧穿"——粒子有一定的概率穿过本不该穿过的能量屏障。

你可以理解为，茶叶里的香气分子们，正在玩命地"穿墙"。

而更有意思的是"叠加态"。

在量子世界里，一个粒子可以同时处于多个状态，直到被观测才"坍缩"成确定状态。

**你杯子里正在舒展的茶叶，其实正在经历一场"叠加态"的表演——**

**它是"卷曲的"也是"舒展的"，是"冷的"也是"热的"，直到你喝下它，这一切都"坍缩"成一个确定的味道。**

---

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
        "emoji": "☕",
        "tags": ["科普", "硬核", "玄学"]
    },
    
    "明朝 × 直播带货": {
        "topic_a": "明朝",
        "topic_b": "直播带货",
        "script": """**【如果郑和活到现在，他可能是李佳琦最强的竞争对手】**

先别笑，我认真的。

你知道郑和下西洋花了多少钱吗？

根据记载，每次远航要动用200多艘船、27000多人，烧掉的银子换算成现在大概是几十个亿。

搁现在，这排面，比薇娅带货还夸张。

但问题来了——

**郑和带货，带的什么货？**

答案是：**大明王朝的流量**。

---

你仔细品品这个逻辑。

郑和每到一处，就"赏赐"当地国王大量金银丝绸。

表面上看，这是天朝上国的面子工程。

但你仔细想想，这不就是最早的"战略性亏损引流"吗？

**郑和的"GMV"，是那些藩属国的朝贡热情。**

他们发现，只要派个使团来中国，进贡几根香料、几头长颈鹿，就能换回一船一船的稀世珍宝。

这ROI，高到离谱。

而直播带货呢？

头部主播告诉你："今天这个价格，是我跟品牌方谈了三天的结果。"

品牌方心里苦，但不敢说——因为主播手里有流量。

**流量在手，价格我有。这套玩法，郑和500年前就玩明白了。**

---

更绝的是，明朝还有一套"差评危机公关"机制。

万历年间，有个叫徐光启的大臣上了一道奏折，说："郑和下西洋这种赔本买卖，不能再搞了。"

结果呢？万历皇帝直接把奏折扔进了垃圾桶。

为什么？

因为**郑和带回来的不只是奇珍异宝，更重要的是——大明王朝的"品牌溢价"。**

就像现在的直播间，品牌宁可亏本也要上链接，只为换一个"被推荐过"的标签。

---

所以你现在明白了吗？

为什么明朝能成为当时世界上最富有的国家？

为什么郑和能七下西洋？

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
        "emoji": "🏴",
        "tags": ["历史", "商业", "大开眼界"]
    }
}


# =============================================================================
# 加载动画文案
# =============================================================================

LOADING_MESSAGES = [
    "🤔 接线员正在疯狂联想中...",
    "🔮 正在挖掘知识的隐藏副本...",
    "⚡ 激活知识跨界模式...",
    "🎭 正在寻找离谱的联系...",
    "🧠 接线员大脑高速运转中...",
    "🌐 正在连接两个平行宇宙...",
    "✨ 发现隐藏成就：离谱接线...",
    "📡 正在校准知识频道...",
]


# =============================================================================
# 辅助函数
# =============================================================================

def load_prompt_template() -> str:
    try:
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Prompt模板文件未找到：{PROMPT_FILE_PATH}")
        return ""


def build_user_prompt(topic_a: str, topic_b: str, prompt_template: str, 
                      zhihu_context: str = "") -> str:
    if zhihu_context:
        context_section = f"""
{'='*60}
【以下是来自知乎的真实内容，请基于这些内容发现话题之间的联系】
{'='*60}
{zhihu_context}

{'='*60}
请根据以上知乎真实内容，发现话题A和话题B之间的隐藏联系。
{'='*60}
"""
    else:
        context_section = ""
    
    return f"""请发现以下两个话题之间的隐藏联系，并用"离谱小国"风格生成知识叙事脚本：

话题A：{topic_a}
话题B：{topic_b}
{context_section}
请严格按照以下格式输出：
1. 【脚本标题】
2. 【开场Hook】2-3句话，制造认知冲突
3. 【主体内容】发现联系的过程，300-500字，有梗有料
4. 【素材关键词】3-5个配图关键词
5. 【彩蛋】可选，一句延伸思考

{prompt_template}"""


def call_deepseek_api(topic_a: str, topic_b: str, zhihu_context: str = "",
                       temperature: float = 0.8) -> tuple[bool, str]:
    if not DEEPSEEK_API_KEY:
        return False, "❌ API密钥未配置。请检查 .env 文件中的 DEEPSEEK_API_KEY"
    
    if DEEPSEEK_API_KEY == "你的API密钥":
        return False, "❌ 请在 .env 文件中设置正确的 DeepSeek API Key"
    
    try:
        prompt_template = load_prompt_template()
        if not prompt_template:
            return False, "❌ 无法加载Prompt模板"
        
        full_prompt = build_user_prompt(topic_a, topic_b, prompt_template, zhihu_context)
        
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
            "max_tokens": 2500,
            "stream": False
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=90)
        
        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", "未知错误")
            return False, f"❌ API调用失败 ({response.status_code}): {error_msg}"
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        return True, content
        
    except requests.exceptions.Timeout:
        return False, "❌ 请求超时，请检查网络连接后重试"
    except requests.exceptions.RequestException as e:
        return False, f"❌ 网络请求失败: {str(e)}"
    except KeyError:
        return False, "❌ 响应解析失败"
    except Exception as e:
        return False, f"❌ 发生未知错误: {str(e)}"


def validate_input(topic_a: str, topic_b: str) -> tuple[bool, str]:
    if not topic_a or not topic_b:
        return False, "请输入两个话题"
    if len(topic_a) > 50 or len(topic_b) > 50:
        return False, "话题长度不能超过50个字符"
    if topic_a.strip() == topic_b.strip():
        return False, "请输入两个不同的话题"
    return True, ""


# =============================================================================
# Streamlit UI
# =============================================================================

def main():
    st.set_page_config(
        page_title="离谱接线员 | 知乎 Hackathon 2026",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS样式
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f8faff 0%, #e8f4ff 100%); }
    
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #0066FF 0%, #00A0FF 50%, #7C4DFF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 0.3rem; letter-spacing: -1px;
    }
    .subtitle { text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem; }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%); border-right: 1px solid #e0e8f5; }
    .sidebar-title { font-size: 1.2rem; font-weight: 700; color: #0066FF; margin-bottom: 0.8rem; padding-bottom: 0.5rem; border-bottom: 2px solid #0066FF; }
    
    .premium-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
        border: 1px solid #e0e8f5; border-radius: 12px; padding: 0.8rem;
        margin: 0.6rem 0; cursor: pointer; transition: all 0.3s ease;
        position: relative; overflow: hidden;
    }
    .premium-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 102, 255, 0.15); border-color: #0066FF; }
    .premium-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #0066FF, #00A0FF); }
    .card-emoji { font-size: 1.3rem; margin-right: 0.5rem; }
    .card-title { font-weight: 600; color: #333; font-size: 0.95rem; }
    .card-tags { display: flex; gap: 0.3rem; margin-top: 0.4rem; flex-wrap: wrap; }
    .tag { background: #e8f4ff; color: #0066FF; padding: 0.1rem 0.4rem; border-radius: 8px; font-size: 0.65rem; font-weight: 500; }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0066FF 0%, #0052CC 100%);
        color: white; border: none; padding: 0.8rem 2rem;
        font-size: 1.1rem; font-weight: 700; border-radius: 12px;
        transition: all 0.3s ease; width: 100%;
        box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 102, 255, 0.4); }
    
    .output-card { background: #ffffff; border-radius: 16px; padding: 1.5rem; margin: 1rem 0; border: 1px solid #e0e8f5; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); }
    
    .loading-container { text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8faff 0%, #e8f4ff 100%); border-radius: 12px; margin: 1rem 0; }
    .loading-text { font-size: 1.2rem; color: #0066FF; font-weight: 600; animation: pulse 1.5s ease-in-out infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    
    .success-box { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border: 1px solid #81c784; border-radius: 10px; padding: 1rem; margin: 1rem 0; }
    
    .demo-badge { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 0.25rem 0.6rem; border-radius: 15px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin-bottom: 0.8rem; }
    
    .history-item { background: #f8faff; border-radius: 8px; padding: 0.5rem 0.7rem; margin: 0.3rem 0; font-size: 0.8rem; border-left: 3px solid transparent; }
    .history-item:hover { border-left-color: #0066FF; }
    
    .footer { text-align: center; color: #999; font-size: 0.85rem; padding: 1.5rem 0; margin-top: 2rem; border-top: 1px solid #e0e8f5; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # ==========================================================================
    # 侧边栏
    # ==========================================================================
    with st.sidebar:
        st.markdown('<p class="demo-badge">🎯 路演防翻车专用</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">⚡ 预置精品案例</p>', unsafe_allow_html=True)
        st.caption("👆 点击直接查看，无需等待AI生成")
        
        if "connection_history" not in st.session_state:
            st.session_state.connection_history = []
        
        for name, data in PREMIUM_EXAMPLES.items():
            if st.button(f"{data['emoji']} {name}", key=f"btn_{name}", use_container_width=True):
                st.session_state.selected_example = name
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📜 本次接线历史")
        if st.session_state.connection_history:
            for a, b, _ in st.session_state.connection_history[-5:]:
                st.markdown(f'<div class="history-item">🔗 {a} × {b}</div>', unsafe_allow_html=True)
        else:
            st.caption("暂无接线记录")
        
        st.markdown("---")
        with st.expander("🔧 系统状态"):
            st.json(get_cache_stats())
            if st.button("🗑️ 清除缓存"):
                clear_cache()
                st.cache_data.clear()
                st.success("缓存已清除")
                st.rerun()
    
    # ==========================================================================
    # 主内容
    # ==========================================================================
    st.markdown('<h1 class="main-title">🔗 离谱接线员</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">发现两个话题之间的隐藏联系，用"离谱小国"风格讲知识故事</p>', unsafe_allow_html=True)
    
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "你的API密钥":
        st.warning("🔑 请在 `.env` 文件中配置 DeepSeek API Key，否则将使用演示模式")
    
    zhihu_client = ZhihuAPIClient()
    
    if "generated_script" not in st.session_state:
        st.session_state.generated_script = None
    if "current_topics" not in st.session_state:
        st.session_state.current_topics = ("", "")
    if "zhihu_context" not in st.session_state:
        st.session_state.zhihu_context = {}
    if "selected_example" not in st.session_state:
        st.session_state.selected_example = None
    
    # ==========================================================================
    # 布局
    # ==========================================================================
    col1, col2 = st.columns([1, 1.3], gap="large")
    
    with col1:
        st.markdown("### 📝 输入话题")
        st.markdown("输入两个看似无关的话题，AI帮你发现它们之间的隐藏联系")
        
        topic_a = st.text_input("话题 A", value=st.session_state.current_topics[0], 
                                placeholder="例如：量子力学", key="topic_a_input")
        topic_b = st.text_input("话题 B", value=st.session_state.current_topics[1], 
                                placeholder="例如：泡茶", key="topic_b_input")
        
        with st.expander("⚙️ 高级选项"):
            temperature = st.slider("🎨 创意度", min_value=0.1, max_value=1.0, value=0.8, step=0.1)
            st.caption("💡 创意度越高，输出越离谱")
        
        generate_button = st.button("🚀 发现隐藏联系", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🔥 今日知乎热榜")
        
        # ==========================================================================
        # 热榜自动加载（使用session_state缓存，5分钟自动刷新）
        # ==========================================================================
        HOT_CACHE_TTL = 300  # 5分钟缓存
        
        # 初始化热榜相关session_state
        if "hot_list" not in st.session_state:
            st.session_state.hot_list = []
        if "hot_list_fetch_time" not in st.session_state:
            st.session_state.hot_list_fetch_time = None
        if "hot_list_source" not in st.session_state:
            st.session_state.hot_list_source = None  # "real" 或 "mock"
        
        # 检查是否需要刷新（缓存过期或首次加载）
        need_refresh = False
        if not st.session_state.hot_list:
            need_refresh = True
        elif st.session_state.hot_list_fetch_time:
            elapsed = time.time() - st.session_state.hot_list_fetch_time
            if elapsed > HOT_CACHE_TTL:
                need_refresh = True
        
        # 自动加载热榜数据
        if need_refresh:
            with st.spinner("📡 加载知乎热榜..."):
                try:
                    hot_result = zhihu_client.get_hot_list(limit=8)
                    
                    # 确保是列表
                    if isinstance(hot_result, list) and hot_result:
                        st.session_state.hot_list = hot_result
                        st.session_state.hot_list_fetch_time = time.time()
                        # 判断数据来源：通过hot_value是否包含"+"来判断（mock数据用50000+格式）
                        first_hot_value = hot_result[0].get('hot_value', '') if isinstance(hot_result[0], dict) else ''
                        st.session_state.hot_list_source = "real" if first_hot_value and not first_hot_value.endswith("+") else "mock"
                    else:
                        st.session_state.hot_list = []
                        st.session_state.hot_list_source = "mock"
                except Exception as e:
                    # 静默降级到mock数据
                    st.session_state.hot_list = zhihu_client._generate_mock_hot_list(8)
                    st.session_state.hot_list_source = "mock"
                    st.session_state.hot_list_fetch_time = time.time()
        
        # 显示数据来源和时间
        source_label = "🔴 实时" if st.session_state.hot_list_source == "real" else "🟡 示例数据"
        if st.session_state.hot_list_fetch_time:
            fetch_time = datetime.fromtimestamp(st.session_state.hot_list_fetch_time).strftime("%H:%M")
            time_hint = f"更新于 {fetch_time}"
        else:
            time_hint = ""
        
        col_source, col_refresh = st.columns([3, 1])
        with col_source:
            if st.session_state.hot_list:
                st.caption(f"{source_label} · {time_hint}" if time_hint else source_label)
        with col_refresh:
            if st.button("🔄", key="refresh_hot", use_container_width=True):
                st.session_state.hot_list = []
                st.session_state.hot_list_fetch_time = None
                st.rerun()
        
        # 显示热榜列表
        if st.session_state.hot_list:
            st.markdown("**点击快速填入：**")
            hot_cols = st.columns(2)
            for i, item in enumerate(st.session_state.hot_list[:6]):
                title = item.get('title', '未知话题')[:18] if isinstance(item, dict) else str(item)[:18]
                rank = item.get('rank', i+1) if isinstance(item, dict) else i+1
                hot_value = item.get('hot_value', '') if isinstance(item, dict) else ''
                
                # 构建按钮标签
                label = f"#{rank} {title}..."
                if hot_value:
                    label += f"\n{hot_value}"
                
                with hot_cols[i % 2]:
                    if st.button(label, key=f"hot_{rank}", use_container_width=True):
                        item_title = item.get('title', '') if isinstance(item, dict) else str(item)
                        if not st.session_state.current_topics[0]:
                            topic_a = item_title
                        else:
                            topic_b = item_title
                        st.session_state.current_topics = (topic_a, topic_b)
                        st.rerun()
        else:
            st.info("暂无热榜数据，请手动输入话题")
        
        st.markdown("---")
        st.markdown("### 💡 快速体验")
        st.caption("点击直接查看精品案例")
        quick_cols = st.columns(2)
        for i, (name, data) in enumerate(list(PREMIUM_EXAMPLES.items())[:4]):
            with quick_cols[i % 2]:
                if st.button(f"{data['emoji']} {name[:12]}", key=f"quick_{i}", use_container_width=True):
                    st.session_state.selected_example = name
                    st.rerun()
    
    # ==========================================================================
    # 结果展示
    # ==========================================================================
    with col2:
        st.markdown("### ✨ 生成结果")
        
        # 预置案例展示
        if st.session_state.selected_example:
            name = st.session_state.selected_example
            data = PREMIUM_EXAMPLES[name]
            
            st.session_state.generated_script = data["script"]
            st.session_state.current_topics = (data["topic_a"], data["topic_b"])
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                        border-radius: 12px; padding: 1rem; margin-bottom: 1rem; 
                        border-left: 4px solid #0066FF;">
                <strong>🎯 预置精品案例</strong> | {data['emoji']} {data['topic_a']} × {data['topic_b']}
                <div style="margin-top: 0.5rem;">
                    {"".join([f'<span class="tag">{tag}</span>' for tag in data['tags']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="output-card">{data["script"]}</div>', unsafe_allow_html=True)
            
            col_copy, col_dl = st.columns(2)
            with col_copy:
                st.session_state.last_copied = data["script"]
                st.success("📋 已准备好复制")
            with col_dl:
                st.download_button("📥 下载脚本", data["script"],
                                  file_name=f"离谱接线员_{data['topic_a']}_{data['topic_b']}.md",
                                  mime="text/markdown", use_container_width=True)
            
            st.info("💡 点击左侧案例按钮可快速切换其他案例")
        
        # AI生成
        elif generate_button:
            is_valid, error_msg = validate_input(topic_a, topic_b)
            
            if not is_valid:
                st.error(error_msg)
            else:
                st.session_state.current_topics = (topic_a, topic_b)
                st.session_state.connection_history.append((topic_a, topic_b, datetime.now().strftime("%H:%M")))
                
                with st.spinner("🔍 正在搜索知乎相关内容..."):
                    try:
                        display_data = zhihu_client.format_for_display(topic_a, topic_b)
                        zhihu_context_str = zhihu_client.format_for_ai(topic_a, topic_b)
                    except Exception as e:
                        st.warning(f"知乎数据获取失败，使用模拟数据: {e}")
                        # 降级到模拟数据
                        display_data = {
                            "topic_a": ZhihuContentSimulator.generate_topic_context(topic_a),
                            "topic_b": ZhihuContentSimulator.generate_topic_context(topic_b),
                            "fetch_time": datetime.now().isoformat(),
                        }
                        zhihu_context_str = ZhihuContentSimulator.format_context_for_ai(display_data["topic_a"]) + "\n\n" + ZhihuContentSimulator.format_context_for_ai(display_data["topic_b"])
                
                st.session_state.zhihu_context = display_data
                
                st.markdown('<div class="success-box"><strong>✅ 已从知乎获取相关内容</strong></div>', unsafe_allow_html=True)
                
                st.markdown("#### 📊 话题数据来源")
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.markdown(f"**📌 {topic_a}**")
                    info_a = display_data["topic_a"]["topic"]
                    st.metric("关注者", f"{info_a.get('followers_count', 0):,}")
                    st.metric("问题数", f"{info_a.get('questions_count', 0):,}")
                
                with info_col2:
                    st.markdown(f"**📌 {topic_b}**")
                    info_b = display_data["topic_b"]["topic"]
                    st.metric("关注者", f"{info_b.get('followers_count', 0):,}")
                    st.metric("问题数", f"{info_b.get('questions_count', 0):,}")
                
                source_a = "来自知乎热榜" if display_data["topic_a"].get("source") == "zhihu_hot" else "AI生成数据"
                source_b = "来自知乎热榜" if display_data["topic_b"].get("source") == "zhihu_hot" else "AI生成数据"
                st.caption(f"📡 {topic_a}: {source_a} | {topic_b}: {source_b}")
                
                st.markdown("---")
                
                # 加载动画
                loading_placeholder = st.empty()
                for msg in LOADING_MESSAGES[:5]:
                    loading_placeholder.markdown(f"""
                    <div class="loading-container">
                        <div class="loading-text">{msg}</div>
                        <div style="margin-top: 1rem;">
                            <div style="display: inline-block; width: 10px; height: 10px; background: #0066FF; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both;"></div>
                            <div style="display: inline-block; width: 10px; height: 10px; background: #0066FF; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out 0.16s both; margin: 0 5px;"></div>
                            <div style="display: inline-block; width: 10px; height: 10px; background: #0066FF; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out 0.32s both;"></div>
                        </div>
                    </div>
                    <style>@keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}</style>
                    """, unsafe_allow_html=True)
                    time.sleep(0.8)
                
                success, result = call_deepseek_api(topic_a, topic_b, zhihu_context_str, temperature)
                loading_placeholder.empty()
                
                if success:
                    st.session_state.generated_script = result
                    st.balloons()
                    st.success("✨ 发现隐藏联系成功！")
                    st.markdown(f'<div class="output-card">{result}</div>', unsafe_allow_html=True)
                    
                    col_copy, col_dl = st.columns(2)
                    with col_copy:
                        st.session_state.last_copied = result
                        st.success("📋 已准备好复制")
                    with col_dl:
                        st.download_button("📥 下载脚本", result,
                                          file_name=f"离谱接线员_{topic_a}_{topic_b}.md",
                                          mime="text/markdown", use_container_width=True)
                else:
                    st.error(result)
                    st.info("💡 请尝试使用左侧的预置精品案例")
        
        # 历史结果
        elif st.session_state.generated_script:
            st.markdown(f'<div class="output-card">{st.session_state.generated_script}</div>', unsafe_allow_html=True)
            
            col_copy, col_dl = st.columns(2)
            topics = st.session_state.current_topics
            with col_dl:
                st.download_button("📥 下载脚本", st.session_state.generated_script,
                                  file_name=f"离谱接线员_{topics[0]}_{topics[1]}.md",
                                  mime="text/markdown", use_container_width=True)
            
            if st.session_state.zhihu_context:
                with st.expander("📋 查看知乎内容来源"):
                    ctx = st.session_state.zhihu_context
                    st.markdown(f"**话题A：{ctx['topic_a']['topic']['name']}**")
                    for q in ctx["topic_a"]["questions"][:2]:
                        st.markdown(f"- {q['title']}")
                    st.markdown(f"**话题B：{ctx['topic_b']['topic']['name']}**")
                    for q in ctx["topic_b"]["questions"][:2]:
                        st.markdown(f"- {q['title']}")
        else:
            st.info("👆 在左侧输入话题或点击预置案例开始体验")
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%); 
                        border-radius: 12px; padding: 1rem; margin: 1rem 0;
                        border-left: 4px solid #ffc107;">
                <strong>🎯 快速体验</strong><br>
                点击左侧边栏的 <strong>预置精品案例</strong>，无需等待AI生成，直接查看完整结果！
            </div>
            """, unsafe_allow_html=True)
    
    # ==========================================================================
    # 底部
    # ==========================================================================
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p>🔗 离谱接线员 | 知乎 Hackathon 2026「灵感引擎」赛道</p>
        <p>Powered by DeepSeek API + 知乎热榜API | 5月16日路演</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
