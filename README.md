🚀 WeChat Local OCR Server | 微信本地 OCR 服务端
极致轻量、隐私安全、低延迟的本地 OCR 解决方案。 A lightweight, privacy-focused, zero-latency local OCR solution based on WeChat's OCR engine.

📖 简介 (Introduction)
本项目将微信 PC 端提取的 OCR 引擎封装为一个本地 HTTP 服务，并提供系统托盘管理。它允许任何第三方软件（如 Obsidian、VSCode、浏览器脚本等）通过简单的 HTTP 请求调用强大的 OCR 功能。

与在线 OCR 相比，它具备以下优势：

🔒 隐私安全：所有图片处理均在本地完成，数据不出本机。

⚡ 极速响应：引擎常驻后台，毫秒级识别，无需等待冷启动。

🆓 完全免费：无需申请 API Key，无调用次数限制。

🖥️ 系统集成：提供系统托盘图标，支持开机自启和内存监控。

🔗 生态与应用 (Ecosystem & Integrations)
本项目旨在作为一个通用的 OCR 底层服务，为各种上层应用提供支持。以下是目前基于该服务开发的项目：

1. Obsidian OCR 图片识别插件 (Obsidian Local OCR)
状态：🚧 开发中

专为 Obsidian 打造的深度集成插件。

交互式选区：识别后在图片上生成可交互的文字选框。

滑动多选：支持类似 iOS 相册的滑动批量选择文字。

定点缩放：支持 Ctrl+滚轮朝着鼠标位置精准缩放预览。

一键复制：自动处理文本换行与拼接。

2. (未来项目占位符...)
欢迎开发者提交 PR 或 Issue，将您的项目链接到这里！无论是 Chrome 插件、桌面工具还是自动化脚本，只要使用了本服务，都可以展示在此处。

🛠️ 功能特性 (Features)
API 驱动：提供标准的 RESTful 接口 (POST /ocr)。

托盘管理：Windows 系统托盘图标，一键查看服务状态。

内存监控：右键菜单实时显示进程内存占用，轻量无负担。

开机自启：安装包支持注册开机启动项，开箱即用。

独立运行：打包为独立 EXE，无需安装 Python 环境。

📥 安装与使用 (Installation & Usage)
方式一：安装包部署 (推荐)
在 Releases 页面下载最新版安装包 WeChatOCR_Setup_v1.7.exe。

运行安装程序，建议勾选“创建桌面快捷方式”和“开机自动启动”。

安装完成后，服务会自动运行（查看任务栏右下角蓝色图标）。

方式二：源码运行 (开发者)
克隆本项目。

确保根目录下包含 wxocr 文件夹（需自行提取或下载 Release 包获取）。

安装依赖：

Bash
pip install -r requirements.txt
运行服务：

Bash
python ocr_tray.py
🔌 API 文档 (API Reference)
执行 OCR 识别
URL: http://127.0.0.1:12345/ocr

Method: POST

Content-Type: application/json

请求参数 (Request):

JSON
{
    "image_path": "C:\\Users\\Photos\\test.png"
}
响应示例 (Response):

JSON
{
    "code": 200,
    "width": 1920,
    "height": 1080,
    "items": [
        {
            "text": "识别到的文字内容",
            "location": { "left": 10, "top": 10, "right": 100, "bottom": 30 }
        }
    ]
}
🙏 致谢 (Acknowledgments)
本项目的诞生离不开开源社区的贡献，特别感谢以下项目和资源：

wechat-ocr : 感谢swigger对微信 OCR 组件的分析与封装，本项目基于其核心逻辑进行了 HTTP 服务化封装。项目地址：https://github.com/swigger/wechat-ocr

Flask & PyStray: 优秀的 Python Web 框架和托盘库。

Tencent WeChat: 提供了如此优秀的本地 OCR 模型。

⚠️ 免责声明 (Disclaimer)
本项目仅供学习和技术交流使用，严禁用于任何商业用途。

本项目调用的 OCR 引擎及相关 DLL 文件归 腾讯公司 (Tencent) 所有。

如果本项目侵犯了您的权益，请联系作者删除。

用户在使用本工具时产生的一切后果由用户自行承担。

Made with ❤️ by zhywjml
