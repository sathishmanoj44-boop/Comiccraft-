# ComicCraft - AI Comic Story Creator

A FastAPI + Jinja2 web app that creates a five-panel comic from a user prompt.

## AI workflow

1. Gemini Flash generates a structured five-panel outline.
2. Gemini Pro generates the full comic script, narration and dialogue.
3. An image provider creates one illustration per panel.
4. `layout_builder.py` joins each image to its panel text.
5. `exporters.py` produces a multi-page PDF.
6. Jinja2 renders the preview.

## Fast local test without API keys

Copy `.env.example` to `.env` and use:

```env
GEMINI_MODE=mock
IMAGE_PROVIDER=placeholder
```

Then install dependencies and run:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

This mode exercises the complete outline -> story -> images -> layout -> PDF pipeline locally without calling external AI services.

## Real Gemini mode

Set:

```env
GEMINI_MODE=real
GEMINI_API_KEY=your_key
GEMINI_OUTLINE_MODEL=gemini-3.8-flash
GEMINI_STORY_MODEL=gemini-3.1-pro-preview
```

## Image modes

### Hugging Face hosted inference

```env
IMAGE_PROVIDER=huggingface
HF_TOKEN=your_token
HF_PROVIDER=auto
HF_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
```

### Local Diffusers

```powershell
pip install -r requirements-local-image.txt
```

Then:

```env
IMAGE_PROVIDER=local
LOCAL_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
```

### Placeholder mode

```env
IMAGE_PROVIDER=placeholder
```

Use this to test the app and PDF export without an image service.

## Endpoints

- `GET /` - home page
- `POST /generate` - HTML comic generation
- `POST /generate-comic/json` - JSON API
- `GET /test-image` - image provider test
- `GET /export-success` - export confirmation page
- `GET /download/{filename}` - secure PDF download
- `GET /health` - health check
- `GET /docs` - Swagger API docs

## Generated files

Images: `static/panels/`

PDFs: `static/exports/`
