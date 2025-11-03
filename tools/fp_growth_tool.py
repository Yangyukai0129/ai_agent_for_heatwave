from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
import math
import numpy as np

def latlon_to_tuple(latlon_str):
    """把 'lat_lon' 字串轉成 float tuple"""
    lat, lon = map(float, latlon_str.split("_"))
    return lat, lon

def calc_distance_km(ante_str, conse_str):
    """計算球面距離 (haversine)"""
    lat1, lon1 = latlon_to_tuple(ante_str)
    lat2, lon2 = latlon_to_tuple(conse_str)
    R = 6371.0  # 地球半徑 km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = np.sin(dphi/2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2.0)**2
    distance = R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))
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
        
        # 計算所有組合的距離
        distances = [calc_distance_km(a, c) for a in ante for c in conse]
        distance_min = min(distances)
        distance_max = max(distances)
        distance_mean = sum(distances) / len(distances)
        
        # 分桶：只要最遠距離 > 2500 km 就算遠距離
        distance_class = "遠距離" if distance_max > 2500 else "近距離"
        
        rules.append({
            "ante": ante if len(ante) > 1 else ante[0],
            "conse": conse if len(conse) > 1 else conse[0],
            "support": round(row['support'], 3),
            "confidence": round(row['confidence'], 3),
            "lift": round(row['lift'], 3),
            "distance_min": round(distance_min, 1),
            "distance_max": round(distance_max, 1),
            "distance_mean": round(distance_mean, 1),
            "distance_class": distance_class
        })

        # 5️⃣ 統計摘要
    def summarize(rules_list):
        if not rules_list:
             return {"count":0, "support_mean":None, "confidence_mean":None, "lift_mean":None,
                      "distance_min":None, "distance_max":None, "distance_mean":None}
        return {
            "count": len(rules_list),
            "support_mean": round(sum(r["support"] for r in rules_list)/len(rules_list),4),
            "confidence_mean": round(sum(r["confidence"] for r in rules_list)/len(rules_list),4),
            "lift_mean": round(sum(r["lift"] for r in rules_list)/len(rules_list),4),
            "distance_min": round(min(r["distance_min"] for r in rules_list),1),
            "distance_max": round(max(r["distance_max"] for r in rules_list),1),
            "distance_mean": round(sum(r["distance_mean"] for r in rules_list)/len(rules_list),1) 
            }

    near_rules = [r for r in rules if r["distance_class"]=="近距離"]
    far_rules = [r for r in rules if r["distance_class"]=="遠距離"]

    all_distances = [r["distance_mean"] for r in rules]
    distance_distribution = {
         "percent_near": round(len(near_rules)/len(rules)*100,1) if rules else 0,
         "percent_far": round(len(far_rules)/len(rules)*100,1) if rules else 0,
         "mean_distance": round(np.mean(all_distances),1) if all_distances else None, 
         "median_distance": round(np.median(all_distances),1) if all_distances else None, 
         "q25_distance": round(np.percentile(all_distances,25),1) if all_distances else None, 
         "q75_distance": round(np.percentile(all_distances,75),1) if all_distances else None 
         }

    summary = {
        "total_rules": len(rules),
        "near_rules_summary": summarize(near_rules),
        "far_rules_summary": summarize(far_rules),
        "distance_distribution": distance_distribution,
        "top_rules_sample": sorted(rules, key=lambda x: x.get("confidence",0), reverse=True)[:20]
    }

    print(f"📦 最終輸出 summary，規則總數 {len(rules)}")
    print('近距離',summarize(near_rules))
    print('遠距離',summarize(far_rules))
    return summary
