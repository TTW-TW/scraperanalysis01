import os
import json
import glob # 推薦使用 glob 模組
import re

input_folder = r"json_test/PTT" 
output_folder = r"json_test/PTT/CKIP"
os.makedirs(output_folder, exist_ok=True)

json_files = glob.glob(os.path.join(input_folder, '*.json')) # 所有待分析的原始文本

for file_path in json_files:
    parts = re.split(r'[/]+', file_path.replace( '\\', '/'))
    print(parts[-1])