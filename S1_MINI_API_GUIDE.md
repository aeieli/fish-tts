# Fish Speech S1-Mini API 服务器使用指南

## 概述

Fish Speech 已经内置了完整的 API 服务器（`tools/api_server.py`），支持 OpenAudio S1-Mini 模型。本指南将帮助您快速启动和使用 S1-Mini 的 TTS API 服务。

## 快速开始

### 1. 确保模型已下载

```bash
# 检查模型文件
ls -lh checkpoints/openaudio-s1-mini/

# 预期文件:
# - model.pth (1.7 GB)
# - codec.pth (1.8 GB) 或 firefly-gan-vq-*.pth
# - config.json
# - tokenizer.tiktoken
# - special_tokens.json

# 如果模型未下载，运行:
python download_s1_mini.py
```

### 2. 启动 API 服务器

#### 方式 1: 使用启动脚本（推荐）

```bash
# 激活虚拟环境
source fishenv/bin/activate

# 前台运行
./start_s1_mini_api.sh

# 后台运行
./start_s1_mini_api.sh --daemon

# 停止服务
./start_s1_mini_api.sh --stop

# 查看状态
./start_s1_mini_api.sh --status
```

#### 方式 2: 直接运行

```bash
# 激活虚拟环境
source fishenv/bin/activate

# 启动服务器
python tools/api_server.py \
  --mode tts \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/firefly-gan-vq-fsq-8x1024-21hz-generator.pth \
  --decoder-config-name firefly_gan_vq \
  --device cuda \
  --listen 127.0.0.1:8080
```

### 3. 访问 API 文档

启动后访问:
- **API 文档**: http://127.0.0.1:8080/docs
- **健康检查**: http://127.0.0.1:8080/health (如果有)

## 配置选项

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mode` | 运行模式 (tts/agent) | tts |
| `--llama-checkpoint-path` | LLaMA 模型路径 | checkpoints/fish-speech-1.5 |
| `--decoder-checkpoint-path` | Decoder 路径 | checkpoints/.../firefly-gan-vq-*.pth |
| `--decoder-config-name` | Decoder 配置名 | firefly_gan_vq |
| `--device` | 设备 (cuda/cpu) | cuda |
| `--half` | 使用半精度 (FP16) | false |
| `--compile` | 编译加速 | false |
| `--listen` | 监听地址 | 127.0.0.1:8080 |
| `--workers` | 工作进程数 | 1 |
| `--max-text-length` | 最大文本长度 | 0 (无限制) |
| `--api-key` | API Key 认证 | None |
| `--load-asr-model` | 加载 ASR 模型 | false |

### 环境变量（使用启动脚本时）

```bash
# S1-Mini 模型路径
export LLAMA_CHECKPOINT="checkpoints/openaudio-s1-mini"

# Decoder 路径（可选，如果使用 codec.pth）
export DECODER_CHECKPOINT="checkpoints/openaudio-s1-mini/codec.pth"

# 服务器配置
export API_HOST="127.0.0.1"
export API_PORT="8080"
export API_DEVICE="cuda"
export API_WORKERS="1"

# 性能优化
export API_HALF="true"          # 使用半精度
export API_COMPILE="true"       # 编译加速

# API Key 认证
export API_KEY="your-secret-key"

# 启动
./start_s1_mini_api.sh
```

## API 端点

### 1. TTS 生成（主要接口）

```bash
POST /v1/tts
```

**请求格式**:
- Content-Type: `application/json` 或 `application/msgpack`

**请求参数**:
```json
{
  "text": "你好，欢迎使用 Fish Speech S1-Mini。",
  "references": [
    {
      "audio": "<base64 encoded audio>",
      "text": "参考音频的文本"
    }
  ],
  "reference_id": "optional_reference_id",
  "format": "wav",
  "normalize": true,
  "latency": "normal"
}
```

**参数说明**:
- `text` (必填): 要合成的文本
- `references` (可选): 参考音频列表
  - `audio`: Base64 编码的音频数据
  - `text`: 参考音频的文本（可选，留空则自动转录）
- `reference_id` (可选): 引用已上传的参考音频 ID
- `format` (可选): 输出格式 (wav/flac/mp3)，默认 wav
- `normalize` (可选): 是否归一化，默认 true
- `latency` (可选): 延迟模式 (normal/balanced/low)，默认 normal

**响应**:
- Content-Type: `audio/wav` (或相应的音频格式)
- Body: 音频数据（二进制）

## 使用示例

### Python 客户端

#### 示例 1: 基础 TTS 生成

```python
import requests
import base64

# 读取参考音频
with open("reference.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

# TTS 请求
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好，欢迎使用 Fish Speech S1-Mini。这是一段测试语音。",
        "references": [
            {
                "audio": audio_data,
                "text": "这是参考音频的文本内容。"
            }
        ],
        "format": "wav"
    }
)

# 保存生成的音频
with open("output.wav", "wb") as f:
    f.write(response.content)

print("生成成功: output.wav")
```

#### 示例 2: 使用现有的 API 客户端

Fish Speech 提供了内置的客户端工具 `tools/api_client.py`:

```python
# 查看客户端使用方法
python tools/api_client.py --help
```

或查看源代码了解如何使用。

### cURL 示例

```bash
# 1. 准备参考音频（Base64 编码）
AUDIO_BASE64=$(base64 -w 0 reference.wav)

# 2. 生成 TTS
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用 Fish Speech S1-Mini。",
    "references": [
      {
        "audio": "'"$AUDIO_BASE64"'",
        "text": "参考音频的文本"
      }
    ],
    "format": "wav"
  }' \
  --output output.wav

echo "生成成功: output.wav"
```

### JavaScript 示例

```javascript
async function generateTTS() {
    // 读取参考音频
    const audioFile = await fetch('reference.wav');
    const audioBuffer = await audioFile.arrayBuffer();
    const audioBase64 = btoa(
        String.fromCharCode(...new Uint8Array(audioBuffer))
    );

    // TTS 请求
    const response = await fetch('http://127.0.0.1:8080/v1/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: '你好，欢迎使用 Fish Speech S1-Mini。',
            references: [
                {
                    audio: audioBase64,
                    text: '参考音频的文本',
                },
            ],
            format: 'wav',
        }),
    });

    // 保存音频
    const audioBlob = await response.blob();
    const url = URL.createObjectURL(audioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.wav';
    a.click();
}

generateTTS();
```

## 性能优化

### 1. 使用半精度 (FP16)

```bash
# 使用脚本
API_HALF=true ./start_s1_mini_api.sh

# 或直接运行
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --half
```

**效果**:
- 内存占用减少约 50%
- 推理速度提升 20-30%
- 音质几乎无损

### 2. 启用编译加速

```bash
# 使用脚本
API_COMPILE=true ./start_s1_mini_api.sh

# 或直接运行
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --compile
```

**效果**:
- 首次推理较慢（需要编译）
- 后续推理速度提升 30-50%

### 3. 多 Worker 进程

```bash
# 使用 4 个 worker 进程
API_WORKERS=4 ./start_s1_mini_api.sh
```

**注意**:
- 每个 worker 会加载一份模型
- 内存占用 = 单模型内存 × Worker 数量
- 适合高并发场景

### 4. 使用 CPU（如果 GPU 内存不足）

```bash
API_DEVICE=cpu ./start_s1_mini_api.sh
```

## 常见问题

### 1. 模型加载失败

**问题**: 启动时提示找不到模型文件

**解决**:
```bash
# 检查模型文件
ls -lh checkpoints/openaudio-s1-mini/

# 重新下载模型
python download_s1_mini.py
```

### 2. CUDA Out of Memory

**问题**: GPU 内存不足

**解决方案**:
```bash
# 方案 1: 使用半精度
API_HALF=true ./start_s1_mini_api.sh

# 方案 2: 使用 CPU
API_DEVICE=cpu ./start_s1_mini_api.sh

# 方案 3: 减少 worker 数量
API_WORKERS=1 ./start_s1_mini_api.sh
```

### 3. 端口被占用

**问题**: `Address already in use`

**解决**:
```bash
# 查找占用进程
lsof -i :8080

# 使用其他端口
API_PORT=9000 ./start_s1_mini_api.sh
```

### 4. 音频质量问题

**症状**: 生成的音频有杂音或质量差

**解决方案**:
1. 使用高质量的参考音频（24kHz 采样率）
2. 提供准确的参考文本
3. 确保参考音频时长适中（3-10 秒）
4. 避免使用背景噪音较大的音频

### 5. 请求超时

**问题**: 长文本生成超时

**解决方案**:
```bash
# 增加最大文本长度限制
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --max-text-length 500
```

### 6. Decoder 文件找不到

**问题**: 找不到 firefly-gan-vq-*.pth 文件

**解决方案**:

S1-Mini 可能使用 `codec.pth` 而不是 `firefly-gan-vq-*.pth`:

```bash
# 方案 1: 使用 codec.pth
DECODER_CHECKPOINT="checkpoints/openaudio-s1-mini/codec.pth" ./start_s1_mini_api.sh

# 方案 2: 下载标准 decoder
python tools/download_models.py
```

## 监控和日志

### 查看日志

```bash
# 后台模式日志
tail -f s1_mini_api.log

# 实时查看（带颜色）
tail -f s1_mini_api.log | grep -E 'ERROR|WARNING|INFO'
```

### 查看状态

```bash
# 使用脚本
./start_s1_mini_api.sh --status

# 手动检查进程
ps aux | grep api_server.py

# 检查端口
lsof -i :8080
```

### 重启服务

```bash
# 使用脚本
./start_s1_mini_api.sh --stop
./start_s1_mini_api.sh --daemon

# 或一行命令
./start_s1_mini_api.sh --stop && ./start_s1_mini_api.sh --daemon
```

## 安全建议

### 1. 启用 API Key 认证

```bash
# 生成随机 API Key
API_KEY=$(openssl rand -hex 32)

# 启动服务器
API_KEY=$API_KEY ./start_s1_mini_api.sh --daemon

# 客户端请求时需要带上 Authorization header
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "测试"}'
```

### 2. 限制监听地址

```bash
# 只监听本地
API_HOST=127.0.0.1 ./start_s1_mini_api.sh

# 监听所有接口（生产环境需要配合防火墙）
API_HOST=0.0.0.0 ./start_s1_mini_api.sh
```

### 3. 使用反向代理 (Nginx)

```nginx
# /etc/nginx/sites-available/fish-speech-api
server {
    listen 80;
    server_name api.example.com;

    # 限制请求大小
    client_max_body_size 50M;

    # 增加超时时间
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 验证 API Key
        if ($http_authorization != "Bearer your-api-key") {
            return 401;
        }
    }
}
```

## 生产部署

### 使用 systemd 服务

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/fish-speech-s1-mini.service
```

```ini
[Unit]
Description=Fish Speech S1-Mini API Server
After=network.target

[Service]
Type=simple
User=eric
WorkingDirectory=/home/eric/src/fishtts
Environment="PATH=/home/eric/src/fishtts/fishenv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/eric/src/fishtts/fishenv/bin/python tools/api_server.py \
  --mode tts \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/firefly-gan-vq-fsq-8x1024-21hz-generator.pth \
  --decoder-config-name firefly_gan_vq \
  --device cuda \
  --listen 127.0.0.1:8080 \
  --half
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# 2. 重新加载 systemd
sudo systemctl daemon-reload

# 3. 启动服务
sudo systemctl start fish-speech-s1-mini

# 4. 设置开机自启
sudo systemctl enable fish-speech-s1-mini

# 5. 查看状态
sudo systemctl status fish-speech-s1-mini

# 6. 查看日志
sudo journalctl -u fish-speech-s1-mini -f
```

### 使用 Docker

```bash
# 1. 构建镜像
docker build -t fish-speech-s1-mini .

# 2. 运行容器
docker run -d \
  --name fish-speech-api \
  --gpus all \
  -p 8080:8080 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  fish-speech-s1-mini \
  python tools/api_server.py \
    --llama-checkpoint-path checkpoints/openaudio-s1-mini \
    --device cuda \
    --listen 0.0.0.0:8080

# 3. 查看日志
docker logs -f fish-speech-api

# 4. 停止容器
docker stop fish-speech-api
```

## 与 Fish Speech 1.5 的对比

| 特性 | Fish Speech 1.5 | OpenAudio S1-Mini |
|------|----------------|-------------------|
| 参数量 | 1.4B | 0.86B |
| 模型文件大小 | ~2.8 GB | ~3.5 GB |
| 内存占用 (GPU) | ~5-6 GB | ~4-5 GB |
| 推理速度 | 基准 | 快 10-20% |
| 音质 (WER) | ~0.015 | 0.011 |
| 音质 (CER) | ~0.008 | 0.005 |
| 支持语言 | 8+ | 13+ |
| 训练数据 | 150 万小时 | 200 万小时 |
| RLHF 训练 | 否 | 是 |

**总结**: S1-Mini 在模型更小的同时，音质和泛化能力都有显著提升。

## 相关链接

- **Fish Speech GitHub**: https://github.com/fishaudio/fish-speech
- **S1-Mini 模型**: https://huggingface.co/fishaudio/openaudio-s1-mini
- **在线演示**: https://fish.audio
- **文档**: https://speech.fish.audio/

## 许可证

OpenAudio S1-Mini 模型使用 CC-BY-NC-SA-4.0 许可证，仅限非商业用途。

---

更新时间: 2025-10-12
Fish Speech S1-Mini API 服务器使用指南
