from tools.fp_growth_tool import fp_growth_tool

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fp_growth_tool",
            "description": "計算交易資料的 FP-Growth 關聯規則。交易資料會自動從 Agent 上下文提供，不需要在參數中指定。", # 更新描述
            "parameters": {
                "type": "object",
                "properties": {
                    # 移除 transactions，因為 agent_core 會自動注入
                    "min_support": {"type": "number", "description": "最小支持度，預設為 0.06"},
                    "min_confidence": {"type": "number", "description": "最小置信度，預設為 0.5"}
                },
                "required": [] # 現在沒有 LLM 必須提供的參數，transactions 會自動補上
            }
        }
    },
]

TOOL_MAPPING = {
    "fp_growth_tool": fp_growth_tool,
}