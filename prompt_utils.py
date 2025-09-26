from typing import List, Dict

def pack_context(question: str, entities: List[Dict], facts: List[Dict]) -> str:
    lines = []
    lines.append("SYSTEM RULES:")
    lines.append("- Answer ONLY using the FACTS provided.")
    lines.append("- If the facts are insufficient, say: 'Not enough data in the graph.'")
    lines.append("- Cite facts using [F#] where # is the fact index.")
    lines.append("")
    lines.append(f"QUESTION: {question}")
    lines.append("")
    lines.append("ENTITIES:")
    for e in entities[:8]:
        if "title" in e:
            lines.append(f"- Movie: {e['title']} ({e.get('year','?')}) [id={e['id']}]")
        else:
            lines.append(f"- Person: {e['name']} [id={e['id']}]")
    lines.append("")
    lines.append("FACTS:")
    for i, f in enumerate(facts[:20], start=1):
        lines.append(f"[F{i}] {f['subj']} {f['rel']} {f['obj']} (fetched_at={f.get('fetched_at','?')})")
    lines.append("")
    lines.append("Provide: a concise answer (2–4 sentences) and reference the used facts like [F1][F3].")
    return "\n".join(lines)
