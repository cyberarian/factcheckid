import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image, ExifTags
import base64
import io
import json
import os

# ── NEW: optional piexif for richer GPS / maker-note parsing ──────────────────
try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False
# ─────────────────────────────────────────────────────────────────────────────


def extract_exif_metadata(image_file):
    """
    Extract EXIF metadata from an uploaded image.
    Uses Pillow's ExifTags (always available) and piexif for GPS details.
    """
    image_file.seek(0)
    img = Image.open(image_file)
    metadata = {
        "format":       img.format,
        "mode":         img.mode,
        "size":         f"{img.width} x {img.height} px",
        "exif":         {},
        "gps":          {},
        "file_size_kb": round(image_file.seek(0, 2) / 1024, 2),
    }
    image_file.seek(0)

    # ── Pillow EXIF (works for JPEG & TIFF) ───────────────────────────────────
    raw_exif = None
    if hasattr(img, "_getexif") and img._getexif():
        raw_exif = img._getexif()
        for tag_id, value in raw_exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):        # skip raw binary blobs
                continue
            metadata["exif"][tag_name] = str(value)

    # ── piexif GPS block (optional, richer than Pillow alone) ────────────────
    if PIEXIF_AVAILABLE:
        try:
            image_file.seek(0)
            exif_dict = piexif.load(image_file.read())
            gps_block = exif_dict.get("GPS", {})
            if gps_block:
                def _ratio(val):           # convert IFDRational tuples → float
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
                    metadata["gps"]["maps_link"]  = (
                        f"https://maps.google.com/?q={lat},{lon}"
                    )

                alt_data = gps_block.get(piexif.GPSIFD.GPSAltitude)
                if alt_data:
                    metadata["gps"]["altitude_m"] = round(_ratio(alt_data), 1)
        except Exception:
            pass    # image has no piexif-parseable EXIF — silently continue

    return metadata


def display_exif_metadata(metadata):
    """Render the extracted metadata in the Streamlit UI."""
    st.subheader("📷 Image Metadata")

    col1, col2, col3 = st.columns(3)
    col1.metric("Format",    metadata.get("format", "Unknown"))
    col2.metric("Dimensions", metadata.get("size",   "Unknown"))
    col3.metric("File Size",  f"{metadata.get('file_size_kb', 0)} KB")

    exif = metadata.get("exif", {})
    if exif:
        # ── Camera / capture info ─────────────────────────────────────────
        camera_fields = ["Make", "Model", "LensModel", "Software"]
        camera_info   = {k: exif[k] for k in camera_fields if k in exif}
        if camera_info:
            st.markdown("**📸 Camera Info**")
            st.table(camera_info)

        # ── Exposure settings ─────────────────────────────────────────────
        exposure_fields = [
            "ExposureTime", "FNumber", "ISOSpeedRatings",
            "FocalLength", "Flash", "WhiteBalance", "ExposureMode"
        ]
        exposure_info = {k: exif[k] for k in exposure_fields if k in exif}
        if exposure_info:
            st.markdown("**⚙️ Exposure Settings**")
            st.table(exposure_info)

        # ── Date / time ───────────────────────────────────────────────────
        date_fields = ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]
        date_info   = {k: exif[k] for k in date_fields if k in exif}
        if date_info:
            st.markdown("**🕒 Date & Time**")
            st.table(date_info)

        # ── Everything else ───────────────────────────────────────────────
        shown = set(camera_fields + exposure_fields + date_fields)
        other = {k: v for k, v in exif.items() if k not in shown}
        if other:
            with st.expander("🔍 All other EXIF tags"):
                st.json(other)
    else:
        st.info("No EXIF data found in this image.")

    # ── GPS block ─────────────────────────────────────────────────────────────
    gps = metadata.get("gps", {})
    if gps:
        st.markdown("**🌍 GPS Location**")
        st.write(f"Latitude: `{gps.get('latitude')}`  |  "
                 f"Longitude: `{gps.get('longitude')}`")
        if "altitude_m" in gps:
            st.write(f"Altitude: `{gps['altitude_m']} m`")
        if "maps_link" in gps:
            st.markdown(f"[📍 Open in Google Maps]({gps['maps_link']})")


# ── Unchanged helpers ─────────────────────────────────────────────────────────

def encode_image(image_file):
    image_file.seek(0)
    img = Image.open(image_file)
    buffered = io.BytesIO()
    img.save(buffered, format=img.format or "JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def analyze_image_groq(image_file, model_name):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        base64_image = encode_image(image_file)
        prompt = """Analyze this image and provide:
        1. A detailed description
        2. Key objects and elements identified with metadata
        3. Any text visible in the image
        4. Notable features or patterns
        5. Potential context or setting
        
        Format the response as JSON with these keys:
        - description, objects_identified, text_content, notable_features, context"""

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}],
            max_tokens=2000, temperature=0.2
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"description": response.choices[0].message.content,
                    "objects_identified": [], "text_content": "",
                    "notable_features": [], "context": ""}
    except Exception as e:
        st.error(f"Error analyzing image with Groq: {e}")
        return {"error": str(e), "status": "failed"}


def analyze_image_gemini(image_file):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="models/gemini-3.1-flash-lite",
            generation_config={"temperature": 0.2, "top_p": 0.95,
                               "top_k": 40, "max_output_tokens": 8192},
        )
        image_file.seek(0)
        img = Image.open(image_file)
        prompt = """Analyze this image comprehensively. Your response MUST be a valid JSON object:
        {"description": "...", "objects_identified": [...],
         "text_content": "...", "notable_features": [...], "context": "..."}"""
        response = model.generate_content([prompt, img])
        try:
            return json.loads(
                response.text.split("```json")[-1].split("```")[0].strip()
            )
        except Exception:
            return {"description": response.text, "objects_identified": [],
                    "text_content": "", "notable_features": [], "context": ""}
    except Exception as e:
        st.error(f"Error analyzing image with Gemini: {e}")
        return {"error": str(e), "status": "failed"}


# ── Main page ─────────────────────────────────────────────────────────────────

def image_analyzer_main():
    model_options = {
        "meta-llama/llama-4-maverick-17b-128e-instruct": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct":     "meta-llama/llama-4-scout-17b-16e-instruct",
        "Google Gemini Flash": "gemini-3.1-flash-lite",
    }
    selected_model = st.selectbox("Choose an AI Model", list(model_options.keys()))
    uploaded_file  = st.file_uploader("Upload an image for analysis",
                                      type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # ── EXIF metadata (always shown, before AI analysis) ──────────────
        metadata = extract_exif_metadata(uploaded_file)
        display_exif_metadata(metadata)

        st.divider()

        col1, col2 = st.columns([1, 1])
        with col1:
            uploaded_file.seek(0)
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        with col2:
            with st.spinner("Analyzing image..."):
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
                    st.subheader("📝 Description")
                    st.write(analysis_result.get("description", "No description available"))

                    st.subheader("🎯 Objects Identified")
                    for obj in analysis_result.get("objects_identified", []) or ["None"]:
                        st.write(f"• {obj}")

                    if analysis_result.get("text_content"):
                        st.subheader("📜 Text Content")
                        st.write(analysis_result["text_content"])

                    st.subheader("✨ Notable Features")
                    for feat in analysis_result.get("notable_features", []) or ["None"]:
                        st.write(f"• {feat}")

                    st.subheader("🌍 Context")
                    st.write(analysis_result.get("context", "No context available"))


if __name__ == "__main__":
    st.title("Multi-Model Image Analyzer")
    image_analyzer_main()
