# YouTube视频转录工具项目汇总

本项目是一个YouTube视频转录工具，用于将YouTube视频中的音频内容转换为带有适当标点符号的中文文本，并保存为Markdown文件。

## 主要功能

1. 读取视频链接列表
2. 下载视频音频
3. 转录音频为中文文本
4. 使用DeepSeek API添加正确的标点符号
5. 保存为Markdown格式文件

## 文件清单

### 1. youtube_transcription.py

主脚本文件，包含所有核心功能。

### 2. requirements.txt

依赖包列表。

```
yt-dlp>=2023.3.4
requests>=2.31.0
```

### 3. fix_certificates.py

解决SSL证书问题的辅助脚本。

### 4. set_api_key.py

用于设置AssemblyAI API密钥的辅助脚本。

### 5. videos.txt

要转录的YouTube视频链接列表。

## 使用方法

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 设置API密钥：
   ```
   python set_api_key.py
   ```

3. 在videos.txt中添加YouTube视频链接（每行一个）

4. 运行转录脚本：
   ```
   python youtube_transcription.py
   ```

5. 转录结果将保存为与视频同名的Markdown文件

## 项目特点

- 使用yt-dlp高效下载音频
- 使用AssemblyAI进行高质量转录 
- 使用DeepSeek添加正确的中文标点符号
- 资源友好型设计，适合本地环境
- 完全自动化流程 