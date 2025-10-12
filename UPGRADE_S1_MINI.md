# 升级到 OpenAudio S1-Mini 模型

本文档介绍如何升级到最新的 OpenAudio S1-Mini 模型。

## 模型介绍

OpenAudio S1-Mini 是 Fish Speech 的最新版本，具有以下特点：

- **参数量**: 0.5B (500M)
- **训练数据**: 超过 200 万小时的多语言音频
- **技术**: 使用在线 RLHF (Reinforcement Learning from Human Feedback)
- **语言支持**: 英语、中文、日语、韩语、法语、德语、阿拉伯语、西班牙语等 13 种语言
- **性能指标** (英语):
  - WER: 0.011
  - CER: 0.005
  - Speaker Distance: 0.380

## 下载模型

### 步骤 1: 同意使用条款

访问模型页面并同意使用条款:
https://huggingface.co/fishaudio/openaudio-s1-mini

### 步骤 2: 登录 Hugging Face

```bash
# 方法 1: 使用 CLI 登录
huggingface-cli login

# 方法 2: 设置环境变量
export HF_TOKEN=your_token_here
```

获取 token: https://huggingface.co/settings/tokens

### 步骤 3: 下载模型

```bash
# 使用提供的下载脚本
python download_s1_mini.py

# 或使用更新后的 download_models.py
python tools/download_models.py
```

模型将下载到 `./checkpoints/openaudio-s1-mini/` 目录。

## 使用新模型

### 1. 命令行推理

```bash
python fish_speech/models/text2semantic/inference.py \
  --checkpoint-path checkpoints/openaudio-s1-mini \
  --text "你要合成的文本" \
  --output-dir temp
```

### 2. API 服务器

启动 API 服务器时指定新模型路径:

```bash
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth
```

**注意**: S1-Mini 使用 `codec.pth` 而不是旧版的 `firefly-gan-vq-fsq-8x1024-21hz-generator.pth`

### 3. WebUI

启动 WebUI:

```bash
python tools/run_webui.py --llama-checkpoint-path checkpoints/openaudio-s1-mini
```

### 4. Python API

```python
from fish_speech.models.text2semantic.inference import load_model, generate_long
import torch

# 加载模型
model, decode_one_token = load_model(
    checkpoint_path="checkpoints/openaudio-s1-mini",
    device="cuda",
    precision=torch.half,
    compile=False
)

# 生成语音
for response in generate_long(
    model=model,
    device="cuda",
    decode_one_token=decode_one_token,
    text="你要合成的文本",
    num_samples=1,
    max_new_tokens=2048,
):
    if response.action == "sample":
        # 处理生成的音频代码
        codes = response.codes
        print(f"Generated codes shape: {codes.shape}")
```

## 模型文件对比

### Fish Speech 1.5 (旧版)
```
checkpoints/fish-speech-1.5/
├── config.json
├── model.pth
├── firefly-gan-vq-fsq-8x1024-21hz-generator.pth  # 旧的 decoder
├── special_tokens.json
└── tokenizer.tiktoken
```

### OpenAudio S1-Mini (新版)
```
checkpoints/openaudio-s1-mini/
├── config.json
├── model.pth
├── codec.pth                                      # 新的 codec
├── special_tokens.json
└── tokenizer.tiktoken
```

## 常见问题

### Q: 为什么需要认证？
A: S1-Mini 是门控模型，需要先同意使用条款才能下载。

### Q: 新模型与旧模型兼容吗？
A: 大部分 API 兼容，但需要注意：
- Decoder 文件名从 `firefly-gan-vq-fsq-8x1024-21hz-generator.pth` 改为 `codec.pth`
- 部分配置可能有变化

### Q: 可以同时使用两个模型吗？
A: 可以，它们在不同的目录下，可以通过 `--checkpoint-path` 参数切换。

### Q: 性能对比如何？
A: S1-Mini (0.5B) 相比 Fish Speech 1.5:
- 模型更小，推理更快
- 使用 RLHF 训练，音质更自然
- 错误率更低 (WER: 0.011, CER: 0.005)

## 更新日志

- 更新了 `tools/download_models.py` 以支持下载 S1-Mini
- 添加了独立的下载脚本 `download_s1_mini.py`
- 所有推理代码已兼容新模型

## 相关链接

- 模型主页: https://huggingface.co/fishaudio/openaudio-s1-mini
- GitHub: https://github.com/fishaudio/fish-speech
- 官方网站: https://openaudio.com
- 在线演示: https://fish.audio
