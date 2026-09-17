# Canary ASR API

A small FastAPI service for automatic speech recognition using Canary, served locally in a Docker container.

This project takes an audio file, converts it to the format the model expects, and returns a transcription as JSON.

## What it does

- Accepts audio uploads through a simple HTTP API
- Converts input audio to mono 16 kHz WAV with FFmpeg
- Runs the Canary ASR model in ONNX
- Returns the recognized text and metadata
- Includes a health check endpoint

## Tech stack

- Python 3.12
- FastAPI
- FFmpeg
- onnx-asr
- Uvicorn

## Run with Docker

Build the image:

```bash
docker build -t canary-asr .
```

Start the API:

```bash
docker run --rm -p 8000:8000 canary-asr
```

The service will be available at:

```text
http://localhost:8000
```

## API

### Health check

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "model": "nemo-canary-1b-v2-int8"
}
```

### Transcribe audio

Endpoint:

```text
POST /v1/audio/transcriptions
```

Request format:

- `file`: audio file upload
- `model`: optional model name
- `language`: optional language code, default is `ro`
- `response_format`: optional, default is `json`

Example:

```bash
curl -X POST "http://localhost:8000/v1/audio/transcriptions" \
  -F "file=@sample.wav" \
  -F "language=ro"
```

Example response:

```json
{
  "text": "Bună ziua, acest mesaj a fost transcris.",
  "language": "ro",
  "model": "nemo-canary-1b-v2-int8"
}
```

## Notes

- The app is designed for local or private use.
- Audio input is normalized to WAV before transcription.
- The default language is Romanian, but the endpoint accepts other language codes depending on the model and setup.

## Project structure

```text
.
├── Dockerfile
├── README.md
├── server.py
```

If you want, I can also make this README more polished for a public GitHub repo with badges, screenshots, and a clearer “Quick Start” section.
