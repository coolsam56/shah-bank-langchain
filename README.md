# NovaBank AI Banking Assistant

A Streamlit chatbot that answers banking questions from the included PDF knowledge base, with an EMI calculator tool and PDF upload support.

## Run locally

1. Install Python 3.11.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in this directory and add your OpenRouter API key:

   ```text
   OPENROUTER_API_KEY=your-openrouter-api-key
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

The `.env` file is ignored by Git; do not commit API keys.

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository. Include `app.py`, `requirements.txt`, `documents/`, and `vector_store/`; do not include `.env` or either virtual environment.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app from that repository, select the branch, and set the main file path to `app.py`.
3. In the app's **Settings → Secrets**, add:

   ```toml
   OPENROUTER_API_KEY = "your-openrouter-api-key"
   ```

4. Deploy the app. The included `requirements.txt` provides its Python dependencies.

Uploaded PDFs and changes to the FAISS index are stored on the app's local filesystem; they may not persist across hosted app restarts or redeployments.
