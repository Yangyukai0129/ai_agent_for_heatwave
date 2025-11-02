# from mlxtend.frequent_patterns import fpgrowth, association_rules
# import pandas as pd
# from mlxtend.preprocessing import TransactionEncoder

# def fp_growth_tool(transactions, min_support=0.06, min_confidence=0.5):
#     print(f"🚀 FP-Growth 收到 {len(transactions)} 筆交易")

#     # -----------------------------
#     # 1️⃣ One-hot 編碼
#     # -----------------------------
#     te = TransactionEncoder()
#     te_ary = te.fit(transactions).transform(transactions)
#     df_te = pd.DataFrame(te_ary, columns=te.columns_)

#     print(f"✅ One-hot 完成，欄位數: {len(df_te.columns)}")

#     # -----------------------------
#     # 2️⃣ FP-Growth 頻繁項目集
#     # -----------------------------
#     freq_itemsets = fpgrowth(df_te, min_support=min_support, use_colnames=True)
#     print(f"✅ 找到 {len(freq_itemsets)} 個頻繁項目集")

#     if freq_itemsets.empty:
#         print("⚠️ 無頻繁項目集，返回空結果")
#         return []

#     # -----------------------------
#     # 3️⃣ 生成關聯規則
#     # -----------------------------
#     rules_df = association_rules(freq_itemsets, metric="confidence", min_threshold=min_confidence)
#     print(f"✅ 產生 {len(rules_df)} 條關聯規則")

#     if rules_df.empty:
#         return []

#     rules = []
#     for _, row in rules_df.iterrows():
#         ante = list(row['antecedents'])
#         conse = list(row['consequents'])
#         rules.append({
#             "ante": ante if len(ante) > 1 else ante[0],
#             "conse": conse if len(conse) > 1 else conse[0],
#             "support": round(row['support'], 3),
#             "confidence": round(row['confidence'], 3),
#             "lift": round(row['lift'], 3)
#         })

#     print(f"📦 最終輸出 {len(rules)} 條規則")
#     return rules

from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
import math

def latlon_to_tuple(latlon_str):
    """把 'lat_lon' 字串轉成 float tuple"""
    lat, lon = map(float, latlon_str.split("_"))
    return lat, lon

def calc_distance_km(ante_str, conse_str):
    """計算 L2 距離並換算成公里"""
    lat1, lon1 = latlon_to_tuple(ante_str)
    lat2, lon2 = latlon_to_tuple(conse_str)
    distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 100
    return distance

def fp_growth_tool(transactions, min_support=0.06, min_confidence=0.5):
    print(f"🚀 FP-Growth 收到 {len(transactions)} 筆交易")

    # -----------------------------
    # 1️⃣ One-hot 編碼
    # -----------------------------
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_te = pd.DataFrame(te_ary, columns=te.columns_)

    print(f"✅ One-hot 完成，欄位數: {len(df_te.columns)}")

    # -----------------------------
    # 2️⃣ FP-Growth 頻繁項目集
    # -----------------------------
    freq_itemsets = fpgrowth(df_te, min_support=min_support, use_colnames=True)
    print(f"✅ 找到 {len(freq_itemsets)} 個頻繁項目集")

    if freq_itemsets.empty:
        print("⚠️ 無頻繁項目集，返回空結果")
        return []

    # -----------------------------
    # 3️⃣ 生成關聯規則
    # -----------------------------
    rules_df = association_rules(freq_itemsets, metric="confidence", min_threshold=min_confidence)
    print(f"✅ 產生 {len(rules_df)} 條關聯規則")

    if rules_df.empty:
        return []

    # -----------------------------
    # 4️⃣ 整理規則並計算距離
    # -----------------------------
    rules = []
    for _, row in rules_df.iterrows():
        ante = list(row['antecedents'])
        conse = list(row['consequents'])
        
        # 只處理單一節點的情況，若多個節點可以取第一個或平均經緯度
        ante_str = ante[0] if len(ante) == 1 else ante[0]
        conse_str = conse[0] if len(conse) == 1 else conse[0]

        distance_km = calc_distance_km(ante_str, conse_str)
        distance_class = "近距離" if distance_km <= 2500 else "遠距離"

        rules.append({
            "ante": ante if len(ante) > 1 else ante[0],
            "conse": conse if len(conse) > 1 else conse[0],
            "support": round(row['support'], 3),
            "confidence": round(row['confidence'], 3),
            "lift": round(row['lift'], 3),
            "distance_km": round(distance_km, 1),
            "distance_class": distance_class
        })

        # 5️⃣ 統計摘要
    def summarize(rules_list):
        if not rules_list:
            return {"count":0, "support_mean":None, "confidence_mean":None, "lift_mean":None}
        return {
            "count": len(rules_list),
            "support_mean": round(sum(r["support"] for r in rules_list)/len(rules_list),4),
            "confidence_mean": round(sum(r["confidence"] for r in rules_list)/len(rules_list),4),
            "lift_mean": round(sum(r["lift"] for r in rules_list)/len(rules_list),4)
        }

    near_rules = [r for r in rules if r["distance_class"]=="近距離"]
    far_rules = [r for r in rules if r["distance_class"]=="遠距離"]

    summary = {
        "total_rules": len(rules),
        "near_rules_summary": summarize(near_rules),
        "far_rules_summary": summarize(far_rules),
        "top_rules_sample": sorted(rules, key=lambda x: x.get("confidence",0), reverse=True)[:20]
    }

    print(f"📦 最終輸出 summary，規則總數 {len(rules)}")
    print('近距離',summarize(near_rules))
    print('遠距離',summarize(far_rules))
    return summary
