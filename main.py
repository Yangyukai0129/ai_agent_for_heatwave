from config.settings import DATA_DIR, RULE_PATH
from utils.data_loader import load_transactions
from config.rule_loader import load_rules
from agent.agent_core import run_agent

# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
# ==========================
# 1️⃣ 載入規則
# ==========================
system_prompt_template, rules_text, retrieval_docs, output_format = load_rules(RULE_PATH)

# ==========================
# 2️⃣ 將 retrieval_docs 轉成文字
# ==========================
retrieval_text = ""
for doc in retrieval_docs:
    retrieval_text += f"- {doc['name']} ({doc.get('type','unknown')}): {doc.get('description','')}\n"

# ==========================
# 3️⃣ 使用者問題
# ==========================
user_question = """
請依照以下步驟：
1. 呼叫 fp_growth_tool(min_support=0.01, min_confidence=0.1) 計算 FP-Growth。
2. 回傳 FP-Growth 結果。
請務必使用 fp_growth_tool 計算 FP-Growth 規則。不要直接生成規則。計算完成後再整理成最終回答。
"""

# ==========================
# 4️⃣ 載入所有交易資料（逐檔）
# ==========================
all_transactions = load_transactions(DATA_DIR)  # 這裡會回傳 dict: {file_name: transactions}

# ==========================
# 5️⃣ 逐檔執行 FP-Growth
# ==========================
for file_name, transactions in all_transactions.items():
    context_text = f"""交易資料摘要:
- 檔案名稱: {file_name}
- 前 5 筆交易: {transactions[:5]}
- 交易總數: {len(transactions)}
"""

    system_prompt = system_prompt_template.format(
        context=context_text,
        rules=rules_text + "\n可用規則摘要:\n" + retrieval_text,
        output_format=output_format
    )

    print(f"\n===============================")
    print(f"🚀 開始處理檔案: {file_name}")
    print(f"===============================\n")

    run_agent(system_prompt, user_question, transactions)