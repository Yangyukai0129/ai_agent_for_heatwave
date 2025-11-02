import os
import pandas as pd
import ast

# def load_transactions(data_dir):
#     all_records = []
#     for file_name in os.listdir(data_dir):
#         if not file_name.endswith(".csv"):
#             continue
#         path = os.path.join(data_dir, file_name)
#         df = pd.read_csv(path, header=0)  # header=0 第一行是 'transaction'
#         for _, row in df.iterrows():
#             transaction_str = row['transaction']
#             if not transaction_str or transaction_str.strip() == '':
#                 continue
#             try:
#                 # 解析成 list of string
#                 transaction_list = ast.literal_eval(transaction_str)
#                 all_records.append(transaction_list)
#             except Exception as e:
#                 print("解析失敗:", transaction_str, e)
#                 continue
#     print(f"總交易筆數: {len(all_records)}")
#     print(all_records[:10])
#     return all_records

def load_transactions(data_dir):
    file_transactions = {}
    for file_name in os.listdir(data_dir):
        if not file_name.endswith(".csv"):
            continue
        path = os.path.join(data_dir, file_name)
        df = pd.read_csv(path)
        transactions = []
        for t_str in df['transaction'].dropna():
            try:
                transactions.append(ast.literal_eval(t_str))
            except Exception as e:
                print("解析失敗:", t_str, e)
                continue
        file_transactions[file_name] = transactions
    return file_transactions