---
name: autofigure-edit
description: AutoFigure-Edit 是西湖大学/ResearAI 开源的 AI 论文绘图工具（ICLR 2026），可将论文方法段文字自动转化为可编辑的 SVG 矢量插图。本 skill 提供完整的安装配置、运行、更新检查工作流。当用户提到以下场景时使用：(1) 使用 AutoFigure-Edit 生成论文插图；(2) 配置 API Key（OpenRouter/Bianxie/Gemini/本地模型）；(3) 配置 SAM3 分割后端（Roboflow/fal.ai/本地）；(4) 检查 GitHub 最新版本或更新项目；(5) 启动 Web 界面或 CLI 运行；(6) 排查 AutoFigure-Edit 报错；(7) 打开/启动网页内联编辑器在浏览器中直接编辑 SVG；(8) 对 SVG 进行文字编辑、颜色修改、元素添加、导出等可视化操作。GitHub: https://github.com/ResearAI/AutoFigure-Edit
---

# AutoFigure-Edit Skill

将论文方法段文字 → 可编辑 SVG 插图的完整工作流。

## 工作流程（四步流水线）

```
方法段文字
  ↓ Step 1  LLM 文生图（需图片生成能力）
figure.png
  ↓ Step 2  SAM3 分割（检测图标区域）
samed.png + boxlib.json
  ↓ Step 3  RMBG-2.0 背景去除
icons/*.png（透明图标）
  ↓ Step 4  VLM 多模态生成 SVG（→ 可选优化 → 组装）
final.svg（可在浏览器 svg-edit 中编辑）
```

## 快速开始

### 方式 A：Web 界面（推荐）
```bash
cd AutoFigure-Edit-main
pip install -r requirements.txt
python server.py
# 访问 http://localhost:8000
```

### 方式 B：CLI（推荐使用封装脚本）
```bash
# 使用 skill 封装脚本（从 .env 读取配置）
python scripts/run_autofigure.py \
  --project-dir /path/to/AutoFigure-Edit-main \
  --method-file paper.txt

# 或直接调用
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider bianxie \
  --api_key YOUR_KEY
```

### 方式 C：Docker（最简单）
```bash
cd AutoFigure-Edit-main
cp .env.example .env   # Windows: Copy-Item .env.example .env
# 编辑 .env 设置 HF_TOKEN 和 API Key
docker compose up -d --build
# 访问 http://localhost:8000
```

## 配置管理

### 使用配置助手（推荐）
```bash
# 交互式配置（引导式填写所有参数）
python scripts/setup_env.py --project-dir /path/to/AutoFigure-Edit-main

# 命令行直接写入配置
python scripts/setup_env.py \
  --project-dir /path/to/AutoFigure-Edit-main \
  --provider bianxie \
  --api-key sk-xxx \
  --hf-token hf_xxx \
  --sam-backend roboflow \
  --roboflow-key your-key

# 查看当前配置（隐藏敏感字段）
python scripts/setup_env.py --project-dir /path/to/AutoFigure-Edit-main --show
```

### 核心参数速查

| 参数 | 说明 | 常用值 |
|------|------|--------|
| `--provider` | LLM 提供商 | `bianxie`（国内）/ `openrouter` / `gemini` |
| `--api_key` | 对应提供商的 API Key | - |
| `--sam_backend` | 图像分割后端 | `roboflow`（免费推荐）/ `local` / `fal` |
| `--optimize_iterations` | SVG 优化轮数 | `0`（跳过，速度快）/ `2`（质量更好） |
| `--reference_image_path` | 风格参考图 | 任意 PNG/JPG 图片路径 |

## 提供商与模型配置

- **详细配置**：见 `references/providers.md`
- **本地大模型**：见 `references/local-llm.md`

**快速选择：**
- 国内用户 → `--provider bianxie`（边界AI，兼容 OpenAI 接口）
- 海外用户 → `--provider openrouter`（聚合多模型）
- Google API → `--provider gemini`
- 本地 Ollama → `--provider bianxie --base_url http://localhost:11434/v1`

## SAM3 配置

- **详细配置**：见 `references/sam3-backends.md`

**快速选择：**
- 无 GPU → `--sam_backend roboflow`（免费，申请 key: https://roboflow.com）
- 有 GPU → 本地安装 SAM3 后用 `--sam_backend local`
- 付费方案 → `--sam_backend fal`（https://fal.ai）

## 网页内联编辑器

生成 `final.svg` 后，可通过内置的网页内联编辑器在浏览器中**直接可视化编辑** SVG，无需任何额外软件。

### 功能概览

| 功能 | 说明 |
|------|------|
| **编辑模式** | 点击工具栏「✏️ 开启编辑」，进入可交互状态 |
| **元素选择** | 点击 SVG 中标记了 `data-editable` 的元素，弹出属性面板 |
| **文字编辑** | 修改文字内容、字号、颜色 |
| **颜色填充** | 工具栏颜色拾取器一键修改选中元素填充色 |
| **添加文字** | 「＋ 添加文字」按钮，插入新文本节点 |
| **添加方块** | 「▭ 添加方块」按钮，插入矩形元素 |
| **撤销/重做** | Ctrl+Z / Ctrl+Y 多步历史记录 |
| **导出 SVG** | 将当前编辑结果保存为 `.svg` 文件 |
| **导出 PNG** | 调用 Canvas 渲染，一键下载 `.png` |

### 启动方式

#### 方式 A：使用 skill 封装脚本（推荐）

```bash
# 用默认浏览器打开指定 SVG 文件的内联编辑器
python scripts/launch_editor.py --svg /path/to/final.svg

# 自定义端口（默认 9900）
python scripts/launch_editor.py --svg /path/to/final.svg --port 9900

# 生成独立 HTML 文件（可离线使用，无需本地服务器）
python scripts/launch_editor.py --svg /path/to/final.svg --standalone
```

#### 方式 B：Web 界面内置编辑器

AutoFigure-Edit Web 界面（`python server.py`）在结果页面已内置编辑器工具栏，生成完成后直接点击「编辑」按钮即可进入编辑模式。

#### 方式 C：手动拖拽

将 `final.svg` 拖入任意支持内联编辑的 HTML 页面，或使用项目自带的 `svg-edit/` 目录中的独立编辑器页面。

### 键盘快捷键

| 快捷键 | 操作 |
|--------|------|
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` / `Ctrl+Shift+Z` | 重做 |
| `Delete` / `Backspace` | 删除选中元素 |
| `Escape` | 取消选中 / 关闭弹窗 |
| `Ctrl+S` | 导出 SVG |
| `Ctrl+Shift+S` | 导出 PNG |

### 常见操作场景

**修改方法图中的标签文字**
1. 开启编辑模式 → 点击文字元素 → 弹窗中修改内容 → 确认

**统一调整配色方案**
1. 开启编辑模式 → 点击某元素 → 工具栏「填充色」拾取新颜色 → 依次选中其他同类元素重复操作

**添加新图注**
1. 开启编辑模式 → 点击「＋ 添加文字」→ 在弹窗填入内容和位置 → 确认

**导出高质量 PNG**
1. 点击工具栏「⬇ 导出 PNG」→ 选择分辨率倍率（1×/2×/3×）→ 自动下载

### 详细文档

- 完整使用指南：见 `references/inline-editor.md`

---

## 检查 GitHub 更新

```bash
# 检查是否有新版本
python scripts/check_update.py --local-dir /path/to/AutoFigure-Edit-main

# 仅查看远端最新 commits
python scripts/check_update.py

# 更新本地代码
cd /path/to/AutoFigure-Edit-main
git pull origin main
pip install -r requirements.txt
```

- **变更日志**：见 `references/changelog.md`
- **项目主页**：https://github.com/ResearAI/AutoFigure-Edit
- **论文**：https://arxiv.org/abs/2603.06674

## 常见问题

### 项目路径不知道怎么找
用户下载的源码一般在 `AutoFigure-Edit-main/` 文件夹，执行时传入该目录的绝对路径。

### 需要 HuggingFace Token
RMBG-2.0（背景去除模型）需要 HF Token 才能下载。申请地址：https://huggingface.co/briaai/RMBG-2.0

### SVG 效果不理想
- 增加优化迭代：`--optimize_iterations 2`
- 换用更强的 SVG 模型（如 Claude 3.7 Sonnet 或 Gemini 3.1 Pro）
- 调整 SAM Prompt：`--sam_prompt "icon,diagram,arrow,block"`

### 图片生成失败
确认 `--image_model` 是支持**原生图片生成**的模型（Gemini 系列），不能用普通 LLM。

### 输出文件在哪里
默认保存在 `outputs/<job_id>/` 目录，包含：
- `figure.png`：生成的初始图
- `samed.png`：SAM3 标注结果
- `icons/`：抠图后的图标
- `template.svg`：SVG 模板
- `final.svg`：最终可编辑矢量图
