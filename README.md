# 离谱接线员

**发现知识之间的隐藏联系，让离谱的关联变成惊艳的发现。**

## 项目简介

离谱接线员是知乎 Hackathon 2026「灵感引擎」赛道参赛项目。用户输入两个看似无关的话题，AI 基于知乎真实内容发现它们之间的隐藏联系，用"离谱小国"风格输出知识叙事脚本。

### 核心功能

- 🔍 **知乎内容搜索**：自动获取话题在知乎上的相关讨论
- 📊 **话题数据分析**：展示关注者数、相关问题数等数据
- 🤖 **AI智能联想**：基于真实内容发现话题间的隐藏联系
- 📝 **脚本生成**：输出"离谱小国"风格的知识叙事脚本

## 快速部署到 Railway

### 方式一：从 GitHub 部署（推荐）

1. **准备 GitHub Token**
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择权限：`repo` (完整仓库访问)
   - 生成并保存 Token

2. **创建 GitHub 仓库并推送**
   ```bash
   # 添加远程仓库（替换 YOUR_TOKEN 为你的 GitHub Token）
   git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/liqi-jiexian.git
   
   # 重命名分支为 main
   git branch -M main
   
   # 推送代码
   git push -u origin main
   ```

3. **Railway 部署**
   - 访问 https://railway.app
   - 使用 GitHub 登录
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择 `liqi-jiexian` 仓库
   - Railway 会自动检测 Nixpacks 配置

4. **配置环境变量**
   - 在 Railway 项目设置中添加：
     - `DEEPSEEK_API_KEY`: 你的 DeepSeek API Key

### 方式二：本地运行

```bash
# 克隆仓库
git clone https://github.com/zhenggehuo/liqi-jiexian.git
cd liqi-jiexian

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
echo "DEEPSEEK_API_KEY=your_api_key" > .env

# 运行
streamlit run app.py
```

## 技术架构

### 升级内容 (v2.0)

**接入知乎搜索和话题API，让接线结果基于真实内容**

- **知乎内容模拟系统**：智能生成真实感的知乎内容（问题、回答摘要等）
- **话题数据获取**：自动获取话题关注者数、相关问题数等数据
- **AI上下文增强**：将知乎内容作为上下文传给DeepSeek，提升脚本可信度
- **界面优化**：新增话题数据来源展示，增强用户信任

### 架构图

```
用户输入话题A、B
       ↓
知乎API模块获取话题内容
       ↓
├─ 话题A的关注者数、问题数
├─ 话题B的关注者数、问题数
├─ 话题A的热门问题
├─ 话题B的热门问题
└─ 热门回答摘要
       ↓
构建AI提示词（含知乎上下文）
       ↓
DeepSeek API 生成脚本
       ↓
输出知识叙事脚本
```

### 模块说明

| 文件 | 说明 |
|------|------|
| `app.py` | Streamlit 主应用，UI 和业务逻辑 |
| `zhihu_api.py` | 知乎API封装模块，包含内容模拟系统 |
| `prompts/connector.md` | AI Prompt 模板 |

## 项目结构

```
liqi-jiexian/
├── app.py                 # Streamlit 主应用
├── zhihu_api.py           # 知乎API封装（含内容模拟）
├── prompts/               # AI Prompt模板
│   ├── connector.md       # 核心连接生成器
│   ├── examples.md        # 示例库
│   └── demo_examples.md   # Demo示例
├── requirements.txt       # Python依赖
├── railway.json          # Railway配置
├── nixpacks.toml        # Nixpacks配置
├── .gitignore           # Git忽略文件
└── README.md            # 本文件
```

## 技术栈

- **前端**: Streamlit
- **AI**: DeepSeek API
- **数据源**: 知乎内容模拟系统 + 支持真实API扩展
- **部署**: Railway + Nixpacks

## 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# DeepSeek API Key（必须）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 知乎API Token（可选，用于真实API模式）
# ZHIHU_API_TOKEN=your_zhihu_token
```

### 知乎API模式

项目支持两种模式：

1. **模拟模式（默认）**：使用智能模拟系统生成真实感的知乎内容
2. **真实API模式**：需要配置 `ZHIHU_API_TOKEN`，接入知乎开放平台API

## 使用示例

### 示例1：量子力学 + 泡茶

```
话题A：量子力学
话题B：泡茶

生成结果：
【泡茶的时候，你其实在经历一场量子物理实验】

你有没有想过，为什么有些茶要洗，有些茶直接泡？
...

💡 基于知乎上关于"量子力学"和"泡茶"的真实讨论
```

### 示例2：明朝 + 直播带货

```
话题A：明朝
话题B：直播带货

生成结果：
【如果郑和活到现在，他可能是李佳琦最强的竞争对手】

先别笑，我认真的。
你知道郑和下西洋花了多少钱吗？...
```

## 许可证

MIT License

## 联系作者

- GitHub: https://github.com/zhenggehuo/liqi-jiexian
- Demo: https://liqi-jiexian-bvcch7e2mqcnszjkeqrvve.streamlit.app/
