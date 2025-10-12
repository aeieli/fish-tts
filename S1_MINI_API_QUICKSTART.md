# Fish Speech S1-Mini API 快速开始

## 一键启动

```bash
# 1. 激活虚拟环境
source fishenv/bin/activate

# 2. 启动 API 服务器（前台）
./start_s1_mini_api.sh

# 或后台运行
./start_s1_mini_api.sh --daemon
```

访问: http://127.0.0.1:8080/docs

## 快速测试

### Python

```python
import requests
import base64

# 读取参考音频
with open("reference.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

# 生成 TTS
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "你好，欢迎使用 Fish Speech S1-Mini。",
        "references": [{"audio": audio_data}],
        "format": "wav"
    }
)

# 保存音频
with open("output.wav", "wb") as f:
    f.write(response.content)
```

### cURL

```bash
# Base64 编码参考音频
AUDIO=$(base64 -w 0 reference.wav)

# 生成 TTS
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"你好\",\"references\":[{\"audio\":\"$AUDIO\"}],\"format\":\"wav\"}" \
  -o output.wav
```

## 常用命令

```bash
# 启动（前台）
./start_s1_mini_api.sh

# 启动（后台）
./start_s1_mini_api.sh --daemon

# 停止服务
./start_s1_mini_api.sh --stop

# 查看状态
./start_s1_mini_api.sh --status

# 查看日志
tail -f s1_mini_api.log

# 使用 CPU
API_DEVICE=cpu ./start_s1_mini_api.sh

# 使用半精度（更快）
API_HALF=true ./start_s1_mini_api.sh

# 自定义端口
API_PORT=9000 ./start_s1_mini_api.sh
```

## 配置选项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| API_HOST | 监听地址 | 127.0.0.1 |
| API_PORT | 监听端口 | 8080 |
| API_DEVICE | 设备 | cuda |
| API_HALF | 半精度 | false |
| API_COMPILE | 编译加速 | false |
| API_WORKERS | Worker数 | 1 |
| API_KEY | API认证 | None |

## API 端点

- **POST /v1/tts** - TTS 生成（主要接口）
- **GET /docs** - API 文档

## 请求格式

```json
{
  "text": "要合成的文本",
  "references": [
    {
      "audio": "<base64_audio>",
      "text": "参考文本（可选）"
    }
  ],
  "format": "wav",
  "normalize": true
}
```

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 模型未找到 | `python download_s1_mini.py` |
| GPU 内存不足 | `API_HALF=true` 或 `API_DEVICE=cpu` |
| 端口被占用 | `API_PORT=9000` |
| 启动失败 | 查看日志 `tail -f s1_mini_api.log` |

## 完整文档

查看 `S1_MINI_API_GUIDE.md` 获取完整文档。

---

快速参考 | Fish Speech S1-Mini API | 2025-10-12
