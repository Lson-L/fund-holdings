#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金代码解析工具
从用户输入中提取基金代码或名称
"""

import re

def extract_fund_code_or_name(user_input: str) -> Dict[str, str]:
    """
    从用户输入中提取基金代码或名称

    Args:
        user_input: 用户的查询字符串

    Returns:
        dict: 包含 'code' 或 'name' 键的字典
    """
    # 去除空格和特殊字符
    cleaned_input = re.sub(r'[^\w\u4e00-\u9fff]', '', user_input)

    # 检查是否包含6位数字（基金代码）
    code_match = re.search(r'\d{6}', user_input)
    if code_match:
        return {'code': code_match.group()}

    # 检查常见的基金查询关键词
    query_patterns = [
        r'(.+?)基金',
        r'(.+?)的持仓',
        r'(.+?)重仓股',
        r'(.+?)前十大'
    ]

    for pattern in query_patterns:
        match = re.search(pattern, user_input)
        if match:
            name = match.group(1).strip()
            if name and len(name) > 1:
                return {'name': name}

    # 如果没有明确的代码或名称，返回原始输入作为名称
    return {'name': cleaned_input}

def search_fund_by_name(fund_name: str) -> Optional[str]:
    """
    根据基金名称搜索基金代码（简化版本）
    实际使用时可能需要调用天天基金网的搜索API
    """
    # 这里可以实现名称到代码的映射
    # 由于天天基金网的搜索API较为复杂，这里提供一个简化方案
    # 在实际应用中，可能需要维护一个基金名称到代码的映射表
    return None

if __name__ == "__main__":
    # 测试函数
    test_inputs = [
        "查询基金001234的最新持仓",
        "查看易方达蓝筹精选的重仓股",
        "005827的前十大持仓",
        "华夏科技创新的持仓情况"
    ]

    for test_input in test_inputs:
        result = extract_fund_code_or_name(test_input)
        print(f"输入: {test_input}")
        print(f"结果: {result}\n")