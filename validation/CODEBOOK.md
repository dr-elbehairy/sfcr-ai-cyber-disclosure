# Codebook given to both validation coders (verbatim, local file paths removed)

The same instructions were given to coder A and coder B, each a separate instance of a large language model (Claude, Anthropic) working independently, with no access to the other coder's file or to `validation_key.csv` (which records why a sentence was sampled).

Input: `to_code.csv` (columns id, sentence; 746 sentences).

For every sentence assign:
- cyber: 1 if the sentence is substantively about cyber risk or information/ICT security (cyber-attacks, data breaches, information security, IT/ICT security risk, ransomware, digital operational resilience/DORA, cyber insurance as a product line), else 0. A passing word in a list of risk types still counts as 1 (code "mention"), but words like "hacked" used in another sense, or 'DORA' as a person's name, count as 0.
- cyber_depth: if cyber=1: "mention" (cyber only named in a list or in passing), "governance" (who is responsible, policies, functions, committees, controls, frameworks), "quantified" (numbers, scenarios, stress tests, capital, losses, incidents described concretely), or "product" (cyber insurance underwriting/exposure). If cyber=0: blank.
- ai: 1 if the sentence is substantively about artificial intelligence, machine learning, generative AI, large language models or the EU AI Act, else 0 (e.g. 'AI' as an abbreviation of something else = 0).
- ai_type: if ai=1: "use" (the insurer uses or plans to use AI in its business), "risk_governance" (AI as a source of risk, AI governance, controls, policies, ethics), "regulation" (AI Act or other AI rules), or "other". If ai=0: blank.

Read every sentence; do not use keyword rules.

Output: `coder_A.csv` / `coder_B.csv` with columns id, cyber, cyber_depth, ai, ai_type.
