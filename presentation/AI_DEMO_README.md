# Spec-RTL Sentinel — 2-Minute AI Demo

An AI-narrated pitch video. The `voiceover_*.wav` files are AI-generated
narration of `voiceover_script.txt`; `build_video.ps1` assembles them with the
deck slides into a ready-to-submit MP4.

## Voiceover options (all under the 2:00 cap)

| File | Voice | Length |
| --- | --- | --- |
| `voiceover_zira.wav` | Microsoft Zira (en-US, female) | ~1:46 |
| `voiceover_ravi.wav` | Microsoft Ravi (en-IN, male)  | ~1:49 |
| `voiceover_hazel.wav`| Microsoft Hazel (en-GB, female) | ~2:02 |

## Storyboard (slide ↔ narration)

| Slide | On screen | Narration beat |
| --- | --- | --- |
| 1 | Title | "Every chip starts as intent…" |
| 2 | The Problem | "…that is how bugs reach silicon." |
| 3 | The Insight (tribal layer) | "Today, catching that drift means manually cross-checking…" |
| 4 | What it does | "Meet Spec-RTL Sentinel, the Design Intent Auditor." |
| 5 | Architecture | "Sentinel ingests every layer of design authority…" |
| 6 | The agents | "…extract testable claims, scan the RTL, reconcile conflicts…" |
| 7 | Live demo — findings | "Here it is on a real example… runs two checks…" |
| 8 | Milestone gates | "And it grades maturity by milestone…" |
| 9 | Why it's different | "Every finding cites its exact source. No hallucinations." |
| 10 | Impact | (held under close) |
| 11 | Roadmap + GitHub | "…catching spec-to-silicon drift before it becomes a bug." |

## Make it stronger (optional)

For maximum impact, replace slide 7's static image in the final edit with a
**screen recording of the live run**:

```bash
python run_demo.py
```

Record the terminal (Win+G or Clipchamp) showing the gate table + findings, and
drop that clip over the demo section. The rest of the deck + AI narration stays.

## How to assemble

Run `build_video.ps1` (needs ffmpeg). It muxes the slides (timed to the
narration) with the chosen voiceover into `spec_rtl_sentinel_demo.mp4`. Then
upload that MP4 to the hackathon project to unblock submission.
