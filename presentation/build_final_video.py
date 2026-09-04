"""
Assemble the final synced demo video:
  each scene = its neural-voice narration + a matching visual, concatenated.
  Demo scene (s07) = live terminal card, then a scroll through the HTML dashboard.
Requires ffmpeg on PATH.
"""
import json, os, subprocess

HERE = os.path.dirname(__file__)
VO = os.path.join(HERE, "vo")
SLIDES = os.path.join(HERE, "video")
OUT = os.path.join(HERE, "spec_rtl_sentinel_demo.mp4")

meta = {m["name"]: m["dur"] for m in json.load(open(os.path.join(VO, "meta.json")))}

def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

VF_IMG = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,fps=30")

def image_scene(img, audio, out, pad_tail=0.4):
    dur = meta[os.path.splitext(os.path.basename(audio))[0]] + pad_tail
    run(["ffmpeg","-y","-loop","1","-framerate","30","-t",f"{dur:.2f}","-i",img,
         "-i",audio,
         "-vf",VF_IMG,
         "-c:v","libx264","-preset","medium","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-af","apad","-shortest",
         "-r","30", out])

# ---- Scenes 1-6, 8, 9, 11: slide image + narration ----
plan = [
    ("s01","slide-01.png"), ("s02","slide-02.png"), ("s03","slide-03.png"),
    ("s04","slide-04.png"), ("s05","slide-05.png"), ("s06","slide-06.png"),
    # s07 handled specially
    ("s08","slide-08.png"), ("s09","slide-09.png"), ("s11","slide-11.png"),
]
segments = []
for name, slide in plan[:6]:
    out = os.path.join(VO, f"scene_{name}.mp4")
    image_scene(os.path.join(SLIDES, slide), os.path.join(VO, name+".mp3"), out)
    segments.append((name, out))

# ---- Scene 7: terminal card (14s) + dashboard scroll (rest) ----
s07_dur = meta["s07"] + 0.4
term_dur = 14.0
scroll_dur = max(s07_dur - term_dur, 8.0)

term_v = os.path.join(VO, "s07_term.mp4")
run(["ffmpeg","-y","-loop","1","-framerate","30","-t",f"{term_dur:.2f}",
     "-i",os.path.join(VO,"terminal.png"),
     "-vf","scale=1920:1080,setsar=1,format=yuv420p,fps=30",
     "-c:v","libx264","-preset","medium","-pix_fmt","yuv420p","-r","30", term_v])

# scroll: pan the tall dashboard through a 1080-tall window
scroll_v = os.path.join(VO, "s07_scroll.mp4")
crop = (f"crop=1920:1080:0:'min(max((ih-1080)*t/{scroll_dur:.2f}\\,0)\\,ih-1080)',"
        "setsar=1,format=yuv420p,fps=30")
run(["ffmpeg","-y","-loop","1","-framerate","30","-t",f"{scroll_dur:.2f}",
     "-i",os.path.join(VO,"dashboard_full.png"),
     "-vf",crop,
     "-c:v","libx264","-preset","medium","-pix_fmt","yuv420p","-r","30", scroll_v])

# concat term + scroll -> s07 video (silent)
concat07 = os.path.join(VO, "s07_concat.txt")
open(concat07,"w").write(f"file '{term_v.replace(os.sep,'/')}'\nfile '{scroll_v.replace(os.sep,'/')}'\n")
s07_v = os.path.join(VO, "s07_v.mp4")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat07,"-c","copy", s07_v])

# mux s07 video + s07 narration
s07_final = os.path.join(VO, "scene_s07.mp4")
run(["ffmpeg","-y","-i",s07_v,"-i",os.path.join(VO,"s07.mp3"),
     "-c:v","copy","-c:a","aac","-b:a","192k","-af","apad","-shortest", s07_final])

# ---- Scenes 8, 9, 11 ----
for name, slide in plan[6:]:
    out = os.path.join(VO, f"scene_{name}.mp4")
    image_scene(os.path.join(SLIDES, slide), os.path.join(VO, name+".mp3"), out)

# ---- Final concat in narrative order ----
order = ["s01","s02","s03","s04","s05","s06","s07","s08","s09","s11"]
listfile = os.path.join(VO, "final_concat.txt")
with open(listfile,"w") as f:
    for n in order:
        p = os.path.join(VO, f"scene_{n}.mp4").replace(os.sep,"/")
        f.write(f"file '{p}'\n")

# re-encode on concat to normalize timestamps
run(["ffmpeg","-y","-f","concat","-safe","0","-i",listfile,
     "-c:v","libx264","-preset","medium","-pix_fmt","yuv420p","-r","30",
     "-c:a","aac","-b:a","192k", OUT])

dur = float(subprocess.check_output(
    ["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",OUT],
    text=True).strip())
print(f"wrote {OUT}  ({int(dur//60)}:{int(dur%60):02d}, {os.path.getsize(OUT)/1e6:.1f} MB)")
