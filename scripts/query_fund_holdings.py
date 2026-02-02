#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金持仓查询脚本 - 支持自定义条数
从天天基金网获取基金最新重仓股信息
"""

import requests
import re
from typing import Dict, List, Optional

def get_fund_holdings(fund_code: str, top_n: int = 20) -> Optional[Dict]:
    """
    获取基金最新持仓数据
    返回格式: {
        'fund_info': {'name': str, 'code': str},
        'report_date': str,  # 报告期
        'holdings': [
            {'stock_code': str, 'stock_name': str, 'proportion': float, 'market_value': str}
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
            holdings.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'proportion': float(proportion),
                'market_value': market_value + "万元"
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

    output = f"基金名称: {result['fund_info']['name']} ({result['fund_info']['code']})\n"
    output += f"报告期: {result['report_date']}\n"
    output += "=" * 60 + "\n"
    output += f"{'排名':<4} {'股票代码':<10} {'股票名称':<12} {'持仓比例(%)':<12} {'持仓市值':<10}\n"
    output += "-" * 60 + "\n"

    for i, holding in enumerate(result['holdings'], 1):
        output += f"{i:<4} {holding['stock_code']:<10} {holding['stock_name']:<12} {holding['proportion']:<12.2f} {holding['market_value']:<10}\n"

    output += f"\n注: 数据来源于天天基金网，显示最新公布的前{len(result['holdings'])}大重仓股。\n"
    return output