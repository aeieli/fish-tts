#!/usr/bin/env python3
"""
Fish Speech S1-Mini TTS API 测试脚本

使用方法:
    # 基本用法（中文/英文）
    python test_s1_mini_tts.py --text "你好，这是一个测试。"

    # 带参考音频（声音克隆）
    python test_s1_mini_tts.py --text "Hello world" --reference audio.wav --ref-text "参考音频的文字内容"

    # 指定输出文件
    python test_s1_mini_tts.py --text "测试" --output output.wav

    # 调整生成参数
    python test_s1_mini_tts.py --text "测试" --temperature 0.9 --top-p 0.85
"""

import argparse
import base64
import requests
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Fish Speech S1-Mini TTS API 测试脚本")

    # API 配置
    parser.add_argument("--host", default="127.0.0.1", help="API 服务器地址")
    parser.add_argument("--port", type=int, default=8080, help="API 服务器端口")

    # TTS 参数
    parser.add_argument("--text", required=True, help="要合成的文本")
    parser.add_argument("--output", default="output.wav", help="输出音频文件路径")
    parser.add_argument("--format", choices=["wav", "mp3", "pcm"], default="wav", help="音频格式")

    # 参考音频（声音克隆）
    parser.add_argument("--reference", help="参考音频文件路径（用于声音克隆）")
    parser.add_argument("--ref-text", help="参考音频对应的文本")

    # 高级参数
    parser.add_argument("--chunk-length", type=int, default=200, help="分块长度 (100-300)")
    parser.add_argument("--max-new-tokens", type=int, default=1024, help="最大生成token数")
    parser.add_argument("--top-p", type=float, default=0.8, help="Top-p 采样 (0.1-1.0)")
    parser.add_argument("--repetition-penalty", type=float, default=1.1, help="重复惩罚 (0.9-2.0)")
    parser.add_argument("--temperature", type=float, default=0.8, help="温度参数 (0.1-1.0)")
    parser.add_argument("--seed", type=int, help="随机种子（可选）")
    parser.add_argument("--normalize", action="store_true", default=True, help="标准化文本")
    parser.add_argument("--no-normalize", action="store_false", dest="normalize", help="不标准化文本")

    args = parser.parse_args()

    # 构建 API URL
    api_url = f"http://{args.host}:{args.port}/v1/tts"

    # 构建请求数据
    request_data = {
        "text": args.text,
        "chunk_length": args.chunk_length,
        "format": args.format,
        "normalize": args.normalize,
        "streaming": False,
        "max_new_tokens": args.max_new_tokens,
        "top_p": args.top_p,
        "repetition_penalty": args.repetition_penalty,
        "temperature": args.temperature,
        "references": []
    }

    # 添加种子（如果指定）
    if args.seed is not None:
        request_data["seed"] = args.seed

    # 添加参考音频（如果指定）
    if args.reference:
        if not args.ref_text:
            print("错误: 使用参考音频时必须指定 --ref-text")
            return

        reference_path = Path(args.reference)
        if not reference_path.exists():
            print(f"错误: 参考音频文件不存在: {args.reference}")
            return

        # 读取参考音频并编码为 base64
        with open(reference_path, "rb") as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        request_data["references"] = [
            {
                "audio": audio_base64,
                "text": args.ref_text
            }
        ]
        print(f"使用参考音频: {args.reference}")
        print(f"参考文本: {args.ref_text}")

    # 打印请求信息
    print(f"\n连接到 API: {api_url}")
    print(f"合成文本: {args.text}")
    print(f"输出格式: {args.format}")
    print(f"参数: temperature={args.temperature}, top_p={args.top_p}, repetition_penalty={args.repetition_penalty}")
    print("\n发送请求...")

    try:
        # 发送请求
        response = requests.post(
            api_url,
            json=request_data,
            timeout=60
        )

        # 检查响应状态
        if response.status_code == 200:
            # 保存音频文件
            output_path = Path(args.output)
            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"\n✓ 成功生成音频!")
            print(f"✓ 已保存到: {output_path.absolute()}")
            print(f"✓ 文件大小: {len(response.content) / 1024:.2f} KB")
        else:
            print(f"\n✗ 请求失败!")
            print(f"✗ 状态码: {response.status_code}")
            print(f"✗ 响应内容: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"\n✗ 连接失败! 请确保 API 服务器正在运行:")
        print(f"   ./start_s1_mini.sh")
    except requests.exceptions.Timeout:
        print(f"\n✗ 请求超时!")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")


if __name__ == "__main__":
    main()
