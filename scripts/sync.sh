#!/bin/bash

REPO_DIR="/Users/zhuzhonghua/work-hour-reminder"
TASK_DIR="/Users/zhuzhonghua/work/work/tasks/monthly"
MONTH=$(date +%Y-%m)
SOURCE_FILE="$TASK_DIR/$MONTH.md"
TARGET_FILE="$REPO_DIR/data/$MONTH.md"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "源文件不存在: $SOURCE_FILE"
    exit 1
fi

cp "$SOURCE_FILE" "$TARGET_FILE"

cd "$REPO_DIR" || exit 1

git add "data/$MONTH.md"

if git diff --cached --quiet; then
    echo "文件无变化，跳过提交"
    exit 0
fi

git commit -m "update: 同步 $MONTH 月计划数据"
git push origin main

echo "同步完成: $MONTH"
