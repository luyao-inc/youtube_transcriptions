#!/bin/bash

# 创建一个新的纯净分支
git checkout --orphan temp_branch

# 添加所有文件
git add -A

# 提交更改
git commit -m "初始化提交：YouTube视频转录工具"

# 删除旧的分支
git branch -D main

# 将当前分支重命名为main
git branch -m main

# 强制推送到GitHub，使用环境变量中的令牌
if [ -z "$GH_TOKEN" ]; then
  echo "错误: 未设置GH_TOKEN环境变量"
  echo "请使用以下命令设置GH_TOKEN:"
  echo "export GH_TOKEN=your_github_token"
  exit 1
fi

git remote set-url origin "https://$GH_TOKEN@github.com/luyao-inc/youtube_transcriptions.git"
git push -f origin main

echo "代码已成功推送到GitHub: https://github.com/luyao-inc/youtube_transcriptions" 