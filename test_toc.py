import os
from dotenv import load_dotenv
load_dotenv()

from pageindex.utils import ChatGPT_API

model = "glm-4.6v"

# Sample page text (first page of the PDF)
content = '''"mcs" — 2018/6/6 — 13:43 — page i — #1
Mathematics for Computer Science
revised Wednesday 6th June, 2018, 13:43
Eric Lehman
Google Inc.
F Thomson Leighton
Department of Mathematics
and the Computer Science and AI Laboratory,
Massachussetts Institute of Technology;
Akamai Technologies
Albert R Meyer
Department of Electrical Engineering and Computer Science
and the Computer Science and AI Laboratory,
Massachussetts Institute of Technology
2018, Eric Lehman, F Tom Leighton, Albert R Meyer. This work is available under the
terms of the Creative Commons Attribution-ShareAlike 3.0 license.'''

prompt = f"""You are a document analyzer. Your task is to detect if the given text contains a table of contents (TOC).

Text to analyze:
{content}

IMPORTANT NOTES:
- Abstract, summary, notation list, figure list, table list, bibliography, index are NOT table of contents
- A table of contents typically contains chapter/section titles with page numbers
- Look for phrases like "Contents", "Table of Contents", "Chapters", "Sections"

Return ONLY a valid JSON object in this exact format (no markdown, no explanations):
```json
{{
    "thinking": "Brief explanation of your analysis",
    "toc_detected": "yes" or "no"
}}
```

Example response:
```json
{{
    "thinking": "The text shows a list of chapters with page numbers",
    "toc_detected": "yes"
}}
```

Remember: Return ONLY the JSON, nothing else."""

print(f"Testing TOC detection with model: {model}\n")
print("Calling API...")

try:
    response = ChatGPT_API(model=model, prompt=prompt)
    print(f"\nResponse:\n{response}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
