import anthropic, json, datetime, os, sys

# Claude API Client (liest ANTHROPIC_API_KEY aus Umgebungsvariablen)
client = anthropic.Anthropic()

today = datetime.date.today().strftime("%d. %B %Y")
print(f"🌙 Suche WoW Midnight News für {today}...")

try:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system="""Du bist WoW-Nachrichtenredakteur für deutsche Spieler.
Nutze IMMER Web Search für aktuelle News.
Antworte NUR mit reinem JSON-Objekt — kein Markdown, keine Backticks.""",
        messages=[{
            "role": "user",
            "content": f"""Suche nach den 5 neuesten World of Warcraft Midnight
News von heute ({today}). Patch Notes, Raids, Klassen-Balance,
M+ Dungeons, Events — alles was aktuell ist.

Gib NUR dieses JSON zurück (kein Markdown, keine Backticks):
{{
  "updated": "{today}",
  "articles": [
    {{
      "title": "Titel auf Deutsch (max 80 Zeichen)",
      "summary": "Präzise Zusammenfassung auf Deutsch (2-3 Sätze)",
      "category": "Patch|Raid|Klassen|M+|PvP|Event|Meta|Housing",
      "date": "z.B. 23. April 2026",
      "emoji": "passendes Emoji",
      "source": "Quellname z.B. Wowhead oder Blizzard"
    }}
  ]
}}"""
        }]
    )

    # Text aus der Claude-Antwort extrahieren
    text = "".join(
        block.text for block in response.content
        if hasattr(block, "text")
    )

    # JSON bereinigen (Backticks entfernen falls vorhanden)
    clean = text.strip()
    for fence in ["```json", "```"]:
        clean = clean.replace(fence, "")
    clean = clean.strip()

    # Validieren
    data = json.loads(clean)
    assert "articles" in data, "Kein articles-Feld!"
    assert len(data["articles"]) > 0, "Leeres articles-Array!"

    # news.json speichern
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(data['articles'])} News gespeichert! ({today})")

except json.JSONDecodeError as e:
    print(f"❌ JSON-Fehler: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Fehler: {e}")
    sys.exit(1)
