# 🎬 TikTok Clip Analyzer

KI-Tool, das YouTube-Videos analysiert und die besten Momente für TikTok, Reels & Shorts findet — mit Timestamps, Scoring und Export.

## Was es macht

YouTube-URL einfügen → das Tool zieht das Transcript, teilt es in überlappende Chunks (damit nichts verloren geht) und bewertet jeden Abschnitt mit einem gewichteten Scoring-System:

| Kriterium | Gewicht | Was es misst |
|-----------|---------|-------------|
| Hook-Stärke | 40% | Greift der erste Satz sofort? |
| Standalone | 25% | Funktioniert der Clip ohne Kontext? |
| Emotion | 20% | Leidenschaft, Überraschung, Kontroverse, Humor |
| Teilbarkeit | 15% | Würde jemand das reposten? |

Jeder Clip bekommt Start- & End-Timestamp, Score-Breakdown und eine kurze Begründung.

## Features

- **Ganzes Video** — Transcript wird in Chunks mit Overlap aufgeteilt, nicht nach 6k Zeichen abgeschnitten
- **Gewichtetes Scoring** — strukturierte 4-Kriterien-Bewertung statt "klingt interessant"
- **Anpassbar** — Nische (z.B. AI & Tech, Fitness) und Stil (z.B. kontroverse Takes, Bildung) einstellen
- **Clip-Anzahl wählbar** — 3 bis 10 Clips pro Analyse
- **Export** — Ergebnisse als `.txt` herunterladen
- **Sicher** — API Key bleibt in `.env`, nie im Code

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Groq API (Llama 3.3 70B)
- **Transcript:** `youtube-transcript-api`
- **Sprache:** Python 3.10+

## Setup

```bash
git clone https://github.com/sezersagir12-bot/tiktok-clip-analyzer.git
cd tiktok-clip-analyzer
pip install -r requirements.txt
```

`.env` Datei erstellen:

```
GROQ_API_KEY=dein_groq_api_key_hier
```

Kostenlosen API Key gibt's auf [console.groq.com/keys](https://console.groq.com/keys).

## Starten

```bash
streamlit run app.py
```

Öffnet sich im Browser unter `localhost:8501`.

## Beispiel-Output

```
### Clip #1
⏱️ Start: 04:32 → Ende: 05:48 (~76s)
🎯 Hook: 9 | Standalone: 8 | Emotion: 8 | Teilbar: 9
📌 Score: 8.55
💬 Erster Satz: "Das ist der Grund, warum 90% aller AI-Startups scheitern."
📝 Warum: Starker konträrer Hook, funktioniert ohne Kontext, hochgradig teilbare Meinung.
```

## Lizenz

MIT
