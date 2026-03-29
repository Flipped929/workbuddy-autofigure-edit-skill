# WorkBuddy Skill — AutoFigure-Edit

> **AutoFigure-Edit** × **WorkBuddy** — 将论文方法段文字一键转化为可编辑 SVG 插图，并支持网页内联可视化编辑。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![AutoFigure-Edit](https://img.shields.io/badge/upstream-ResearAI%2FAutoFigure--Edit-brightgreen)](https://github.com/ResearAI/AutoFigure-Edit)
[![ICLR 2026](https://img.shields.io/badge/paper-ICLR%202026-orange)](https://arxiv.org/abs/2603.06674)

---

## 预览

![预览图](assets/preview_banner.png)

---

## 功能特性

- **四步 AI 流水线**：文字 → 图片生成 → SAM3 分割 → 背景去除 → SVG 组装
- **多 LLM 提供商**：支持 OpenRouter、边界AI（国内）、Google Gemini、本地 Ollama
- **网页内联编辑器**：生成后直接在浏览器中可视化编辑 SVG，无需安装额外软件
  - 🖱️ **拖拽移动**：直接拖拽元素，支持 SVG viewBox 坐标系自动换算
  - ↩ **撤销/重做**：最多 60 步历史，覆盖所有操作类型
  - 🔲 **多选 & 橡皮筋框选**：Ctrl+单击或拖拽框选，支持批量移动/删除
  - 📐 **智能对齐辅助线**：拖拽时黄色磁吸辅助线，8px 自动对齐
  - 📊 **对齐工具栏**：6 种对齐 + 2 种均匀分布，一键整齐排版
- **环境配置向导**：交互式 / 命令行两种方式管理 `.env` 配置
- **自动更新检查**：一键对比本地与 GitHub 最新版本

---

## 目录结构

```
workbuddy-autofigure-edit-skill/
├── SKILL.md              # WorkBuddy Skill 主文件
├── scripts/
│   ├── setup_env.py      # 环境配置助手
│   ├── run_autofigure.py # CLI 运行封装
│   ├── launch_editor.py  # 网页内联编辑器启动脚本
│   └── check_update.py   # GitHub 更新检查
├── references/
│   ├── providers.md      # LLM 提供商配置详解
│   ├── sam3-backends.md  # SAM3 后端配置详解
│   ├── local-llm.md      # 本地大模型配置
│   ├── inline-editor.md  # 网页内联编辑器完整文档
│   └── changelog.md      # 变更日志
└── assets/
    ├── editor-demo.html  # 内联编辑器演示页（可直接浏览器打开）
    ├── preview_banner.png
    └── preview_fullpage.png
```

---

## 快速安装

### 在 WorkBuddy 中安装此 Skill

1. 下载或克隆本仓库
2. 将文件夹整体复制到 WorkBuddy Skills 目录：
   - **Windows**：`%USERPROFILE%\.workbuddy\skills\autofigure-edit\`
   - **macOS/Linux**：`~/.workbuddy/skills/autofigure-edit/`
3. 在 WorkBuddy 对话中输入：`使用 AutoFigure-Edit 生成论文插图` 即可触发

---

## 使用示例

### 生成论文插图（CLI）

```bash
python scripts/run_autofigure.py \
  --project-dir /path/to/AutoFigure-Edit-main \
  --method-file paper.txt
```

### 配置环境（交互式）

```bash
python scripts/setup_env.py --project-dir /path/to/AutoFigure-Edit-main
```

### 启动网页内联编辑器

```bash
# 打开已生成的 SVG 进行可视化编辑
python scripts/launch_editor.py --svg /path/to/final.svg

# 生成独立 HTML（可离线使用）
python scripts/launch_editor.py --svg /path/to/final.svg --standalone
```

### 在线演示编辑器

直接打开 [`assets/editor-demo.html`](assets/editor-demo.html) 即可体验完整的网页内联编辑器功能（无需服务器）。

---

## 网页内联编辑器功能

### 核心编辑能力

| 功能 | 说明 |
|------|------|
| ✏️ 编辑模式 | 点击工具栏「开启编辑」进入可交互状态 |
| 🖱️ 拖拽移动 | 直接拖拽任意元素（rect/text/g），自动换算 SVG viewBox 坐标系；拖拽距离 < 4px 触发属性弹窗 |
| 🎨 颜色填充 | 工具栏颜色拾取器一键修改元素填充色 |
| 📝 文字编辑 | 修改文字内容、字号、颜色 |
| ＋ 添加元素 | 插入新文本节点或矩形元素 |
| ↩ 撤销/重做 | Ctrl+Z / Ctrl+Y，最多 60 步历史记录，覆盖移动/样式/新增/删除所有操作 |
| ⬇ 导出 | 一键导出 SVG 或 PNG（支持 1×/2×/3× 分辨率） |

### 多选与批量操作

| 功能 | 说明 |
|------|------|
| 🔲 Ctrl + 单击多选 | 按住 Ctrl 逐个点击，累积选中多个元素 |
| ⬜ 橡皮筋框选 | 在空白处拖拽绘制选框，松开后框内所有元素被选中 |
| 🗑️ 批量删除 | 选中多个元素后按 `Delete` 一次性删除 |
| 🔀 批量移动 | 多选后整体拖拽，所有选中元素保持相对位置移动 |

### 智能对齐系统

| 功能 | 说明 |
|------|------|
| 📐 智能对齐辅助线 | 拖拽时实时显示黄色参考线，8px 磁吸阈值，自动对齐其他元素的边缘/中心 |
| ◀ 左对齐 | 所有选中元素向最左侧元素的左边缘对齐 |
| ↔ 水平居中对齐 | 所有选中元素的水平中心对齐 |
| ▶ 右对齐 | 所有选中元素向最右侧元素的右边缘对齐 |
| ▲ 顶对齐 | 所有选中元素向最顶部元素的上边缘对齐 |
| ↕ 垂直居中对齐 | 所有选中元素的垂直中心对齐 |
| ▼ 底对齐 | 所有选中元素向最底部元素的下边缘对齐 |
| ↔ 横向均匀分布 | 选中元素在水平方向等间距分布 |
| ↕ 纵向均匀分布 | 选中元素在垂直方向等间距分布 |

### 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` | 重做 |
| `Ctrl+S` | 导出 SVG |
| `Delete` | 删除选中元素 |
| `Esc` | 取消选中 |
| `↑ ↓ ← →` | 方向键微调位置（1 单位） |
| `Shift + 方向键` | 大步微调位置（10 单位） |
| `Ctrl + 单击` | 追加/取消多选 |

---

## 上游项目

本 Skill 为 [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit)（西湖大学 / ResearAI，ICLR 2026）的 WorkBuddy 集成封装。

- **上游仓库**：https://github.com/ResearAI/AutoFigure-Edit
- **论文**：https://arxiv.org/abs/2603.06674
- **许可证**：Apache 2.0（同上游项目）

---

## License

Apache License 2.0 — 详见 [LICENSE](LICENSE)
