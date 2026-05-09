# 离谱接线员

**发现知识之间的隐藏联系，让离谱的关联变成惊艳的发现。**

## 一句话介绍

输入两个话题，AI帮你发现它们之间意想不到的奇妙联系。

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
     - `ZHIHU_API_KEY`: 知乎API Key（如需要）

### 方式二：本地运行

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/liqi-jiexian.git
cd liqi-jiexian

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
echo "DEEPSEEK_API_KEY=your_api_key" > .env

# 运行
streamlit run app.py
```

## 项目结构

```
liqi-jiexian/
├── app.py                 # Streamlit 主应用
├── zhihu_api.py           # 知乎API封装
├── prompts/               # AI Prompt模板
│   ├── connector.md       # 核心连接生成器
│   ├── examples.md        # 示例库
│   └── demo_examples.md   # Demo示例
├── requirements.txt       # Python依赖
├── railway.json          # Railway配置
├── nixpacks.toml         # Nixpacks配置
├── .gitignore            # Git忽略文件
└── README.md             # 本文件
```

## 技术栈

- **前端**: Streamlit
- **AI**: DeepSeek API
- **数据源**: 知乎API
- **部署**: Railway + Nixpacks
