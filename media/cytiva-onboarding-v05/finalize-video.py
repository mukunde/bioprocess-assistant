"""Finalize and inspect the locally rendered onboarding without touching the app."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tools-directory', type=Path, default=ROOT)
args = parser.parse_args()
OUT = ROOT / 'renders'
(OUT/'work').mkdir(parents=True, exist_ok=True)
FFMPEG = args.tools_directory / 'node_modules/ffmpeg-static/ffmpeg.exe'
FFPROBE = args.tools_directory / 'node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe'

def ff(*args):
    subprocess.run([str(FFMPEG), '-hide_banner', '-loglevel', 'warning', *args], check=True)

def probe(path):
    return json.loads(subprocess.check_output([
        str(FFPROBE), '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ], text=True, encoding='utf-8'))

raw = OUT / 'onboarding.raw.mp4'
assert raw.stat().st_size > 100_000
raw_info = probe(raw)
for i, at in enumerate((3, 7, 10.5, 12.8, 15.5, 20, 28, 32)):
    ff('-y', '-ss', str(at), '-i', str(raw), '-frames:v', '1',
       str(OUT / f'work/decoded-{i+1}.png'))
# Settled citation scene: actual source identifier, page and continuous excerpt.
ff('-y', '-ss', '20', '-i', str(raw), '-frames:v', '1', '-q:v', '2', str(OUT/'onboarding.jpg'))
# Preserve the full 1020-frame timeline and copy audio without another audio encode.
ff('-y', '-i', str(raw), '-i', str(OUT/'onboarding.jpg'),
   '-filter_complex', "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",
   '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-crf', '18',
   '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
   '-movflags', '+faststart', '-metadata', 'title=Cytiva local demo — source-first onboarding',
   '-metadata', 'comment=Edited real demo UI. Music: Sascha Ende, CC BY 4.0. See ATTRIBUTION.md.',
   str(OUT/'onboarding.mp4'))
info = probe(OUT/'onboarding.mp4')
video = next(s for s in info['streams'] if s['codec_type'] == 'video')
audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
assert (video['width'], video['height']) == (1920, 1080)
assert video['r_frame_rate'] == '30/1'
assert int(video['nb_frames']) == 1020
assert abs(float(info['format']['duration'])-34) < .1
assert audio['codec_name'] == 'aac'
ff('-y', '-i', str(OUT/'onboarding.mp4'), '-frames:v', '1', str(OUT/'work/final-first-frame.png'))
volume = subprocess.run([str(FFMPEG), '-hide_banner', '-i', str(OUT/'onboarding.mp4'),
    '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
assert volume.returncode == 0
(OUT/'work/audio-volume.log').write_text(volume.stderr, encoding='utf-8')
(OUT/'work/video-verification.json').write_text(json.dumps({
    'raw': raw_info, 'final': info, 'poster_time_seconds': 20,
    'poster_baked_as_frame_0': True, 'expected_frames': 1020,
    'decoded_review_times': [3, 7, 10.5, 12.8, 15.5, 20, 28, 32],
    'audio_reencoded_in_finalization': False,
}, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'duration': info['format']['duration'], 'frames': video['nb_frames'],
    'resolution': [video['width'], video['height']], 'audio': audio['codec_name'],
    'bytes': (OUT/'onboarding.mp4').stat().st_size}))
