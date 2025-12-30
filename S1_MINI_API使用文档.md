# Fish Speech S1-Mini API 使用文档

## API 服务器信息

- **地址**: `http://127.0.0.1:8080` (或 `http://0.0.0.0:8445`)
- **API 文档**: `http://127.0.0.1:8080/docs` (OpenAPI/Swagger)
- **健康检查**: `GET http://127.0.0.1:8080/v1/health`

## 主要 API 端点

### 1. TTS 语音合成 (POST /v1/tts)

生成语音的主要接口。

#### 请求格式

```bash
POST http://127.0.0.1:8080/v1/tts
Content-Type: application/json
```

#### 请求参数 (JSON Body)

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | 是 | - | 要合成的文本内容 |
| `format` | string | 否 | "wav" | 音频格式: "wav", "mp3", "pcm" |
| `chunk_length` | int | 否 | 200 | 分块长度 (100-300) |
| `references` | array | 否 | [] | 参考音频列表（用于声音克隆） |
| `reference_id` | string | 否 | null | 在线参考音频ID |
| `seed` | int | 否 | null | 随机种子（固定可复现结果） |
| `normalize` | bool | 否 | true | 是否标准化文本（数字等） |
| `streaming` | bool | 否 | false | 是否流式返回（仅支持wav） |
| `max_new_tokens` | int | 否 | 1024 | 最大生成token数 |
| `top_p` | float | 否 | 0.8 | Top-p 采样 (0.1-1.0) |
| `repetition_penalty` | float | 否 | 1.1 | 重复惩罚 (0.9-2.0) |
| `temperature` | float | 否 | 0.8 | 温度参数 (0.1-1.0) |

#### 参考音频格式 (references)

```json
{
  "audio": "base64编码的音频数据",
  "text": "参考音频对应的文本"
}
```

#### 响应格式

- **Content-Type**: `audio/wav` 或 `audio/mpeg` 或 `audio/pcm`
- **Content-Disposition**: `attachment; filename=audio.{format}`
- **Body**: 音频二进制数据

---

## 使用示例

### 示例 1: 基本文本转语音 (curl)

```bash
curl -X POST "http://127.0.0.1:8080/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个语音合成测试。",
    "format": "wav"
  }' \
  --output output.wav
```

### 示例 2: 带参数的请求 (curl)

```bash
curl -X POST "http://127.0.0.1:8080/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the Fish Speech S1-Mini model.",
    "format": "mp3",
    "temperature": 0.9,
    "top_p": 0.85,
    "repetition_penalty": 1.2,
    "max_new_tokens": 2048,
    "seed": 42
  }' \
  --output output.mp3
```

### 示例 3: 使用参考音频（声音克隆） (curl)

```bash
# 首先将参考音频转换为 base64
AUDIO_BASE64=$(base64 -w 0 reference.wav)

# 发送请求
curl -X POST "http://127.0.0.1:8080/v1/tts" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"这是使用参考音频生成的语音。\",
    \"format\": \"wav\",
    \"references\": [
      {
        \"audio\": \"$AUDIO_BASE64\",
        \"text\": \"参考音频中说的话\"
      }
    ]
  }" \
  --output cloned_output.wav
```

### 示例 4: Python 请求

```python
import requests
import base64

# API 配置
API_URL = "http://127.0.0.1:8080/v1/tts"

# 基本请求
response = requests.post(
    API_URL,
    json={
        "text": "你好，世界！",
        "format": "wav",
        "temperature": 0.8,
        "top_p": 0.8
    }
)

# 保存音频
if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("✓ 音频生成成功!")
else:
    print(f"✗ 请求失败: {response.status_code}")
    print(response.text)
```

### 示例 5: Python 带参考音频（声音克隆）

```python
import requests
import base64

API_URL = "http://127.0.0.1:8080/v1/tts"

# 读取参考音频
with open("reference.wav", "rb") as f:
    audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

# 发送请求
response = requests.post(
    API_URL,
    json={
        "text": "这是克隆的声音说的话。",
        "format": "wav",
        "references": [
            {
                "audio": audio_base64,
                "text": "参考音频里说的原文"
            }
        ],
        "temperature": 0.8
    }
)

# 保存结果
if response.status_code == 200:
    with open("cloned_output.wav", "wb") as f:
        f.write(response.content)
    print("✓ 声音克隆成功!")
```

### 示例 6: JavaScript/Node.js 请求

```javascript
const fs = require('fs');
const axios = require('axios');

async function generateSpeech() {
    const response = await axios.post(
        'http://127.0.0.1:8080/v1/tts',
        {
            text: '你好，这是一个测试。',
            format: 'wav',
            temperature: 0.8,
            top_p: 0.8
        },
        {
            responseType: 'arraybuffer'
        }
    );

    fs.writeFileSync('output.wav', response.data);
    console.log('✓ 音频生成成功!');
}

generateSpeech().catch(console.error);
```

---

## 其他 API 端点

### 2. VQGAN 编码 (POST /v1/vqgan/encode)

将音频编码为 token。

```bash
curl -X POST "http://127.0.0.1:8080/v1/vqgan/encode" \
  -H "Content-Type: application/json" \
  -d '{
    "audios": ["<base64编码的音频数据>"]
  }'
```

**响应**: MessagePack 格式，包含 tokens 数组

### 3. VQGAN 解码 (POST /v1/vqgan/decode)

将 token 解码为音频。

```bash
curl -X POST "http://127.0.0.1:8080/v1/vqgan/decode" \
  -H "Content-Type: application/json" \
  -d '{
    "tokens": [[[...token数据...]]]
  }'
```

**响应**: MessagePack 格式，包含 PCM float16 音频数据

### 4. 健康检查 (GET /v1/health)

```bash
curl http://127.0.0.1:8080/v1/health
```

**响应**:
```json
{
  "status": "ok"
}
```

---

## 参数调优建议

### Temperature (温度)
- **范围**: 0.1 - 1.0
- **低值 (0.5-0.7)**: 更稳定、更保守，适合朗读
- **中值 (0.8)**: 平衡自然度和稳定性（推荐）
- **高值 (0.9-1.0)**: 更有表现力，但可能不稳定

### Top-p (核采样)
- **范围**: 0.1 - 1.0
- **0.7-0.8**: 较为保守，质量稳定
- **0.8-0.9**: 平衡值（推荐）
- **0.9-1.0**: 更多样化

### Repetition Penalty (重复惩罚)
- **范围**: 0.9 - 2.0
- **1.0-1.1**: 轻微惩罚（推荐）
- **1.2-1.5**: 中等惩罚，避免重复
- **1.5+**: 强力惩罚，可能影响自然度

### Chunk Length (分块长度)
- **范围**: 100 - 300
- **100-150**: 短句，更快响应
- **200**: 平衡值（推荐）
- **250-300**: 长句，更连贯但延迟高

---

## 错误处理

### 常见错误码

| 状态码 | 说明 | 解决方法 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查 JSON 格式和参数范围 |
| 401 | 认证失败 | 检查 API Key（如果启用） |
| 500 | 服务器内部错误 | 查看服务器日志 |
| 503 | 服务不可用 | 检查服务器是否正常运行 |

### 错误响应示例

```json
{
  "detail": "Text is too long, max length is 2000"
}
```

---

## 注意事项

1. **音频格式**:
   - WAV: 无损，文件较大
   - MP3: 有损压缩，文件较小
   - PCM: 原始音频数据

2. **流式模式**:
   - 仅支持 WAV 格式
   - 设置 `"streaming": true`

3. **参考音频**:
   - 支持 WAV, MP3 等常见格式
   - 需要 base64 编码
   - 建议 3-10 秒长度
   - 需提供准确的转录文本

4. **文本长度**:
   - 默认限制可在服务器启动时配置
   - 过长文本可能影响质量

5. **并发请求**:
   - 默认 1 个 worker，不支持并发
   - 可通过 `--workers` 参数增加

---

## 启动配置

查看完整的启动选项:

```bash
./start_s1_mini.sh --help
```

环境变量配置:
```bash
# 修改端口
API_PORT=9000 ./start_s1_mini.sh

# 使用 CPU
API_DEVICE=cpu ./start_s1_mini.sh

# 启用半精度
API_HALF=true ./start_s1_mini.sh

# 后台运行
./start_s1_mini.sh --daemon

# 查看日志
tail -f s1_mini.log
```

---

## 在线 API 文档

启动服务器后，访问以下地址查看交互式 API 文档:

- **Swagger UI**: `http://127.0.0.1:8080/docs`
- **ReDoc**: `http://127.0.0.1:8080/redoc`

这些页面提供:
- 完整的 API 规范
- 交互式测试界面
- 请求/响应示例
- 参数说明
