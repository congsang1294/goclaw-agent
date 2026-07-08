"""
gen-video.py — Tao video clip tu prompt theo CHAIN nha cung cap (uu tien FREE):
  1. Pollinations  — model wan-fast (free, credit tang moi ngay). Can POLLINATIONS_KEY.
  2. Hugging Face  — model video mo (free credit hang thang). Can HF_TOKEN.
  3. Kling 1.6     — tra phi (chi khi tai khoan co credit). Can KLING_SECRET_KEY (+ KLING_API_BASE).

Provider khong co key -> bo qua. Loi bat ky -> retry 1 lan roi chuyen provider ke tiep.
DRY_RUN=true -> bo qua het (chi sinh prompt + script o buoc truoc).
Output: output/video_raw.mp4 (build-final.py se loop cho du do dai giong doc 15-25s).

Usage:
  python scripts/gen-video.py --prompt-file output/prompt.json --aspect 9:16
"""

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import shutil
import argparse
import subprocess
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_HERE = Path(__file__).resolve()
for _envp in (_HERE.parents[1] / ".env", _HERE.parents[3] / ".env"):
    if _envp.exists():
        load_dotenv(dotenv_path=_envp, override=False)

try:
    import requests
except ImportError:
    print("[FAIL] Thieu requests. Chay: pip install requests")
    sys.exit(1)

try:
    from openai import OpenAI
    import base64 as b64_mod
except ImportError:
    print("[FAIL] Thieu openai. Chay: pip install openai")
    sys.exit(1)

SKILL_DIR = _HERE.parents[1]
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

POLL_TIMEOUT = int(os.getenv("VIDEO_TIMEOUT", "300"))  # giay (video gen lau)
POLLINATIONS_MODEL = os.getenv("POLLINATIONS_VIDEO_MODEL", "wan-fast")  # re nhat
# Ken Burns (FREE): anh Pollinations Flux (mien phi) + ffmpeg zoom/pan -> video
KENBURNS_SECONDS = int(os.getenv("KENBURNS_SECONDS", "25"))  # >= do dai voice toi da
POLLINATIONS_IMG_MODEL = os.getenv("POLLINATIONS_IMG_MODEL", "flux")
_SCENES = []  # danh sach prompt anh (scene_prompts) — main set tu prompt.json
HF_VIDEO_MODEL = os.getenv("HF_VIDEO_MODEL", "ali-vilab/text-to-video-ms-1.7b")
# Kling
KLING_BASE = os.getenv("KLING_API_BASE", "https://api.klingai.com").rstrip("/")
KLING_MODEL = os.getenv("KLING_MODEL", "kling-v1-6")
KLING_DURATION = os.getenv("KLING_DURATION", "5")  # 5 re hon 10
KLING_MODE = os.getenv("KLING_MODE", "std")        # std re hon pro


def is_dry_run() -> bool:
    return os.getenv("DRY_RUN", "false").strip().lower() in ("1", "true", "yes")


class SkipProvider(Exception):
    """Provider thieu key -> bo qua (KHONG retry). Dung class rieng vi requests.HTTPError
    ke thua OSError (== EnvironmentError) -> neu bao skip bang EnvironmentError se nuot ca loi API."""
    pass


def _is_video(resp) -> bool:
    ct = resp.headers.get("content-type", "").lower()
    return "video" in ct or "mp4" in ct or "octet-stream" in ct


# ─────────────────────────────────────────────
# PROVIDER 1 — Pollinations (free, wan-fast)
# ─────────────────────────────────────────────
def provider_pollinations(prompt, negative, aspect, out_path):
    key = os.getenv("POLLINATIONS_KEY") or os.getenv("POLLINATIONS_TOKEN")
    if not key:
        raise SkipProvider("POLLINATIONS_KEY chua set — bo qua")
    enc = urllib.parse.quote(prompt[:1500])
    url = f"https://gen.pollinations.ai/video/{enc}"
    params = {"model": POLLINATIONS_MODEL, "aspectRatio": aspect}
    r = requests.get(url, params=params, headers={"Authorization": f"Bearer {key}"}, timeout=POLL_TIMEOUT)
    r.raise_for_status()
    if not _is_video(r):
        raise ValueError(f"khong phai video ({r.headers.get('content-type')}): {r.text[:160]}")
    out_path.write_bytes(r.content)


# ─────────────────────────────────────────────
# PROVIDER 2 — Hugging Face (free, model video mo)
# ─────────────────────────────────────────────
def provider_huggingface(prompt, negative, aspect, out_path):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise SkipProvider("HF_TOKEN chua set — bo qua")
    url = f"https://api-inference.huggingface.co/models/{HF_VIDEO_MODEL}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": prompt[:1500]}
    r = requests.post(url, headers=headers, json=payload, timeout=POLL_TIMEOUT)
    if r.status_code == 503:  # model dang load
        wait = 20
        try:
            wait = int(r.json().get("estimated_time", 20)) + 5
        except Exception:
            pass
        print(f"  [HF] model dang khoi dong, doi {wait}s...")
        time.sleep(wait)
        r = requests.post(url, headers=headers, json=payload, timeout=POLL_TIMEOUT)
    r.raise_for_status()
    if not _is_video(r):
        raise ValueError(f"khong phai video ({r.headers.get('content-type')}): {r.text[:160]}")
    out_path.write_bytes(r.content)


# ─────────────────────────────────────────────
# PROVIDER 3 — Kling 1.6 (tra phi)
# ─────────────────────────────────────────────
def _b64url(raw: bytes) -> bytes:
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def _kling_jwt(ak: str, sk: str) -> str:
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    now = int(time.time())
    payload = _b64url(json.dumps({"iss": ak, "exp": now + 1800, "nbf": now - 5},
                                 separators=(",", ":")).encode())
    si = header + b"." + payload
    sig = _b64url(hmac.new(sk.encode(), si, hashlib.sha256).digest())
    return (si + b"." + sig).decode()


def _kling_headers() -> dict:
    sk = os.getenv("KLING_SECRET_KEY", "")
    ak = os.getenv("KLING_ACCESS_KEY", "")
    token = _kling_jwt(ak, sk) if ak else sk  # JWT neu co access key, nguoc lai Bearer tho
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def provider_kling(prompt, negative, aspect, out_path):
    if not os.getenv("KLING_SECRET_KEY"):
        raise SkipProvider("KLING_SECRET_KEY chua set — bo qua")
    payload = {
        "model_name": KLING_MODEL, "prompt": prompt[:2400], "negative_prompt": negative[:2400],
        "cfg_scale": 0.5, "mode": KLING_MODE, "aspect_ratio": aspect, "duration": KLING_DURATION,
    }
    r = requests.post(f"{KLING_BASE}/v1/videos/text2video", headers=_kling_headers(),
                      json=payload, timeout=60)
    r.raise_for_status()
    task_id = (r.json().get("data") or {}).get("task_id")
    if not task_id:
        raise ValueError(f"khong co task_id: {str(r.json())[:160]}")
    # poll
    waited, interval = 0, 10
    while waited < POLL_TIMEOUT:
        time.sleep(interval); waited += interval
        pr = requests.get(f"{KLING_BASE}/v1/videos/text2video/{task_id}",
                          headers=_kling_headers(), timeout=30)
        pr.raise_for_status()
        data = pr.json().get("data") or {}
        status = data.get("task_status", "")
        print(f"  [Kling +{waited}s] {status}")
        if status == "succeed":
            videos = (data.get("task_result") or {}).get("videos") or []
            if videos and videos[0].get("url"):
                vr = requests.get(videos[0]["url"], timeout=180)
                vr.raise_for_status()
                out_path.write_bytes(vr.content)
                return
            raise ValueError("succeed nhung khong co URL video")
        if status == "failed":
            raise RuntimeError(f"Kling failed: {data.get('task_status_msg', '')}")
    raise TimeoutError(f"Kling qua {POLL_TIMEOUT}s chua xong")


# ─────────────────────────────────────────────
# PROVIDER 0 — Ken Burns (FREE 100%): anh Flux free + ffmpeg zoom/pan
# ─────────────────────────────────────────────
def _ffmpeg_kenburns(image_path, out_path, seconds, aspect, effect="in"):
    """1 anh tinh -> 1 clip co chuyen dong (zoom-in hoac pan ngang)."""
    w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    fps = 30
    frames = max(1, int(seconds * fps))
    cy = "ih/2-(ih/zoom/2)"
    if effect == "pan":
        zp = f"zoompan=z=1.2:x='(iw-iw/zoom)*on/{frames}':y='{cy}':d={frames}:s={w}x{h}:fps={fps}"
    else:  # zoom-in cham
        zp = f"zoompan=z='min(zoom+0.0008,1.45)':x='iw/2-(iw/zoom/2)':y='{cy}':d={frames}:s={w}x{h}:fps={fps}"
    vf = f"scale={w*4}:-1,{zp},setsar=1"
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-vf", vf,
           "-t", str(seconds), "-r", str(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg kenburns loi: {proc.stderr[-300:]}")


def _ffmpeg_concat(segments, out_path):
    """Noi nhieu clip (cung thong so) thanh 1 video."""
    listfile = OUTPUT_DIR / "kb_list.txt"
    listfile.write_text("".join(f"file '{Path(s).name}'\n" for s in segments), encoding="utf-8")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(out_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(OUTPUT_DIR))
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg concat loi: {proc.stderr[-300:]}")


def provider_kenburns(prompt, negative, aspect, out_path):
    if not shutil.which("ffmpeg"):
        raise SkipProvider("ffmpeg chua co bo qua KenBurns")
    api_key = os.getenv("OPENAI_KEY_REAL") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SkipProvider("OPENAI_API_KEY chua set bo qua")
    client = OpenAI(api_key=api_key)
    scenes = _SCENES if _SCENES else [prompt]
    iw, ih = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    per = max(5, KENBURNS_SECONDS // len(scenes))
    effects = ["in", "pan", "in"]
    segments = []
    for i, sc in enumerate(scenes):
        print("  [KenBurns] tao anh canh " + str(i+1) + "/" + str(len(scenes)) + "...")
        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=str(sc)[:1500],
                size="1024x1024",
                quality="medium",
                n=1,
            )
            if not result.data or not result.data[0].b64_json:
                raise ValueError("OpenAI khong tra ve anh")
            img_bytes = base64.b64decode(result.data[0].b64_json, validate=True)
        except Exception as e:
            print("  [KenBurns] OpenAI fail canh " + str(i+1) + ": " + str(e)[:100])
            raise
        img = OUTPUT_DIR / ("kb_img" + str(i) + ".png")
        img.write_bytes(img_bytes)
        seg = OUTPUT_DIR / ("kb_seg" + str(i) + ".mp4")
        fx = effects[i % len(effects)]
        print("  [KenBurns] canh " + str(i+1) + "/" + str(len(scenes)) + ": " + str(len(img_bytes)//1024) + "KB -> " + fx + " " + str(per) + "s")
        _ffmpeg_kenburns(img, seg, per, aspect, fx)
        segments.append(seg)
    if len(segments) == 1:
        shutil.copy(str(segments[0]), str(out_path))
    else:
        _ffmpeg_concat(segments, out_path)
    print("  [KenBurns] " + str(len(segments)) + " canh -> " + str(out_path))


CHAIN = [
    ("KenBurns", provider_kenburns),
    ("Pollinations", provider_pollinations),
    ("HuggingFace", provider_huggingface),
    ("Kling", provider_kling),
]


def generate_with_fallback(prompt, negative, aspect, out_path) -> str:
    """Thu tung provider; skip neu thieu key; retry 1 lan; chuyen provider neu fail."""
    last_err = None
    for name, fn in CHAIN:
        for attempt in range(2):
            try:
                print(f"  -> [{name}] dang tao video...")
                fn(prompt, negative, aspect, out_path)
                size_kb = out_path.stat().st_size // 1024
                print(f"  [OK] [{name}] {out_path} ({size_kb} KB)")
                return name
            except SkipProvider as e:
                print(f"  [SKIP] [{name}] {e}")
                break  # khong co key -> sang provider khac luon
            except Exception as e:
                last_err = e
                print(f"  [FAIL] [{name}] thu {attempt + 1}: {str(e)[:160]}")
                if attempt == 0:
                    print("  -> retry sau 5s...")
                    time.sleep(5)
        print(f"  -> chuyen provider tiep theo...")
    raise RuntimeError(
        f"Tat ca provider video that bai. Loi cuoi: {last_err}\n"
        "Them POLLINATIONS_KEY (enter.pollinations.ai) hoac HF_TOKEN (huggingface.co) vao .env."
    )


def main():
    parser = argparse.ArgumentParser(description="Tao video clip theo chain: Pollinations -> HuggingFace -> Kling")
    parser.add_argument("--prompt-file", default="", help="Doc video_prompt + negative_prompt tu prompt.json")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--negative", default="")
    parser.add_argument("--aspect", default="9:16")
    parser.add_argument("--out", default=str(OUTPUT_DIR / "video_raw.mp4"))
    args = parser.parse_args()

    prompt, negative = args.prompt, args.negative
    if args.prompt_file:
        data = json.loads(Path(args.prompt_file).read_text(encoding="utf-8"))
        prompt = prompt or data.get("video_prompt", "")
        negative = negative or data.get("negative_prompt", "")
        global _SCENES
        _SCENES = [str(s).strip() for s in (data.get("scene_prompts") or []) if str(s).strip()]
    if not prompt:
        print("[FAIL] Can --prompt hoac --prompt-file")
        sys.exit(1)

    if is_dry_run():
        print("[DRY_RUN] Bo qua tao video.")
        (OUTPUT_DIR / "dry_run_video.txt").write_text(
            f"DRY_RUN.\nPROMPT:\n{prompt}\n\nNEGATIVE:\n{negative}\n", encoding="utf-8")
        sys.exit(0)

    active = []
    if shutil.which("ffmpeg"):
        active.append("KenBurns(free)")
    if os.getenv("POLLINATIONS_KEY") or os.getenv("POLLINATIONS_TOKEN"):
        active.append(f"Pollinations({POLLINATIONS_MODEL})")
    if os.getenv("HF_TOKEN"):
        active.append(f"HuggingFace({HF_VIDEO_MODEL})")
    if os.getenv("KLING_SECRET_KEY"):
        active.append("Kling")
    print(f"\n[GEN-VIDEO] aspect={args.aspect} | provider chain: {' -> '.join(active) or '(KHONG co key nao!)'}")

    try:
        provider = generate_with_fallback(prompt, negative, args.aspect, Path(args.out))
    except RuntimeError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
    print(f"\n[OK] Video raw ({provider}): {args.out}")
    print("Buoc tiep theo: python scripts/build-final.py")


if __name__ == "__main__":
    main()
