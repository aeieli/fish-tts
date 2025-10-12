#!/usr/bin/env python3
"""
下载 OpenAudio S1-Mini 模型的脚本

使用方法:
1. 首先登录 Hugging Face:
   huggingface-cli login

2. 或者直接使用 token:
   export HF_TOKEN=your_token_here
   python download_s1_mini.py

3. 获取 token: https://huggingface.co/settings/tokens
4. 同意模型使用条款: https://huggingface.co/fishaudio/openaudio-s1-mini
"""

import os
import sys
from huggingface_hub import hf_hub_download, snapshot_download

# 模型配置
REPO_ID = "fishaudio/openaudio-s1-mini"
LOCAL_DIR = "./checkpoints/openaudio-s1-mini"

# 需要下载的文件
FILES = [
    "config.json",
    "model.pth",
    "codec.pth",
    "special_tokens.json",
    "tokenizer.tiktoken",
    "README.md",
]

def download_model():
    """下载 S1-Mini 模型"""

    # 获取 token (如果有)
    token = os.environ.get("HF_TOKEN", None)

    print(f"开始下载 OpenAudio S1-Mini 模型...")
    print(f"目标目录: {LOCAL_DIR}")
    print()

    # 创建目录
    os.makedirs(LOCAL_DIR, exist_ok=True)

    try:
        # 使用 snapshot_download 下载整个模型
        print("正在下载模型文件...")
        snapshot_download(
            repo_id=REPO_ID,
            local_dir=LOCAL_DIR,
            token=token,
            ignore_patterns=["*.gitattributes", ".git*"],
        )

        print("\n✓ 模型下载完成!")
        print(f"模型位置: {LOCAL_DIR}")
        print()
        print("使用方法:")
        print(f"  python fish_speech/models/text2semantic/inference.py \\")
        print(f"    --checkpoint-path {LOCAL_DIR} \\")
        print(f"    --text '你要合成的文本'")

    except Exception as e:
        error_msg = str(e)
        print(f"\n✗ 下载失败: {error_msg}", file=sys.stderr)

        if "gated" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            print("\n模型访问受限，需要先完成以下步骤:", file=sys.stderr)
            print("1. 访问模型页面同意使用条款:", file=sys.stderr)
            print(f"   https://huggingface.co/{REPO_ID}", file=sys.stderr)
            print("\n2. 登录 Hugging Face:", file=sys.stderr)
            print("   huggingface-cli login", file=sys.stderr)
            print("\n   或者设置环境变量:", file=sys.stderr)
            print("   export HF_TOKEN=your_token_here", file=sys.stderr)
            print("\n   获取 token: https://huggingface.co/settings/tokens", file=sys.stderr)

        sys.exit(1)

if __name__ == "__main__":
    download_model()
