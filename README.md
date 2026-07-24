# 工时提醒助手

每日18:00自动统计工时并发送企业微信提醒。

## 功能

- 读取月计划文件
- 统计需求/运维工时
- 需求12h按10h换算
- 计算今日达成率
- 通过企业微信webhook发送提醒

## 目录结构

```
work-hour-reminder/
├── .github/workflows/
│   └── daily-reminder.yml    # GitHub Actions配置
├── scripts/
│   ├── reminder.py           # 提醒脚本
│   └── sync.sh               # 本地同步脚本
├── data/
│   └── YYYY-MM.md            # 月计划数据
└── README.md
```

## 使用步骤

### 1. 创建GitHub仓库

在GitHub上创建仓库 `work-hour-reminder`，然后：

```bash
cd /Users/zhuzhonghua/work-hour-reminder
git init
git remote add origin https://github.com/你的用户名/work-hour-reminder.git
```

### 2. 设置Secrets

在GitHub仓库 Settings -> Secrets and variables -> Actions 中添加：

- `WEBHOOK_URL`: 企业微信webhook地址

### 3. 首次同步

```bash
# 复制当前月计划到仓库
cp /Users/zhuzhonghua/work/work/tasks/monthly/2026-07.md /Users/zhuzhonghua/work-hour-reminder/data/

# 提交并推送
cd /Users/zhuzhonghua/work-hour-reminder
git add .
git commit -m "init: 初始化项目"
git push -u origin main
```

### 4. 日常使用

每次更新月计划后，运行同步脚本：

```bash
bash /Users/zhuzhonghua/work-hour-reminder/scripts/sync.sh
```

或者手动复制并推送：

```bash
cp /Users/zhuzhonghua/work/work/tasks/monthly/2026-07.md /Users/zhuzhonghua/work-hour-reminder/data/
cd /Users/zhuzhonghua/work-hour-reminder
git add .
git commit -m "update: 同步月计划"
git push
```

### 5. 手动触发提醒

在GitHub仓库 Actions 页面，点击 "Daily Work Hour Reminder" -> "Run workflow"。

## 本地测试

```bash
python3 /Users/zhuzhonghua/work-hour-reminder/scripts/reminder.py
```

## 消息示例

```
# 📊 今日工时统计

**月份**：2026-07
**统计日期**：2026-07-24

## 📈 工时汇总

| 类型 | 任务数 | 实际工时 | 换算工时 |
|------|--------|----------|----------|
| 需求 | 8个 | 128h | 106.67h |
| 运维 | 6个 | 24h | 24h |
| **合计** | **14个** | **152h** | **130.67h** |

## 🎯 今日达成情况

**今日工作日**：第18天（共23天）
**今日标准工时**：144h
**今日已完成**：130.67h
**今日达成率**：90.7%

## 📅 本月目标

**本月标准工时**：184h
**本月已完成**：130.67h
**本月达成率**：71.0%
**距月底目标**：53.33h

> ✅ 今日进度正常，今日截止应完成 144h，实际完成 130.67h
> 今日还差 13.33h 未完成
```
