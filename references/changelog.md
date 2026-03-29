# AutoFigure-Edit 更新日志与版本追踪

## 关于版本检查

运行 `scripts/check_update.py` 自动检查 GitHub 最新更新：

```bash
# 检查更新（需网络）
python scripts/check_update.py --local-dir /path/to/AutoFigure-Edit-main

# 仅查看远端最新状态
python scripts/check_update.py
```

GitHub 仓库：https://github.com/ResearAI/AutoFigure-Edit

---

## 已知版本历史

### 2026-03-24（最新）
- **新增**：DeepScientist v1.5 联动（姊妹项目发布）
- **仓库**：https://github.com/ResearAI/DeepScientist

### 2026-03-11
- **发布**：AutoFigure-Edit 论文上传 arXiv（arXiv:2603.06674）
- **收录**：HuggingFace Daily Papers
- **链接**：https://arxiv.org/abs/2603.06674

### 2026-02-17
- **上线**：AutoFigure-Edit 在线平台 deepscientist.cc
- **功能**：免费在线体验，无需本地安装

### 2026-01-26
- **接收**：AutoFigure 被 ICLR 2026 正式接收
- **论文**：https://arxiv.org/abs/2602.03828

---

## 手动更新步骤

如果 check_update.py 检测到新版本：

```bash
# 1. 进入项目目录
cd /path/to/AutoFigure-Edit-main

# 2. 查看远端变化（不修改本地文件）
git fetch origin
git log HEAD..origin/main --oneline

# 3. 更新到最新版本
git pull origin main

# 4. 重新安装依赖（如有更新）
pip install -r requirements.txt

# 5. 如果使用 Docker
docker compose build --no-cache
docker compose up -d
```

---

## 重大变更注意事项

更新前，注意以下可能影响使用的变更类型：

| 变更类型 | 说明 | 操作 |
|----------|------|------|
| `requirements.txt` 变更 | 依赖版本更新 | 重新 `pip install -r requirements.txt` |
| `server.py` 接口变更 | API 参数变化 | 检查 RunRequest 模型定义 |
| `autofigure2.py` 参数变更 | CLI 参数增删 | 查看文件顶部注释说明 |
| Provider 配置变更 | 新增/删除 LLM 提供商 | 查看 `PROVIDER_CONFIGS` 字典 |
| 默认模型变更 | 默认使用的模型名称更新 | 注意 `default_image_model` / `default_svg_model` |

---

## 反馈与问题

- **GitHub Issues**：https://github.com/ResearAI/AutoFigure-Edit/issues
- **论文联系**：tuchuan@mail.hfut.edu.cn
- **微信交流群**：见项目 README 中的二维码
