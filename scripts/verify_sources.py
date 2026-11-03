from datasets import load_dataset

d = load_dataset("rungalileo/ragbench", "delucionqa")
print(d)
print(d["train"].column_names)   # expect question, documents, response, adherence_score, completeness_score
print(d["train"][0]["adherence_score"], len(d["train"][0]["documents"]))

h = load_dataset("rungalileo/ragbench", "hotpotqa", split="test[:5]")
print(h.column_names, h[0]["question"])

i = load_dataset("deepset/prompt-injections")
print(i)
print(i["train"][0])             # confirm which label value means injection, and the language mix

j = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors")
print(j)                         # expect harmful and benign splits; do not print the text
