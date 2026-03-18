import re

def ask_llm(prompt, context):

    if not context or context.strip() == "":
        return "No content found in document."

    prompt = prompt.lower()
    lines = context.split("\n")

    best_lines = []

    for line in lines:
        line_lower = line.lower()

        # agar question ke words line me milte hain
        for word in prompt.split():
            if word in line_lower:
                best_lines.append(line.strip())
                break

    if best_lines:
        return "\n".join(best_lines[:5])   # top 5 relevant lines

    return "Answer not found in document"