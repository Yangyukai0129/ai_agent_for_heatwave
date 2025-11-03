import json
from config.settings import client, MODEL
from tools.schema import TOOLS, TOOL_MAPPING

def run_agent(system_prompt, user_question, transactions):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    # 🔹 第一階段：LLM 決策階段（Agent）
    # 第一次呼叫 LLM
    response_1_raw = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS
    )

    if not response_1_raw or not hasattr(response_1_raw, "choices"):
        print("⚠️ LLM 回傳 None 或格式不正確")
        return

    assistant_msg = response_1_raw.choices[0].message
    assistant_dict = {
        "role": "assistant",
        "content": assistant_msg.content,
        "tool_calls": getattr(assistant_msg, "tool_calls", [])
    }
    messages.append(assistant_dict)
    tool_calls = assistant_dict["tool_calls"] or []

    if not tool_calls:
        print("LLM 沒有呼叫工具")
        return

    print(f"LLM 有呼叫 {len(tool_calls)} 個工具")

    # 🔹 第二階段：工具執行階段（Agent Core）
    # 執行工具
    for idx, tool_call in enumerate(tool_calls, 1):
        tool_name = tool_call.function.name
        tool_args = {}
        tool_content_summary = ""

        try:
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except Exception:
                import ast
                tool_args = ast.literal_eval(tool_call.function.arguments)

            if tool_name == "fp_growth_tool":
                tool_args["transactions"] = transactions
                tool_args["min_support"] = 0.06
                tool_args["min_confidence"] = 0.5

            tool_response = TOOL_MAPPING[tool_name](**tool_args)

            if tool_name == "fp_growth_tool" and isinstance(tool_response, dict):
                tool_content_summary = {
                    "total_rules": tool_response["total_rules"],
                    "near_summary": tool_response["near_rules_summary"],
                    "far_summary": tool_response["far_rules_summary"],
                    "distance_distribution": tool_response.get("distance_distribution"),
                    "top_rules_sample": tool_response.get("top_rules_sample")
                }
            else:
                tool_content_summary = f"工具 {tool_name} 已完成。結果簡要：{str(tool_response)[:500]}..."

        except Exception as e:
            print(f"⚠️ 執行工具 {tool_name} 發生錯誤:", e)
            tool_content_summary = f"工具 {tool_name} 執行失敗: {str(e)}"

        messages.append({
            "role": "tool",
            "tool_call_id": str(tool_call.id),
            "content": tool_content_summary
        })

    # 🔹 第三階段：LLM 回應階段（LLM）
    # 第二次呼叫 LLM
    safe_messages = []
    for m in messages:
        if not isinstance(m, dict):
            m = m.model_dump() if hasattr(m, "model_dump") else m.__dict__
        item = {"role": m.get("role","user"), "content": str(m.get("content",""))}
        if m.get("role")=="assistant" and "tool_calls" in m and m["tool_calls"]:
            item["tool_calls"] = m["tool_calls"]
        if m.get("role")=="tool" and "tool_call_id" in m:
            item["tool_call_id"] = m["tool_call_id"]
        safe_messages.append(item)

    summary_prompt = f"""
        以下是 FP-Growth 結果摘要：

        總規則數: {tool_content_summary.get("total_rules", "N/A")}

        近距離規則統計 (distance ≤ 2500 km):
        {json.dumps(tool_content_summary.get("near_summary", {}), ensure_ascii=False, indent=2)}

        遠距離規則統計 (distance > 2500 km):
        {json.dumps(tool_content_summary.get("far_summary", {}), ensure_ascii=False, indent=2)}

        距離分布統計:
        {json.dumps(tool_content_summary.get("distance_distribution", {}), ensure_ascii=False, indent=2)}

        Top {len(tool_content_summary.get("top_rules_sample", []))} 規則樣本:
        {json.dumps(tool_content_summary.get("top_rules_sample", []), ensure_ascii=False, indent=2)}

        請根據摘要生成報告，包含：

        總規則數與平均強度 (support / confidence / lift)

        近距離與遠距離規則的特性差異，並說明距離統計 (min / max / mean)

        可能代表的熱浪事件傳播特徵，並討論近距離 vs 遠距離規則的意義
        """
    response_2_raw = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是氣候資料分析助理，請根據摘要生成報告"},
            {"role": "user", "content": summary_prompt}
        ]
    )

    if not response_2_raw or not hasattr(response_2_raw, "choices"):
        print("⚠️ 第二次 LLM 回傳 None 或格式不正確")
        return

    final_answer = response_2_raw.choices[0].message.content
    print("\n=== LLM 最終回答 ===\n")
    print(final_answer)
