from classifier import CattleClassifier
c = CattleClassifier()
res = c.predict("test.jpg")
r = res[0]

try:
    if hasattr(r, "probs"):
        top_idx = int(r.probs.top1) if hasattr(r.probs, "top1") else int(r.probs.argmax())
        top_name = r.names[top_idx]
        top_prob = float(r.probs[top_idx])
        print("TOP:", top_name, f"({top_prob:.3f})")
    else:
        print("Result object:", r)
except Exception as e:
    print("Could not parse result:", e)
    print("Raw result:", r)
