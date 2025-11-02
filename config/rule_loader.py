import yaml

# def load_rules(rule_path):
#     with open(rule_path, "r", encoding="utf-8") as f:
#         rules_yaml = yaml.safe_load(f)
#     system_prompt_template = rules_yaml.get("system_prompt_template", "{context}\n{rules}")
#     retrieval_docs = rules_yaml.get("retrieval_docs", [])
#     rules_text = "\n".join([
#     f"- {doc['name']}（{doc.get('type', 'unknown')}）: {doc.get('description', '')}"
#     for doc in retrieval_docs
#     ])
#     return system_prompt_template, rules_text

# def load_rules(rule_path):
#     with open(rule_path, "r", encoding="utf-8") as f:
#         rules_yaml = yaml.safe_load(f)

#     system_prompt_template = rules_yaml.get("system_prompt_template", "{context}\n{rules}")
#     retrieval_docs = rules_yaml.get("retrieval_docs", [])

#     rules_text = "\n".join([
#         f"- {doc['name']}（{doc.get('type', 'unknown')}）: {doc.get('description', '')}"
#         for doc in retrieval_docs
#     ])

#     return system_prompt_template, rules_text, retrieval_docs  # ✅ 多回傳 retrieval_docs

def load_rules(rule_path):
    with open(rule_path, "r", encoding="utf-8") as f:
        rules_yaml = yaml.safe_load(f)
    system_prompt_template = rules_yaml.get("system_prompt_template", "{context}\n{rules}")
    retrieval_docs = rules_yaml.get("retrieval_docs", [])
    output_format = rules_yaml.get("output_format", "")
    rules_text = "\n".join([f"- {doc['name']}（{doc.get('type', 'unknown')}）: {doc.get('description','')}" for doc in retrieval_docs])
    return system_prompt_template, rules_text, retrieval_docs, output_format