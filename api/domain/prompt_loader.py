"""
Prompt 文件加载器

从 api/domain/prompts/ 目录加载 markdown 格式的 prompt 文件。
支持变量替换和缓存。
"""
import os
from pathlib import Path
from typing import Optional

PROMPTS_DIR = Path(__file__).parent / "prompts"

_cache: dict[str, str] = {}

def load_prompt(category: str, name: str, **kwargs) -> str:
    """加载 prompt 文件。
    
    Args:
        category: 分类目录（dm, companion, assistant, review, safety）
        name: 文件名（不含 .md 后缀）
        **kwargs: 变量替换参数
    
    Returns:
        prompt 内容
    """
    cache_key = f"{category}/{name}"
    if cache_key in _cache:
        content = _cache[cache_key]
    else:
        file_path = PROMPTS_DIR / category / f"{name}.md"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt 文件不存在: {file_path}")
        content = file_path.read_text(encoding="utf-8")
        _cache[cache_key] = content
    
    # 变量替换
    for key, value in kwargs.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    
    return content

def list_prompts() -> dict[str, list[str]]:
    """列出所有可用的 prompt 文件。"""
    result = {}
    for category_dir in PROMPTS_DIR.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("_"):
            prompts = [f.stem for f in category_dir.glob("*.md")]
            if prompts:
                result[category_dir.name] = sorted(prompts)
    return result

def clear_cache():
    """清除 prompt 缓存。"""
    _cache.clear()
