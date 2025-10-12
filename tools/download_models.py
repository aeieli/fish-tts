import os
import sys

from huggingface_hub import hf_hub_download


# Download
def check_and_download_files(repo_id, file_list, local_dir, token=None):
    os.makedirs(local_dir, exist_ok=True)
    for file in file_list:
        file_path = os.path.join(local_dir, file)
        if not os.path.exists(file_path):
            print(f"{file} 不存在，从 Hugging Face 仓库下载...")
            try:
                hf_hub_download(
                    repo_id=repo_id,
                    filename=file,
                    local_dir=local_dir,
                    token=token,
                )
            except Exception as e:
                print(f"下载 {file} 失败: {e}")
                if "gated repo" in str(e).lower() or "401" in str(e):
                    print(f"\n模型 {repo_id} 需要认证。")
                    print("请先登录 Hugging Face:")
                    print("  huggingface-cli login")
                    print("或访问 https://huggingface.co/settings/tokens 获取 token")
                    sys.exit(1)
        else:
            print(f"{file} 已存在，跳过下载。")


# 1st - Fish Speech 1.5 (Legacy)
repo_id_1 = "fishaudio/fish-speech-1.5"
local_dir_1 = "./checkpoints/fish-speech-1.5"
files_1 = [
    ".gitattributes",
    "model.pth",
    "README.md",
    "special_tokens.json",
    "tokenizer.tiktoken",
    "config.json",
    "firefly-gan-vq-fsq-8x1024-21hz-generator.pth",
]

# 2nd - OpenAudio S1-Mini (Latest)
repo_id_2 = "fishaudio/openaudio-s1-mini"
local_dir_2 = "./checkpoints/openaudio-s1-mini"
files_2 = [
    ".gitattributes",
    "README.md",
    "codec.pth",
    "config.json",
    "model.pth",
    "special_tokens.json",
    "tokenizer.tiktoken",
]

# 3rd
repo_id_3 = "fishaudio/fish-speech-1"
local_dir_3 = "./"
files_3 = [
    "ffmpeg.exe",
    "ffprobe.exe",
]

# 4th
repo_id_4 = "SpicyqSama007/fish-speech-packed"
local_dir_4 = "./"
files_4 = [
    "asr-label-win-x64.exe",
]

check_and_download_files(repo_id_1, files_1, local_dir_1)
check_and_download_files(repo_id_2, files_2, local_dir_2)

check_and_download_files(repo_id_3, files_3, local_dir_3)
check_and_download_files(repo_id_4, files_4, local_dir_4)
