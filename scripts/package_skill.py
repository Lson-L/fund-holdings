#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包脚本
"""

import os
import zipfile
import sys

def package_skill(skill_dir, output_dir="."):
    """打包技能为 .skill 文件"""
    skill_name = os.path.basename(skill_dir)
    skill_file = os.path.join(output_dir, f"{skill_name}.skill")

    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算在zip中的相对路径
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"技能已打包到: {skill_file}")
    return skill_file

if __name__ == "__main__":
    skill_dir = "fund-holdings-skill"
    output_dir = "."

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    package_skill(skill_dir, output_dir)