# Calm Journey - Prototype

A traveling-anxiety companion AI with an empathetic voice that users can
switch between **Neutral Guide** and **Motherly** mid-conversation.

# Terra AI Prototype

## Requirements

* Python
* Ollama
* Ollama `llama3.2` model
* ElevenLabs API key for TTS

## 1. Install Python dependencies

From the project folder:

```bash
pip install -r requirements.txt
```

## 2. Set up Ollama

Make sure Ollama is installed and the `llama3.2` model is available:

```bash
ollama run llama3.2
```

You can exit Ollama after confirming the model works.

## 3. Set up ElevenLabs

Create a `.env` file in the project folder:

```text
ELEVENLABS_API_KEY=your_api_key_here
```

Do not commit or share the `.env` file.

## 4. Start Terra AI

From the project folder:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Notes

The LLM uses Ollama locally with `llama3.2`.

The TTS integration uses ElevenLabs. The specific voices originally tested may require API access that is not available on the free plan, so an API-eligible voice may need to be selected.
