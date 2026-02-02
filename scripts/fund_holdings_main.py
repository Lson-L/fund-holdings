#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金持仓查询主入口脚本
支持自定义查询条数
"""

import sys
import os
import re
sys.path.append(os.path.dirname(__file__))

from query_fund_holdings import get_fund_holdings, format_holdings_output

def extract_fund_code_and_top_n(user_input: str) -> tuple:
    """从用户输入中提取基金代码和top_n参数"""
    # 查找6位数字（基金代码）
    code_match = re.search(r'\d{6}', user_input)
    fund_code = code_match.group() if code_match else None

    # 查找top_n参数，支持"前X条"、"top X"、"前X大"等格式
    top_n = 20  # 默认值

    # 匹配中文格式：前(\d+)条、前(\d+)大、前(\d+)个
    chinese_match = re.search(r'前(\d+)[条大个]', user_input)
    if chinese_match:
        top_n = int(chinese_match.group(1))

    # 匹配英文格式：top\s+(\d+)
    english_match = re.search(r'top\s+(\d+)', user_input, re.IGNORECASE)
    if english_match:
        top_n = int(english_match.group(1))

    # 限制最大值为20（天天基金网限制）
    top_n = min(top_n, 20)
    top_n = max(top_n, 1)  # 至少1条

    return fund_code, top_n

def query_fund_holdings_main(user_query: str) -> str:
    """
    主查询函数

    Args:
        user_query: 用户的查询字符串

    Returns:
        str: 格式化的查询结果
    """
    fund_code, top_n = extract_fund_code_and_top_n(user_query)

    if fund_code:
        result = get_fund_holdings(fund_code, top_n)
        return format_holdings_output(result)
    else:
        return "请提供基金代码（6位数字）以查询持仓信息。例如：'查询基金005827的最新持仓' 或 '查询基金005827前10条重仓股'"

def main():
    """命令行测试"""
    if len(sys.argv) < 2:
        print("用法: python fund_holdings_main.py '<查询语句>'")
        print("示例: ")
        print("  python fund_holdings_main.py '查询基金005827的最新持仓'")
        print("  python fund_holdings_main.py '查询基金005827前10条重仓股'")
        print("  python fund_holdings_main.py '查询基金005827 top 15'")
        return

    user_query = ' '.join(sys.argv[1:])
    result = query_fund_holdings_main(user_query)
    print(result)

if __name__ == "__main__":
    main()