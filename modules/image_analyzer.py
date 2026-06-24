import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image, ExifTags
import base64
import io
import json

# ── Optional: piexif for richer GPS parsing ───────────────────────────────────
try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════════
# EXIF EXTRACTION
# ═════════════════════════════════════════════════════════════════════════════

def extract_exif_metadata(image_file):
    """
    Extract EXIF metadata from an uploaded image.
    Uses Pillow's ExifTags (always available) and piexif for GPS details.
    """
    image_file.seek(0)
    img = Image.open(image_file)

    # File size
    image_file.seek(0, 2)
    file_size_kb = round(image_file.seek(0, 2) / 1024, 2)
    image_file.seek(0)

    metadata = {
        "format":       img.format,
        "mode":         img.mode,
        "size":         f"{img.width} x {img.height} px",
        "exif":         {},
        "gps":          {},
        "file_size_kb": file_size_kb,
    }

    # ── Pillow EXIF ───────────────────────────────────────────────────────────
    if hasattr(img, "_getexif") and img._getexif():
        for tag_id, value in img._getexif().items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):
                continue
            metadata["exif"][tag_name] = str(value)

    # ── piexif GPS block ──────────────────────────────────────────────────────
    if PIEXIF_AVAILABLE:
        try:
            image_file.seek(0)
            exif_dict = piexif.load(image_file.read())
            gps_block = exif_dict.get("GPS", {})
            if gps_block:
                def _ratio(val):
                    return val[0] / val[1] if val[1] else 0

                lat_data = gps_block.get(piexif.GPSIFD.GPSLatitude)
                lon_data = gps_block.get(piexif.GPSIFD.GPSLongitude)
                lat_ref  = gps_block.get(piexif.GPSIFD.GPSLatitudeRef,  b"N").decode()
                lon_ref  = gps_block.get(piexif.GPSIFD.GPSLongitudeRef, b"E").decode()

                if lat_data and lon_data:
                    lat = _ratio(lat_data[0]) + _ratio(lat_data[1])/60 + _ratio(lat_data[2])/3600
                    lon = _ratio(lon_data[0]) + _ratio(lon_data[1])/60 + _ratio(lon_data[2])/3600
                    if lat_ref == "S": lat = -lat
                    if lon_ref == "W": lon = -lon
                    metadata["gps"]["latitude"]  = round(lat, 6)
                    metadata["gps"]["longitude"] = round(lon, 6)
                    metadata["gps"]["maps_link"]  = f"https://maps.google.com/?q={lat},{lon}"

                alt_data = gps_block.get(piexif.GPSIFD.GPSAltitude)
                if alt_data:
                    metadata["gps"]["altitude_m"] = round(_ratio(alt_data), 1)
        except Exception:
            pass

    return metadata


# ═════════════════════════════════════════════════════════════════════════════
# EXIF DISPLAY
# ═════════════════════════════════════════════════════════════════════════════

def _fmt_exif(key, value):
    """Convert raw EXIF values into human-readable strings."""
    try:
        if key == "ExposureTime":
            v = float(value)
            return f"1/{int(round(1/v))}s" if v < 1 else f"{v}s"
        if key == "FNumber":
            return f"f/{float(value):.1f}"
        if key == "FocalLength":
            return f"{float(value):.0f} mm"
        if key == "ISOSpeedRatings":
            return f"ISO {value}"
        if key == "Flash":
            return "On" if str(value) != "0" else "Off"
        if key == "WhiteBalance":
            return "Auto" if str(value) == "0" else "Manual"
        if key == "ExposureMode":
            return {"0": "Auto", "1": "Manual", "2": "Auto bracket"}.get(str(value), value)
        if key == "MeteringMode":
            modes = {"0":"Unknown","1":"Average","2":"Center-weighted","3":"Spot",
                     "4":"Multi-spot","5":"Multi-segment","6":"Partial"}
            return modes.get(str(value), value)
        if key == "Orientation":
            ori = {"1":"Normal","2":"Mirrored","3":"Rotated 180°","4":"Mirrored vertical",
                   "5":"Mirrored + rotated 90° CCW","6":"Rotated 90° CW",
                   "7":"Mirrored + rotated 90° CW","8":"Rotated 90° CCW"}
            return ori.get(str(value), value)
        if key in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
            parts = str(value).split(" ")
            d = parts[0].split(":")
            t = parts[1][:5] if len(parts) > 1 else ""
            months = ["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"]
            m = months[int(d[1]) - 1]
            return f"{m} {int(d[2])}, {d[0]}  ·  {t}"
    except Exception:
        pass
    return str(value)


def display_exif_metadata(metadata):
    """Render the extracted metadata in a clean, human-readable way."""
    st.subheader("📷 Image Metadata")

    # ── Top-level file stats ──────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Format",     metadata.get("format", "Unknown"))
    col2.metric("Mode",       metadata.get("mode",   "Unknown"))
    col3.metric("Dimensions", metadata.get("size",   "Unknown"))
    col4.metric("File Size",  f"{metadata.get('file_size_kb', 0)} KB")

    exif = metadata.get("exif", {})

    if exif:
        # ── Camera info ───────────────────────────────────────────────────────
        camera_map = {
            "Make":        ("🏭", "Manufacturer"),
            "Model":       ("📷", "Camera Model"),
            "LensModel":   ("🔭", "Lens"),
            "Software":    ("💾", "Software"),
        }
        camera_rows = [
            (icon, label, _fmt_exif(k, exif[k]))
            for k, (icon, label) in camera_map.items() if k in exif
        ]
        if camera_rows:
            st.markdown("**Camera**")
            cols = st.columns(len(camera_rows))
            for col, (icon, label, val) in zip(cols, camera_rows):
                col.metric(f"{icon} {label}", val)

        st.markdown("")

        # ── Exposure settings ─────────────────────────────────────────────────
        exposure_map = {
            "ExposureTime":    ("⏱", "Shutter Speed"),
            "FNumber":         ("🔆", "Aperture"),
            "ISOSpeedRatings": ("🎞", "ISO"),
            "FocalLength":     ("🔭", "Focal Length"),
            "Flash":           ("⚡", "Flash"),
            "WhiteBalance":    ("🌡", "White Balance"),
            "ExposureMode":    ("📊", "Exposure Mode"),
            "MeteringMode":    ("🎯", "Metering Mode"),
        }
        exposure_rows = [
            (icon, label, _fmt_exif(k, exif[k]))
            for k, (icon, label) in exposure_map.items() if k in exif
        ]
        if exposure_rows:
            st.markdown("**Exposure Settings**")
            # Render in rows of 4
            for i in range(0, len(exposure_rows), 4):
                chunk = exposure_rows[i:i+4]
                cols  = st.columns(4)
                for col, (icon, label, val) in zip(cols, chunk):
                    col.metric(f"{icon} {label}", val)

        st.markdown("")

        # ── Date / time ───────────────────────────────────────────────────────
        date_map = {
            "DateTimeOriginal":  ("📸", "Shot On"),
            "DateTime":          ("🗂", "File Date"),
            "DateTimeDigitized": ("💽", "Digitized"),
        }
        date_rows = [
            (icon, label, _fmt_exif(k, exif[k]))
            for k, (icon, label) in date_map.items() if k in exif
        ]
        if date_rows:
            st.markdown("**Date & Time**")
            cols = st.columns(len(date_rows))
            for col, (icon, label, val) in zip(cols, date_rows):
                col.metric(f"{icon} {label}", val)

        # ── Remaining tags collapsed ──────────────────────────────────────────
        shown_keys = set(camera_map) | set(exposure_map) | set(date_map)
        other = {k: v for k, v in exif.items() if k not in shown_keys}
        if other:
            with st.expander("🔍 All other EXIF tags"):
                for k, v in other.items():
                    st.markdown(f"`{k}` — {v}")
    else:
        st.info("No EXIF data found in this image.")

    # ── GPS block ─────────────────────────────────────────────────────────────
    gps = metadata.get("gps", {})
    if gps:
        st.markdown("")
        st.markdown("**📍 GPS Location**")
        lat = gps.get("latitude")
        lon = gps.get("longitude")
        gcols = st.columns(3)
        if lat and lon:
            gcols[0].metric("🌐 Latitude",  lat)
            gcols[1].metric("🌐 Longitude", lon)
        if "altitude_m" in gps:
            gcols[2].metric("⛰ Altitude", f"{gps['altitude_m']} m")
        if "maps_link" in gps:
            st.markdown(f"[📍 Open in Google Maps]({gps['maps_link']})")


# ═════════════════════════════════════════════════════════════════════════════
# AI ANALYSIS DISPLAY
# ═════════════════════════════════════════════════════════════════════════════

def display_analysis_results(analysis_result):
    """Render AI analysis in a clean, human-readable layout."""

    # ── Description ───────────────────────────────────────────────────────────
    description = analysis_result.get("description", "").strip()
    if description:
        st.markdown("### 📝 Description")
        st.markdown(
            f"""<div style="
                background: #f8f9fa;
                border-left: 4px solid #4A90D9;
                border-radius: 6px;
                padding: 14px 18px;
                font-size: 0.97rem;
                line-height: 1.7;
                color: #222;
            ">{description}</div>""",
            unsafe_allow_html=True,
        )
        st.markdown("")

    # ── Objects identified ────────────────────────────────────────────────────
    objects = [o for o in analysis_result.get("objects_identified", []) if o]
    if objects:
        st.markdown("### 🎯 Objects Identified")
        badges = "".join(
            f'<span style="display:inline-block; background:#E8F0FE; color:#1a4fa0;'
            f'border-radius:20px; padding:3px 12px; margin:3px 4px 3px 0;'
            f'font-size:0.88rem; font-weight:500;">{obj}</span>'
            for obj in objects
        )
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown("")

    # ── Text found in image ───────────────────────────────────────────────────
    text_content = analysis_result.get("text_content", "").strip()
    if text_content:
        st.markdown("### 📜 Text in Image")
        st.code(text_content, language=None)

    # ── Notable features ─────────────────────────────────────────────────────
    features = [f for f in analysis_result.get("notable_features", []) if f]
    if features:
        st.markdown("### ✨ Notable Features")
        for feat in features:
            st.markdown(
                f"""<div style="
                    display:flex; align-items:flex-start; gap:8px;
                    margin-bottom:6px; font-size:0.95rem; line-height:1.6;
                ">
                    <span style="color:#f5a623; margin-top:2px;">◆</span>
                    <span>{feat}</span>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("")

    # ── Context ───────────────────────────────────────────────────────────────
    context = analysis_result.get("context", "").strip()
    if context:
        st.markdown("### 🌍 Context")
        st.markdown(
            f"""<div style="
                background: #f0fdf4;
                border-left: 4px solid #34a853;
                border-radius: 6px;
                padding: 14px 18px;
                font-size: 0.95rem;
                line-height: 1.7;
                color: #1a3a2a;
            ">{context}</div>""",
            unsafe_allow_html=True,
        )


# ═════════════════════════════════════════════════════════════════════════════
# IMAGE ENCODING
# ═════════════════════════════════════════════════════════════════════════════

def encode_image(image_file):
    """Convert uploaded image to base64 string."""
    image_file.seek(0)
    img = Image.open(image_file)
    buffered = io.BytesIO()
    img.save(buffered, format=img.format or "JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


# ═════════════════════════════════════════════════════════════════════════════
# AI BACKENDS
# ═════════════════════════════════════════════════════════════════════════════

ANALYSIS_PROMPT = """Analyze this image and provide:
1. A detailed description
2. Key objects and elements identified
3. Any text visible in the image
4. Notable features or patterns
5. Potential context or setting

Respond ONLY with a valid JSON object using exactly these keys:
{
    "description": "A thorough, human-readable description of the image",
    "objects_identified": ["object1", "object2", "..."],
    "text_content": "Any text found in the image, or empty string if none",
    "notable_features": ["feature1", "feature2", "..."],
    "context": "The likely setting, purpose, or broader context of this image"
}
Do not include markdown fences or any text outside the JSON object."""


def _parse_json_response(raw_text):
    """Safely parse a JSON response, stripping markdown fences if present."""
    text = raw_text.strip()
    # Strip ```json ... ``` fences
    if "```" in text:
        text = text.split("```json")[-1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "description": raw_text,
            "objects_identified": [],
            "text_content": "",
            "notable_features": [],
            "context": "",
        }


def analyze_image_groq(image_file, model_name):
    """Analyze image using Groq vision models."""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        base64_image = encode_image(image_file)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": ANALYSIS_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=2000,
            temperature=0.2,
        )
        return _parse_json_response(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error analyzing image with Groq: {e}")
        return {"error": str(e), "status": "failed"}


def analyze_image_gemini(image_file):
    """Analyze image using Google Gemini."""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="models/gemini-3.1-flash-lite",
            generation_config={
                "temperature": 0.2,
                "top_p":       0.95,
                "top_k":       40,
                "max_output_tokens": 8192,
            },
        )
        image_file.seek(0)
        img = Image.open(image_file)
        response = model.generate_content([ANALYSIS_PROMPT, img])
        return _parse_json_response(response.text)

    except Exception as e:
        st.error(f"Error analyzing image with Gemini: {e}")
        return {"error": str(e), "status": "failed"}


# ═════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ═════════════════════════════════════════════════════════════════════════════

def image_analyzer_main():
    """Main function for the image analysis page."""

    model_options = {
        "Llama 4 Maverick (Groq)": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "Llama 4 Scout (Groq)":    "meta-llama/llama-4-scout-17b-16e-instruct",
        "Google Gemini Flash":     "gemini-3.1-flash-lite",
    }

    selected_model = st.selectbox("Choose an AI Model", list(model_options.keys()))

    uploaded_file = st.file_uploader(
        "Upload an image for analysis",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:

        # ── Preview ───────────────────────────────────────────────────────────
        uploaded_file.seek(0)
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=False, width=480)

        st.divider()

        # ── EXIF metadata ─────────────────────────────────────────────────────
        uploaded_file.seek(0)
        metadata = extract_exif_metadata(uploaded_file)
        display_exif_metadata(metadata)

        st.divider()

        # ── AI analysis ───────────────────────────────────────────────────────
        st.subheader("🤖 AI Analysis")
        with st.spinner("Analyzing image…"):
            uploaded_file.seek(0)
            if selected_model.startswith("Google"):
                analysis_result = analyze_image_gemini(uploaded_file)
            else:
                analysis_result = analyze_image_groq(
                    uploaded_file, model_options[selected_model]
                )

        if "error" in analysis_result:
            st.error("Analysis failed. Please try again.")
        else:
            display_analysis_results(analysis_result)


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    st.set_page_config(
        page_title="Multi-Model Image Analyzer",
        page_icon="🖼️",
        layout="wide",
    )
    st.title("🖼️ Multi-Model Image Analyzer")
    st.caption("Upload an image to extract EXIF metadata and get an AI-powered analysis.")
    st.divider()
    image_analyzer_main()
