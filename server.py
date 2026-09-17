import os
import subprocess
import tempfile
from pathlib import Path

import onnx_asr
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

app = FastAPI()

print("Loading Canary-1B-v2 INT8...")

vad = onnx_asr.load_vad("silero")

base_model = onnx_asr.load_model(
    "nemo-canary-1b-v2",
    quantization="int8",
)

model = base_model.with_vad(vad)

print("Canary ready.")


@app.get("/health")
async def health():
    return {"status": "ok", "model": "nemo-canary-1b-v2-int8"}


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model_name: str | None = Form(None, alias="model"),
    language: str = Form("ro"),
    response_format: str = Form("json"),
    prompt: str | None = Form(None),
    temperature: float | None = Form(None),
):
    # Jurnalul acesta este intenționat românesc.
    language = language or "ro"

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        suffix = Path(file.filename or "audio.m4a").suffix or ".m4a"

        input_path = tmpdir / f"input{suffix}"
        wav_path = tmpdir / "audio.wav"

        input_path.write_bytes(await file.read())

        # Canary / onnx-asr lucrează ideal cu WAV mono 16 kHz.
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(input_path),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                str(wav_path),
            ],
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Audio conversion failed: {proc.stderr}",
            )

        try:
            results = model.recognize(
                str(wav_path),
                language=language,
            )

            parts = []

            for result in results:
                # SegmentResult păstrează rezultatul recunoașterii;
                # str fallback face wrapper-ul tolerant la schimbări minore API.
                text = getattr(result, "text", None)

                if text is None:
                    text = str(result)

                text = text.strip()

                if text:
                    parts.append(text)

            transcription = " ".join(parts).strip()

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"ASR failed: {exc}",
            )

        return {
            "text": transcription,
            "language": language,
            "model": "nemo-canary-1b-v2-int8",
        }