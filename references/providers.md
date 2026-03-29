# AutoFigure-Edit LLM 提供商配置参考

## 目录
- [支持的 Provider 概览](#支持的-provider-概览)
- [OpenRouter](#openrouter)
- [Bianxie（边界AI）](#bianxie边界ai)
- [Gemini（Google 官方）](#geminigoogle-官方)
- [自定义 OpenAI 兼容接口](#自定义-openai-兼容接口)
- [模型选择建议](#模型选择建议)
- [常见错误排查](#常见错误排查)

---

## 支持的 Provider 概览

| Provider | 参数值 | Base URL | 国内可用 | 特点 |
|----------|--------|----------|----------|------|
| OpenRouter | `openrouter` | `openrouter.ai/api/v1` | 需要代理 | 聚合多模型，支持 Gemini/Claude/GPT |
| Bianxie | `bianxie` | `api.bianxie.ai/v1` | ✅ | OpenAI 兼容，国内友好 |
| Gemini | `gemini` | `generativelanguage.googleapis.com/v1beta` | 需要代理 | Google 官方，成本较低 |
| 自定义 | `bianxie` + `--base_url` | 任意 OpenAI 兼容地址 | 视情况 | 本地模型、私有部署 |

---

## OpenRouter

申请地址：https://openrouter.ai/

```bash
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider openrouter \
  --api_key sk-or-v1-xxxxxxxx \
  --image_model google/gemini-3-pro-image-preview \
  --svg_model google/gemini-3.1-pro-preview
```

**默认模型：**
- 图片生成：`google/gemini-3-pro-image-preview`
- SVG 生成：`google/gemini-3.1-pro-preview`

**其他推荐模型（OpenRouter 可用）：**
- `google/gemini-2.5-flash-preview` - 速度快，成本低
- `anthropic/claude-3.7-sonnet` - SVG 生成质量好
- `openai/gpt-4o` - 通用强模型

**注意：** 图片生成模型必须支持 `image_generation` 能力（如 Gemini 系列），SVG 生成模型需支持多模态输入（图片理解）。

---

## Bianxie（边界AI）

申请地址：https://api.bianxie.ai/

```bash
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider bianxie \
  --api_key YOUR_BIANXIE_KEY
```

**默认模型：**
- 图片生成：`gemini-3-pro-image-preview`
- SVG 生成：`gemini-3.1-pro-preview`

**特点：** 国内可直接访问，兼容 OpenAI SDK，支持 Gemini 全系模型。

---

## Gemini（Google 官方）

申请地址：https://aistudio.google.com/apikey

```bash
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider gemini \
  --api_key YOUR_GEMINI_KEY \
  --image_model gemini-3-pro-image-preview \
  --svg_model gemini-3.1-pro
```

**默认模型：**
- 图片生成：`gemini-3-pro-image-preview`
- SVG 生成：`gemini-3.1-pro`

**注意：** 需要网络能访问 `generativelanguage.googleapis.com`，国内需代理。

---

## 自定义 OpenAI 兼容接口

适用于：本地 Ollama、LM Studio、私有部署的 vLLM 服务等。

使用 `bianxie` provider 类型 + `--base_url` 参数：

```bash
# Ollama 本地服务（需模型支持图片生成和视觉理解）
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider bianxie \
  --base_url http://localhost:11434/v1 \
  --api_key ollama \
  --image_model llava:34b \
  --svg_model qwen2.5-vl:72b

# vLLM 私有部署
python autofigure2.py \
  --method_file paper.txt \
  --output_dir ./outputs \
  --provider bianxie \
  --base_url http://your-server:8000/v1 \
  --api_key YOUR_KEY \
  --image_model your-image-model \
  --svg_model your-vlm-model
```

⚠️ **本地模型限制：**
- `image_model` 必须支持**图片生成**（text-to-image），大多数 LLM 不具备此能力
- `svg_model` 必须支持**视觉输入**（multimodal/VLM）
- 实际上，图片生成步骤对本地模型挑战极大，推荐 SVG 步骤用本地模型 + 图片生成用 API

详见 `local-llm.md` 了解本地大模型配置方案。

---

## 模型选择建议

### 图片生成模型（Step 1）
必须是**原生图片生成**模型，不是 VLM：
- ✅ Gemini 系列（推荐）：`gemini-3-pro-image-preview`
- ✅ DALL-E 系列（通过 OpenRouter）：`openai/dall-e-3`
- ❌ 普通 LLM（GPT-4, Claude）：不能生成图片

### SVG 生成模型（Step 4）
必须是**多模态 VLM**，可理解图片并输出 SVG 代码：
- ✅ Gemini Pro / Pro Preview（推荐）
- ✅ Claude 3.7 Sonnet（代码能力强）
- ✅ GPT-4o
- ⚠️ Qwen2.5-VL, LLaVA（本地，质量稍弱）

---

## 常见错误排查

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `401 Unauthorized` | API Key 错误 | 检查 Key 是否复制完整 |
| `404 Not Found` | 模型名错误 | 检查模型 ID 拼写 |
| `RateLimitError` | 请求频率过高 | 减少并发或升级套餐 |
| `Image generation failed` | 模型不支持图片生成 | 换用 Gemini 图片模型 |
| `SVG parse error` | SVG 格式不合法 | 增加优化迭代次数（--optimize_iterations 2） |
| `Connection timeout` | 网络问题 | 检查代理或换用国内接口 |
