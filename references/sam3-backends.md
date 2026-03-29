# SAM3 后端配置参考

## 目录
- [后端概览](#后端概览)
- [Roboflow API（推荐）](#roboflow-api推荐)
- [fal.ai API](#falai-api)
- [本地 SAM3 安装](#本地-sam3-安装)
- [SAM Prompt 调优](#sam-prompt-调优)
- [Box 合并配置](#box-合并配置)

---

## 后端概览

SAM3（Segment Anything Model 3）用于图像分割，检测论文图中的图标区域。

| 后端 | 参数值 | 费用 | 安装难度 | 推荐度 |
|------|--------|------|----------|--------|
| Roboflow | `roboflow` | **免费** | 无需安装 | ⭐⭐⭐⭐⭐ |
| fal.ai | `fal` | 付费 | 无需安装 | ⭐⭐⭐ |
| 本地 SAM3 | `local` | 免费 | 高（需GPU） | ⭐⭐ |

---

## Roboflow API（推荐）

免费使用，无需本地 GPU，官方推荐方案。

### 申请步骤
1. 访问 https://roboflow.com/ 注册账号
2. 进入 Dashboard → Settings → API Keys
3. 复制 API Key

### 配置方式

```bash
# 方式 1：环境变量
export ROBOFLOW_API_KEY="your-key"
python autofigure2.py --method_file paper.txt --sam_backend roboflow

# 方式 2：命令行参数
python autofigure2.py \
  --method_file paper.txt \
  --sam_backend roboflow \
  --sam_api_key your-key

# 方式 3：.env 文件
ROBOFLOW_API_KEY=your-key
AUTOFIGURE_SAM_BACKEND=roboflow
```

### 网络问题排查

如果遇到 DNS 解析失败（Docker 内）：
```bash
# .env 中添加 DNS 覆盖
DOCKER_DNS_1=223.5.5.5
DOCKER_DNS_2=119.29.29.29

# 或自定义 Roboflow 接口地址
ROBOFLOW_API_URL=https://serverless.roboflow.com/sam3/concept_segment
ROBOFLOW_API_FALLBACK_URLS=...
```

---

## fal.ai API

付费 API，性能稳定，支持更多 mask 数量。

### 申请步骤
1. 访问 https://fal.ai/ 注册
2. 充值后获取 API Key

### 配置方式

```bash
export FAL_KEY="your-fal-key"
python autofigure2.py \
  --method_file paper.txt \
  --sam_backend fal \
  --sam_max_masks 64    # 默认 32，fal.ai 支持更高值
```

---

## 本地 SAM3 安装

适用于有 GPU 的本地环境，完全离线运行。

### 系统要求
- Python 3.12+
- PyTorch 2.7+
- CUDA 12.6（GPU 模式）
- 显存 ≥ 8GB（推荐 16GB+）

### 安装步骤

```bash
# 1. 克隆 SAM3 仓库
git clone https://github.com/facebookresearch/sam3.git
cd sam3
pip install -e .

# 2. 登录 HuggingFace（下载模型权重）
huggingface-cli login
# 或设置环境变量
export HF_TOKEN=hf_xxx

# 3. 模型会在首次运行时自动下载到 ~/.cache/huggingface/
```

SAM3 HuggingFace 页面：https://huggingface.co/facebook/sam3

### 使用本地 SAM3

```bash
python autofigure2.py \
  --method_file paper.txt \
  --sam_backend local
```

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `CUDA out of memory` | 降低 `--sam_max_masks` 值 |
| `huggingface_hub.errors.GatedRepoError` | 申请 HF 访问权限并设置 HF_TOKEN |
| `ModuleNotFoundError: sam3` | 确认已 `pip install -e .` 安装 SAM3 |

---

## SAM Prompt 调优

`--sam_prompt` 参数支持逗号分隔的多个提示词，系统会对每个词分别检测并合并结果。

### 默认 Prompt
```
icon,person,robot,animal
```

### 针对不同类型论文的推荐 Prompt

**AI/ML 方法图：**
```
icon,diagram,arrow,block,module,encoder,decoder,attention
```

**生物医学图：**
```
icon,cell,molecule,protein,pathway,arrow,diagram
```

**系统架构图：**
```
icon,box,component,server,database,arrow,flow
```

**通用科学图：**
```
icon,diagram,chart,figure,symbol,arrow,element
```

### 调优建议
- 提示词越多，检测越全面，但也可能引入噪声
- 建议从 3-5 个关键词开始
- 如检测区域过多，可减少提示词或调高 `--merge_threshold`

---

## Box 合并配置

`--merge_threshold` 控制重叠区域的合并策略。

合并公式：`overlap = 交集面积 / 较小Box面积`

| 值 | 效果 |
|----|------|
| `0` | 禁用合并，保留所有检测结果 |
| `0.5` | 中等合并，50% 以上重叠才合并 |
| `0.9` | 激进合并（默认），高度重叠才合并 |
| `0.01` | 几乎全部合并 |

```bash
# 禁用合并（保留所有检测）
python autofigure2.py ... --merge_threshold 0

# 较宽松合并
python autofigure2.py ... --merge_threshold 0.5
```
