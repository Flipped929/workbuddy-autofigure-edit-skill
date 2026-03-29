# 本地大模型配置指南

## 概述

AutoFigure-Edit 的两个核心步骤对模型的要求不同：

| 步骤 | 功能 | 模型要求 | 本地可用性 |
|------|------|----------|------------|
| Step 1 | 文本 → 论文风格图片 | 必须支持**原生图片生成** | ❌ 极难（几乎无开源本地方案） |
| Step 4 | 多模态 → SVG 代码 | 必须支持**视觉输入（VLM）** | ✅ 可用（多种方案） |

> **实际建议：** Step 1 图片生成使用云端 API（Gemini），Step 4 SVG 生成可用本地 VLM。目前没有完全离线的端到端方案。

---

## 混合方案：云端生图 + 本地 SVG

**推荐配置：** 图片生成用 Gemini API，SVG 生成用本地 Ollama

```bash
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider bianxie \
  --api_key YOUR_BIANXIE_KEY \
  --image_model gemini-3-pro-image-preview \
  --base_url http://localhost:11434/v1 \
  --svg_model qwen2.5-vl:32b
```

**注意：** `--provider bianxie` 同时控制 image 和 svg 的 base_url。如需 image 走云端、svg 走本地，需修改源码或使用两次运行。

---

## Ollama 配置

### 安装 Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 下载安装包: https://ollama.ai/download
```

### 推荐的 VLM 模型（用于 SVG 生成）

| 模型 | 命令 | 显存需求 | SVG 质量 |
|------|------|----------|----------|
| Qwen2.5-VL 7B | `ollama pull qwen2.5-vl:7b` | ~8GB | ⭐⭐⭐ |
| Qwen2.5-VL 32B | `ollama pull qwen2.5-vl:32b` | ~20GB | ⭐⭐⭐⭐ |
| LLaVA 34B | `ollama pull llava:34b` | ~24GB | ⭐⭐⭐ |
| Llama3.2-Vision | `ollama pull llama3.2-vision:11b` | ~10GB | ⭐⭐⭐ |

### 使用 Ollama

```bash
# 1. 启动 Ollama 服务（通常自动启动）
ollama serve

# 2. 拉取模型
ollama pull qwen2.5-vl:7b

# 3. 运行 AutoFigure（仅 SVG 步骤用本地，图片步骤仍需 API）
python autofigure2.py \
  --method_file paper.txt \
  --provider bianxie \
  --api_key YOUR_CLOUD_KEY \
  --base_url http://localhost:11434/v1 \
  --image_model gemini-3-pro-image-preview \
  --svg_model qwen2.5-vl:7b
```

---

## LM Studio 配置

LM Studio 提供 GUI 界面管理本地模型，并内置 OpenAI 兼容服务。

1. 下载：https://lmstudio.ai/
2. 搜索并下载支持视觉的模型（如 Qwen2.5-VL、LLaVA）
3. 启动本地服务器（默认端口 1234）
4. 配置：

```bash
python autofigure2.py \
  --method_file paper.txt \
  --provider bianxie \
  --base_url http://localhost:1234/v1 \
  --api_key lm-studio \
  --svg_model your-loaded-model-id
```

---

## vLLM 私有部署

适用于团队共享的高性能 GPU 服务器。

```bash
# 部署 Qwen2.5-VL
vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --trust-remote-code

# 使用
python autofigure2.py \
  --method_file paper.txt \
  --provider bianxie \
  --base_url http://your-server:8000/v1 \
  --api_key token-xxx \
  --svg_model Qwen/Qwen2.5-VL-7B-Instruct
```

---

## 限制与注意事项

### 图片生成（Step 1）的本地化难题

目前能在本地生成"论文学术风格图"的开源模型极少。AutoFigure-Edit 调用的是 Gemini 的 **原生多模态图片生成**能力（不是 Stable Diffusion，而是 LLM 直接输出图片）。本地替代方案：

1. **完全跳过图片生成**：手动提供一张参考图，直接从 Step 2 SAM3 开始
   - 将论文中的方法图保存为 PNG
   - 使用 `autofigure2.py` 的中间步骤
   
2. **使用 FLUX 等模型**（Stable Diffusion 类）：效果与 Gemini 差异较大，不推荐

### SVG 生成质量对比

| 方案 | SVG 质量 | 速度 | 成本 |
|------|----------|------|------|
| Gemini 3.1 Pro（云端） | ⭐⭐⭐⭐⭐ | 中 | 中 |
| Claude 3.7 Sonnet（云端） | ⭐⭐⭐⭐⭐ | 中 | 高 |
| Qwen2.5-VL 32B（本地） | ⭐⭐⭐⭐ | 慢 | 免费 |
| Qwen2.5-VL 7B（本地） | ⭐⭐⭐ | 快 | 免费 |
