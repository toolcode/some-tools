import pandas as pd
from json import loads, dumps

excel地址 = ""
json文件夹地址 =""

# 读取Excel文件
excel_file = excel地址
xls = pd.ExcelFile(excel_file)
print(xls.sheet_names)
# 遍历每个sheet并转换为JSON
for sheet_name in xls.sheet_names:
    # 读取sheet为DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    # 将DataFrame转换为JSON
    json_data = df.to_json(orient="index")
    parsed = loads(json_data)
    format_data = dumps(parsed, indent=4, ensure_ascii=False)
    # 写入JSON文件
    json_file = f"{json文件夹地址}/{sheet_name}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        f.write(format_data)
    print(f'JSON file "{json_file}" created successfully.')