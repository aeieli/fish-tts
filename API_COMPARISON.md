# Fish Speech vs F5-TTS API 接口对比

## 重要说明

**Fish Speech API 和 F5-TTS Go 版本的 API 格式完全不同！**

这是两个独立的 TTS 项目，使用不同的接口设计。

## 接口对比

### 1. 请求格式

#### F5-TTS (Go 版本)

```bash
# 端点: POST /tts
# 格式: multipart/form-data

curl -X POST http://localhost:8080/tts \
  -F "text=你好，欢迎使用 F5-TTS。" \
  -F "audio=@reference.wav" \
  -F "ref_text=参考文本" \
  -F "remove_silence=true" \
  -F "speed=1.0"
```

**参数**:
- `text` (string, 必填): 要合成的文本
- `audio` (file, 可选): 参考音频文件
- `audio_file` (string, 可选): 已上传的音频文件名
- `ref_text` (string, 可选): 参考文本
- `output_file` (string, 可选): 输出文件名
- `remove_silence` (bool, 可选): 是否移除静音
- `speed` (float, 可选): 语速
- `cross_fade_duration` (float, 可选): 交叉淡化时长

**响应**:
```json
{
  "success": true,
  "message": "TTS 生成成功",
  "audio_url": "/download/output_xxx.wav",
  "audio_path": "./outputs/output_xxx.wav",
  "sample_rate": 24000,
  "duration": 3.5
}
```

#### Fish Speech (S1-Mini)

```bash
# 端点: POST /v1/tts
# 格式: application/json 或 application/msgpack

curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用 Fish Speech。",
    "references": [
      {
        "audio": "<base64_encoded_audio>",
        "text": "参考文本"
      }
    ],
    "format": "wav",
    "normalize": true,
    "streaming": false
  }'
```

**参数**:
```json
{
  "text": "要合成的文本（必填）",
  "references": [
    {
      "audio": "base64 编码的音频数据（bytes）",
      "text": "参考音频的文本"
    }
  ],
  "reference_id": "可选，引用已上传的音频 ID",
  "format": "wav/pcm/mp3（默认 wav）",
  "normalize": true,
  "streaming": false,
  "chunk_length": 200,
  "max_new_tokens": 1024,
  "top_p": 0.7,
  "temperature": 0.7,
  "repetition_penalty": 1.2,
  "seed": null,
  "use_memory_cache": "off"
}
```

**响应**:
- Content-Type: `audio/wav` (或相应格式)
- Body: 二进制音频数据（直接返回音频文件，不是 JSON）

## 关键差异

| 特性 | F5-TTS (Go) | Fish Speech (S1-Mini) |
|------|-------------|----------------------|
| **端点** | `/tts` | `/v1/tts` |
| **请求格式** | `multipart/form-data` | `application/json` 或 `msgpack` |
| **音频上传** | 直接上传文件 | Base64 编码字符串 |
| **响应格式** | JSON (包含下载链接) | 直接返回音频二进制数据 |
| **参考音频** | 单个文件 | 多个参考音频（数组） |
| **文件管理** | 支持文件列表和复用 | 不支持（每次需要重新编码） |
| **流式输出** | 不支持 | 支持 (streaming=true) |
| **认证** | 无（或自定义） | Bearer Token |

## 详细对比

### 请求方式

#### F5-TTS
- ✅ 简单直观（直接上传文件）
- ✅ 支持文件复用（upload + audio_file）
- ✅ 返回 JSON 响应（包含元数据）
- ❌ 不支持流式输出

#### Fish Speech
- ✅ 标准 REST API 设计
- ✅ 支持流式输出
- ✅ 支持多个参考音频
- ✅ 更多调优参数（temperature, top_p 等）
- ❌ 需要 Base64 编码音频（增加数据量）
- ❌ 没有文件管理功能

### 使用场景

#### F5-TTS 适合:
- 简单的 TTS 应用
- 需要文件管理和复用
- 希望获得 JSON 响应和元数据
- Web 应用（文件上传）

#### Fish Speech 适合:
- 需要流式输出的场景
- 需要精细控制生成参数
- API 到 API 的集成
- 使用多个参考音频的场景

## 代码示例对比

### F5-TTS Python 客户端

```python
import requests

# 上传参考音频
with open("reference.wav", "rb") as f:
    files = {"audio": f}
    data = {"text": "你好"}
    response = requests.post(
        "http://localhost:8080/tts",
        files=files,
        data=data
    )

result = response.json()
audio_url = result["audio_url"]

# 下载音频
audio = requests.get(f"http://localhost:8080{audio_url}")
with open("output.wav", "wb") as f:
    f.write(audio.content)
```

### Fish Speech Python 客户端

```python
import requests
import base64

# 读取并编码参考音频
with open("reference.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

# TTS 请求
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好",
        "references": [{"audio": audio_data, "text": "参考文本"}],
        "format": "wav"
    }
)

# 直接保存音频
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## 如何选择

### 选择 F5-TTS 如果:
1. 你需要简单的文件上传接口
2. 你希望复用已上传的参考音频
3. 你需要 JSON 响应和元数据
4. 你在构建 Web 应用

### 选择 Fish Speech 如果:
1. 你需要流式输出（低延迟）
2. 你需要更多的生成控制参数
3. 你在构建 API 到 API 的集成
4. 你需要使用多个参考音频

## 兼容性方案

如果你想让 Fish Speech 使用 F5-TTS 风格的接口，需要创建一个适配层：

### 适配层示例

```python
from fastapi import FastAPI, File, UploadFile, Form
import base64
import requests

app = FastAPI()

@app.post("/tts")
async def f5tts_style_api(
    text: str = Form(...),
    audio: UploadFile = File(None),
    ref_text: str = Form(None)
):
    """F5-TTS 风格的接口，内部调用 Fish Speech API"""

    # 读取并编码音频
    if audio:
        audio_content = await audio.read()
        audio_base64 = base64.b64encode(audio_content).decode()
    else:
        raise HTTPException(400, "需要提供参考音频")

    # 调用 Fish Speech API
    response = requests.post(
        "http://127.0.0.1:8080/v1/tts",
        json={
            "text": text,
            "references": [{"audio": audio_base64, "text": ref_text or ""}],
            "format": "wav"
        }
    )

    # 保存音频并返回 JSON
    output_file = f"output_{uuid.uuid4().hex[:8]}.wav"
    with open(f"outputs/{output_file}", "wb") as f:
        f.write(response.content)

    return {
        "success": True,
        "message": "TTS 生成成功",
        "audio_url": f"/download/{output_file}"
    }
```

## 总结

Fish Speech 和 F5-TTS 是两个独立的项目，API 接口设计完全不同：

| 项目 | API 风格 | 优势 |
|------|---------|------|
| **F5-TTS** | 文件上传风格 | 简单、直观、支持文件管理 |
| **Fish Speech** | RESTful JSON | 标准化、流式输出、参数丰富 |

**建议**:
- 如果你习惯 F5-TTS 的接口，可以创建适配层
- 如果直接使用 Fish Speech，建议遵循其 JSON API 设计
- 两种接口各有优势，选择适合你场景的即可

---

对比文档 | Fish Speech vs F5-TTS | 2025-10-12
