#!/usr/bin/env python3
import re
import json
import os
import requests
from datetime import datetime, date
from calendar import monthcalendar

WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=18e67358-71b5-4526-a9cf-8b00d2c3ee42')


def get_workdays(year, month):
    cal = monthcalendar(year, month)
    workdays = 0
    for week in cal:
        for i in range(5):
            if week[i] != 0:
                workdays += 1
    return workdays


def get_passed_workdays(year, month, today=None):
    if today is None:
        today = date.today()
    
    cal = monthcalendar(year, month)
    workdays = 0
    
    for week in cal:
        for i in range(5):
            if week[i] != 0:
                day = date(year, month, week[i])
                if day <= today:
                    workdays += 1
    return workdays


def parse_tasks(file_path):
    demand_hours = 0
    ops_hours = 0
    demand_count = 0
    ops_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None, None, None, None
    
    pattern = r'- \[x\] \[.+?\] \[(.+?)\] .+? \|.+\| 实际: (\d+)h'
    
    for match in re.finditer(pattern, content):
        task_type = match.group(1)
        hours = int(match.group(2))
        
        if task_type == '需求':
            demand_hours += hours
            demand_count += 1
        elif task_type == '运维':
            ops_hours += hours
            ops_count += 1
    
    return demand_count, demand_hours, ops_count, ops_hours


def calculate_stats(demand_hours, ops_hours):
    demand_converted = demand_hours * 10 / 12
    total_converted = demand_converted + ops_hours
    
    return demand_converted, total_converted


def build_message(year, month, demand_count, demand_hours, demand_converted,
                  ops_count, ops_hours, total_converted, workdays, passed_workdays):
    today = date.today()
    standard_hours = workdays * 8
    passed_standard = passed_workdays * 8
    achievement_rate = (total_converted / standard_hours * 100) if standard_hours > 0 else 0
    current_rate = (total_converted / passed_standard * 100) if passed_standard > 0 else 0
    remaining = standard_hours - total_converted
    today_remaining = passed_standard - total_converted
    
    if current_rate >= 100:
        status = "🎉 今日已超额完成"
    elif current_rate >= 80:
        status = "✅ 今日进度正常"
    elif current_rate >= 60:
        status = "⚠️ 今日进度稍慢"
    else:
        status = "🚨 今日进度滞后"
    
    content = f"""# 📊 今日工时统计

**月份**：{year}-{month:02d}
**统计日期**：{today.strftime('%Y-%m-%d')}

## 📈 工时汇总

| 类型 | 任务数 | 实际工时 | 换算工时 |
|------|--------|----------|----------|
| 需求 | {demand_count}个 | {demand_hours}h | {demand_converted:.2f}h |
| 运维 | {ops_count}个 | {ops_hours}h | {ops_hours}h |
| **合计** | **{demand_count + ops_count}个** | **{demand_hours + ops_hours}h** | **{total_converted:.2f}h** |

## 🎯 今日达成情况

**今日工作日**：第{passed_workdays}天（共{workdays}天）
**今日标准工时**：{passed_standard}h
**今日已完成**：{total_converted:.2f}h
**今日达成率**：{current_rate:.1f}%

## 📅 本月目标

**本月标准工时**：{standard_hours}h
**本月已完成**：{total_converted:.2f}h
**本月达成率**：{achievement_rate:.1f}%
**距月底目标**：{remaining:.2f}h

> {status}，今日截止应完成 {passed_standard}h，实际完成 {total_converted:.2f}h"""
    
    if today_remaining > 0:
        content += f"\n> 今日还差 {today_remaining:.2f}h 未完成"
    else:
        content += f"\n> 今日超额完成 {-today_remaining:.2f}h"
    
    return content


def send_webhook(content):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    response = requests.post(WEBHOOK_URL, json=data, timeout=10)
    return response.json()


def main():
    today = date.today()
    year = today.year
    month = today.month
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    file_path = os.path.join(repo_dir, 'data', f'{year}-{month:02d}.md')
    
    result = parse_tasks(file_path)
    
    if result[0] is None:
        print(f"文件不存在: {file_path}")
        return
    
    demand_count, demand_hours, ops_count, ops_hours = result
    
    demand_converted, total_converted = calculate_stats(demand_hours, ops_hours)
    
    workdays = get_workdays(year, month)
    passed_workdays = get_passed_workdays(year, month, today)
    
    content = build_message(year, month, demand_count, demand_hours, demand_converted,
                           ops_count, ops_hours, total_converted, workdays, passed_workdays)
    
    print("发送消息：")
    print(content)
    print("\n" + "="*50 + "\n")
    
    result = send_webhook(content)
    print("发送结果：", json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
