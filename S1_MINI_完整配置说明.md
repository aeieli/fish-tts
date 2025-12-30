# S1-Mini 完整配置说明

## 🎉 配置完成

恭喜！您已成功完成从Fish Speech 1.5到OpenAudio S1-Mini的升级。

---

## 📋 当前配置

### 可用模型

| 模型 | 端口 | 启动命令 | 状态 |
|------|------|---------|------|
| **S1-Mini** | 8445 | `./start_s1_mini.sh --daemon` | ✅ 当前运行 |
| **Fish 1.5** | 8445 | `./start_fish15_api.sh --daemon` | ✅ 可用 |

**注意**: 两个模型共用8445端口，同时只能运行一个。

---

## 🚀 快速开始

### 基本操作

```bash
# 查看当前服务状态
./start_s1_mini.sh --status

# 生成中文语音
curl -X POST http://127.0.0.1:8445/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"你好，欢迎使用S1-Mini"}' \
  -o output.wav

# 生成英文语音
curl -X POST http://127.0.0.1:8445/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, welcome to S1-Mini"}' \
  -o output_en.wav
```

### 模型切换

```bash
# 方法1: 使用快捷脚本（推荐）
./switch_to_s1mini.sh    # 切换到 S1-Mini
./switch_to_fish15.sh    # 切换到 Fish 1.5

# 方法2: 手动切换
./start_s1_mini.sh --stop && ./start_fish15_api.sh --daemon
```

---

## 🌐 从 Windows 访问

### 一次性配置

在 Windows PowerShell（**管理员权限**）运行：

```powershell
cd \path\to\fishtts
.\setup_wsl2_port_forward.ps1
```

### 访问方式

配置后，使用localhost访问（无需关心WSL2 IP变化）：

```powershell
# 测试连接
curl http://localhost:8445/v1/health

# 生成语音
curl -X POST http://localhost:8445/v1/tts `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"你好世界\"}' `
  -o output.wav
```

---

## 📊 S1-Mini vs Fish 1.5

### S1-Mini（当前运行）

**核心优势**:
- ✅ **音质最佳**: WER 0.011（vs Fish 1.5的0.015）
- ✅ **10 codebooks**: 更强的表现力
- ✅ **RLHF训练**: 更自然、更人性化
- ✅ **13+语言**: 支持更多语言
- ✅ **200万小时训练**: vs Fish 1.5的150万

**技术规格**:
```
模型: OpenAudio S1-Mini
架构: DAC (Descript Audio Codec)
Codebooks: 10 (1语义 + 9常规)
参数: 0.86B
训练数据: 200万小时多语言数据
```

### Fish 1.5

**核心优势**:
- ✅ **速度更快**: 生成速度约快20%
- ✅ **内存更少**: GPU内存占用约4GB（vs S1-Mini的5GB）
- ✅ **久经验证**: 稳定性高

**适用场景**:
- 要求快速响应
- 资源受限环境
- 大批量生成

---

## ⚙️ 性能优化

### 启用半精度（FP16）

```bash
# 减少内存占用约50%，提速20-30%
API_HALF=true ./start_s1_mini.sh --daemon
```

### 启用编译加速

```bash
# 首次编译较慢，后续提速30-50%
API_COMPILE=true ./start_s1_mini.sh --daemon
```

### 组合优化

```bash
# 最佳性能配置
API_HALF=true API_COMPILE=true ./start_s1_mini.sh --daemon
```

---

## 🧪 测试验证

### 已完成测试

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 健康检查 | ✅ | `{"status":"ok"}` |
| 中文TTS | ✅ | 233-325KB，9-10秒 |
| 英文TTS | ✅ | 477KB，14秒 |
| 中英混合 | ✅ | 461KB，13秒 |
| Fish 1.5兼容 | ✅ | 完全保留 |

### 手动测试

```bash
# 测试脚本（如果存在）
./test_tts_service.sh

# 或手动测试
curl -X POST http://127.0.0.1:8445/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"测试文本"}' \
  -o test.wav && file test.wav
```

---

## 📚 完整文档

### 必读文档

1. **`切换模型指南.md`** - 模型切换和对比
2. **`S1_MINI_UPGRADE_COMPLETE.md`** - 升级完整报告
3. **`使用说明.md`** - 简明使用指南

### 参考文档

4. **`S1_MINI_SOLUTION_GUIDE.md`** - 技术细节和问题分析
5. **`FISH15_QUICK_START.md`** - Fish 1.5使用指南
6. **`TORCHCODEC_FIX_GUIDE.md`** - 问题排查指南

---

## 🔧 系统信息

### 环境配置

```
操作系统: WSL2 Ubuntu
GPU: NVIDIA RTX 5070 Ti (16GB, sm_120)
CUDA: 12.8
PyTorch: 2.10.0.dev+cu128
Driver: 581.29
```

### 模型文件

```
S1-Mini 模型:
  checkpoints/openaudio-s1-mini/
  ├── model.pth (1.7GB)
  ├── codec.pth (1.8GB) ← DAC架构
  ├── config.json
  ├── tokenizer.tiktoken
  └── special_tokens.json

Fish 1.5 模型:
  checkpoints/fish-speech-1.5/
  ├── model.pth (1.2GB)
  ├── firefly-gan-vq-*.pth (180MB) ← VQGAN架构
  ├── config.json
  └── tokenizer.tiktoken
```

---

## 🆘 故障排除

### 常见问题

**1. 端口被占用**
```bash
# 检查占用
lsof -i :8445

# 停止所有服务
./start_s1_mini.sh --stop
./start_fish15_api.sh --stop
```

**2. 服务启动失败**
```bash
# 查看日志
tail -50 s1_mini.log

# 检查GPU
nvidia-smi
```

**3. CUDA内存不足**
```bash
# 使用半精度模式
API_HALF=true ./start_s1_mini.sh --daemon

# 或切换到Fish 1.5（内存占用更少）
./switch_to_fish15.sh
```

**4. 从Windows无法访问**
```bash
# 在WSL2中检查服务
curl http://127.0.0.1:8445/v1/health

# 在Windows PowerShell管理员模式重新配置
.\setup_wsl2_port_forward.ps1
```

---

## 💡 使用建议

### 日常推荐

**默认使用 S1-Mini**:
- 音质最佳
- 功能最强
- 是未来方向

### 切换到 Fish 1.5 的场景

- 需要快速批量生成
- GPU内存紧张
- 要求最快响应速度

---

## 📞 获取帮助

### 查看日志

```bash
# S1-Mini日志
tail -f s1_mini.log

# Fish 1.5日志
tail -f fish15_api.log

# 实时监控
watch -n 1 'ps aux | grep api_server'
```

### 检查状态

```bash
# 服务状态
./start_s1_mini.sh --status

# GPU状态
nvidia-smi

# 端口占用
lsof -i :8445
```

---

## 🎯 快速命令参考

```bash
# === 启动/停止 ===
./start_s1_mini.sh --daemon     # 启动S1-Mini
./start_fish15_api.sh --daemon  # 启动Fish 1.5
./start_s1_mini.sh --stop       # 停止S1-Mini
./start_fish15_api.sh --stop    # 停止Fish 1.5

# === 快速切换 ===
./switch_to_s1mini.sh           # 切换到S1-Mini
./switch_to_fish15.sh           # 切换到Fish 1.5

# === 测试 ===
curl http://127.0.0.1:8445/v1/health  # 健康检查
./test_tts_service.sh           # 完整测试（如果存在）

# === 日志 ===
tail -f s1_mini.log             # 查看S1-Mini日志
tail -f fish15_api.log          # 查看Fish 1.5日志

# === 从Windows访问 ===
# PowerShell管理员模式
.\setup_wsl2_port_forward.ps1   # 配置端口转发
curl http://localhost:8445/v1/health  # 测试访问
```

---

## ✅ 验收检查清单

- [x] S1-Mini成功启动在8445端口
- [x] 中文TTS测试通过
- [x] 英文TTS测试通过
- [x] 健康检查正常
- [x] Fish 1.5向后兼容
- [x] 切换脚本已创建
- [x] 文档完整
- [x] 端口转发配置可用

---

**配置完成时间**: 2025-11-05 22:05
**配置状态**: ✅ 完全就绪
**推荐**: 优先使用S1-Mini获得最佳体验

🎉 **配置完成，祝使用愉快！** 🚀
