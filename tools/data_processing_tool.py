import pandas as pd
import ast

def preprocess_transactions(transactions):
    """
    清理已讀好的交易列表：
    - 確保每筆交易是 list[str]
    - 過濾掉空交易或非字串元素
    """
    cleaned_records = []
    for tx in transactions:
        if isinstance(tx, list) and all(isinstance(t, str) for t in tx) and len(tx) > 0:
            cleaned_records.append(tx)
    return cleaned_records