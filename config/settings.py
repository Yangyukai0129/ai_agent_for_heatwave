from openai import OpenAI

OPENROUTER_API_KEY = "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"
MODEL = "mistralai/voxtral-small-24b-2507"

DATA_DIR = "./data/post"
RULE_PATH = "./rule/rag_rules_transaction.yaml"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)