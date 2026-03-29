#!/usr/bin/env python3
"""
AutoFigure-Edit 运行封装工具
从 .env 文件或命令行参数读取配置，构建并执行 autofigure2.py 命令。

用法:
    # 读取 .env 配置运行（推荐）
    python run_autofigure.py --project-dir /path/to/AutoFigure-Edit-main \
        --method-file paper.txt

    # 直接传参运行
    python run_autofigure.py --project-dir /path/to/AutoFigure-Edit-main \
        --method-text "We propose a novel method..." \
        --provider bianxie --api-key sk-xxx

    # 启动 Web 服务
    python run_autofigure.py --project-dir /path/to/AutoFigure-Edit-main --web

    # 使用风格参考图
    python run_autofigure.py --project-dir /path/to/AutoFigure-Edit-main \
        --method-file paper.txt --reference-image style.png
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def read_env(env_path: Path) -> dict:
    """读取 .env 文件"""
    config = {}
    if not env_path.exists():
        return config
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            config[key.strip()] = val.strip()
    return config


def find_python(project_dir: Path) -> str:
    """寻找可用的 Python 解释器"""
    # 1. 项目虚拟环境
    for venv_python in [
        project_dir / ".venv" / "Scripts" / "python.exe",   # Windows
        project_dir / ".venv" / "bin" / "python",            # Unix
        project_dir / "venv" / "Scripts" / "python.exe",
        project_dir / "venv" / "bin" / "python",
    ]:
        if venv_python.exists():
            return str(venv_python)

    # 2. 系统 Python
    for cmd in ["python3", "python", "py"]:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return cmd

    return sys.executable


def build_cli_command(python_exe: str, project_dir: Path, cfg: dict, args) -> list[str]:
    """构建 autofigure2.py 的命令行参数列表"""
    cmd = [python_exe, str(project_dir / "autofigure2.py")]

    # 方法文本
    if args.method_text:
        cmd += ["--method_text", args.method_text]
    elif args.method_file:
        method_file = Path(args.method_file)
        if not method_file.is_absolute():
            method_file = Path.cwd() / method_file
        cmd += ["--method_file", str(method_file)]
    else:
        print("[错误] 必须提供 --method-text 或 --method-file")
        sys.exit(1)

    # 输出目录
    output_dir = args.output_dir or str(project_dir / "outputs" / "run")
    cmd += ["--output_dir", output_dir]

    # Provider 配置
    provider = args.provider or cfg.get("AUTOFIGURE_PROVIDER", "bianxie")
    api_key = args.api_key or cfg.get("AUTOFIGURE_API_KEY", "")
    base_url = args.base_url or cfg.get("AUTOFIGURE_BASE_URL", "")
    image_model = args.image_model or cfg.get("AUTOFIGURE_IMAGE_MODEL", "")
    svg_model = args.svg_model or cfg.get("AUTOFIGURE_SVG_MODEL", "")

    cmd += ["--provider", provider]
    if api_key:
        cmd += ["--api_key", api_key]
    if base_url:
        cmd += ["--base_url", base_url]
    if image_model:
        cmd += ["--image_model", image_model]
    if svg_model:
        cmd += ["--svg_model", svg_model]

    # SAM3 配置
    sam_backend = args.sam_backend or cfg.get("AUTOFIGURE_SAM_BACKEND", "roboflow")
    cmd += ["--sam_backend", sam_backend]

    sam_api_key = args.sam_api_key or cfg.get("ROBOFLOW_API_KEY") or cfg.get("FAL_KEY", "")
    if sam_api_key:
        cmd += ["--sam_api_key", sam_api_key]

    # SAM Prompt
    if args.sam_prompt:
        cmd += ["--sam_prompt", args.sam_prompt]

    # 优化迭代
    if args.optimize_iterations is not None:
        cmd += ["--optimize_iterations", str(args.optimize_iterations)]

    # 合并阈值
    if args.merge_threshold is not None:
        cmd += ["--merge_threshold", str(args.merge_threshold)]

    # 参考图
    if args.reference_image:
        cmd += ["--reference_image_path", args.reference_image]

    return cmd


def main():
    parser = argparse.ArgumentParser(description="AutoFigure-Edit 运行封装")
    parser.add_argument("--project-dir", required=True, help="AutoFigure-Edit 项目目录")
    parser.add_argument("--web", action="store_true", help="启动 Web 服务而非 CLI")
    parser.add_argument("--method-file", help="论文方法段文本文件路径")
    parser.add_argument("--method-text", help="直接输入方法段文本")
    parser.add_argument("--output-dir", help="输出目录（默认: 项目/outputs/run）")
    parser.add_argument("--provider", help="LLM 提供商 (openrouter/bianxie/gemini/custom)")
    parser.add_argument("--api-key", help="API Key（覆盖 .env）")
    parser.add_argument("--base-url", help="自定义 Base URL（本地模型）")
    parser.add_argument("--image-model", help="图片生成模型")
    parser.add_argument("--svg-model", help="SVG 生成模型")
    parser.add_argument("--sam-backend", help="SAM3 后端 (local/roboflow/fal)")
    parser.add_argument("--sam-api-key", help="SAM3 API Key")
    parser.add_argument("--sam-prompt", default="icon,person,robot,animal", help="SAM3 提示词（逗号分隔）")
    parser.add_argument("--optimize-iterations", type=int, help="SVG 优化迭代次数（0=跳过）")
    parser.add_argument("--merge-threshold", type=float, help="Box 合并阈值（0=禁用）")
    parser.add_argument("--reference-image", help="风格参考图路径")
    parser.add_argument("--dry-run", action="store_true", help="只打印命令，不执行")
    args = parser.parse_args()

    project_dir = Path(os.path.expanduser(args.project_dir))
    if not project_dir.is_dir():
        print(f"[错误] 项目目录不存在: {project_dir}")
        sys.exit(1)

    # 读取配置
    env_path = project_dir / ".env"
    cfg = read_env(env_path)
    if not cfg:
        print(f"[提示] 未找到 .env 配置文件，将使用命令行参数")
        print(f"       运行 setup_env.py 可以创建配置文件")

    # 注入 HF_TOKEN 到环境变量
    hf_token = cfg.get("HF_TOKEN", "")
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    python_exe = find_python(project_dir)

    if args.web:
        # 启动 Web 服务
        cmd = [python_exe, str(project_dir / "server.py")]
        print(f"🌐 启动 Web 服务...")
        print(f"   命令: {' '.join(cmd)}")
        print(f"   访问: http://localhost:8000\n")
        if not args.dry_run:
            subprocess.run(cmd, cwd=str(project_dir))
    else:
        # CLI 模式
        cmd = build_cli_command(python_exe, project_dir, cfg, args)

        # 脱敏打印命令
        safe_cmd = []
        hide_next = False
        for token in cmd:
            if hide_next:
                safe_cmd.append("****")
                hide_next = False
            else:
                safe_cmd.append(token)
            if token in ("--api_key", "--sam_api_key"):
                hide_next = True

        print(f"🎨 运行 AutoFigure-Edit...")
        print(f"   命令: {' '.join(safe_cmd)}\n")

        if args.dry_run:
            print("[dry-run] 未实际执行")
            return

        result = subprocess.run(cmd, cwd=str(project_dir))
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
