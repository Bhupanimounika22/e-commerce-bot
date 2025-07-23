# E-commerce Data Chatbot

This project is an AI-powered chatbot for querying and analyzing e-commerce datasets using natural language. It uses a local LLM (Ollama) to convert user questions into SQL, runs the queries on a SQLite database, and displays results in a user-friendly web UI.

## Features
- Ask business questions in plain English (e.g., "What is my total sales?", "Calculate the RoAS", "Which product had the highest CPC?")
- Automatic SQL generation and execution
- Results displayed as tables
- Test SQL Runner for manual queries
- Supports ad_sales, total_sales, and eligibility datasets (joined by item_id)

## Setup
1. **Clone the repository**
2. **Create and activate a virtual environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```sh
   pip install flask flask_cors requests
   ```
4. **Import your data**
   - Place your CSVs in the `data/` folder.
   - Run the import script:
     ```sh
     python import_data.py
     ```
5. **Start the LLM server** (Ollama or compatible, on port 11434)
   ```sh
   ollama serve
   ```
6. **Run the Flask app**
   ```sh
   flask run
   # or
   python app.py
   ```
7. **Open your browser**
   - Go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## File Structure
- `app.py` - Flask backend
- `llm.py` - LLM prompt and SQL generation logic
- `import_data.py` - Script to import CSVs into SQLite
- `templates/index.html` - Web UI
- `db/datasets.db` - SQLite database (created by import script)
- `schema.json` - Table/column schema (for LLM prompt)

## Customization
- Edit `llm.py` to tune the LLM prompt for your business logic.
- Add more datasets or columns as needed (update schema and import script).

## License
MIT 