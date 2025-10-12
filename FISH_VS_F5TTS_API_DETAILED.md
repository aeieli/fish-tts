# Fish Speech vs F5-TTS API 详细对比

## 修改说明

已修改 Fish Speech API (`tools/server/views.py`)，新增以下功能：

1. ✅ 支持保存音频文件到本地目录
2. ✅ 返回 JSON 响应（类似 F5-TTS）
3. ✅ 添加 `/download/{filename}` 端点
4. ✅ 添加 `/files` 端点列出已生成文件

**配置方式**:
```bash
# 启用文件保存（返回 JSON）
export FISH_SAVE_AUDIO=true
export FISH_OUTPUT_DIR="./outputs"

# 禁用文件保存（返回音频流，默认）
export FISH_SAVE_AUDIO=false
```

---

## API 接口完整对比

### 1. TTS 生成接口

#### F5-TTS API

**端点**: `POST /tts`

**请求格式**: `multipart/form-data`

**请求参数**:
```bash
curl -X POST http://localhost:8080/tts \
  -F "text=你好，欢迎使用 F5-TTS。" \
  -F "audio=@reference.wav" \
  -F "ref_text=参考音频的文本" \
  -F "remove_silence=true" \
  -F "speed=1.0" \
  -F "cross_fade_duration=0.15"
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | ✅ | - | 要合成的文本 |
| audio | file | ⚠️ | - | 参考音频文件（与 audio_file 二选一） |
| audio_file | string | ⚠️ | - | 已上传的音频文件名 |
| ref_text | string | ❌ | 自动转录 | 参考音频的文本 |
| output_file | string | ❌ | 自动生成 | 输出文件名 |
| remove_silence | bool | ❌ | false | 是否移除静音 |
| speed | float | ❌ | 1.0 | 语速（0.5-2.0） |
| cross_fade_duration | float | ❌ | 0.15 | 交叉淡化时长 |

**响应格式**: `application/json`

```json
{
  "success": true,
  "message": "TTS 生成成功",
  "audio_url": "/download/output_abc12345.wav",
  "audio_path": "./outputs/output_abc12345.wav",
  "sample_rate": 24000,
  "duration": 3.5
}
```

---

#### Fish Speech API (修改后)

**端点**: `POST /v1/tts`

**请求格式**: `application/json` 或 `application/msgpack`

**请求参数**:
```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用 Fish Speech。",
    "references": [
      {
        "audio": "<base64_encoded_audio>",
        "text": "参考音频的文本"
      }
    ],
    "format": "wav",
    "normalize": true,
    "streaming": false,
    "chunk_length": 200,
    "top_p": 0.7,
    "temperature": 0.7,
    "repetition_penalty": 1.2
  }'
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | ✅ | - | 要合成的文本 |
| references | array | ❌ | [] | 参考音频列表（支持多个） |
| references[].audio | bytes | ✅ | - | Base64 编码的音频数据 |
| references[].text | string | ✅ | - | 参考音频的文本 |
| reference_id | string | ❌ | null | 引用已上传的音频 ID |
| format | string | ❌ | wav | 输出格式（wav/pcm/mp3） |
| normalize | bool | ❌ | true | 是否归一化文本 |
| streaming | bool | ❌ | false | 是否流式输出 |
| chunk_length | int | ❌ | 200 | 文本分块长度（100-300） |
| max_new_tokens | int | ❌ | 1024 | 最大生成 token 数 |
| top_p | float | ❌ | 0.7 | 核采样参数（0.1-1.0） |
| temperature | float | ❌ | 0.7 | 温度参数（0.1-1.0） |
| repetition_penalty | float | ❌ | 1.2 | 重复惩罚（0.9-2.0） |
| seed | int | ❌ | null | 随机种子 |
| use_memory_cache | string | ❌ | off | 内存缓存（on/off） |

**响应格式** (启用 `FISH_SAVE_AUDIO=true`): `application/json`

```json
{
  "success": true,
  "message": "TTS generation successful",
  "audio_url": "/download/output_abc12345.wav",
  "audio_path": "/path/to/outputs/output_abc12345.wav",
  "sample_rate": 44100,
  "duration": 3.5,
  "format": "wav",
  "inference_time_ms": 1234,
  "timestamp": "2025-10-12T10:30:45.123456"
}
```

**响应格式** (默认 `FISH_SAVE_AUDIO=false`): `audio/wav` (二进制音频流)

---

### 2. 文件管理接口

#### F5-TTS API

##### 2.1 上传参考音频

```bash
POST /upload
Content-Type: multipart/form-data

curl -X POST http://localhost:8080/upload \
  -F "audio=@reference.wav"
```

**响应**:
```json
{
  "success": true,
  "message": "文件上传成功",
  "filename": "abc12345_reference.wav",
  "size": 1234567
}
```

##### 2.2 列出已上传文件

```bash
GET /files

curl http://localhost:8080/files
```

**响应**:
```json
[
  {
    "filename": "abc12345_reference.wav",
    "path": "./uploads/abc12345_reference.wav",
    "size": 1234567,
    "upload_time": "2025-10-12 10:30:45"
  }
]
```

##### 2.3 下载音频文件

```bash
GET /download/{filename}

curl http://localhost:8080/download/output_abc12345.wav -o output.wav
```

---

#### Fish Speech API (修改后)

##### 2.1 上传参考音频

❌ **不支持单独上传** - 需要每次在请求中 Base64 编码音频

##### 2.2 列出已生成文件

```bash
GET /files

curl http://127.0.0.1:8080/files
```

**响应** (仅在 `FISH_SAVE_AUDIO=true` 时可用):
```json
{
  "files": [
    {
      "filename": "output_abc12345.wav",
      "path": "/path/to/outputs/output_abc12345.wav",
      "size": 1234567,
      "created_time": "2025-10-12T10:30:45.123456",
      "modified_time": "2025-10-12T10:30:45.123456"
    }
  ],
  "count": 1,
  "output_dir": "/path/to/outputs"
}
```

##### 2.3 下载音频文件

```bash
GET /download/{filename}

curl http://127.0.0.1:8080/download/output_abc12345.wav -o output.wav
```

**仅在 `FISH_SAVE_AUDIO=true` 时可用**

---

### 3. 健康检查接口

#### F5-TTS API

```bash
GET /health

curl http://localhost:8080/health
```

**响应**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "upload_dir": "./uploads",
  "output_dir": "./outputs",
  "uploaded_files_count": 5
}
```

#### Fish Speech API

```bash
POST /v1/health

curl -X POST http://127.0.0.1:8080/v1/health
```

**响应**:
```json
{
  "status": "ok"
}
```

---

## 核心差异总结

### 请求格式

| 特性 | F5-TTS | Fish Speech |
|------|--------|-------------|
| **协议** | HTTP REST | HTTP REST |
| **数据格式** | multipart/form-data | JSON / MessagePack |
| **音频传递** | 直接文件上传 | Base64 编码字符串 |
| **参数风格** | 表单字段 | JSON 对象 |

### 响应格式

| 特性 | F5-TTS | Fish Speech (修改前) | Fish Speech (修改后) |
|------|--------|---------------------|---------------------|
| **默认响应** | JSON | 音频流 | 可配置 |
| **包含元数据** | ✅ | ❌ | ✅ (启用保存时) |
| **下载链接** | ✅ | ❌ | ✅ (启用保存时) |
| **音频信息** | ✅ | ❌ | ✅ (启用保存时) |

### 功能对比

| 功能 | F5-TTS | Fish Speech (原版) | Fish Speech (修改后) |
|------|--------|-------------------|---------------------|
| **文件上传** | ✅ | ❌ | ❌ |
| **文件复用** | ✅ | ❌ | ❌ |
| **本地保存** | ✅ | ❌ | ✅ (可配置) |
| **文件管理** | ✅ | ❌ | ✅ (可配置) |
| **流式输出** | ❌ | ✅ | ✅ |
| **多参考音频** | ❌ | ✅ | ✅ |
| **高级参数** | ❌ | ✅ | ✅ |

### 参数对比

#### 共同参数

| 参数 | F5-TTS | Fish Speech | 说明 |
|------|--------|-------------|------|
| text | ✅ | ✅ | 要合成的文本 |
| 参考音频 | audio | references[].audio | 音频格式不同 |
| 参考文本 | ref_text | references[].text | - |
| 输出格式 | ❌ | format | Fish 支持 wav/pcm/mp3 |

#### F5-TTS 独有参数

| 参数 | 说明 |
|------|------|
| audio_file | 引用已上传文件 |
| output_file | 指定输出文件名 |
| remove_silence | 移除静音 |
| speed | 语速控制 |
| cross_fade_duration | 交叉淡化 |

#### Fish Speech 独有参数

| 参数 | 说明 |
|------|------|
| reference_id | 引用在线参考音频 |
| streaming | 流式输出 |
| chunk_length | 文本分块 |
| normalize | 文本归一化 |
| top_p | 核采样参数 |
| temperature | 温度参数 |
| repetition_penalty | 重复惩罚 |
| seed | 随机种子 |
| max_new_tokens | 最大 token 数 |
| use_memory_cache | 内存缓存 |

---

## 使用场景对比

### F5-TTS 适合:

1. ✅ **Web 应用** - 直接文件上传，无需编码
2. ✅ **简单集成** - 接口简单直观
3. ✅ **文件管理** - 需要复用参考音频
4. ✅ **元数据需求** - 需要详细的音频信息
5. ✅ **快速原型** - 快速搭建 TTS 服务

### Fish Speech 适合:

1. ✅ **API 集成** - 标准 RESTful JSON API
2. ✅ **流式输出** - 低延迟场景
3. ✅ **精细控制** - 需要调整生成参数
4. ✅ **多参考音频** - 使用多个说话人
5. ✅ **高级应用** - 需要 temperature、top_p 等参数

---

## 代码示例对比

### F5-TTS 客户端

```python
import requests

# 1. 上传参考音频（可选，可复用）
with open("reference.wav", "rb") as f:
    upload_resp = requests.post(
        "http://localhost:8080/upload",
        files={"audio": f}
    )
    audio_filename = upload_resp.json()["filename"]

# 2. 生成 TTS（使用已上传文件）
tts_resp = requests.post(
    "http://localhost:8080/tts",
    data={
        "text": "你好，欢迎使用 F5-TTS。",
        "audio_file": audio_filename,  # 复用已上传文件
        "remove_silence": "true",
        "speed": "1.0"
    }
)

result = tts_resp.json()
print(f"音频地址: {result['audio_url']}")
print(f"时长: {result['duration']}秒")

# 3. 下载音频
audio_resp = requests.get(f"http://localhost:8080{result['audio_url']}")
with open("output.wav", "wb") as f:
    f.write(audio_resp.content)
```

### Fish Speech 客户端 (修改后，启用文件保存)

```python
import requests
import base64

# 1. 读取并编码参考音频（每次都需要）
with open("reference.wav", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode()

# 2. 生成 TTS
tts_resp = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好，欢迎使用 Fish Speech。",
        "references": [
            {
                "audio": audio_base64,  # Base64 编码
                "text": "参考音频的文本"
            }
        ],
        "format": "wav",
        "normalize": True,
        "temperature": 0.7,
        "top_p": 0.7
    }
)

# 如果启用了 FISH_SAVE_AUDIO=true
result = tts_resp.json()
print(f"音频地址: {result['audio_url']}")
print(f"时长: {result['duration']}秒")
print(f"推理时间: {result['inference_time_ms']}ms")

# 3. 下载音频
audio_resp = requests.get(f"http://127.0.0.1:8080{result['audio_url']}")
with open("output.wav", "wb") as f:
    f.write(audio_resp.content)
```

### Fish Speech 客户端 (默认，直接返回音频流)

```python
import requests
import base64

# 读取并编码参考音频
with open("reference.wav", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode()

# 生成 TTS（直接获取音频流）
tts_resp = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好，欢迎使用 Fish Speech。",
        "references": [{"audio": audio_base64, "text": "参考文本"}],
        "format": "wav"
    }
)

# 直接保存音频（无需下载步骤）
with open("output.wav", "wb") as f:
    f.write(tts_resp.content)
```

---

## 性能对比

| 指标 | F5-TTS | Fish Speech |
|------|--------|-------------|
| **首次请求** | 5-10秒 | 5-10秒 |
| **后续请求** | 100-500ms | 100-500ms |
| **流式输出** | ❌ | ✅ (降低 TTFB) |
| **并发能力** | 好 | 好 |
| **网络开销** | 小（直传文件） | 大（Base64 +33%） |

---

## 迁移指南

### 从 Fish Speech 默认模式 迁移到 文件保存模式

```bash
# 1. 设置环境变量
export FISH_SAVE_AUDIO=true
export FISH_OUTPUT_DIR="./outputs"

# 2. 启动服务器
./start_s1_mini_api.sh

# 3. 客户端代码无需修改（如果处理 JSON 响应）
```

### 从 F5-TTS 迁移到 Fish Speech

**主要改动**:

1. **音频编码**: 文件上传 → Base64 编码
2. **请求格式**: multipart/form-data → JSON
3. **响应处理**:
   - 默认: 解析 JSON → 直接保存二进制
   - 启用保存: 保持不变（JSON 响应）
4. **参数映射**:
   - `audio` → `references[0].audio`
   - `ref_text` → `references[0].text`

**示例转换**:

```python
# F5-TTS 请求
response = requests.post(
    "http://localhost:8080/tts",
    files={"audio": open("ref.wav", "rb")},
    data={"text": "测试", "ref_text": "参考"}
)

# Fish Speech 请求（启用文件保存）
audio_b64 = base64.b64encode(open("ref.wav", "rb").read()).decode()
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "测试",
        "references": [{"audio": audio_b64, "text": "参考"}]
    }
)
```

---

## 配置总结

### Fish Speech API 新增配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `FISH_SAVE_AUDIO` | false | 是否保存音频到本地 |
| `FISH_OUTPUT_DIR` | ./outputs | 输出目录路径 |

**行为对比**:

```bash
# 默认模式（FISH_SAVE_AUDIO=false）
- 响应: 直接返回音频流
- 文件: 不保存
- /download: 不可用
- /files: 不可用

# 文件保存模式（FISH_SAVE_AUDIO=true）
- 响应: 返回 JSON（包含下载链接）
- 文件: 保存到 FISH_OUTPUT_DIR
- /download: 可用
- /files: 可用
```

---

## 建议

### 选择 Fish Speech (文件保存模式) 如果:

1. 需要与 F5-TTS 类似的接口风格
2. 需要文件管理功能
3. 需要 JSON 响应和元数据
4. 需要 Fish Speech 的高级参数（temperature, top_p 等）

### 选择 Fish Speech (默认模式) 如果:

1. 需要低延迟（直接返回音频流）
2. 需要流式输出
3. 不需要文件管理
4. 追求最高性能

### 选择 F5-TTS 如果:

1. 需要文件上传和复用
2. 需要简单的 multipart/form-data 接口
3. 不需要高级生成参数
4. 追求最简单的集成方式

---

**更新时间**: 2025-10-12
**修改内容**: Fish Speech API 增加文件保存和 JSON 响应功能
