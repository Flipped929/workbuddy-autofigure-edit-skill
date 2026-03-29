#!/usr/bin/env python3
"""
AutoFigure-Edit 环境配置助手
交互式配置或命令行配置 .env 文件，支持所有主要 API 参数。

用法:
    # 交互式配置
    python setup_env.py --project-dir /path/to/AutoFigure-Edit-main

    # 命令行直接写入
    python setup_env.py --project-dir /path/to/AutoFigure-Edit-main \
        --provider openrouter \
        --api-key sk-or-v1-xxx \
        --hf-token hf_xxx \
        --sam-backend roboflow \
        --roboflow-key xxx

    # 只读取当前配置
    python setup_env.py --project-dir /path/to/AutoFigure-Edit-main --show
"""

import argparse
import os
import sys
from pathlib import Path


ENV_TEMPLATE = """\
# =====================================================
# AutoFigure-Edit 配置文件
# 由 autofigure-edit skill 生成
# =====================================================

# ----- LLM Provider 配置 -----
# 支持: openrouter | bianxie | gemini | custom
AUTOFIGURE_PROVIDER={provider}

# API Key（对应所选 Provider）
AUTOFIGURE_API_KEY={api_key}

# 自定义 Base URL（留空则使用默认）
# 本地模型示例: http://localhost:11434/v1
AUTOFIGURE_BASE_URL={base_url}

# 图片生成模型（文本→图片，需支持图片生成）
AUTOFIGURE_IMAGE_MODEL={image_model}

# SVG 生成模型（多模态理解，支持图片输入）
AUTOFIGURE_SVG_MODEL={svg_model}

# ----- HuggingFace 配置（RMBG-2.0 背景去除）-----
HF_TOKEN={hf_token}

# ----- SAM3 分割后端 -----
# 支持: local | roboflow | fal | api
AUTOFIGURE_SAM_BACKEND={sam_backend}

# Roboflow API Key（SAM3 免费 API，推荐）
ROBOFLOW_API_KEY={roboflow_key}

# fal.ai API Key（SAM3 付费 API）
FAL_KEY={fal_key}

# ----- 高级配置 -----
# OpenRouter 多模态重试次数
OPENROUTER_MULTIMODAL_RETRIES=3
OPENROUTER_MULTIMODAL_RETRY_DELAY=1.5
"""

PROVIDER_DEFAULTS = {
    "openrouter": {
        "base_url": "",
        "image_model": "google/gemini-3-pro-image-preview",
        "svg_model": "google/gemini-3.1-pro-preview",
    },
    "bianxie": {
        "base_url": "",
        "image_model": "gemini-3-pro-image-preview",
        "svg_model": "gemini-3.1-pro-preview",
    },
    "gemini": {
        "base_url": "",
        "image_model": "gemini-3-pro-image-preview",
        "svg_model": "gemini-3.1-pro",
    },
    "custom": {
        "base_url": "http://localhost:11434/v1",
        "image_model": "llava",
        "svg_model": "qwen2.5-coder:32b",
    },
}


def read_existing_env(env_path: Path) -> dict:
    """读取现有 .env 文件"""
    config = {}
    if not env_path.exists():
        return config
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            config[key.strip()] = val.strip()
    return config


def show_config(env_path: Path) -> None:
    """展示当前配置（隐藏敏感字段）"""
    if not env_path.exists():
        print(f"[信息] 未找到 .env 文件: {env_path}")
        return
    config = read_existing_env(env_path)
    secret_keys = {"AUTOFIGURE_API_KEY", "HF_TOKEN", "ROBOFLOW_API_KEY", "FAL_KEY"}
    print(f"\n当前配置 ({env_path}):\n" + "-" * 50)
    for k, v in config.items():
        display_v = ("*" * 8 + v[-4:] if len(v) > 4 else "****") if k in secret_keys and v else (v or "(未设置)")
        print(f"  {k} = {display_v}")
    print("-" * 50)


def write_env(env_path: Path, cfg: dict) -> None:
    """写入 .env 配置文件"""
    content = ENV_TEMPLATE.format(
        provider=cfg.get("provider", "bianxie"),
        api_key=cfg.get("api_key", ""),
        base_url=cfg.get("base_url", ""),
        image_model=cfg.get("image_model", ""),
        svg_model=cfg.get("svg_model", ""),
        hf_token=cfg.get("hf_token", ""),
        sam_backend=cfg.get("sam_backend", "roboflow"),
        roboflow_key=cfg.get("roboflow_key", ""),
        fal_key=cfg.get("fal_key", ""),
    )
    env_path.write_text(content, encoding="utf-8")
    print(f"\n✅ 配置已写入: {env_path}")


def interactive_setup(existing: dict) -> dict:
    """交互式配置流程"""
    print("\n🚀 AutoFigure-Edit 交互式配置向导")
    print("=" * 50)
    print("按 Enter 保留现有值，输入新值则覆盖\n")

    cfg = {}

    # Provider
    providers = list(PROVIDER_DEFAULTS.keys())
    cur_provider = existing.get("AUTOFIGURE_PROVIDER", "bianxie")
    print(f"LLM 提供商 [{'/'.join(providers)}]")
    print(f"  openrouter = 聚合多模型（Gemini/Claude/GPT）")
    print(f"  bianxie    = 国内可用，兼容 OpenAI 接口")
    print(f"  gemini     = Google 官方 API")
    print(f"  custom     = 自定义（本地 Ollama/LM Studio 等）")
    val = input(f"Provider [{cur_provider}]: ").strip() or cur_provider
    cfg["provider"] = val if val in PROVIDER_DEFAULTS else "bianxie"

    defaults = PROVIDER_DEFAULTS.get(cfg["provider"], PROVIDER_DEFAULTS["bianxie"])

    # API Key
    cur_key = existing.get("AUTOFIGURE_API_KEY", "")
    display_cur = ("****" + cur_key[-4:] if len(cur_key) > 4 else "****") if cur_key else "(未设置)"
    val = input(f"API Key [{display_cur}]: ").strip()
    cfg["api_key"] = val if val else cur_key

    # Base URL
    cur_url = existing.get("AUTOFIGURE_BASE_URL", defaults["base_url"])
    if cfg["provider"] == "custom":
        val = input(f"Base URL (如 http://localhost:11434/v1) [{cur_url}]: ").strip()
        cfg["base_url"] = val if val else cur_url
    else:
        cfg["base_url"] = ""
        print(f"Base URL: (使用 {cfg['provider']} 默认地址)")

    # Models
    cur_img = existing.get("AUTOFIGURE_IMAGE_MODEL", defaults["image_model"])
    val = input(f"图片生成模型 [{cur_img}]: ").strip()
    cfg["image_model"] = val if val else cur_img

    cur_svg = existing.get("AUTOFIGURE_SVG_MODEL", defaults["svg_model"])
    val = input(f"SVG 生成模型 [{cur_svg}]: ").strip()
    cfg["svg_model"] = val if val else cur_svg

    # HF Token
    cur_hf = existing.get("HF_TOKEN", "")
    display_hf = ("****" + cur_hf[-4:] if len(cur_hf) > 4 else "****") if cur_hf else "(未设置)"
    print(f"\nHuggingFace Token（用于下载 RMBG-2.0 模型）")
    print(f"  申请: https://huggingface.co/briaai/RMBG-2.0")
    val = input(f"HF_TOKEN [{display_hf}]: ").strip()
    cfg["hf_token"] = val if val else cur_hf

    # SAM Backend
    cur_sam = existing.get("AUTOFIGURE_SAM_BACKEND", "roboflow")
    print(f"\nSAM3 后端 [local/roboflow/fal]")
    print(f"  roboflow = 推荐，免费 API")
    print(f"  local    = 本地 GPU，需安装 SAM3")
    print(f"  fal      = fal.ai 付费 API")
    val = input(f"SAM Backend [{cur_sam}]: ").strip()
    cfg["sam_backend"] = val if val in ("local", "roboflow", "fal") else cur_sam

    if cfg["sam_backend"] == "roboflow":
        cur_rb = existing.get("ROBOFLOW_API_KEY", "")
        display_rb = ("****" + cur_rb[-4:] if len(cur_rb) > 4 else "****") if cur_rb else "(未设置)"
        print(f"  申请 Roboflow Key: https://roboflow.com/")
        val = input(f"  ROBOFLOW_API_KEY [{display_rb}]: ").strip()
        cfg["roboflow_key"] = val if val else cur_rb
        cfg["fal_key"] = existing.get("FAL_KEY", "")
    elif cfg["sam_backend"] == "fal":
        cur_fal = existing.get("FAL_KEY", "")
        display_fal = ("****" + cur_fal[-4:] if len(cur_fal) > 4 else "****") if cur_fal else "(未设置)"
        val = input(f"  FAL_KEY [{display_fal}]: ").strip()
        cfg["fal_key"] = val if val else cur_fal
        cfg["roboflow_key"] = existing.get("ROBOFLOW_API_KEY", "")
    else:
        cfg["roboflow_key"] = existing.get("ROBOFLOW_API_KEY", "")
        cfg["fal_key"] = existing.get("FAL_KEY", "")

    return cfg


def main():
    parser = argparse.ArgumentParser(description="AutoFigure-Edit 环境配置助手")
    parser.add_argument("--project-dir", default=".", help="AutoFigure-Edit 项目目录")
    parser.add_argument("--show", action="store_true", help="仅显示当前配置")
    parser.add_argument("--provider", help="LLM 提供商")
    parser.add_argument("--api-key", help="API Key")
    parser.add_argument("--base-url", default="", help="自定义 Base URL（本地模型用）")
    parser.add_argument("--image-model", help="图片生成模型")
    parser.add_argument("--svg-model", help="SVG 生成模型")
    parser.add_argument("--hf-token", help="HuggingFace Token")
    parser.add_argument("--sam-backend", default="roboflow", help="SAM3 后端")
    parser.add_argument("--roboflow-key", default="", help="Roboflow API Key")
    parser.add_argument("--fal-key", default="", help="fal.ai API Key")
    args = parser.parse_args()

    project_dir = Path(os.path.expanduser(args.project_dir))
    env_path = project_dir / ".env"
    existing = read_existing_env(env_path)

    if args.show:
        show_config(env_path)
        return

    # 命令行模式
    if args.provider or args.api_key:
        provider = args.provider or existing.get("AUTOFIGURE_PROVIDER", "bianxie")
        defaults = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["bianxie"])
        cfg = {
            "provider": provider,
            "api_key": args.api_key or existing.get("AUTOFIGURE_API_KEY", ""),
            "base_url": args.base_url or existing.get("AUTOFIGURE_BASE_URL", ""),
            "image_model": args.image_model or existing.get("AUTOFIGURE_IMAGE_MODEL", defaults["image_model"]),
            "svg_model": args.svg_model or existing.get("AUTOFIGURE_SVG_MODEL", defaults["svg_model"]),
            "hf_token": args.hf_token or existing.get("HF_TOKEN", ""),
            "sam_backend": args.sam_backend or existing.get("AUTOFIGURE_SAM_BACKEND", "roboflow"),
            "roboflow_key": args.roboflow_key or existing.get("ROBOFLOW_API_KEY", ""),
            "fal_key": args.fal_key or existing.get("FAL_KEY", ""),
        }
        write_env(env_path, cfg)
        show_config(env_path)
    else:
        # 交互模式
        cfg = interactive_setup(existing)
        write_env(env_path, cfg)
        print("\n💡 配置完成！运行方式：")
        print(f"   cd {project_dir}")
        print(f"   python server.py           # Web 界面（推荐）")
        print(f"   python autofigure2.py --method_file paper.txt --output_dir ./outputs")


if __name__ == "__main__":
    main()
