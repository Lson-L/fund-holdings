#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金持仓查询脚本 - 支持自定义条数
从天天基金网获取基金最新重仓股信息
"""

import requests
import re
import json
from typing import Dict, List, Optional

def get_stock_price_change(stock_code: str) -> Optional[str]:
    """
    获取股票当前涨跌幅度
    使用腾讯股票API获取实时价格信息

    Args:
        stock_code: 股票代码（6位数字）

    Returns:
        str: 涨跌幅度，如 "+2.35%" 或 "-1.23%"，如果获取失败返回 "--"
    """
    try:
        # 确定股票市场前缀
        if stock_code.startswith('6'):
            market_prefix = 'sh'
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            market_prefix = 'sz'
        else:
            return "--"

        symbol = f"s_{market_prefix}{stock_code}"
        url = f"http://qt.gtimg.cn/q={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "--"

        # 解析返回的数据
        # 格式: v_s_sh603259="1~药明康德~603259~93.20~-2.00~-2.10~362993~342464~~2780.86~GP-A~";
        data = response.text
        match = re.search(r'"([^"]+)"', data)
        if not match:
            return "--"

        values = match.group(1).split('~')
        if len(values) < 6:
            return "--"

        # 第5个值是涨跌幅度（百分比）
        change_percent_str = values[5]
        try:
            change_percent = float(change_percent_str)
            if change_percent >= 0:
                return f"+{change_percent:.2f}%"
            else:
                return f"{change_percent:.2f}%"
        except ValueError:
            return "--"

    except Exception as e:
        return "--"

def calculate_fund_estimate(holdings: List[Dict]) -> str:
    """
    基于持仓股票的涨跌幅计算基金估值预测

    Args:
        holdings: 持仓列表，包含股票代码、名称、持仓比例、涨跌幅度

    Returns:
        str: 基金估值预测涨跌幅
    """
    total_weight = 0.0
    weighted_change = 0.0

    for holding in holdings:
        proportion = holding['proportion']
        change_str = holding['change_percent']

        # 跳过无法获取涨跌数据的股票
        if change_str == "--":
            continue

        try:
            # 移除%符号并转换为浮点数
            change_value = float(change_str.replace('+', '').replace('%', ''))
            total_weight += proportion
            weighted_change += proportion * change_value
        except (ValueError, TypeError):
            continue

    if total_weight == 0:
        return "无法预测（无有效涨跌数据）"

    # 计算加权平均涨跌幅
    estimated_change = weighted_change / total_weight

    if estimated_change >= 0:
        return f"+{estimated_change:.2f}%"
    else:
        return f"{estimated_change:.2f}%"

def get_fund_holdings(fund_code: str, top_n: int = 20) -> Optional[Dict]:
    """
    获取基金最新持仓数据
    返回格式: {
        'fund_info': {'name': str, 'code': str},
        'report_date': str,  # 报告期
        'holdings': [
            {'stock_code': str, 'stock_name': str, 'proportion': float, 'change_percent': str}
        ]
    }

    Args:
        fund_code: 基金代码（6位数字）
        top_n: 查询前N条重仓股，默认为20
    """
    try:
        # 天天基金网最多支持查询前20条，所以限制最大值为20
        top_n = min(top_n, 20)
        url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={fund_code}&topline={top_n}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        text = response.text

        # 提取基金名称
        fund_name_match = re.search(r"title='([^']+)'[^>]*href='http://fund\.eastmoney\.com/\d+\.html'", text)
        fund_name = fund_name_match.group(1) if fund_name_match else "未知基金"

        # 提取报告期
        date_match = re.search(r"截止至：<font[^>]*>(\d{4}-\d{2}-\d{2})</font>", text)
        report_date = date_match.group(1) if date_match else "未知"

        # 提取重仓股
        holdings = []
        pattern = r'<td><a[^>]*>(\d+)</a></td>\s*<td[^>]*><a[^>]*>([^<]+)</a></td>.*?<td[^>]*class=\'tor\'>([\d.]+)%</td>.*?<td[^>]*class=\'tor\'>([\d,]+(?:\.\d+)?)</td>'

        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches[:top_n]:
            stock_code, stock_name, proportion, market_value = match
            # 获取涨跌幅度
            change_percent = get_stock_price_change(stock_code)
            holdings.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'proportion': float(proportion),
                'change_percent': change_percent
            })

        if not holdings:
            return None

        return {
            'fund_info': {'name': fund_name, 'code': fund_code},
            'report_date': report_date,
            'holdings': holdings
        }

    except Exception as e:
        return None

def format_holdings_output(result: Dict) -> str:
    """格式化输出结果"""
    if not result:
        return "未找到基金持仓数据。请检查基金代码是否正确，或该基金可能暂无持仓数据（如货币基金）。"

    # 计算基金估值预测
    estimated_change = calculate_fund_estimate(result['holdings'])

    output = f"基金名称: {result['fund_info']['name']} ({result['fund_info']['code']})\n"
    output += f"报告期: {result['report_date']}\n"
    output += f"基金估值预测涨跌幅: {estimated_change}\n"
    output += "=" * 70 + "\n"
    output += f"{'排名':<4} {'股票代码':<10} {'股票名称':<12} {'持仓比例(%)':<12} {'涨跌幅度':<10}\n"
    output += "-" * 70 + "\n"

    for i, holding in enumerate(result['holdings'], 1):
        output += f"{i:<4} {holding['stock_code']:<10} {holding['stock_name']:<12} {holding['proportion']:<12.2f} {holding['change_percent']:<10}\n"

    output += f"\n注: 数据来源于天天基金网，显示最新公布的前{len(result['holdings'])}大重仓股。涨跌幅度为当前实时数据。\n"
    output += "基金估值预测基于重仓股的加权平均涨跌幅计算，仅供参考，实际净值以基金公司公布为准。\n"
    return output