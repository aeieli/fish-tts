# S1-Mini 参考音频API完整文档

## 📖 概述

S1-Mini支持通过参考音频进行**声音克隆**和**风格迁移**，可以让生成的语音模仿参考音频的音色、语调和说话风格。

---

## 🎯 API端点

```
POST http://127.0.0.1:8445/v1/tts
```

---

## 📊 完整参数速查表

```json
{
  "text": "要生成的文本",
  "chunk_length": 200,
  "format": "wav",
  "references": [],
  "reference_id": null,
  "seed": null,
  "use_memory_cache": "off",
  "normalize": true,
  "streaming": false,
  "max_new_tokens": 1024,
  "top_p": 0.8,
  "repetition_penalty": 1.1,
  "temperature": 0.8
}
```

**必填参数**: 仅`text`是必填，其他都有默认值

**快速参考**:
- 💬 **文本**: `text`, `chunk_length`, `normalize`
- 🎤 **参考音频**: `references`, `reference_id`
- 🎨 **生成控制**: `temperature`, `top_p`, `repetition_penalty`, `max_new_tokens`
- 📦 **输出格式**: `format` (wav/pcm/mp3), `streaming`
- 🔧 **高级**: `seed`, `use_memory_cache`

---

## 📋 请求参数详解

### 核心参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | ✅ | - | 要生成的文本内容（支持多语言和混合语言） |
| `references` | array | ❌ | `[]` | 参考音频列表（用于声音克隆） |
| `reference_id` | string | ❌ | `null` | 已保存的参考音频ID |
| `format` | string | ❌ | `"wav"` | 输出格式：`wav`, `pcm`, `mp3` |
| `normalize` | boolean | ❌ | `true` | 是否标准化文本（推荐开启） |

### 语言支持和自动检测

**S1-Mini支持13种语言**:
- 🌍 英语 (English)、中文 (Chinese)、日语 (Japanese)、韩语 (Korean)
- 🌍 法语 (French)、德语 (German)、西班牙语 (Spanish)、阿拉伯语 (Arabic)
- 🌍 俄语 (Russian)、荷兰语 (Dutch)、意大利语 (Italian)、波兰语 (Polish)、葡萄牙语 (Portuguese)

**重要特性**:
1. **无需指定语言参数** - 模型自动识别和处理文本语言
2. **支持多语言混合** - 可在同一文本中混合使用多种语言
3. **不依赖音素** - 强大的泛化能力，可处理任何语言脚本

**避免语言误识别的技巧**:
```python
# ✅ 推荐：使用纯语言文本
{
    "text": "你好，欢迎使用语音合成系统。",  # 纯中文
    "normalize": True
}

# ✅ 推荐：清晰的语言分隔
{
    "text": "Hello everyone. 欢迎大家。Welcome. 感谢支持。",
    "normalize": True
}

# ⚠️ 注意：短文本可能误识别
{
    "text": "OK",  # 可能被识别为多种语言
    # 解决方案：添加更多上下文
    "text": "OK, let's start now."  # 更明确
}

# ✅ 使用参考音频引导语言
{
    "text": "こんにちは",  # 日语
    "references": [{
        "audio": japanese_speaker_audio_base64,
        "text": "日本語のサンプル"  # 日语参考音频
    }]
}
```

### references 参数结构

```json
{
  "references": [
    {
      "audio": "base64编码的音频数据",
      "text": "参考音频的文本内容（可选）"
    }
  ]
}
```

**详细说明**:
- `audio`: Base64编码的音频文件（支持WAV, MP3, FLAC等格式）
- `text`: 参考音频对应的文本
  - ✅ **推荐**: 提供准确的文本以获得最佳效果
  - ⚠️ **可选**: 留空字符串`""`时系统会自动转录（可能不够准确）
  - 💡 **提示**: 参考文本应与音频内容完全匹配，包括语言

### 文本处理参数

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `chunk_length` | int | 100-300 | 200 | 文本分块长度（字符数）<br>• 较大值：生成更连贯，但响应较慢<br>• 较小值：响应更快，但可能不够流畅<br>• 长文本时自动分块处理 |
| `normalize` | boolean | - | true | 文本标准化（强烈推荐）<br>• 自动处理数字：`2025` → "二零二五"<br>• 标准化标点符号<br>• 适用于英文和中文<br>• 提高生成稳定性 |

### 生成控制参数

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `max_new_tokens` | int | 1-4096 | 1024 | 最大生成token数<br>• 限制生成音频的最大长度<br>• 过小可能截断输出<br>• 过大会增加内存占用 |
| `temperature` | float | 0.1-1.0 | 0.8 | 采样温度（控制随机性）<br>• **0.5-0.7**: 保守稳定（新闻、配音）<br>• **0.8**: 平衡（通用场景）<br>• **0.9-1.0**: 富有变化（对话、情感） |
| `top_p` | float | 0.1-1.0 | 0.8 | 核采样（Top-P）<br>• **0.7**: 保守，只选最可能的70%候选<br>• **0.8**: 推荐值<br>• **0.9-1.0**: 更多样化 |
| `repetition_penalty` | float | 0.9-2.0 | 1.1 | 重复惩罚系数<br>• **1.0**: 无惩罚（可能重复）<br>• **1.1**: 轻度惩罚（默认）<br>• **1.2-1.5**: 中度惩罚（推荐用于长文本）<br>• **1.5+**: 强力惩罚（可能不自然） |

### 高级参数

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `seed` | int | - | `null` | 随机种子<br>• 设置相同种子可获得可重现结果<br>• 用于调试和A/B测试<br>• `null`表示每次随机 |
| `streaming` | boolean | - | false | 流式返回音频<br>• `true`: 边生成边返回（降低延迟）<br>• `false`: 生成完成后一次性返回<br>• ⚠️ 流式模式仅支持WAV格式 |
| `use_memory_cache` | string | - | `"off"` | 内存缓存控制<br>• `"on"`: 启用缓存（相同输入快速返回）<br>• `"off"`: 禁用缓存（每次重新生成） |

---

## 💻 完整使用示例

### 方法1: Python + Base64编码参考音频

#### 基础示例

```python
import requests
import base64

# 读取参考音频文件
with open("reference.wav", "rb") as f:
    audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# 构建请求
request_data = {
    "text": "你好，这是使用参考音频生成的语音。",
    "references": [
        {
            "audio": audio_base64,
            "text": "这是参考音频的文本内容"  # 可选，为空则自动转录
        }
    ],
    "format": "wav"
}

# 发送请求
response = requests.post(
    "http://127.0.0.1:8445/v1/tts",
    json=request_data
)

# 保存生成的音频
if response.status_code == 200:
    with open("output_cloned.wav", "wb") as f:
        f.write(response.content)
    print("✓ 语音生成成功: output_cloned.wav")
else:
    print(f"✗ 生成失败: {response.status_code}")
    print(response.text)
```

#### 多个参考音频（推荐）

```python
import requests
import base64

def load_audio_base64(file_path):
    """加载音频文件并转为Base64"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

# 使用多个参考音频可以获得更好的效果
request_data = {
    "text": "欢迎来到人工智能语音合成系统。",
    "references": [
        {
            "audio": load_audio_base64("reference1.wav"),
            "text": "第一段参考文本"
        },
        {
            "audio": load_audio_base64("reference2.wav"),
            "text": "第二段参考文本"
        }
    ],
    "format": "wav",
    # 高级参数调优
    "temperature": 0.7,      # 降低随机性，更稳定
    "top_p": 0.8,
    "repetition_penalty": 1.2
}

response = requests.post(
    "http://127.0.0.1:8445/v1/tts",
    json=request_data
)

with open("output_multi_ref.wav", "wb") as f:
    f.write(response.content)
```

#### 中英文混合

```python
request_data = {
    "text": "Hello大家好，this is a bilingual test使用S1-Mini。",
    "references": [
        {
            "audio": load_audio_base64("bilingual_reference.wav"),
            "text": "Hello你好，I can speak both languages我会说两种语言"
        }
    ],
    "normalize": True  # 自动标准化数字和特殊符号
}

response = requests.post(
    "http://127.0.0.1:8445/v1/tts",
    json=request_data
)
```

---

### 方法2: cURL命令行

#### 基础用法

```bash
# 1. 将音频文件转为Base64
AUDIO_BASE64=$(base64 -w 0 reference.wav)

# 2. 发送请求
curl -X POST http://127.0.0.1:8445/v1/tts \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"你好，这是测试\",
    \"references\": [
      {
        \"audio\": \"$AUDIO_BASE64\",
        \"text\": \"参考音频文本\"
      }
    ],
    \"format\": \"wav\"
  }" \
  -o output.wav
```

#### 使用JSON文件

```bash
# 1. 准备参考音频
AUDIO_BASE64=$(base64 -w 0 reference.wav)

# 2. 创建JSON文件
cat > request.json << EOF
{
  "text": "欢迎使用S1-Mini语音合成系统",
  "references": [
    {
      "audio": "$AUDIO_BASE64",
      "text": "这是参考音频的对应文本"
    }
  ],
  "format": "wav",
  "temperature": 0.7,
  "top_p": 0.8
}
EOF

# 3. 发送请求
curl -X POST http://127.0.0.1:8445/v1/tts \
  -H "Content-Type: application/json" \
  -d @request.json \
  -o output.wav

echo "生成完成: output.wav"
```

---

### 方法3: JavaScript/TypeScript

#### Node.js

```javascript
const fs = require('fs');
const fetch = require('node-fetch');

async function generateWithReference() {
    // 读取参考音频
    const audioBuffer = fs.readFileSync('reference.wav');
    const audioBase64 = audioBuffer.toString('base64');

    // 构建请求
    const requestData = {
        text: "你好，这是使用参考音频生成的语音。",
        references: [
            {
                audio: audioBase64,
                text: "参考音频的文本内容"
            }
        ],
        format: "wav"
    };

    // 发送请求
    const response = await fetch('http://127.0.0.1:8445/v1/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    });

    // 保存音频
    const audioBuffer = await response.buffer();
    fs.writeFileSync('output.wav', audioBuffer);
    console.log('✓ 生成成功: output.wav');
}

generateWithReference();
```

#### 浏览器端

```javascript
async function generateTTSWithReference(referenceFile, text) {
    // 读取上传的参考音频文件
    const audioBase64 = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.readAsDataURL(referenceFile);
    });

    // 发送请求
    const response = await fetch('http://127.0.0.1:8445/v1/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            references: [
                {
                    audio: audioBase64,
                    text: ""  // 留空自动转录
                }
            ],
            format: "wav"
        })
    });

    // 播放或下载音频
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    // 方式1: 直接播放
    const audio = new Audio(url);
    audio.play();

    // 方式2: 下载
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.wav';
    a.click();
}

// HTML使用示例
// <input type="file" id="referenceAudio" accept="audio/*">
// <button onclick="generateTTS()">生成语音</button>
function generateTTS() {
    const fileInput = document.getElementById('referenceAudio');
    const file = fileInput.files[0];
    const text = "要生成的文本";
    generateTTSWithReference(file, text);
}
```

---

## 🎨 参数调优指南

### 声音克隆效果优化

#### 参考音频准备建议

1. **音频质量**:
   - ✅ 清晰、无背景噪音
   - ✅ 采样率：44.1kHz或更高
   - ✅ 格式：WAV（推荐）、MP3、FLAC均可
   - ✅ 时长：3-10秒最佳

2. **参考文本**:
   - ✅ 尽量提供准确的文本
   - ✅ 如果留空，系统会自动转录（可能不够准确）
   - ✅ 文本应与音频内容完全匹配

3. **多参考音频**:
   ```python
   # 使用2-3个参考音频可以获得更稳定的效果
   "references": [
       {"audio": audio1_base64, "text": "文本1"},
       {"audio": audio2_base64, "text": "文本2"},
       {"audio": audio3_base64, "text": "文本3"}
   ]
   ```

### Temperature参数影响

| Temperature | 效果 | 适用场景 |
|-------------|------|---------|
| 0.5-0.7 | 稳定、保守 | 新闻播报、正式内容 |
| **0.8 (默认)** | 平衡 | 通用场景 |
| 0.9-1.0 | 多样、富有变化 | 对话、情感表达 |

```python
# 稳定模式（推荐用于克隆）
{
    "temperature": 0.7,
    "top_p": 0.8,
    "repetition_penalty": 1.2
}

# 富有变化（用于对话）
{
    "temperature": 0.9,
    "top_p": 0.9,
    "repetition_penalty": 1.0
}
```

### Top-P参数影响

| Top-P | 效果 | 说明 |
|-------|------|------|
| 0.7 | 保守 | 只选择最可能的70%候选 |
| **0.8 (默认)** | 平衡 | 推荐值 |
| 0.9-1.0 | 多样 | 更多随机性 |

### Repetition Penalty

| 值 | 效果 |
|----|------|
| 1.0 | 无惩罚（可能重复） |
| **1.1 (默认)** | 轻度惩罚 |
| 1.2-1.5 | 中度惩罚（推荐） |
| 1.5+ | 强力惩罚（可能不自然） |

---

## 🎯 常见场景示例

### 场景1: 专业配音（新闻、有声书）

```python
request_data = {
    "text": "今天是2025年11月5日，欢迎收听今日新闻。",
    "references": [
        {
            "audio": news_anchor_audio_base64,
            "text": "各位观众晚上好，欢迎收看今日新闻。"
        }
    ],
    "temperature": 0.7,      # 稳定
    "top_p": 0.8,
    "repetition_penalty": 1.3,  # 避免重复
    "normalize": True        # 标准化数字
}
```

### 场景2: 对话/客服

```python
request_data = {
    "text": "您好，请问有什么可以帮助您的吗？",
    "references": [
        {
            "audio": customer_service_audio_base64,
            "text": "您好，很高兴为您服务。"
        }
    ],
    "temperature": 0.8,      # 自然
    "top_p": 0.85,
    "repetition_penalty": 1.1
}
```

### 场景3: 情感表达

```python
request_data = {
    "text": "太棒了！我真的很开心！",
    "references": [
        {
            "audio": emotional_audio_base64,
            "text": "哇！这真是太令人兴奋了！"
        }
    ],
    "temperature": 0.9,      # 富有变化
    "top_p": 0.9,
    "repetition_penalty": 1.0   # 允许自然重复
}
```

### 场景4: 多语言混合

```python
request_data = {
    "text": "Welcome to Beijing欢迎来到北京，here you can enjoy beautiful scenery可以欣赏美丽的风景。",
    "references": [
        {
            "audio": bilingual_speaker_audio_base64,
            "text": "Hello大家好，I'm your tour guide我是你们的导游。"
        }
    ],
    "normalize": True
}
```

---

## 🔍 调试和验证

### 检查Base64编码

```python
import base64

# 读取音频
with open("reference.wav", "rb") as f:
    audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# 验证
print(f"原始大小: {len(audio_bytes)} bytes")
print(f"Base64大小: {len(audio_base64)} chars")
print(f"Base64前50字符: {audio_base64[:50]}")

# 解码验证
decoded = base64.b64decode(audio_base64)
assert decoded == audio_bytes, "编解码不一致！"
print("✓ Base64编码正确")
```

### 测试API响应

```python
import requests

response = requests.post(
    "http://127.0.0.1:8445/v1/tts",
    json=request_data
)

print(f"状态码: {response.status_code}")
print(f"响应头: {response.headers.get('Content-Type')}")
print(f"音频大小: {len(response.content)} bytes")

if response.status_code != 200:
    print(f"错误: {response.text}")
```

---

## ⚠️ 常见问题

### 1. 语言识别和误识别问题

#### Q: S1-Mini如何识别文本语言？

**A**: S1-Mini **没有language参数**，而是通过以下方式自动处理语言：
- 基于深度学习的自动语言识别
- 不依赖传统音素系统
- 支持13种语言的自动检测

#### Q: 如何避免中文、日文等被误识别？

**解决方案**:

**方法1: 提供足够的上下文**
```python
# ❌ 可能误识别（文本太短）
{"text": "明日"}  # "明日"在中日文中都存在

# ✅ 添加更多上下文
{"text": "明日我们将举行会议。"}  # 明确是中文
{"text": "明日の天気は晴れです。"}  # 明确是日语
```

**方法2: 使用参考音频引导**
```python
# 使用特定语言的参考音频
{
    "text": "今天天气很好",  # 中文
    "references": [{
        "audio": chinese_speaker_audio_base64,  # 中文说话人
        "text": "大家好，我是中文说话人。"  # 中文参考文本
    }]
}

# 日语示例
{
    "text": "今日はいい天気ですね",  # 日语
    "references": [{
        "audio": japanese_speaker_audio_base64,  # 日语说话人
        "text": "こんにちは、日本語です。"  # 日语参考文本
    }]
}
```

**方法3: 使用纯语言文本（最推荐）**
```python
# ✅ 纯中文
{"text": "欢迎使用语音合成系统，今天天气不错。"}

# ✅ 纯日语
{"text": "音声合成システムへようこそ、今日はいい天気です。"}

# ✅ 纯英文
{"text": "Welcome to the voice synthesis system, nice weather today."}

# ⚠️ 避免：同一句子混合相似字符
{"text": "今日weather很nice"}  # 可能导致识别混乱
```

**方法4: 多语言混合时使用清晰分隔**
```python
# ✅ 推荐：使用标点符号分隔
{
    "text": "Hello everyone. 大家好。Welcome to China. 欢迎来到中国。",
    "normalize": True
}

# ✅ 推荐：句子级别分隔
{
    "text": "This is English. これは日本語です。这是中文。",
    "normalize": True
}
```

#### Q: 为什么没有language参数可以选择？

**A**: S1-Mini采用端到端的多语言训练方式：
- 在200万小时多语言数据上训练
- 模型内部自动学习语言特征
- 无需显式指定语言参数
- 这种方式在多语言混合场景下效果更好

**对比传统方法**:
```python
# 传统TTS (其他系统)
{"text": "你好", "language": "zh-CN"}  # 需要指定

# S1-Mini (自动检测)
{"text": "你好"}  # 无需指定，自动识别
{"text": "Hello大家好"}  # 自动处理混合语言
```

#### Q: 如何测试语言识别是否正确？

**测试方法**:
```python
import requests
import base64

def test_language_detection(text, description):
    """测试语言识别"""
    response = requests.post(
        "http://127.0.0.1:8445/v1/tts",
        json={"text": text, "format": "wav"}
    )

    if response.status_code == 200:
        filename = f"test_{description}.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✓ {description}: {filename}")
        return True
    else:
        print(f"✗ {description} 失败: {response.status_code}")
        return False

# 测试不同语言
test_language_detection("你好世界", "chinese")
test_language_detection("こんにちは世界", "japanese")
test_language_detection("Hello world", "english")
test_language_detection("你好world", "mixed_cn_en")

# 听取生成的音频，验证语言是否正确
```

### 2. 参考音频不生效

**可能原因**:
- 参考音频质量差（有噪音）
- 参考文本不准确或缺失
- 参考音频太短（<2秒）
- 参考音频语言与目标文本语言不匹配

**解决方案**:
```python
# 使用多个高质量参考，且语言匹配
"references": [
    {
        "audio": audio1,  # 清晰的中文音频
        "text": "准确的中文文本1"
    },
    {
        "audio": audio2,  # 清晰的中文音频
        "text": "准确的中文文本2"
    }
]
```

### 3. Base64编码错误

**症状**: `400 Bad Request` 或解码错误

**解决方案**:
```python
# 确保正确编码
audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
# 不要包含 'data:audio/wav;base64,' 前缀
```

### 3. 音频过大导致请求超时

**限制**: 建议单个音频 < 5MB

**解决方案**:
```python
# 压缩音频或降低采样率
from pydub import AudioSegment

audio = AudioSegment.from_wav("reference.wav")
# 降采样到22050Hz
audio = audio.set_frame_rate(22050)
audio.export("reference_compressed.wav", format="wav")
```

### 4. 生成音频与参考差异大

**调优参数**:
```python
{
    "temperature": 0.6,      # 降低随机性
    "top_p": 0.7,           # 更保守的采样
    "repetition_penalty": 1.5  # 增加一致性
}
```

---

## 📊 性能建议

### 请求大小优化

| 参考音频时长 | 文件大小(WAV) | Base64大小 | 建议 |
|-------------|--------------|-----------|------|
| 3秒 | ~250KB | ~330KB | ✅ 理想 |
| 5秒 | ~420KB | ~560KB | ✅ 推荐 |
| 10秒 | ~840KB | ~1.1MB | ⚠️ 可用但偏大 |
| 20秒+ | >1.6MB | >2.1MB | ❌ 过大，建议压缩 |

### 批量生成优化

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def generate_tts(text, reference_audio):
    response = requests.post(
        "http://127.0.0.1:8445/v1/tts",
        json={
            "text": text,
            "references": [{"audio": reference_audio, "text": ""}]
        }
    )
    return response.content

# 并发生成（注意：服务器可能有并发限制）
texts = ["文本1", "文本2", "文本3"]
with ThreadPoolExecutor(max_workers=3) as executor:
    audios = list(executor.map(
        lambda t: generate_tts(t, reference_audio_base64),
        texts
    ))
```

---

## 🔗 相关端点

| 端点 | 方法 | 说明 | 状态 |
|------|------|------|------|
| `/v1/tts` | POST | TTS生成（支持参考音频） | ✅ 可用 |
| `/v1/health` | POST | 健康检查 | ✅ 可用 |
| `/v1/vqgan/encode` | POST | 音频编码为tokens | ✅ 可用 |
| `/v1/vqgan/decode` | POST | Tokens解码为音频 | ✅ 可用 |
| `/v1/references/add` | POST | 添加参考音频 | ⚠️ 已禁用* |

*注: 参考音频管理API因框架兼容性问题临时禁用，请使用`references`参数直接传递Base64编码的音频。

---

## 📖 在线API文档

访问Swagger UI查看完整交互式文档：

```
http://127.0.0.1:8445/
```

---

## 🎓 最佳实践总结

1. **参考音频**:
   - 使用清晰、无噪音的音频
   - 3-10秒最佳
   - 提供准确的参考文本
   - 多个参考音频效果更好

2. **参数调优**:
   - 开始使用默认值
   - 需要稳定性 → 降低temperature
   - 需要多样性 → 提高temperature
   - 避免重复 → 增加repetition_penalty

3. **性能优化**:
   - 压缩大音频文件
   - 使用适当的音频格式
   - 合理控制并发请求

4. **测试验证**:
   - 先用小样本测试
   - 对比不同参数效果
   - 记录最佳配置

---

**文档版本**: 2.0
**最后更新**: 2025-11-05
**适用模型**: S1-Mini (OpenAudio)
**API版本**: v1

**更新内容**:
- ✅ 添加完整参数速查表（13个参数）
- ✅ 详细说明所有参数用法和范围
- ✅ 添加语言支持和自动检测说明（13种语言）
- ✅ 提供避免语言误识别的4种方法
- ✅ 增加语言检测测试代码示例
