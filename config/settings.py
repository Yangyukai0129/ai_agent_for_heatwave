from openai import OpenAI

OPENROUTER_API_KEY = "xxx"
MODEL = "mistralai/voxtral-small-24b-2507"

DATA_DIR = "./data/post"
RULE_PATH = "./rule/rag_rules_transaction.yaml"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)