import asyncio, os, subprocess, json
import edge_tts

VOICE = "en-US-GuyNeural"
OUT = os.path.join(os.path.dirname(__file__), "vo")
os.makedirs(OUT, exist_ok=True)

SCENES = [
    ("s01", "Every chip starts as intent. A high-level spec, refined into a micro-architecture spec, then built as R-T-L."),
    ("s02", "But intent drifts. A bus width changes in a review. A register moves in a meeting. And those decisions rarely make it back into the spec. When the R-T-L no longer matches the intent, that is how bugs, and security holes, reach silicon."),
    ("s03", "Today, catching that drift means manually cross-checking the R-T-L against the high-level spec, the micro-architecture spec, and a scattered trail of review notes. It is slow, inconsistent, and the first thing dropped under deadline pressure."),
    ("s04", "Meet Spec-R-T-L Sentinel, the Design Intent Auditor."),
    ("s05", "Sentinel ingests every layer of design authority into a RAG knowledge store: the high-level spec, the micro-architecture spec, and the real decisions from reviews and meetings."),
    ("s06", "Its agents extract testable claims, scan the R-T-L, and reconcile conflicts by authority and recency, so a newer review outranks a stale spec."),
    ("s07", "Here it is on a real example: a hardware compression accelerator. One command, and in seconds, Sentinel runs two checks. Spec to spec coverage, and spec to R-T-L conformance. It catches a thirty-two bit bus where sixty-four is required. A missing state in the control machine. A performance counter never implemented. And an interrupt register a review moved, which the R-T-L correctly followed."),
    ("s08", "And it grades maturity by milestone: the interface, then function, then error, D-F-T, and performance. Here, the design fails its very first gate."),
    ("s09", "Every finding cites its exact source. No hallucinations. Just grounded, traceable evidence."),
    ("s11", "Spec-R-T-L Sentinel: catching spec to silicon drift, before it becomes a bug."),
]

async def gen():
    meta = []
    for name, text in SCENES:
        mp3 = os.path.join(OUT, name + ".mp3")
        com = edge_tts.Communicate(text, VOICE, rate="+6%")
        await com.save(mp3)
        # measure duration with ffprobe
        dur = float(subprocess.check_output(
            ["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=nw=1:nk=1", mp3], text=True).strip())
        meta.append({"name": name, "dur": round(dur,2)})
        print(f"{name}: {dur:.2f}s")
    total = sum(m["dur"] for m in meta)
    print(f"TOTAL narration: {total:.1f}s ({int(total//60)}:{int(total%60):02d})")
    json.dump(meta, open(os.path.join(OUT,"meta.json"),"w"), indent=2)

asyncio.run(gen())
