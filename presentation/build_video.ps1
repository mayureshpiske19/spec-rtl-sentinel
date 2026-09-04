# Assembles the 2-minute AI demo video: deck slides timed to the AI narration.
# Requires ffmpeg on PATH. Usage:
#   powershell -File build_video.ps1                 # uses Zira voiceover
#   powershell -File build_video.ps1 -Voice ravi     # uses Ravi voiceover
param([string]$Voice = "zira")

$ErrorActionPreference = "Stop"
$dir = $PSScriptRoot
$slides = Join-Path $dir "video"
$audio = Join-Path $dir "voiceover_$Voice.wav"
$out = Join-Path $dir "spec_rtl_sentinel_demo.mp4"

if (-not (Test-Path $audio)) { throw "voiceover not found: $audio" }

# Per-slide display seconds (sum ~= narration length; last slide auto-extends
# to match the audio via -shortest on the audio, plus tpad on video).
$plan = @(
    @{ img = "slide-01.png"; sec = 6 },
    @{ img = "slide-02.png"; sec = 14 },
    @{ img = "slide-03.png"; sec = 14 },
    @{ img = "slide-04.png"; sec = 8 },
    @{ img = "slide-05.png"; sec = 12 },
    @{ img = "slide-06.png"; sec = 6 },
    @{ img = "slide-07.png"; sec = 16 },
    @{ img = "slide-08.png"; sec = 12 },
    @{ img = "slide-09.png"; sec = 8 },
    @{ img = "slide-10.png"; sec = 4 },
    @{ img = "slide-11.png"; sec = 8 }
)

# Build the ffmpeg concat list.
$listPath = Join-Path $env:TEMP "slides_concat.txt"
$lines = @()
foreach ($p in $plan) {
    $img = (Join-Path $slides $p.img) -replace '\\', '/'
    $lines += "file '$img'"
    $lines += "duration $($p.sec)"
}
# concat demuxer needs the last file repeated (no duration) to flush it.
$lastImg = (Join-Path $slides $plan[-1].img) -replace '\\', '/'
$lines += "file '$lastImg'"
Set-Content -LiteralPath $listPath -Value ($lines -join "`n") -Encoding ASCII

# Encode: slideshow video + AAC audio, stop at the shorter stream (audio),
# pad video so it never ends before the audio.
& ffmpeg -y -f concat -safe 0 -i $listPath -i $audio `
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p,tpad=stop_mode=clone:stop_duration=5" `
    -c:v libx264 -r 30 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest `
    $out

Write-Output "wrote $out"
