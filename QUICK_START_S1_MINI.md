# OpenAudio S1-Mini 快速开始

## 一键下载和测试

### 1. 登录 Hugging Face

```bash
# 同意模型使用条款
# 访问: https://huggingface.co/fishaudio/openaudio-s1-mini

# 登录 Hugging Face
huggingface-cli login
# 或 hf auth login
```

### 2. 下载模型

```bash
# 使用专用下载脚本
python download_s1_mini.py

# 或使用通用脚本
python tools/download_models.py
```

### 3. 测试模型

```bash
# 激活虚拟环境
source fishenv/bin/activate

# 测试模型加载
python -c "
from fish_speech.models.text2semantic.llama import BaseTransformer
model = BaseTransformer.from_pretrained('checkpoints/openaudio-s1-mini', load_weights=True)
print('✓ S1-Mini 模型加载成功!')
print(f'参数数量: {sum(p.numel() for p in model.parameters())/1e6:.1f}M')
"
```

## 基本使用

### 命令行推理

```bash
# 基础用法
python fish_speech/models/text2semantic/inference.py \
  --checkpoint-path checkpoints/openaudio-s1-mini \
  --text "你好，欢迎使用 OpenAudio S1-Mini 模型。" \
  --output-dir temp

# 带参考音频的语音克隆
python fish_speech/models/text2semantic/inference.py \
  --checkpoint-path checkpoints/openaudio-s1-mini \
  --text "你要合成的文本" \
  --prompt-text "参考音频的文本" \
  --prompt-tokens path/to/reference_audio.npy \
  --output-dir temp
```

### API 服务器

```bash
# 启动 API 服务器
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
  --listen 127.0.0.1:8080

# 使用 API（另一个终端）
curl -X POST http://127.0.0.1:8080/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个测试。",
    "format": "wav"
  }' \
  --output output.wav
```

### WebUI

```bash
# 启动 WebUI
python tools/run_webui.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini

# 在浏览器中打开 http://127.0.0.1:7860
```

## Python 集成

```python
from fish_speech.models.text2semantic.inference import load_model, generate_long
import torch
import numpy as np

# 1. 加载模型
model, decode_one_token = load_model(
    checkpoint_path="checkpoints/openaudio-s1-mini",
    device="cuda",  # 或 "cpu"
    precision=torch.half,  # 使用 FP16 加速
    compile=False
)

# 2. 设置缓存
model.setup_caches(
    max_batch_size=1,
    max_seq_len=model.config.max_seq_len,
    dtype=torch.half
)

# 3. 生成语音
text = "你好，欢迎使用 OpenAudio S1-Mini。"

for response in generate_long(
    model=model,
    device="cuda",
    decode_one_token=decode_one_token,
    text=text,
    num_samples=1,
    max_new_tokens=2048,
    top_p=0.7,
    temperature=0.7,
    repetition_penalty=1.2,
):
    if response.action == "sample":
        # 保存生成的代码
        codes = response.codes
        np.save("output_codes.npy", codes.cpu().numpy())
        print(f"生成代码形状: {codes.shape}")
    elif response.action == "next":
        print("完成生成")
```

## 常见参数说明

### 推理参数

- `--checkpoint-path`: 模型路径
- `--text`: 要合成的文本
- `--num-samples`: 生成样本数量（默认：1）
- `--max-new-tokens`: 最大生成 token 数（默认：0，自动）
- `--top-p`: 核采样参数（默认：0.7，范围：0-1）
- `--temperature`: 温度参数（默认：0.7，范围：0-2）
- `--repetition-penalty`: 重复惩罚（默认：1.2，范围：0-2）
- `--device`: 设备（cuda/cpu）
- `--half`: 使用半精度（FP16）

### 语音克隆参数

- `--prompt-text`: 参考音频的文本
- `--prompt-tokens`: 参考音频的特征文件（.npy）
- `--iterative-prompt`: 是否使用迭代提示（默认：True）
- `--chunk-length`: 文本分块长度（默认：100）

## 性能优化

### 1. 使用编译加速

```bash
python fish_speech/models/text2semantic/inference.py \
  --checkpoint-path checkpoints/openaudio-s1-mini \
  --text "你的文本" \
  --compile  # 启用 torch.compile
```

### 2. 批量处理

```python
# 批量生成多个样本
for response in generate_long(
    model=model,
    device="cuda",
    decode_one_token=decode_one_token,
    text=text,
    num_samples=4,  # 同时生成 4 个样本
):
    pass
```

### 3. 调整参数

```python
# 更快的推理（降低质量）
generate_long(
    model=model,
    top_p=0.9,  # 更高的 top_p
    temperature=0.9,  # 更高的温度
    max_new_tokens=1024,  # 限制长度
)

# 更高的质量（更慢）
generate_long(
    model=model,
    top_p=0.5,  # 更低的 top_p
    temperature=0.5,  # 更低的温度
    repetition_penalty=1.5,  # 更高的惩罚
)
```

## 故障排除

### 问题 1: 401 Unauthorized

```bash
# 解决方案：确保已登录 Hugging Face
huggingface-cli login

# 检查登录状态
huggingface-cli whoami
```

### 问题 2: CUDA Out of Memory

```bash
# 解决方案 1: 使用半精度
--half

# 解决方案 2: 减少 max_new_tokens
--max-new-tokens 1024

# 解决方案 3: 使用 CPU
--device cpu
```

### 问题 3: 模型加载失败

```python
# 检查模型文件
import os
model_dir = "checkpoints/openaudio-s1-mini"
for file in ["model.pth", "codec.pth", "config.json"]:
    path = os.path.join(model_dir, file)
    exists = "✓" if os.path.exists(path) else "✗"
    print(f"{exists} {file}")
```

## 下一步

1. 阅读完整文档: `UPGRADE_S1_MINI.md`
2. 查看示例: `inference.ipynb`
3. 探索 API: `tools/api_server.py`
4. 自定义微调: 参考官方文档

## 相关链接

- 模型主页: https://huggingface.co/fishaudio/openaudio-s1-mini
- GitHub: https://github.com/fishaudio/fish-speech
- 文档: https://speech.fish.audio/
- 在线演示: https://fish.audio

---

更新时间: 2025-10-12
