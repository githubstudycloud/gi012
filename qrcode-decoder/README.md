# QR Code Decoder - 二维码解码工具

一个强大的Python二维码解码工具，支持多种码类型的识别和解码。

## 功能特点

- **多种码类型支持**：QR码、条形码(EAN/UPC/Code128等)、DataMatrix、PDF417
- **智能识别**：自动识别二维码类型，包括微信小程序码
- **图像增强**：对质量不佳的图片进行预处理以提高识别率
- **详细分析**：提供二维码的视觉特征分析和解码建议

## 安装

```bash
cd qrcode-decoder
pip install -r requirements.txt
```

### 依赖说明

- `opencv-python`: 图像处理和QR码检测
- `pyzbar`: 多格式条码/二维码解码
- `Pillow`: 图像处理
- `numpy`: 数值计算

### Windows用户注意

pyzbar需要zbar库，Windows上可能需要额外安装：

```bash
# 方法1: 使用预编译wheel
pip install pyzbar[scripts]

# 方法2: 如果上面失败，手动安装zbar
# 下载: https://github.com/NaturalHistoryMuseum/pyzbar/#windows
```

## 使用方法

### 基本使用

```bash
python main.py image.png
```

### JSON输出

```bash
python main.py image.png --json
```

### 保存检测区域

```bash
python main.py image.png --save-roi
```

### Python代码调用

```python
from qr_decoder import decode_qrcode, QRCodeType

# 解码图片
results = decode_qrcode("image.png")

for result in results:
    if result.success:
        print(f"类型: {result.qr_type}")
        print(f"内容: {result.content}")
        print(f"内容类型: {result.content_type}")
    else:
        print(f"信息: {result.message}")
```

### 高级分析

```python
from advanced_decoder import analyze_qrcode

analysis = analyze_qrcode("image.png")

print(f"检测到码: {analysis.detected}")
print(f"类型: {analysis.code_type}")
print(f"可解码: {analysis.is_decodable}")
print(f"内容: {analysis.content}")

for rec in analysis.recommendations:
    print(rec)
```

## 支持的码类型

| 类型 | 可检测 | 可解码 | 说明 |
|------|--------|--------|------|
| 标准QR码 | ✅ | ✅ | ISO/IEC 18004标准 |
| 条形码 | ✅ | ✅ | EAN-13/8, UPC-A/E, Code128/39/93 |
| DataMatrix | ✅ | ✅ | ISO/IEC 16022标准 |
| PDF417 | ✅ | ✅ | ISO/IEC 15438标准 |
| Aztec | ✅ | ✅ | ISO/IEC 24778标准 |
| **微信小程序码** | ✅ | ❌ | 微信专有格式 |

## ⚠️ 关于微信小程序码

### 什么是小程序码？

微信小程序码（也叫"太阳码"或"葵花码"）是微信专有的二维码格式：

- **外观**：圆形，中心有三个定位点呈三角形排列
- **编码**：使用微信专有加密算法
- **用途**：扫码打开微信小程序

### 为什么无法解码？

小程序码**不是**标准QR码，它使用微信自研的编码方式：

1. **专有格式**：编码规范未公开
2. **加密传输**：内容经过加密处理
3. **服务端验证**：需要微信服务器解析

这意味着**任何开源库都无法解码小程序码**，这不是技术限制，而是设计如此。

### 如何获取小程序码内容？

#### 方法1：微信扫一扫（推荐）
直接用微信扫码即可打开对应小程序。

#### 方法2：微信开发者工具
如果你是小程序开发者，可以使用微信开发者工具解析。

#### 方法3：调用微信官方API
需要小程序的AppID和AppSecret：

```python
import requests

def get_miniprogram_info(appid, secret):
    # 1. 获取access_token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    token_resp = requests.get(token_url).json()
    access_token = token_resp['access_token']

    # 2. 使用wxacode.get等接口
    # 注意：这只能生成小程序码，不能"逆向解析"已有的小程序码
```

**重要提示**：微信官方API只能**生成**小程序码，没有提供"逆向解析"小程序码内容的接口。

### 小程序码 vs 普通QR码对比

```
普通QR码 (可解码)          小程序码 (不可解码)
┌─────────────┐           ╭─────────────╮
│ ▄▄▄ ▄▄▄ ▄▄▄│           │   ◉     ◉   │
│ █ █     █ █│           │      ▓      │
│ ▀▀▀ ▀▀▀ ▀▀▀│           │   ◉         │
│ ▄▄▄▄▄▄▄▄▄▄▄│           │  ░▒▓▒░▒▓▒░  │
│ ▄▄▄     ▄▄▄│           │ ░▒▓▒░▒▓▒░▒▓ │
│ █ █     █ █│           │  ░▒▓▒░▒▓▒░  │
└─────────────┘           ╰─────────────╯
  标准ISO格式                微信专有格式
```

## 输出示例

### 成功解码QR码

```
处理文件: example.png
检测到 1 个结果

============================================================
结果 #1
============================================================
状态: ✓ 成功
类型: 标准QR码
内容: https://example.com
内容类型: url
位置: x=100, y=100, w=200, h=200
置信度: 100.00%
说明: 使用pyzbar成功解码 QRCODE
```

### 检测到小程序码

```
处理文件: miniprogram.png
检测到 1 个结果

============================================================
结果 #1
============================================================
状态: ✗ 失败
类型: 微信小程序码 (圆形太阳码)
内容类型: wechat_miniprogram
位置: x=50, y=50, w=300, h=300
置信度: 80.00%
说明: 检测到微信小程序码（圆形太阳码）。此类型二维码使用微信专有加密编码，
      无法通过标准库解码。只能通过微信扫一扫或调用微信官方API解析。
```

## 项目结构

```
qrcode-decoder/
├── main.py              # 命令行入口
├── qr_decoder.py        # 核心解码模块
├── advanced_decoder.py  # 高级分析模块
├── requirements.txt     # 依赖列表
└── README.md            # 说明文档
```

## API参考

### QRCodeResult

```python
@dataclass
class QRCodeResult:
    success: bool           # 是否成功解码
    qr_type: QRCodeType     # 二维码类型
    content: Optional[str]  # 解码内容
    content_type: str       # 内容类型 (url, text, etc.)
    rect: Tuple[int,int,int,int]  # 位置 (x,y,w,h)
    confidence: float       # 置信度
    message: str            # 附加信息
```

### QRCodeType

```python
class QRCodeType(Enum):
    STANDARD_QR = "standard_qr"        # 标准QR码
    WECHAT_MINIPROGRAM = "wechat_mini" # 微信小程序码
    WECHAT_QR = "wechat_qr"            # 微信二维码
    BARCODE = "barcode"                 # 条形码
    DATAMATRIX = "datamatrix"          # DataMatrix码
    PDF417 = "pdf417"                   # PDF417码
    AZTEC = "aztec"                     # Aztec码
    UNKNOWN = "unknown"                 # 未知类型
```

## License

MIT License
