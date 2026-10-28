"""結構指標：字數、XML 區塊、理由句、強制語、持續性規則、範例數，以及各頂層區塊字數。
用法：python -I metrics.py <file> [<file> ...]
"""
import os
import re
import sys

TOP = ["product_information", "refusal_handling", "legal_and_financial_advice", "medical_guidance",
       "tone_and_formatting", "proactivity", "user_wellbeing", "anthropic_reminders", "evenhandedness",
       "responding_to_mistakes_and_criticism", "additional_info", "knowledge_cutoff", "default_stance",
       "fable_safeguards_routing", "tool_discovery", "respond_without_citing_system_prompt",
       "acting_vs_clarifying", "capability_check", "tone_preference", "reply_after_tool_calls",
       "conversational_register"]


def section_words(t, tag):
    m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), t, re.S)
    return len(m.group(1).split()) if m else 0


for f in sys.argv[1:]:
    t = open(f, encoding="utf-8").read()
    name = os.path.basename(f).replace("__default.txt", "")
    tags = sorted(set(re.findall(r"<([a-z_]+)>", t)))
    low = t.lower()
    row = {
        "words": len(t.split()),
        "tags": len(tags),
        "because": len(re.findall(r"\bbecause\b", low)),
        "never": len(re.findall(r"\bnever\b", low)),
        "CAPS": len(re.findall(r"\b(NEVER|MUST|REFUSE|CRITICAL)\b", t)),
        "rest_of_conv": low.count("rest of the conversation") + low.count("rest of that conversation"),
        "examples": t.count("<example>"),
        "paragraphs": len([p for p in re.split(r"\n\s*\n", t) if p.strip()]),
    }
    print(name)
    print("   " + "  ".join("%s=%s" % kv for kv in row.items()))
    secs = ["%s=%d" % (s, section_words(t, s)) for s in TOP if section_words(t, s)]
    print("   " + "  ".join(secs))
