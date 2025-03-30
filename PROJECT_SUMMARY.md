# YouTube视频转录工具项目汇总

本项目是一个YouTube视频转录工具，用于将YouTube视频中的音频内容转换为带有适当标点符号的中文文本，并保存为Markdown文件。

## 主要功能

1. 自动搜索指定关键词的YouTube视频
2. 支持从关键字文件读取多个关键字，同时命中所有关键字才抓取视频
3. 支持在配置文件中设置每次抓取的视频数量
4. 读取视频链接列表
5. 下载视频音频
6. 转录音频为中文文本
7. 使用DeepSeek API添加正确的标点符号
8. 保存为Markdown格式文件到output目录
9. 自动化执行搜索和转录流程
10. 交互式管理关键字和视频数量配置

## 文件清单

### 1. youtube_transcription.py

主脚本文件，包含所有核心转录功能。

### 2. search_youtube_videos.py

基础搜索脚本，使用BeautifulSoup搜索YouTube视频并保存链接。支持从keywords.txt文件读取多个关键字和视频数量配置。

### 3. advanced_search.py

高级搜索脚本，使用Selenium进行更可靠的YouTube视频搜索，适用于普通网络请求不可用的情况。支持从keywords.txt文件读取多个关键字和视频数量配置。

### 4. auto_search_and_transcribe.py

自动化脚本，一键执行搜索和转录任务，支持从keywords.txt文件读取关键字和数量配置。

### 5. keywords.txt

包含搜索配置的文件，格式如下：
- 第一行：搜索关键字，多个关键字用逗号分隔，搜索时要求视频同时包含所有关键字
- 第二行：每次抓取的视频数量

示例：
```
紫微斗数,八字
20
```

### 6. run.sh

交互式Shell脚本，提供菜单驱动的用户界面，包含管理关键字和视频数量的功能。

### 7. requirements.txt

依赖包列表。

```
yt-dlp>=2023.3.4
requests>=2.31.0
beautifulsoup4>=4.9.3
selenium>=4.9.0
webdriver-manager>=3.8.6
```

### 8. fix_certificates.py

解决SSL证书问题的辅助脚本。

### 9. set_api_key.py

用于设置AssemblyAI API密钥的辅助脚本。

### 10. videos.txt

要转录的YouTube视频链接列表。

### 11. output/

转录结果输出目录，所有生成的Markdown文件都会保存在此目录中。

## 使用方法

### 快速开始（交互式界面）

```
./run.sh
```

通过交互菜单可以：
- 一键搜索和转录视频
- 单独执行搜索或转录
- 管理搜索关键字和视频数量
- 查看当前配置

### 自动搜索和转录（一键执行）

```
python auto_search_and_transcribe.py
```

可选参数：
- `--keywords-file keywords.txt` - 自定义关键字文件路径
- `--limit 10` - 自定义搜索结果数量（覆盖配置文件中的设置）
- `--use-selenium` - 使用Selenium进行更可靠的搜索
- `--skip-search` - 跳过搜索步骤，直接执行转录
- `--skip-transcribe` - 仅执行搜索步骤，不执行转录

### 管理配置

1. 使用 `./run.sh` 脚本并选择"管理配置"选项，可以：
   - 修改关键字
   - 修改视频数量
   - 同时修改关键字和视频数量

2. 或者直接编辑 keywords.txt 文件，确保格式正确：
   - 第一行：关键字（逗号分隔）
   - 第二行：视频数量

示例 keywords.txt 文件内容：
```
紫微斗数,八字,命理
30
```

### 仅搜索视频

基础搜索（简单、无依赖）：
```
python search_youtube_videos.py
```

高级搜索（更可靠，需要Chrome浏览器）：
```
python advanced_search.py
```

自定义搜索示例：
```
python search_youtube_videos.py --keywords-file my_keywords.txt --limit 10
```

### 仅转录视频

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 设置API密钥：
   ```
   python set_api_key.py
   ```

3. 运行转录脚本：
   ```
   python youtube_transcription.py
   ```

4. 转录结果将保存为与视频同名的Markdown文件，存放在output目录中

## 项目特点

- 自动搜索相关YouTube视频
- 支持多关键字搜索，要求同时满足所有关键字
- 提供两种搜索方式（基础和高级）
- 避免重复添加已有视频链接
- 通过配置文件控制搜索参数
- 交互式管理关键字和视频数量
- 使用yt-dlp高效下载音频
- 使用AssemblyAI进行高质量转录 
- 使用DeepSeek添加正确的中文标点符号
- 所有转录结果统一保存在output目录，便于管理
- 资源友好型设计，适合本地环境
- 完全自动化流程
- 支持一键执行整个工作流 