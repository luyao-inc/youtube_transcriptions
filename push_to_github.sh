#!/bin/bash

# 设置GitHub用户名和仓库名
GH_USERNAME="luyao-inc"
GH_REPO="youtube_transcriptions"

# 显示使用说明
echo "GitHub推送脚本"
echo "================="
echo "使用方法："
echo "  1. 请先设置GH_TOKEN环境变量："
echo "     export GH_TOKEN=your_github_token"
echo "  2. 然后运行此脚本"
echo ""

# 检查环境变量
if [ -z "$GH_TOKEN" ]; then
  echo "错误: 未设置GH_TOKEN环境变量"
  echo "请使用以下命令设置GH_TOKEN:"
  echo "export GH_TOKEN=your_github_token"
  exit 1
fi

# 设置Git远程URL
git remote add origin https://github.com/${GH_USERNAME}/${GH_REPO}.git 2>/dev/null || git remote set-url origin https://github.com/${GH_USERNAME}/${GH_REPO}.git

# 向GitHub推送代码时使用API令牌
git -c http.extraheader="AUTHORIZATION: bearer ${GH_TOKEN}" push -u origin main

echo "代码已推送到GitHub: https://github.com/${GH_USERNAME}/${GH_REPO}" 