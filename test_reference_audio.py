#!/usr/bin/env python3
"""
S1-Mini 参考音频测试脚本
演示如何使用参考音频进行声音克隆
"""

import requests
import base64
import sys

def generate_with_reference(reference_path, reference_text, target_text, output_path):
    """
    使用参考音频生成语音
    
    参数:
        reference_path: 参考音频文件路径
        reference_text: 参考音频的文本内容
        target_text: 要生成的目标文本
        output_path: 输出音频文件路径
    """
    print(f"📖 读取参考音频: {reference_path}")
    
    # 读取并编码参考音频
    try:
        with open(reference_path, "rb") as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print(f"✓ 参考音频大小: {len(audio_bytes)} bytes")
        print(f"✓ Base64编码长度: {len(audio_base64)} chars")
    except FileNotFoundError:
        print(f"✗ 错误: 找不到文件 {reference_path}")
        return False
    
    # 构建请求
    request_data = {
        "text": target_text,
        "references": [
            {
                "audio": audio_base64,
                "text": reference_text
            }
        ],
        "format": "wav",
        "temperature": 0.7,
        "top_p": 0.8,
        "repetition_penalty": 1.2
    }
    
    print(f"\n🚀 发送TTS请求...")
    print(f"   目标文本: {target_text}")
    print(f"   参考文本: {reference_text}")
    
    # 发送请求
    try:
        response = requests.post(
            "http://127.0.0.1:8445/v1/tts",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            # 保存生成的音频
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"\n✅ 生成成功!")
            print(f"   输出文件: {output_path}")
            print(f"   文件大小: {len(response.content)} bytes")
            return True
        else:
            print(f"\n✗ 生成失败: HTTP {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ 请求错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("S1-Mini 参考音频测试")
    print("=" * 60)
    print()
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} <参考音频.wav>")
        print()
        print("示例:")
        print(f"  {sys.argv[0]} reference.wav")
        sys.exit(1)
    
    reference_path = sys.argv[1]
    
    # 测试1: 使用参考音频生成中文
    print("\n【测试1】中文语音克隆")
    print("-" * 60)
    success1 = generate_with_reference(
        reference_path=reference_path,
        reference_text="这是参考音频的文本",  # 如果不知道，留空字符串""
        target_text="你好，这是使用参考音频生成的中文语音。",
        output_path="output_chinese_cloned.wav"
    )
    
    # 测试2: 使用参考音频生成英文
    print("\n" + "=" * 60)
    print("【测试2】英文语音克隆")
    print("-" * 60)
    success2 = generate_with_reference(
        reference_path=reference_path,
        reference_text="",  # 留空让系统自动转录
        target_text="Hello, this is a cloned voice using reference audio.",
        output_path="output_english_cloned.wav"
    )
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"中文克隆: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"英文克隆: {'✅ 成功' if success2 else '❌ 失败'}")
    print()
    print("生成的文件:")
    if success1:
        print("  - output_chinese_cloned.wav")
    if success2:
        print("  - output_english_cloned.wav")
    print()

if __name__ == "__main__":
    main()
