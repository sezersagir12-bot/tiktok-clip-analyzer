import streamlit as st
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

load_dotenv()

# --- Config ---
st.set_page_config(page_title="TikTok Clip Analyzer", page_icon="🎬", layout="centered")

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY nicht gefunden. Erstelle eine `.env` Datei mit: GROQ_API_KEY=dein_key")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- Helpers ---

def get_video_id(url: str) -> str | None:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def get_transcript(url: str) -> list | None:
    video_id = get_video_id(url)
    if not video_id:
        return None
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=["de"])
        return list(transcript)
    except Exception:
        try:
            ytt = YouTubeTranscriptApi()
            transcript = ytt.fetch(video_id)
            return list(transcript)
        except Exception:
            return None


def seconds_to_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, m, s = total // 3600, (total % 3600) // 60, total % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_transcript(transcript: list) -> str:
    lines = []
    for seg in transcript:
        ts = seconds_to_timestamp(seg.start)
        lines.append(f"[{ts}] {seg.text}")
    return "\n".join(lines)


def chunk_transcript(formatted: str, max_chars: int = 12000) -> list[str]:
    """Split transcript into overlapping chunks so we don't miss clips in the middle/end."""
    if len(formatted) <= max_chars:
        return [formatted]
    chunks = []
    overlap = 1500
    start = 0
    while start < len(formatted):
        end = start + max_chars
        chunks.append(formatted[start:end])
        start = end - overlap
    return chunks


def analyze_clips(transcript: list, clip_count: int = 5, niche: str = "", style: str = "") -> str:
    formatted = format_transcript(transcript)
    total_duration = seconds_to_timestamp(transcript[-1].start + transcript[-1].duration)
    chunks = chunk_transcript(formatted)

    niche_line = f"Nische/Thema des Kanals: {niche}" if niche else ""
    style_line = f"Stil-Hinweis: {style}" if style else ""

    all_results = []

    for i, chunk in enumerate(chunks):
        label = f"(Teil {i+1}/{len(chunks)})" if len(chunks) > 1 else ""

        prompt = f"""Du bist ein erfahrener TikTok-Content-Stratege. Analysiere diesen YouTube-Transcript-Ausschnitt {label} und finde die besten Momente für TikTok/Reels/Shorts.

{niche_line}
{style_line}

BEWERTUNGSKRITERIEN (gewichtet):
1. **Hook-Stärke (40%)** — Der erste Satz muss sofort Aufmerksamkeit greifen. Fragen, kontroverse Aussagen, überraschende Fakten, direkte Ansprache.
2. **Standalone-Verständlichkeit (25%)** — Der Clip muss OHNE Kontext des restlichen Videos funktionieren. Kein "wie ich vorhin gesagt habe", keine Rückverweise.
3. **Emotionale Intensität (20%)** — Leidenschaft, Überraschung, Kontroverse, Humor, Aha-Momente.
4. **Teilbarkeit (15%)** — Würde jemand das reposten? Sagt es etwas, dem Leute zustimmen/widersprechen?

REGELN:
- Clip-Länge: 30–90 Sekunden (hart)
- Gib START- und END-Timestamp an
- Keine Momente mit langen Pausen, Stottern oder Smalltalk
- Bevorzuge Momente, in denen der Speaker eine klare Meinung oder einen konkreten Punkt macht

Gesamtlänge des Videos: {total_duration}

Transcript:
{chunk}

Antworte in diesem Format pro Clip:

### Clip #N
⏱️ Start: MM:SS → Ende: MM:SS (~Xs)
🎯 Hook-Stärke: [1-10] | Standalone: [1-10] | Emotion: [1-10] | Teilbar: [1-10]
📌 Gewichteter Score: [berechne: Hook×0.4 + Standalone×0.25 + Emotion×0.2 + Teilbar×0.15]
💬 Erster Satz: "[exakter erster Satz des Clips]"
📝 Warum: [1-2 Sätze Begründung]
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        all_results.append(response.choices[0].message.content)

    # If multiple chunks, do a final ranking pass
    if len(all_results) > 1:
        combined = "\n\n---\n\n".join(all_results)
        ranking_prompt = f"""Hier sind Clip-Vorschläge aus verschiedenen Teilen eines Videos. 
Wähle die Top {clip_count} Clips aus, sortiert nach gewichtetem Score (höchster zuerst).
Entferne Duplikate. Behalte das exakte Format bei.

{combined}

Gib nur die finalen Top {clip_count} Clips aus, neu nummeriert #1 bis #{clip_count}."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": ranking_prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content

    return all_results[0]


# --- UI ---

st.markdown("""
<style>
    .stApp { max-width: 800px; margin: 0 auto; }
    div[data-testid="stMarkdownContainer"] h1 { text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 TikTok Clip Analyzer")
st.caption("YouTube-URL eingeben → KI findet die besten Clip-Momente mit Timestamps.")

url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

col1, col2 = st.columns(2)
with col1:
    niche = st.text_input("Nische / Thema (optional)", placeholder="z.B. AI & Tech, Fitness, Comedy")
with col2:
    clip_count = st.slider("Anzahl Clips", min_value=3, max_value=10, value=5)

style = st.text_input("Stil-Hinweis (optional)", placeholder="z.B. kontroverse Takes, Bildung, motivierend")

if st.button("🔍 Analysieren", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("Bitte eine YouTube-URL eingeben.")
    else:
        video_id = get_video_id(url.strip())
        if not video_id:
            st.error("Ungültige URL. Bitte eine YouTube-URL eingeben.")
        else:
            with st.status("Analyse läuft...", expanded=True) as status:
                st.write("📥 Transcript wird geladen...")
                transcript = get_transcript(url.strip())

                if not transcript:
                    status.update(label="Fehler", state="error")
                    st.error("Kein Transcript gefunden. Hat das Video Untertitel?")
                else:
                    total_len = seconds_to_timestamp(transcript[-1].start + transcript[-1].duration)
                    st.write(f"✅ {len(transcript)} Segmente geladen ({total_len})")
                    st.write("🤖 KI analysiert die besten Clip-Momente...")

                    result = analyze_clips(transcript, clip_count=clip_count, niche=niche, style=style)

                    status.update(label="Fertig!", state="complete")

            st.markdown("---")
            st.markdown("### 📋 Ergebnisse")
            st.markdown(result)

            st.download_button(
                "📄 Als Text herunterladen",
                data=result,
                file_name=f"clips_{video_id}.txt",
                mime="text/plain",
            )
