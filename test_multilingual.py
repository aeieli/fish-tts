#!/usr/bin/env python3
"""
S1-Mini 多语言测试脚本
测试语言自动检测和多语言混合功能
"""

import requests
import sys
from pathlib import Path

# API配置
API_URL = "http://127.0.0.1:8445/v1/tts"

# 测试用例：涵盖13种支持的语言
TEST_CASES = [
    # 1. 纯语言测试
    {
        "name": "chinese_pure",
        "text": "你好，欢迎使用S1-Mini语音合成系统。今天天气很好。",
        "description": "纯中文"
    },
    {
        "name": "english_pure",
        "text": "Hello, welcome to the S1-Mini speech synthesis system. The weather is nice today.",
        "description": "纯英文"
    },
    {
        "name": "japanese_pure",
        "text": "こんにちは、S1-Mini音声合成システムへようこそ。今日はいい天気ですね。",
        "description": "纯日语"
    },
    {
        "name": "korean_pure",
        "text": "안녕하세요, S1-Mini 음성 합성 시스템에 오신 것을 환영합니다. 오늘 날씨가 좋네요.",
        "description": "纯韩语"
    },
    {
        "name": "french_pure",
        "text": "Bonjour, bienvenue dans le système de synthèse vocale S1-Mini. Il fait beau aujourd'hui.",
        "description": "纯法语"
    },
    {
        "name": "german_pure",
        "text": "Hallo, willkommen beim S1-Mini Sprachsynthesesystem. Das Wetter ist heute schön.",
        "description": "纯德语"
    },
    {
        "name": "spanish_pure",
        "text": "Hola, bienvenido al sistema de síntesis de voz S1-Mini. Hace buen tiempo hoy.",
        "description": "纯西班牙语"
    },
    {
        "name": "russian_pure",
        "text": "Здравствуйте, добро пожаловать в систему синтеза речи S1-Mini. Сегодня хорошая погода.",
        "description": "纯俄语"
    },

    # 2. 混合语言测试
    {
        "name": "chinese_english_mixed",
        "text": "Hello大家好，welcome to China欢迎来到中国。",
        "description": "中英混合"
    },
    {
        "name": "multi_language_sentence",
        "text": "Hello everyone. 大家好。こんにちは。Bonjour. Hola.",
        "description": "多语言问候"
    },

    # 3. 易混淆字符测试（中日共用汉字）
    {
        "name": "chinese_with_context",
        "text": "明日我们将举行重要会议，请大家准时参加。",
        "description": "中文（带上下文）"
    },
    {
        "name": "japanese_with_context",
        "text": "明日は重要な会議を開催しますので、時間通りにご参加ください。",
        "description": "日语（带上下文）"
    },

    # 4. 短文本测试（可能存在误识别风险）
    {
        "name": "short_chinese",
        "text": "你好世界",
        "description": "短文本-中文"
    },
    {
        "name": "short_english",
        "text": "Hello world",
        "description": "短文本-英文"
    },
    {
        "name": "short_japanese",
        "text": "こんにちは世界",
        "description": "短文本-日语"
    },
]

def generate_tts(text, output_path, **kwargs):
    """
    生成TTS音频

    参数:
        text: 要生成的文本
        output_path: 输出文件路径
        **kwargs: 其他TTS参数（temperature, top_p等）
    """
    request_data = {
        "text": text,
        "format": "wav",
        **kwargs
    }

    try:
        response = requests.post(API_URL, json=request_data, timeout=60)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True, len(response.content)
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def run_tests(output_dir="multilingual_test_outputs"):
    """运行所有测试"""
    print("=" * 70)
    print("S1-Mini 多语言测试")
    print("=" * 70)
    print()

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    print(f"📁 输出目录: {output_path.absolute()}")
    print()

    # 运行测试
    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        name = test_case["name"]
        text = test_case["text"]
        desc = test_case["description"]

        print(f"[{i}/{len(TEST_CASES)}] 测试: {desc}")
        print(f"   文本: {text[:50]}{'...' if len(text) > 50 else ''}")

        output_file = output_path / f"{name}.wav"
        success, result = generate_tts(text, output_file)

        if success:
            size_kb = result / 1024
            print(f"   ✅ 成功: {output_file.name} ({size_kb:.1f} KB)")
            results.append((desc, "✅ 成功", f"{size_kb:.1f} KB"))
        else:
            print(f"   ❌ 失败: {result}")
            results.append((desc, "❌ 失败", result))

        print()

    # 打印总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print()

    success_count = sum(1 for r in results if "✅" in r[1])
    total_count = len(results)

    print(f"总测试数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    print()

    print("详细结果:")
    print("-" * 70)
    for desc, status, info in results:
        print(f"{status} {desc:30s} {info}")

    print()
    print(f"🎧 所有音频文件已保存到: {output_path.absolute()}")
    print()
    print("💡 建议:")
    print("   1. 播放生成的音频文件，验证语言识别是否正确")
    print("   2. 对比纯语言和混合语言的生成质量")
    print("   3. 注意短文本的识别准确度")
    print("   4. 如发现误识别，参考文档中的避免方法")
    print()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = "multilingual_test_outputs"

    print()
    print("🌍 S1-Mini支持的语言:")
    print("   中文、英语、日语、韩语、法语、德语、西班牙语")
    print("   阿拉伯语、俄语、荷兰语、意大利语、波兰语、葡萄牙语")
    print()
    print(f"📝 本测试将生成 {len(TEST_CASES)} 个音频文件")
    print()

    try:
        # 先测试API是否可用
        response = requests.get("http://127.0.0.1:8445/v1/health", timeout=5)
        if response.status_code != 200:
            print("❌ 错误: S1-Mini服务未运行或不可用")
            print("   请先启动服务: ./start_s1_mini.sh --daemon")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: 无法连接到S1-Mini服务")
        print(f"   {e}")
        print("   请先启动服务: ./start_s1_mini.sh --daemon")
        sys.exit(1)

    run_tests(output_dir)

if __name__ == "__main__":
    main()
