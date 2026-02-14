"""
VidPress — Professional video compression and optimization toolkit.

Supports WhatsApp, Instagram, Telegram, and general social media platforms.
Features color-accurate encoding with BT.709 HD, H.264 High Profile,
video trimming, frame rate control, and platform-specific presets.

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
import shutil


APP_VERSION = "5.1.0"

FFMPEG_THREADS = 0

_temp_files = []
APP_TITLE = "VidPress"
APP_TAGLINE = "Kompresi & Optimasi Video Profesional"

SUPPORTED_FORMATS = ["mp4", "mov", "mkv", "avi", "webm"]

RESOLUTION_MAP = {
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
}

SPEED_OPTIONS = ["ultrafast", "fast", "medium", "slow", "veryslow"]

FRAMERATE_OPTIONS = {
    "Bawaan (Tidak diubah)": None,
    "60 FPS": 60,
    "30 FPS": 30,
    "24 FPS (Sinematik)": 24,
}

ASPECT_RATIOS = {
    "Bawaan (Tidak diubah)": None,
    "16:9 (Landscape)": "16:9",
    "9:16 (Portrait/Story)": "9:16",
    "1:1 (Square)": "1:1",
    "4:3 (Klasik)": "4:3",
}

PLATFORM_PRESETS = {
    "Custom (Manual)": {
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
        "description": "Optimal untuk pengiriman via WhatsApp. Ukuran kecil, kualitas tetap bagus.",
    },
    "Instagram Feed": {
        "crf": 23,
        "preset": "slow",
        "resolution": "1080p",
        "max_bitrate": "3.5M",
        "fps": 30,
        "aspect": "1:1",
        "description": "Square format untuk feed Instagram. Kualitas tinggi.",
    },
    "Instagram Story/Reels": {
        "crf": 23,
        "preset": "slow",
        "resolution": "1080p",
        "max_bitrate": "4M",
        "fps": 30,
        "aspect": "9:16",
        "description": "Format vertikal penuh untuk Story dan Reels.",
    },
    "Telegram": {
        "crf": 26,
        "preset": "medium",
        "resolution": "720p",
        "max_bitrate": None,
        "fps": None,
        "aspect": None,
        "description": "Pengiriman via Telegram dengan kualitas dan ukuran seimbang.",
    },
    "Email / Ukuran Minimal": {
        "crf": 32,
        "preset": "slow",
        "resolution": "480p",
        "max_bitrate": "1M",
        "fps": 24,
        "aspect": None,
        "description": "Ukuran file sekecil mungkin untuk lampiran email.",
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

    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.6rem;
        margin: 0.8rem 0;
    }

    .info-tile {
        background: linear-gradient(145deg, rgba(124, 58, 237, 0.07), rgba(99, 102, 241, 0.03));
        border: 1px solid rgba(124, 58, 237, 0.15);
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }

    .info-tile .tile-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 0.15rem;
    }

    .info-tile .tile-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e2e8f0;
    }

    .file-card {
        background: linear-gradient(145deg, rgba(124, 58, 237, 0.08), rgba(99, 102, 241, 0.03));
        border: 1px solid rgba(124, 58, 237, 0.18);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }

    .file-card .file-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        word-break: break-all;
    }

    .file-card .file-size {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.2rem;
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

    .result-panel .reduction-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-weight: 700;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
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

    div[data-testid="stExpander"] {
        border: 1px solid rgba(124, 58, 237, 0.12);
        border-radius: 12px;
        overflow: hidden;
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

    .tab-section-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        font-weight: 600;
        margin: 1rem 0 0.4rem;
    }
</style>
"""


def format_filesize(size_bytes: int) -> str:
    """Mengubah ukuran byte menjadi format yang mudah dibaca."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    exp = min(int(math.log(size_bytes, 1024)), len(units) - 1)
    value = size_bytes / (1024 ** exp)
    return f"{value:.2f} {units[exp]}"


def format_duration(seconds: float) -> str:
    """Mengubah durasi detik menjadi format mm:ss atau hh:mm:ss."""
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def calculate_reduction(original: int, compressed: int) -> float:
    """Menghitung persentase pengurangan ukuran file."""
    if original == 0:
        return 0.0
    return ((original - compressed) / original) * 100


@st.cache_data(show_spinner=False, ttl=300)
def probe_video(file_path: str) -> dict | None:
    """Mendapatkan metadata video menggunakan ffprobe. Hasil di-cache selama 5 menit."""
    try:
        info = ffmpeg.probe(file_path)
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
            "bitrate_text": f"{bitrate // 1000} kbps" if bitrate else "N/A",
            "has_audio": audio_stream is not None,
        }

        if video_stream:
            fps_parts = video_stream.get("r_frame_rate", "0/1").split("/")
            fps = round(int(fps_parts[0]) / max(int(fps_parts[1]), 1), 1) if len(fps_parts) == 2 else 0

            result.update({
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "codec": video_stream.get("codec_name", "unknown").upper(),
                "fps": fps,
                "resolution_text": f"{video_stream.get('width')}×{video_stream.get('height')}",
            })

        if audio_stream:
            result["audio_codec"] = audio_stream.get("codec_name", "unknown").upper()
            result["audio_bitrate"] = int(audio_stream.get("bit_rate", 0)) // 1000

        return result

    except Exception:
        return None


def build_scale_filter(resolution: str, target_height: int) -> tuple[str, int | str]:
    """Membuat parameter scale filter berdasarkan resolusi target."""
    if resolution == "original":
        return ("trunc(iw/2)*2", "trunc(ih/2)*2")
    return ("trunc(oh*a/2)*2", target_height)


def compress_video(
    input_path: str,
    output_path: str,
    crf: int,
    preset: str,
    mute_audio: bool,
    resolution: str,
    trim_start: float | None = None,
    trim_end: float | None = None,
    target_fps: int | None = None,
    aspect_ratio: str | None = None,
    max_bitrate: str | None = None,
    progress_callback=None,
    duration_seconds: float = 0,
) -> tuple[bool, str | None]:
    """
    Menjalankan proses kompresi dan optimasi video.

    Menggunakan H.264 High Profile dengan kalibrasi warna BT.709.
    Mendukung trimming, perubahan FPS, crop aspect ratio, bitrate limiting,
    dan multi-threaded encoding untuk performa optimal.

    Returns:
        Tuple berisi status sukses (bool) dan pesan error jika gagal.
    """
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
            ratio_map = {
                "16:9": "16/9",
                "9:16": "9/16",
                "1:1": "1",
                "4:3": "4/3",
            }
            if aspect_ratio in ratio_map:
                video = ffmpeg.filter(
                    video, "crop",
                    f"if(gt(iw/ih,{ratio_map[aspect_ratio]}),ih*{ratio_map[aspect_ratio]},iw)",
                    f"if(gt(iw/ih,{ratio_map[aspect_ratio]}),ih,iw/({ratio_map[aspect_ratio]}))",
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
            **COLOR_PROFILE,
        }

        if max_bitrate:
            encoding_params["maxrate"] = max_bitrate
            encoding_params["bufsize"] = max_bitrate

        if mute_audio:
            output = ffmpeg.output(video, output_path, **encoding_params, an=None)
        else:
            audio_params = {"c:a": "aac", "b:a": "96k", "ac": 2}
            output = ffmpeg.output(
                audio, video, output_path, **audio_params, **encoding_params
            )

        cmd = ffmpeg.compile(output, overwrite_output=True)

        if progress_callback and duration_seconds > 0:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            stderr_output: list[str] = []

            if process.stderr is not None:
                for line in iter(process.stderr.readline, ""):
                    stderr_output.append(line)
                    match = pattern.search(line)
                    if match:
                        h, m, s = float(match.group(1)), float(match.group(2)), float(match.group(3))
                        elapsed = h * 3600 + m * 60 + s
                        pct = min(elapsed / duration_seconds, 1.0)
                        progress_callback(pct)

            process.wait()
            if process.returncode != 0:
                tail = stderr_output[-50:] if len(stderr_output) > 50 else stderr_output
                return False, "".join(tail)
        else:
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return True, None

    except ffmpeg.Error as err:
        error_detail = err.stderr.decode("utf-8") if err.stderr else "Proses encoding gagal"
        return False, error_detail


def save_upload_to_temp(uploaded_file) -> str:
    """Menyimpan file upload ke lokasi sementara. Dipanggil hanya sekali per file."""
    suffix = pathlib.Path(uploaded_file.name).suffix or ".mp4"
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    _temp_files.append(temp.name)
    temp.write(uploaded_file.getbuffer())
    temp.close()
    return temp.name


def cleanup_temp_files():
    """Menghapus semua file sementara yang dibuat selama sesi."""
    for path in _temp_files:
        try:
            if os.path.exists(path):
                os.unlink(path)
            compressed = path + "_compressed.mp4"
            if os.path.exists(compressed):
                os.unlink(compressed)
        except OSError:
            pass
    _temp_files.clear()


atexit.register(cleanup_temp_files)


@st.cache_data(show_spinner=False, ttl=600)
def load_file_bytes(file_path: str) -> bytes:
    """Membaca file dan meng-cache hasilnya untuk download yang lebih cepat."""
    with open(file_path, "rb") as f:
        return f.read()


def render_header():
    """Menampilkan header dan branding aplikasi."""
    st.markdown(PAGE_STYLES, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="app-hero">
            <div class="brand">{APP_TITLE}</div>
            <p class="tagline">{APP_TAGLINE}</p>
            <span class="version-badge">v{APP_VERSION}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_video_info(metadata: dict):
    """Menampilkan informasi metadata video dalam grid."""
    cols = []
    cols.append({"label": "Durasi", "value": metadata.get("duration_text", "N/A")})
    cols.append({"label": "Resolusi", "value": metadata.get("resolution_text", "N/A")})
    cols.append({"label": "Codec", "value": metadata.get("codec", "N/A")})
    cols.append({"label": "Frame Rate", "value": f"{metadata.get('fps', 0)} FPS"})
    cols.append({"label": "Bitrate", "value": metadata.get("bitrate_text", "N/A")})
    cols.append({"label": "Audio", "value": metadata.get("audio_codec", "Tidak ada")})

    tiles_html = ""
    for col in cols:
        tiles_html += f"""
            <div class="info-tile">
                <div class="tile-label">{col['label']}</div>
                <div class="tile-value">{col['value']}</div>
            </div>
        """

    st.markdown(f'<div class="info-grid">{tiles_html}</div>', unsafe_allow_html=True)


def render_platform_presets() -> dict:
    """Menampilkan pemilihan platform preset."""
    preset_name = st.selectbox(
        "Platform Target",
        list(PLATFORM_PRESETS.keys()),
        index=0,
        help="Pilih platform tujuan untuk mengatur parameter secara otomatis.",
    )

    preset = PLATFORM_PRESETS[preset_name]

    if preset_name != "Custom (Manual)":
        st.markdown(
            f'<div class="preset-info">{preset["description"]}</div>',
            unsafe_allow_html=True,
        )

    return {"name": preset_name, **preset}


def render_compression_controls(preset: dict, video_metadata: dict | None) -> dict:
    """Menampilkan kontrol pengaturan kompresi."""
    is_custom = preset["name"] == "Custom (Manual)"
    settings = {}

    with st.expander("Kompresi & Kualitas", expanded=True):
        if is_custom:
            settings["crf"] = st.slider(
                "Level Kompresi (CRF)",
                min_value=18,
                max_value=36,
                value=preset["crf"],
                help="Nilai lebih tinggi = file lebih kecil, kualitas sedikit berkurang. 18-22 hampir lossless, 28-32 untuk ukuran minimal.",
            )
            settings["preset"] = st.select_slider(
                "Kecepatan Encoding",
                options=SPEED_OPTIONS,
                value=preset["preset"],
                help="Encoding lebih lambat menghasilkan kompresi lebih efisien dengan kualitas yang sama.",
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
                f"CRF: {preset['crf']} · Preset: {preset['preset']} · "
                f"Resolusi: {preset['resolution']}",
            )

        settings["mute_audio"] = st.checkbox("Nonaktifkan Audio")

    return settings


def render_advanced_controls(preset: dict, video_metadata: dict | None) -> dict:
    """Menampilkan kontrol lanjutan: trimming, FPS, aspect ratio."""
    advanced = {}

    with st.expander("Pengaturan Lanjutan"):
        st.markdown('<div class="tab-section-title">Potong Video</div>', unsafe_allow_html=True)

        max_duration = video_metadata.get("duration", 600) if video_metadata else 600

        col_start, col_end = st.columns(2)
        with col_start:
            trim_start = st.number_input(
                "Mulai dari (detik)",
                min_value=0.0,
                max_value=max_duration,
                value=0.0,
                step=0.5,
                format="%.1f",
            )
        with col_end:
            trim_end = st.number_input(
                "Sampai (detik)",
                min_value=0.0,
                max_value=max_duration,
                value=0.0,
                step=0.5,
                format="%.1f",
                help="Isi 0 untuk memproses sampai akhir video.",
            )

        advanced["trim_start"] = trim_start if trim_start > 0 else None
        advanced["trim_end"] = trim_end if trim_end > 0 else None

        st.markdown('<div class="tab-section-title">Frame Rate & Rasio</div>', unsafe_allow_html=True)

        col_fps, col_ratio = st.columns(2)

        is_custom = preset["name"] == "Custom (Manual)"

        with col_fps:
            if is_custom:
                fps_label = st.selectbox("Frame Rate", list(FRAMERATE_OPTIONS.keys()), index=0)
                advanced["target_fps"] = FRAMERATE_OPTIONS[fps_label]
            else:
                advanced["target_fps"] = preset.get("fps")
                fps_display = f"{preset['fps']} FPS" if preset.get("fps") else "Bawaan"
                st.text_input("Frame Rate", value=fps_display, disabled=True)

        with col_ratio:
            if is_custom:
                aspect_label = st.selectbox("Aspect Ratio", list(ASPECT_RATIOS.keys()), index=0)
                advanced["aspect_ratio"] = ASPECT_RATIOS[aspect_label]
            else:
                advanced["aspect_ratio"] = preset.get("aspect")
                aspect_display = preset.get("aspect", "Bawaan") or "Bawaan"
                st.text_input("Aspect Ratio", value=aspect_display, disabled=True)

        advanced["max_bitrate"] = preset.get("max_bitrate")

    return advanced


def render_result(output_path: str, original_size: int):
    """Menampilkan hasil kompresi beserta statistik."""
    compressed_size = os.path.getsize(output_path)
    reduction = calculate_reduction(original_size, compressed_size)

    st.markdown(
        f"""
        <div class="result-panel">
            <h3>Kompresi Berhasil</h3>
            <div class="result-stats">
                {format_filesize(original_size)} → <strong>{format_filesize(compressed_size)}</strong>
                &nbsp;&nbsp;
                <span class="reduction-badge">-{reduction:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.video(output_path)

    file_data = load_file_bytes(output_path)
    stem = pathlib.Path(output_path).stem.replace("_compressed", "")
    output_name = f"vidpress_{stem}.mp4"
    st.download_button(
        label="Download Hasil",
        data=file_data,
        file_name=output_name,
        mime="video/mp4",
    )


def render_footer():
    """Menampilkan footer kredit dan lisensi."""
    st.markdown(
        f"""
        <div class="footer-section">
            Dibuat oleh <a href="#">Garden</a> &middot; VidPress v{APP_VERSION}<br>
            <span style="font-size: 0.75rem; color: #475569;">
                Dilisensikan di bawah GNU General Public License v3.0
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title=f"{APP_TITLE} — {APP_TAGLINE}",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    render_header()

    uploaded_file = st.file_uploader(
        "Pilih file video",
        type=SUPPORTED_FORMATS,
        help="Format yang didukung: MP4, MOV, MKV, AVI, WebM — Maks 500MB",
    )

    if uploaded_file is None:
        if "input_path" in st.session_state:
            del st.session_state["input_path"]
            del st.session_state["input_name"]
            del st.session_state["input_size"]
            if "video_metadata" in st.session_state:
                del st.session_state["video_metadata"]

        st.markdown(
            """
            <div style="text-align: center; padding: 2.5rem 0; color: #64748b;">
                <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎬</p>
                <p style="font-size: 0.92rem; margin: 0;">
                    Drop video di atas atau klik untuk memilih file.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_footer()
        return

    file_changed = (
        "input_name" not in st.session_state
        or st.session_state["input_name"] != uploaded_file.name
        or st.session_state.get("input_size_raw") != uploaded_file.size
    )

    if file_changed:
        input_path = save_upload_to_temp(uploaded_file)
        original_size = os.path.getsize(input_path)
        video_metadata = probe_video(input_path)

        st.session_state["input_path"] = input_path
        st.session_state["input_name"] = uploaded_file.name
        st.session_state["input_size"] = original_size
        st.session_state["input_size_raw"] = uploaded_file.size
        st.session_state["video_metadata"] = video_metadata
    else:
        input_path = st.session_state["input_path"]
        original_size = st.session_state["input_size"]
        video_metadata = st.session_state.get("video_metadata")

    st.markdown(
        f"""
        <div class="file-card">
            <div class="file-name">{uploaded_file.name}</div>
            <div class="file-size">{format_filesize(original_size)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if video_metadata:
        render_video_info(video_metadata)

    preset = render_platform_presets()
    settings = render_compression_controls(preset, video_metadata)
    advanced = render_advanced_controls(preset, video_metadata)

    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)

    if st.button("Mulai Kompresi", use_container_width=True):
        output_path = input_path + "_compressed.mp4"
        _temp_files.append(output_path)

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
                text=f"Encoding: {int(pct * 100)}%",
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
            render_result(output_path, original_size)
        else:
            progress_bar.empty()
            st.error("Terjadi kesalahan saat memproses video.")
            with st.expander("Detail Error"):
                st.code(error_msg, language="text")

    render_footer()


if __name__ == "__main__":
    main()