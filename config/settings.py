from openai import OpenAI

OPENROUTER_API_KEY = "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"
MODEL = "mistralai/voxtral-small-24b-2507"

DATA_DIR = "./data/post"
RULE_PATH = "./rule/rag_rules_transaction.yaml"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)