"""
Kompres - Kompresi dan optimasi video untuk platform sosial media.

Mendukung WhatsApp, Instagram, Telegram dengan encoding H.264 High Profile
dan kalibrasi warna BT.709.

Copyright (C) 2026 Garden
Licensed under GNU General Public License v3.0
"""

import streamlit as st
import ffmpeg
import os
import tempfile
import pathlib
import math
import subprocess
import re
import atexit
import base64
import json
import time
import uuid

APP_VERSION = "6.1.0"
APP_TITLE = "Kompres"
APP_TAGLINE = "Kompresi Video Profesional"

SUPPORTED_FORMATS = ["mp4", "mov", "mkv", "avi", "webm"]
FFMPEG_THREADS = 0
SESSION_DIR = "/tmp/kompres_sessions"
SESSION_MAX_AGE = 3600

_temp_files = []

RESOLUTION_MAP = {
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
}

SPEED_OPTIONS = ["ultrafast", "fast", "medium", "slow", "veryslow"]

FRAMERATE_OPTIONS = {
    "Bawaan": None,
    "60 FPS": 60,
    "30 FPS": 30,
    "24 FPS": 24,
}

ASPECT_RATIOS = {
    "Bawaan": None,
    "16:9 Landscape": "16:9",
    "9:16 Portrait": "9:16",
    "1:1 Square": "1:1",
    "4:3 Klasik": "4:3",
}

PLATFORM_PRESETS = {
    "Custom": {
        "crf": 28,
        "preset": "medium",
        "resolution": "720p",
        "max_bitrate": None,
        "fps": None,
        "aspect": None,
        "description": "Atur semua parameter secara manual.",
    },
    "WhatsApp": {
        "crf": 28,
        "preset": "medium",
        "resolution": "720p",
        "max_bitrate": "2M",
        "fps": 30,
        "aspect": None,
        "description": "Optimal untuk pengiriman via WhatsApp.",
    },
    "Instagram Feed": {
        "crf": 23,
        "preset": "slow",
        "resolution": "1080p",
        "max_bitrate": "3.5M",
        "fps": 30,
        "aspect": "1:1",
        "description": "Square format untuk feed Instagram.",
    },
    "Instagram Story": {
        "crf": 23,
        "preset": "slow",
        "resolution": "1080p",
        "max_bitrate": "4M",
        "fps": 30,
        "aspect": "9:16",
        "description": "Format vertikal untuk Story dan Reels.",
    },
    "Telegram": {
        "crf": 26,
        "preset": "medium",
        "resolution": "720p",
        "max_bitrate": None,
        "fps": None,
        "aspect": None,
        "description": "Kualitas dan ukuran seimbang untuk Telegram.",
    },
    "Email": {
        "crf": 32,
        "preset": "slow",
        "resolution": "480p",
        "max_bitrate": "1M",
        "fps": 24,
        "aspect": None,
        "description": "Ukuran file minimal untuk lampiran email.",
    },
}

COLOR_PROFILE = {
    "pix_fmt": "yuv420p",
    "colorspace": "bt709",
    "color_primaries": "bt709",
    "color_trc": "bt709",
    "color_range": "tv",
}

PAGE_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main .block-container {
        max-width: 780px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: rgba(14, 17, 23, 0.94);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .app-hero {
        text-align: center;
        padding: 2rem 0 1.5rem;
    }

    .app-hero .brand {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 40%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
    }

    .app-hero .tagline {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 400;
        margin: 0;
    }

    .app-hero .version-badge {
        display: inline-block;
        background: rgba(124, 58, 237, 0.15);
        color: #a78bfa;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        margin-top: 0.5rem;
        letter-spacing: 0.04em;
    }

    .preset-info {
        background: rgba(99, 102, 241, 0.08);
        border-left: 3px solid #7c3aed;
        padding: 0.7rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: #cbd5e1;
    }

    .result-panel {
        background: linear-gradient(145deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.03));
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 14px;
        padding: 1.4rem;
        margin: 1rem 0;
    }

    .result-panel h3 {
        color: #34d399;
        font-weight: 700;
        margin-bottom: 0.3rem;
        font-size: 1.15rem;
    }

    .result-panel .result-stats {
        color: #cbd5e1;
        font-size: 0.92rem;
    }

    .reduction-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-weight: 700;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }

    .section-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1.2rem 0 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }

    .footer-section {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #64748b;
        font-size: 0.82rem;
        border-top: 1px solid rgba(148, 163, 184, 0.08);
        margin-top: 3rem;
    }

    .footer-section a {
        color: #a78bfa;
        text-decoration: none;
        font-weight: 500;
    }

    .footer-section a:hover {
        text-decoration: underline;
    }

    div[data-testid="stFileUploader"] {
        border: 2px dashed rgba(124, 58, 237, 0.22);
        border-radius: 14px;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(124, 58, 237, 0.5);
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.01em;
        transition: all 0.25s ease;
        box-shadow: 0 4px 16px rgba(109, 40, 217, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(109, 40, 217, 0.45);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    div[data-testid="stDownloadButton"] > button {
        width: 100%;
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(5, 150, 105, 0.25);
    }

    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(5, 150, 105, 0.4);
    }

</style>
"""


def format_filesize(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    exp = min(int(math.log(size_bytes, 1024)), len(units) - 1)
    value = size_bytes / (1024 ** exp)
    return f"{value:.2f} {units[exp]}"


def format_duration(seconds):
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def calculate_reduction(original, compressed):
    if original == 0:
        return 0.0
    return ((original - compressed) / original) * 100


def get_clean_filename(uploaded_name):
    p = pathlib.Path(uploaded_name)
    return "kompres_" + p.stem + ".mp4"


def extract_frame(video_path, timestamp=1.0):
    """Ambil satu frame dari video dan kembalikan sebagai base64 JPEG."""
    try:
        out_path = video_path + "_thumb.jpg"
        _temp_files.append(out_path)
        (
            ffmpeg
            .input(video_path, ss=timestamp)
            .output(out_path, vframes=1, format="image2", **{"q:v": 2})
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        if os.path.exists(out_path):
            with open(out_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass
    return None


def probe_video(file_path):
    try:
        info = ffmpeg.probe(file_path, analyzeduration="5000000", probesize="5000000")
        video_stream = next(
            (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )
        audio_stream = next(
            (s for s in info.get("streams", []) if s.get("codec_type") == "audio"),
            None,
        )

        duration = float(info.get("format", {}).get("duration", 0))
        bitrate = int(info.get("format", {}).get("bit_rate", 0))

        result = {
            "duration": duration,
            "duration_text": format_duration(duration),
            "bitrate": bitrate,
            "bitrate_text": (str(bitrate // 1000) + " kbps") if bitrate else "N/A",
            "has_audio": audio_stream is not None,
        }

        if video_stream:
            fps_parts = video_stream.get("r_frame_rate", "0/1").split("/")
            if len(fps_parts) == 2 and int(fps_parts[1]) > 0:
                fps = round(int(fps_parts[0]) / int(fps_parts[1]), 1)
            else:
                fps = 0
            result["width"] = int(video_stream.get("width", 0))
            result["height"] = int(video_stream.get("height", 0))
            result["codec"] = video_stream.get("codec_name", "unknown").upper()
            result["fps"] = fps
            result["resolution_text"] = str(video_stream.get("width", 0)) + "x" + str(video_stream.get("height", 0))

        if audio_stream:
            result["audio_codec"] = audio_stream.get("codec_name", "unknown").upper()
            ab = audio_stream.get("bit_rate", 0)
            result["audio_bitrate"] = int(ab) // 1000 if ab else 0

        return result
    except Exception:
        return None


def compress_video(
    input_path,
    output_path,
    crf,
    preset,
    mute_audio,
    resolution,
    trim_start=None,
    trim_end=None,
    target_fps=None,
    aspect_ratio=None,
    max_bitrate=None,
    progress_callback=None,
    duration_seconds=0,
):
    try:
        input_args = {}
        if trim_start is not None and trim_start > 0:
            input_args["ss"] = trim_start
        if trim_end is not None and trim_end > 0:
            input_args["to"] = trim_end

        source = ffmpeg.input(input_path, **input_args)
        video = source.video
        audio = source.audio

        if resolution in RESOLUTION_MAP:
            target_h = RESOLUTION_MAP[resolution]
            video = ffmpeg.filter(video, "scale", "trunc(oh*a/2)*2", target_h)
        else:
            video = ffmpeg.filter(video, "scale", "trunc(iw/2)*2", "trunc(ih/2)*2")

        if aspect_ratio:
            ratio_map = {"16:9": "16/9", "9:16": "9/16", "1:1": "1", "4:3": "4/3"}
            if aspect_ratio in ratio_map:
                r = ratio_map[aspect_ratio]
                video = ffmpeg.filter(
                    video, "crop",
                    "if(gt(iw/ih," + r + "),ih*" + r + ",iw)",
                    "if(gt(iw/ih," + r + "),ih,iw/(" + r + "))",
                )
                video = ffmpeg.filter(video, "scale", "trunc(iw/2)*2", "trunc(ih/2)*2")

        if target_fps:
            video = ffmpeg.filter(video, "fps", fps=target_fps)

        encoding_params = {
            "vcodec": "libx264",
            "crf": crf,
            "preset": preset,
            "movflags": "+faststart",
            "profile:v": "high",
            "tune": "film",
            "threads": FFMPEG_THREADS,
        }
        encoding_params.update(COLOR_PROFILE)

        if max_bitrate:
            encoding_params["maxrate"] = max_bitrate
            encoding_params["bufsize"] = max_bitrate

        if mute_audio:
            output = ffmpeg.output(video, output_path, an=None, **encoding_params)
        else:
            audio_params = {"c:a": "aac", "b:a": "96k", "ac": 2}
            output = ffmpeg.output(audio, video, output_path, **audio_params, **encoding_params)

        cmd = ffmpeg.compile(output, overwrite_output=True)

        if progress_callback and duration_seconds > 0:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            stderr_lines = []

            if process.stderr is not None:
                for line in iter(process.stderr.readline, ""):
                    stderr_lines.append(line)
                    match = pattern.search(line)
                    if match:
                        h = float(match.group(1))
                        m = float(match.group(2))
                        s = float(match.group(3))
                        elapsed = h * 3600 + m * 60 + s
                        pct = min(elapsed / duration_seconds, 1.0)
                        progress_callback(pct)

            process.wait()
            if process.returncode != 0:
                tail = stderr_lines[-50:] if len(stderr_lines) > 50 else stderr_lines
                return False, "".join(tail)
        else:
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return True, None

    except ffmpeg.Error as err:
        error_detail = err.stderr.decode("utf-8") if err.stderr else "Proses encoding gagal"
        return False, error_detail


def save_upload_to_temp(uploaded_file, token):
    """Simpan file upload ke direktori sesi persisten dengan token unik."""
    os.makedirs(SESSION_DIR, exist_ok=True)
    cleanup_old_sessions()

    suffix = pathlib.Path(uploaded_file.name).suffix or ".mp4"
    session_id = str(int(time.time() * 1000))
    file_path = os.path.join(SESSION_DIR, session_id + suffix)
    meta_path = os.path.join(SESSION_DIR, session_id + ".json")

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    meta = {
        "original_name": uploaded_file.name,
        "file_path": file_path,
        "file_size": uploaded_file.size,
        "timestamp": time.time(),
        "session_id": session_id,
        "token": token,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f)

    _temp_files.append(file_path)
    _temp_files.append(meta_path)
    return file_path


def find_recent_session(token):
    """Cari sesi upload terakhir yang cocok dengan token browser ini."""
    if not os.path.isdir(SESSION_DIR):
        return None
    if not token:
        return None
    now = time.time()
    best = None
    for name in os.listdir(SESSION_DIR):
        if not name.endswith(".json"):
            continue
        meta_path = os.path.join(SESSION_DIR, name)
        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)
            if meta.get("token") != token:
                continue
            age = now - meta.get("timestamp", 0)
            if age > SESSION_MAX_AGE:
                continue
            if not os.path.exists(meta.get("file_path", "")):
                continue
            if best is None or meta["timestamp"] > best["timestamp"]:
                best = meta
        except (json.JSONDecodeError, OSError):
            continue
    return best


def cleanup_old_sessions():
    """Hapus file sesi yang lebih dari 1 jam."""
    if not os.path.isdir(SESSION_DIR):
        return
    now = time.time()
    for name in os.listdir(SESSION_DIR):
        full = os.path.join(SESSION_DIR, name)
        try:
            if now - os.path.getmtime(full) > SESSION_MAX_AGE:
                os.unlink(full)
        except OSError:
            pass


def cleanup_temp_files():
    for path in _temp_files:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except OSError:
            pass
    _temp_files.clear()


atexit.register(cleanup_temp_files)


@st.cache_data(show_spinner=False, ttl=600)
def load_file_bytes(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def render_header():
    st.markdown(PAGE_STYLES, unsafe_allow_html=True)
    st.markdown(
        '<div class="app-hero">'
        '<div class="brand">' + APP_TITLE + '</div>'
        '<p class="tagline">' + APP_TAGLINE + '</p>'
        '<span class="version-badge">v' + APP_VERSION + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_video_info(metadata):
    c1, c2, c3 = st.columns(3)
    c1.metric("Durasi", metadata.get("duration_text", "N/A"))
    c2.metric("Resolusi", metadata.get("resolution_text", "N/A"))
    c3.metric("Codec", metadata.get("codec", "N/A"))

    c4, c5, c6 = st.columns(3)
    c4.metric("FPS", str(metadata.get("fps", 0)))
    c5.metric("Bitrate", metadata.get("bitrate_text", "N/A"))
    c6.metric("Audio", metadata.get("audio_codec", "Tidak ada"))


def render_platform_presets():
    preset_name = st.selectbox(
        "Platform Target",
        list(PLATFORM_PRESETS.keys()),
        index=0,
        help="Pilih platform tujuan untuk mengatur parameter otomatis.",
    )
    preset = PLATFORM_PRESETS[preset_name]

    if preset_name != "Custom":
        st.markdown(
            '<div class="preset-info">' + preset["description"] + '</div>',
            unsafe_allow_html=True,
        )

    return {"name": preset_name, **preset}


def render_compression_controls(preset, video_metadata):
    is_custom = preset["name"] == "Custom"
    settings = {}

    st.markdown('<div class="section-title">Kompresi dan Kualitas</div>', unsafe_allow_html=True)

    if is_custom:
        settings["crf"] = st.slider(
            "Level Kompresi (CRF)",
            min_value=18,
            max_value=36,
            value=preset["crf"],
            help="Nilai lebih tinggi = file lebih kecil. 18-22 hampir lossless, 28-32 ukuran minimal.",
        )
        settings["preset"] = st.select_slider(
            "Kecepatan Encoding",
            options=SPEED_OPTIONS,
            value=preset["preset"],
            help="Encoding lambat menghasilkan kompresi lebih efisien.",
        )
        res_options = ["Resolusi Asli"] + list(RESOLUTION_MAP.keys())
        res_index = 0
        if preset["resolution"] in RESOLUTION_MAP:
            res_index = list(RESOLUTION_MAP.keys()).index(preset["resolution"]) + 1
        selected_res = st.selectbox("Resolusi Output", res_options, index=res_index)
        settings["resolution"] = "original" if selected_res == "Resolusi Asli" else selected_res
    else:
        settings["crf"] = preset["crf"]
        settings["preset"] = preset["preset"]
        settings["resolution"] = preset["resolution"]
        st.info(
            "CRF: " + str(preset["crf"]) + " | Preset: " + preset["preset"]
            + " | Resolusi: " + preset["resolution"]
        )

    settings["mute_audio"] = st.checkbox("Nonaktifkan Audio")

    return settings


def render_advanced_controls(preset, video_metadata):
    advanced = {}

    st.markdown('<div class="section-title">Pengaturan Lanjutan</div>', unsafe_allow_html=True)

    max_duration = video_metadata.get("duration", 600) if video_metadata else 600

    col_start, col_end = st.columns(2)
    with col_start:
        trim_start = st.number_input(
            "Potong mulai (detik)",
            min_value=0.0,
            max_value=float(max_duration),
            value=0.0,
            step=0.5,
            format="%.1f",
        )
    with col_end:
        trim_end = st.number_input(
            "Potong sampai (detik)",
            min_value=0.0,
            max_value=float(max_duration),
            value=0.0,
            step=0.5,
            format="%.1f",
            help="Isi 0 untuk memproses sampai akhir video.",
        )

    advanced["trim_start"] = trim_start if trim_start > 0 else None
    advanced["trim_end"] = trim_end if trim_end > 0 else None

    is_custom = preset["name"] == "Custom"

    col_fps, col_ratio = st.columns(2)
    with col_fps:
        if is_custom:
            fps_label = st.selectbox("Frame Rate", list(FRAMERATE_OPTIONS.keys()), index=0)
            advanced["target_fps"] = FRAMERATE_OPTIONS[fps_label]
        else:
            advanced["target_fps"] = preset.get("fps")
            fps_display = str(preset["fps"]) + " FPS" if preset.get("fps") else "Bawaan"
            st.text_input("Frame Rate", value=fps_display, disabled=True)

    with col_ratio:
        if is_custom:
            aspect_label = st.selectbox("Aspect Ratio", list(ASPECT_RATIOS.keys()), index=0)
            advanced["aspect_ratio"] = ASPECT_RATIOS[aspect_label]
        else:
            advanced["aspect_ratio"] = preset.get("aspect")
            aspect_display = preset.get("aspect") or "Bawaan"
            st.text_input("Aspect Ratio", value=aspect_display, disabled=True)

    advanced["max_bitrate"] = preset.get("max_bitrate")

    return advanced


def render_comparison_slider(input_path, output_path, duration):
    """Render before/after image comparison slider menggunakan iframe component."""
    import streamlit.components.v1 as components

    timestamp = min(duration * 0.3, 5.0) if duration > 0 else 1.0

    before_b64 = extract_frame(input_path, timestamp)
    after_b64 = extract_frame(output_path, timestamp)

    if not before_b64 or not after_b64:
        col_a, col_b = st.columns(2)
        with col_a:
            st.caption("ASLI")
            st.video(input_path)
        with col_b:
            st.caption("HASIL")
            st.video(output_path)
        return

    html_code = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: transparent; overflow: hidden; font-family: 'Inter', sans-serif; }
.wrap {
    position: relative;
    width: 100%;
    overflow: hidden;
    border-radius: 12px;
    cursor: col-resize;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
}
.wrap img.bg {
    display: block;
    width: 100%;
    height: auto;
}
.overlay {
    position: absolute;
    top: 0; left: 0;
    width: 50%;
    height: 100%;
    overflow: hidden;
}
.overlay img {
    position: absolute;
    top: 0;
    left: 0;
    display: block;
    height: 100%;
    max-width: none;
}
.line {
    position: absolute;
    top: 0; left: 50%;
    width: 3px;
    height: 100%;
    background: #fff;
    box-shadow: 0 0 6px rgba(0,0,0,0.6);
    z-index: 10;
    transform: translateX(-50%);
    pointer-events: none;
}
.handle {
    position: absolute;
    top: 50%; left: 50%;
    width: 38px; height: 38px;
    background: #fff;
    border-radius: 50%;
    z-index: 11;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.45);
    pointer-events: none;
}
.handle svg { width: 18px; height: 18px; }
.tag {
    position: absolute;
    top: 8px;
    padding: 3px 10px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    z-index: 12;
    text-transform: uppercase;
    pointer-events: none;
}
.tag-before { right: 8px; background: rgba(239,68,68,0.85); color: #fff; }
.tag-after { left: 8px; background: rgba(16,185,129,0.85); color: #fff; }
.hint {
    text-align: center;
    font-size: 12px;
    color: #94a3b8;
    padding: 8px 0 0;
}
</style>
</head>
<body>
<div class="wrap" id="wrap">
    <span class="tag tag-before">Asli</span>
    <span class="tag tag-after">Hasil</span>
    <img class="bg" id="bg" src="data:image/jpeg;base64,__BEFORE__" />
    <div class="overlay" id="overlay">
        <img id="afterImg" src="data:image/jpeg;base64,__AFTER__" />
    </div>
    <div class="line" id="line"></div>
    <div class="handle" id="handle">
        <svg viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2.5" stroke-linecap="round">
            <path d="M8 4l-6 8 6 8"/><path d="M16 4l6 8-6 8"/>
        </svg>
    </div>
</div>
<div class="hint">Geser ke kiri/kanan untuk membandingkan</div>
<script>
(function(){
    var wrap = document.getElementById('wrap');
    var overlay = document.getElementById('overlay');
    var afterImg = document.getElementById('afterImg');
    var line = document.getElementById('line');
    var handle = document.getElementById('handle');
    var bg = document.getElementById('bg');
    var dragging = false;

    function syncSize() {
        afterImg.style.width = wrap.offsetWidth + 'px';
    }

    function getPos(e) {
        var r = wrap.getBoundingClientRect();
        var cx = e.touches ? e.touches[0].clientX : e.clientX;
        var x = cx - r.left;
        return Math.max(0, Math.min(x / r.width * 100, 100));
    }

    function moveTo(pct) {
        overlay.style.width = pct + '%';
        line.style.left = pct + '%';
        handle.style.left = pct + '%';
    }

    function onStart(e) {
        dragging = true;
        moveTo(getPos(e));
        e.preventDefault();
    }
    function onMove(e) {
        if (!dragging) return;
        moveTo(getPos(e));
        e.preventDefault();
    }
    function onEnd() { dragging = false; }

    wrap.addEventListener('mousedown', onStart);
    wrap.addEventListener('mousemove', onMove);
    wrap.addEventListener('mouseup', onEnd);
    wrap.addEventListener('mouseleave', onEnd);
    wrap.addEventListener('touchstart', onStart, {passive:false});
    wrap.addEventListener('touchmove', onMove, {passive:false});
    wrap.addEventListener('touchend', onEnd);

    bg.onload = function() {
        syncSize();
        var h = bg.offsetHeight + 30;
        window.parent.postMessage({type:'streamlit:setFrameHeight', height: h}, '*');
    };
    window.addEventListener('resize', function() {
        syncSize();
        var h = bg.offsetHeight + 30;
        window.parent.postMessage({type:'streamlit:setFrameHeight', height: h}, '*');
    });
    setTimeout(function(){ syncSize(); }, 200);
})();
</script>
</body>
</html>"""

    html_final = html_code.replace("__BEFORE__", before_b64).replace("__AFTER__", after_b64)
    components.html(html_final, height=500, scrolling=False)


def render_before_after(input_path, output_path, original_size, uploaded_name, video_metadata):
    compressed_size = os.path.getsize(output_path)
    reduction = calculate_reduction(original_size, compressed_size)

    st.markdown(
        '<div class="result-panel">'
        '<h3>Kompresi Berhasil</h3>'
        '<div class="result-stats">'
        + format_filesize(original_size) + ' menjadi '
        '<strong>' + format_filesize(compressed_size) + '</strong>'
        ' &nbsp; '
        '<span class="reduction-badge">Hemat ' + f"{reduction:.1f}" + '%</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    duration = video_metadata.get("duration", 0) if video_metadata else 0
    render_comparison_slider(input_path, output_path, duration)

    st.markdown('<div class="section-title">Ukuran File</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Asli", format_filesize(original_size))
    col_s2.metric("Hasil", format_filesize(compressed_size), delta="-" + f"{reduction:.1f}" + "%", delta_color="normal")

    output_meta = probe_video(output_path)
    if video_metadata and output_meta:
        st.markdown('<div class="section-title">Detail Teknis</div>', unsafe_allow_html=True)
        col_h1, col_h2, col_h3 = st.columns(3)
        col_h1.write("**Parameter**")
        col_h2.write("**Asli**")
        col_h3.write("**Hasil**")

        params = [
            ("Resolusi", video_metadata.get("resolution_text", "-"), output_meta.get("resolution_text", "-")),
            ("Codec", video_metadata.get("codec", "-"), output_meta.get("codec", "-")),
            ("FPS", str(video_metadata.get("fps", "-")), str(output_meta.get("fps", "-"))),
            ("Bitrate", video_metadata.get("bitrate_text", "-"), output_meta.get("bitrate_text", "-")),
        ]
        for label, val_before, val_after in params:
            c1, c2, c3 = st.columns(3)
            c1.write(label)
            c2.write(val_before)
            c3.write(val_after)

    st.write("")

    st.video(output_path)

    download_name = get_clean_filename(uploaded_name)
    file_data = load_file_bytes(output_path)
    st.download_button(
        label="Download Hasil Kompresi",
        data=file_data,
        file_name=download_name,
        mime="video/mp4",
    )


def render_features():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Aman**")
        st.caption("Video tidak disimpan permanen di server.")
    with c2:
        st.markdown("**Tanpa Watermark**")
        st.caption("Hasil kompresi bersih tanpa tanda air.")
    with c3:
        st.markdown("**Gratis**")
        st.caption("Gunakan tanpa batas, tanpa biaya.")


def render_footer():
    st.markdown(
        '<div class="footer-section">'
        'Dibuat oleh <a href="#">Garden</a> &middot; ' + APP_TITLE + ' v' + APP_VERSION + '<br>'
        '<span style="font-size: 0.75rem; color: #475569;">'
        'Dilisensikan di bawah GNU General Public License v3.0'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title=APP_TITLE + " - " + APP_TAGLINE,
        page_icon="https://em-content.zobj.net/source/twitter/408/film-frames_1f39e-fe0f.png",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    render_header()
    render_features()
    st.divider()

    uploaded_file = st.file_uploader(
        "Pilih file video",
        type=SUPPORTED_FORMATS,
        help="Format: MP4, MOV, MKV, AVI, WebM. Maks 500MB.",
    )

    # --- Session token: unik per browser/tab ---
    params = st.query_params
    session_token = params.get("sid", "")
    if not session_token:
        session_token = uuid.uuid4().hex[:16]
        st.query_params["sid"] = session_token

    if uploaded_file is None:
        has_session = (
            "input_path" in st.session_state
            and os.path.exists(st.session_state["input_path"])
        )

        if has_session:
            input_path = st.session_state["input_path"]
            original_size = st.session_state["input_size"]
        else:
            recent = find_recent_session(session_token)
            if recent and os.path.exists(recent.get("file_path", "")):
                st.info("Kami menemukan sesi sebelumnya.")
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(
                        "**" + recent["original_name"] + "** ("
                        + format_filesize(recent["file_size"]) + ")"
                    )
                    age_min = int((time.time() - recent["timestamp"]) / 60)
                    st.caption(str(age_min) + " menit yang lalu")
                with col_btn:
                    if st.button("Lanjutkan", use_container_width=True):
                        st.session_state["input_path"] = recent["file_path"]
                        st.session_state["input_name"] = recent["original_name"]
                        st.session_state["input_size"] = recent["file_size"]
                        st.session_state["input_size_raw"] = recent["file_size"]
                        st.session_state.pop("video_metadata", None)
                        st.rerun()
            else:
                st.info("Upload video untuk memulai kompresi.")

            render_footer()
            return
    else:
        file_changed = (
            "input_name" not in st.session_state
            or st.session_state["input_name"] != uploaded_file.name
            or st.session_state.get("input_size_raw") != uploaded_file.size
        )

        if file_changed:
            with st.spinner("Menyimpan video..."):
                input_path = save_upload_to_temp(uploaded_file, session_token)
                original_size = os.path.getsize(input_path)

            st.session_state["input_path"] = input_path
            st.session_state["input_name"] = uploaded_file.name
            st.session_state["input_size"] = original_size
            st.session_state["input_size_raw"] = uploaded_file.size
            st.session_state.pop("video_metadata", None)
        else:
            input_path = st.session_state["input_path"]
            original_size = st.session_state["input_size"]

    uploaded_name = st.session_state.get("input_name", "video.mp4")

    st.success("File terpilih: **" + uploaded_name + "** (**" + format_filesize(original_size) + "**)")

    video_metadata = st.session_state.get("video_metadata")

    show_info = st.checkbox("Tampilkan info video", value=False)
    if show_info:
        if video_metadata is None:
            with st.spinner("Membaca metadata..."):
                video_metadata = probe_video(input_path)
                st.session_state["video_metadata"] = video_metadata
        if video_metadata:
            render_video_info(video_metadata)

    preset = render_platform_presets()
    settings = render_compression_controls(preset, video_metadata)

    show_advanced = st.checkbox("Tampilkan pengaturan lanjutan", value=False)
    if show_advanced:
        advanced = render_advanced_controls(preset, video_metadata)
    else:
        advanced = {
            "trim_start": None,
            "trim_end": None,
            "target_fps": preset.get("fps"),
            "aspect_ratio": preset.get("aspect"),
            "max_bitrate": preset.get("max_bitrate"),
        }

    st.write("")

    if st.button("Mulai Kompresi", use_container_width=True):
        output_path = input_path + "_out.mp4"
        _temp_files.append(output_path)

        if video_metadata is None:
            with st.spinner("Membaca metadata..."):
                video_metadata = probe_video(input_path)
                st.session_state["video_metadata"] = video_metadata

        total_duration = 0
        if video_metadata:
            total_duration = video_metadata.get("duration", 0)
            if advanced.get("trim_start") or advanced.get("trim_end"):
                start = advanced.get("trim_start") or 0
                end = advanced.get("trim_end") or total_duration
                total_duration = max(end - start, 0)

        progress_bar = st.progress(0, text="Mempersiapkan encoding...")

        def on_progress(pct):
            progress_bar.progress(
                min(int(pct * 100), 99),
                text="Encoding: " + str(int(pct * 100)) + "%",
            )

        success, error_msg = compress_video(
            input_path=input_path,
            output_path=output_path,
            crf=settings["crf"],
            preset=settings["preset"],
            mute_audio=settings["mute_audio"],
            resolution=settings["resolution"],
            trim_start=advanced.get("trim_start"),
            trim_end=advanced.get("trim_end"),
            target_fps=advanced.get("target_fps"),
            aspect_ratio=advanced.get("aspect_ratio"),
            max_bitrate=advanced.get("max_bitrate"),
            progress_callback=on_progress,
            duration_seconds=total_duration,
        )

        if success:
            progress_bar.progress(100, text="Selesai!")
            render_before_after(input_path, output_path, original_size, uploaded_name, video_metadata)
        else:
            progress_bar.empty()
            st.error("Terjadi kesalahan saat memproses video.")
            with st.container():
                st.code(error_msg, language="text")

    render_footer()


if __name__ == "__main__":
    main()