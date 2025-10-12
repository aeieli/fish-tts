# Fish Speech API 文件保存功能指南

## 概述

已修改 Fish Speech API，添加文件保存功能，可以像 F5-TTS 一样返回 JSON 响应并保存文件到本地。

## 快速开始

### 启用文件保存模式

```bash
# 方式 1: 使用环境变量
export FISH_SAVE_AUDIO=true
export FISH_OUTPUT_DIR="./outputs"
./start_s1_mini_api.sh

# 方式 2: 一行命令
FISH_SAVE_AUDIO=true ./start_s1_mini_api.sh
```

### 默认模式（直接返回音频流）

```bash
# 不设置环境变量，或明确设置为 false
./start_s1_mini_api.sh

# 或
FISH_SAVE_AUDIO=false ./start_s1_mini_api.sh
```

## 两种模式对比

### 模式 1: 文件保存模式 (FISH_SAVE_AUDIO=true)

**特点**:
- ✅ 保存音频文件到本地目录
- ✅ 返回 JSON 响应（包含下载链接）
- ✅ 支持 `/download/{filename}` 端点
- ✅ 支持 `/files` 端点列出文件
- ✅ 类似 F5-TTS 的接口风格

**请求示例**:
```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用 Fish Speech。",
    "references": [{"audio": "<base64_audio>", "text": "参考文本"}],
    "format": "wav"
  }'
```

**响应** (JSON):
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

**下载音频**:
```bash
curl http://127.0.0.1:8080/download/output_abc12345.wav -o output.wav
```

### 模式 2: 默认模式 (FISH_SAVE_AUDIO=false 或未设置)

**特点**:
- ✅ 直接返回音频二进制流
- ✅ 最低延迟
- ✅ 不占用磁盘空间
- ❌ 不支持 `/download/` 端点
- ❌ 不支持 `/files` 端点

**请求示例**:
```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用 Fish Speech。",
    "references": [{"audio": "<base64_audio>", "text": "参考文本"}],
    "format": "wav"
  }' \
  -o output.wav
```

**响应**: 直接返回 `audio/wav` 二进制数据

## 新增端点

### 1. 下载音频文件

```bash
GET /download/{filename}
```

仅在 `FISH_SAVE_AUDIO=true` 时可用。

**示例**:
```bash
curl http://127.0.0.1:8080/download/output_abc12345.wav -o output.wav
```

### 2. 列出已生成文件

```bash
GET /files
```

仅在 `FISH_SAVE_AUDIO=true` 时可用。

**示例**:
```bash
curl http://127.0.0.1:8080/files
```

**响应**:
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

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `FISH_SAVE_AUDIO` | false | 是否保存音频到本地 |
| `FISH_OUTPUT_DIR` | ./outputs | 输出目录路径 |

## 使用场景

### 场景 1: Web 应用（文件保存模式）

```bash
# 启动服务器
FISH_SAVE_AUDIO=true FISH_OUTPUT_DIR=/var/www/audio ./start_s1_mini_api.sh --daemon
```

**优势**:
- 可以管理已生成的音频文件
- JSON 响应便于前端处理
- 支持文件列表和下载

### 场景 2: 实时应用（默认模式）

```bash
# 启动服务器
./start_s1_mini_api.sh --daemon
```

**优势**:
- 最低延迟
- 不占用磁盘空间
- 适合一次性使用场景

### 场景 3: 流式输出（默认模式 + streaming）

```bash
# 启动服务器（默认模式）
./start_s1_mini_api.sh --daemon

# 请求时启用流式输出
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "streaming": true, "format": "wav"}' \
  -o output.wav
```

**优势**:
- 边生成边传输
- 最低的首字节延迟 (TTFB)

## Python 客户端示例

### 文件保存模式

```python
import requests
import base64

# 读取参考音频
with open("reference.wav", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode()

# TTS 请求
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好，欢迎使用 Fish Speech。",
        "references": [{"audio": audio_base64, "text": "参考文本"}],
        "format": "wav"
    }
)

# 解析 JSON 响应
result = response.json()
print(f"成功: {result['success']}")
print(f"音频地址: {result['audio_url']}")
print(f"时长: {result['duration']}秒")
print(f"推理时间: {result['inference_time_ms']}ms")

# 下载音频
audio_response = requests.get(f"http://127.0.0.1:8080{result['audio_url']}")
with open("output.wav", "wb") as f:
    f.write(audio_response.content)
```

### 默认模式

```python
import requests
import base64

# 读取参考音频
with open("reference.wav", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode()

# TTS 请求（直接获取音频流）
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好，欢迎使用 Fish Speech。",
        "references": [{"audio": audio_base64, "text": "参考文本"}],
        "format": "wav"
    }
)

# 直接保存音频（无需额外下载）
with open("output.wav", "wb") as f:
    f.write(response.content)

print("音频已保存")
```

## 与 F5-TTS 的差异

### 相同点

| 特性 | Fish (文件保存) | F5-TTS |
|------|----------------|--------|
| 保存到本地 | ✅ | ✅ |
| JSON 响应 | ✅ | ✅ |
| 下载端点 | ✅ | ✅ |
| 文件列表 | ✅ | ✅ |

### 差异点

| 特性 | Fish (文件保存) | F5-TTS |
|------|----------------|--------|
| **请求格式** | JSON + Base64 | multipart/form-data |
| **音频上传** | Base64 编码 | 直接文件上传 |
| **文件复用** | ❌ | ✅ (audio_file 参数) |
| **流式输出** | ✅ | ❌ |
| **高级参数** | ✅ (temperature等) | ❌ |

## 迁移建议

### 从 F5-TTS 迁移到 Fish Speech

1. **启用文件保存模式**:
   ```bash
   FISH_SAVE_AUDIO=true ./start_s1_mini_api.sh
   ```

2. **修改请求代码**:
   ```python
   # F5-TTS
   requests.post(url, files={"audio": f}, data={"text": "..."})

   # Fish Speech
   audio_b64 = base64.b64encode(f.read()).decode()
   requests.post(url, json={"text": "...", "references": [{"audio": audio_b64}]})
   ```

3. **响应处理保持不变**:
   - 都返回 JSON
   - 都包含 `audio_url`
   - 都支持 `/download/` 端点

## 故障排除

### 问题 1: 文件保存不生效

**症状**: 设置了 `FISH_SAVE_AUDIO=true` 但仍返回音频流

**解决**:
```bash
# 确保环境变量正确设置
echo $FISH_SAVE_AUDIO

# 检查日志中的启动信息
tail -f s1_mini_api.log | grep "Audio files will be saved"

# 重启服务器
./start_s1_mini_api.sh --stop
FISH_SAVE_AUDIO=true ./start_s1_mini_api.sh --daemon
```

### 问题 2: 下载端点 404

**症状**: 访问 `/download/` 返回 404

**原因**: 未启用文件保存模式

**解决**:
```bash
FISH_SAVE_AUDIO=true ./start_s1_mini_api.sh
```

### 问题 3: 输出目录不存在

**症状**: 启动失败，提示目录错误

**解决**:
```bash
# 确保目录存在
mkdir -p ./outputs

# 或使用绝对路径
FISH_OUTPUT_DIR=/path/to/outputs ./start_s1_mini_api.sh
```

## 性能对比

| 模式 | 响应时间 | 磁盘占用 | 内存占用 | 适用场景 |
|------|---------|---------|---------|---------|
| **文件保存** | 推理时间 | 有（累积） | 正常 | Web应用、文件管理 |
| **默认模式** | 推理时间 | 无 | 正常 | 实时应用、一次性使用 |
| **流式输出** | TTFB极低 | 无 | 正常 | 低延迟场景 |

## 总结

Fish Speech API 现在支持两种模式：

1. **文件保存模式** (`FISH_SAVE_AUDIO=true`)
   - 类似 F5-TTS
   - 返回 JSON
   - 支持文件管理
   - 适合 Web 应用

2. **默认模式** (`FISH_SAVE_AUDIO=false`)
   - Fish Speech 原生行为
   - 返回音频流
   - 最低延迟
   - 适合实时应用

根据你的使用场景选择合适的模式！

---

**更新时间**: 2025-10-12
**修改文件**: `tools/server/views.py`
**新增端点**: `/download/{filename}`, `/files`
