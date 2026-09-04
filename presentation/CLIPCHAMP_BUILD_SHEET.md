# Clipchamp Build Sheet — Spec-RTL Sentinel (2-minute demo)

Everything you need to assemble the video in **Microsoft Clipchamp** with its
built-in **AI text-to-speech**. Target length: **≤ 2:00**, format 1080p MP4.

---

## 1. Assets to import

**Slide images (1920×1080 PNG)** — drag all 11 into Clipchamp's media bin:

```
C:\Users\mpiske\OneDrive - Microsoft\Documents\Hackathon_26\Spec-RTL-Sentinel\repo\presentation\video\
  slide-01.png … slide-11.png
```

Optional extra visuals (from `...\repo\docs\`):
- `architecture.png`   — the pipeline diagram (already on slide 5, use as a zoom-in if you want)
- `ui_screenshot.png`  — the dashboard (already on slide 7 verdict; nice as a full-screen beat)

**Best upgrade:** screen-record a live run for the demo section (scene 7).
Open a terminal and run:
```
python run_demo.py
```
Record the gate table + findings scrolling (Clipchamp has a Screen recorder:
*Record & create → Screen*). Drop that clip over scene 7 instead of slide-07.

---

## 2. AI voiceover in Clipchamp

Clipchamp → **Record & create → Text to speech**.
- **Language:** English (United States) or English (India)
- **Recommended voices:**
  - US: **Aria** or **Guy** (neural, clear) 
  - India: **Neerja** (female) or **Prabhat** (male)
- **Speed:** Normal (nudge to +5–10% only if you run over 2:00)
- Paste the narration (below). You can generate it as **one block**, or
  **per scene** (cleaner sync — recommended). Each generated clip lands on the
  timeline; line it up under its slide.

---

## 3. Scene-by-scene timeline

Total ≈ 1:50. Each scene: slide image on screen for the listed seconds, with the
matching voiceover under it.

### Scene 1 — Title  ·  slide-01.png  ·  ~6s
> Every chip starts as intent. A high-level spec, refined into a micro-architecture spec, then built as RTL.

### Scene 2 — The Problem  ·  slide-02.png  ·  ~15s
> But intent drifts. A bus width changes in a review. A register moves in a meeting. And those decisions rarely make it back into the spec. When the RTL no longer matches the intent, that is how bugs — and security holes — reach silicon.

### Scene 3 — The Insight  ·  slide-03.png  ·  ~14s
> Today, catching that drift means manually cross-checking the RTL against the high-level spec, the micro-architecture spec, and a scattered trail of review notes. It is slow, inconsistent, and the first thing dropped under deadline pressure.

### Scene 4 — Meet Sentinel  ·  slide-04.png  ·  ~7s
> Meet Spec-RTL Sentinel, the Design Intent Auditor.

### Scene 5 — Architecture  ·  slide-05.png  ·  ~14s
> Sentinel ingests every layer of design authority into a RAG knowledge store: the high-level spec, the micro-architecture spec, and the real decisions from reviews and meetings.

### Scene 6 — The Agents  ·  slide-06.png  ·  ~9s
> Its agents extract testable claims, scan the RTL, and reconcile conflicts by authority and recency — so a newer review outranks a stale spec.

### Scene 7 — Live Demo  ·  slide-07.png (or screen recording)  ·  ~18s
> Here it is on a real example: a hardware compression accelerator. One command, and in seconds Sentinel runs two checks — spec-to-spec coverage, and spec-to-RTL conformance. It catches a thirty-two-bit bus where sixty-four is required, a missing state in the control machine, a performance counter never implemented, and an interrupt register a review moved — which the RTL correctly followed.

### Scene 8 — Milestone Gates  ·  slide-08.png  ·  ~12s
> And it grades maturity by milestone: the interface, then function, then error, D-F-T, and performance. Here, the design fails its very first gate.

### Scene 9 — Why It's Different  ·  slide-09.png  ·  ~9s
> Every finding cites its exact source. No hallucinations. Just grounded, traceable evidence.

### Scene 10 — Impact  ·  slide-10.png  ·  ~4s
> (no narration — hold briefly, or let scene 9 audio run under it)

### Scene 11 — Close  ·  slide-11.png  ·  ~7s
> Spec-RTL Sentinel: catching spec-to-silicon drift before it becomes a bug.

---

## 4. Assembly steps in Clipchamp

1. **New project** → 1080p.
2. **Import** the 11 slide PNGs (and any screen recording).
3. Drag slides onto the timeline **in order**; set each slide's duration per the
   seconds above (drag its edge, or right-click → Duration).
4. **Text to speech** per scene: paste each scene's text, pick the voice,
   generate, then drag the audio clip under its slide and align.
5. (Optional) Add **captions**: Clipchamp can auto-caption from the audio, or
   paste the same text as text overlays.
6. (Optional) Add subtle **background music** at low volume (Clipchamp stock →
   "corporate/tech", set to ~10–15%).
7. Add a 0.3–0.5s **crossfade/dissolve** between slides for polish.
8. Check the total is **under 2:00** (trim scene gaps if needed).
9. **Export → 1080p → MP4.**

---

## 5. Submit

Upload the exported MP4 to the hackathon project page (Media → Upload video).
That clears the "video required" blocker and lets you submit.

---

### Full script (one block, if you prefer single TTS)

Every chip starts as intent. A high-level spec, refined into a micro-architecture spec, then built as RTL. But intent drifts. A bus width changes in a review. A register moves in a meeting. And those decisions rarely make it back into the spec. When the RTL no longer matches the intent, that is how bugs, and security holes, reach silicon. Today, catching that drift means manually cross-checking the RTL against the high-level spec, the micro-architecture spec, and a scattered trail of review notes. It is slow, inconsistent, and the first thing dropped under deadline pressure. Meet Spec-RTL Sentinel, the Design Intent Auditor. Sentinel ingests every layer of design authority into a RAG knowledge store: the high-level spec, the micro-architecture spec, and the real decisions from reviews and meetings. Its agents extract testable claims, scan the RTL, and reconcile conflicts by authority and recency, so a newer review outranks a stale spec. Here it is on a real example, a hardware compression accelerator. One command, and in seconds Sentinel runs two checks: spec-to-spec coverage, and spec-to-RTL conformance. It catches a thirty-two-bit bus where sixty-four is required, a missing state in the control machine, a performance counter never implemented, and an interrupt register a review moved, which the RTL correctly followed. And it grades maturity by milestone: the interface, then function, then error, D-F-T, and performance. Here, the design fails its very first gate. Every finding cites its exact source. No hallucinations. Just grounded, traceable evidence. Spec-RTL Sentinel: catching spec-to-silicon drift before it becomes a bug.
