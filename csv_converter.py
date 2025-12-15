import csv
import os
import glob

def convert_csv_column_to_row(input_dir, output_dir):
    # 出力フォルダが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)

    # フォルダ内のすべてのCSVを取得
    for file in glob.glob(os.path.join(input_dir, "*.csv")):
        filename = os.path.basename(file)
        output_file = os.path.join(output_dir, filename)

        # CSVを読み込み（1列だけを1行に変換）
        with open(file, newline='', encoding="utf-8") as f_in:
            reader = csv.reader(f_in)
            data = [row[0] for row in reader if row]  # 空行は無視

        # 出力フォルダに書き込み
        with open(output_file, "w", newline='', encoding="utf-8") as f_out:
            writer = csv.writer(f_out)
            writer.writerow(data)

        print(f"変換完了: {filename}")

# -------------------------
# 使用例
# -------------------------

input_folder = r"C:\Users\arusu\OneDrive\ドキュメント\ExperimentOfCooling\1\MSSQ"   # フォルダ1
output_folder = r"C:\Users\arusu\OneDrive\ドキュメント\ExperimentOfCooling\2\MSSQ" # フォルダ2

convert_csv_column_to_row(input_folder, output_folder)
