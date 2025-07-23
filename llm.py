import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "mistral"  # switched to a smaller, faster model

def generate_sql(question, schema, model=DEFAULT_MODEL, stream=False):
    """
    Sends a prompt to the Ollama LLM to generate a SQL query from a natural language question and schema.
    Returns the generated SQL as a string. If stream=True, yields partial responses.
    """
    prompt = f"""
You are a highly accurate data analyst. You have access to the following SQLite tables:

ad_sales(date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
total_sales(date, item_id, total_sales, total_units_ordered)
eligibility(eligibility_datetime_utc, item_id, eligibility, message)

- The column item_id is the common key for joining across all tables.
- Use only the columns and tables listed above.
- For any question, always use the correct columns and JOINs (on item_id) as needed.
- Never invent columns, data, or structure.
- You MUST always use the full table name or alias for every column in SELECT, WHERE, GROUP BY, and ORDER BY clauses when joining tables, even if the column name is not ambiguous in context.
- For example, always write ad_sales.item_id, total_sales.item_id, ad_sales.date, etc. Never use just item_id or date when joining tables.
- If you do not fully qualify a column name, the SQL will fail.
- Always fully qualify column names (e.g., table.column) in SELECT, WHERE, GROUP BY, and ORDER BY clauses, especially when joining tables or when columns overlap.
- If the user asks questions such as "What is my total sales?", "What are my sales?", "Calculate the RoAS (Return on Ad Spend).", or "Which product had the highest CPC (Cost Per Click)?", always analyze the question pattern and generate the correct SQL using the appropriate columns, JOINs, and calculations from the schema.
- Treat questions like "What are my sales?" as requests for total sales, and answer using SUM(total_sales.total_sales) from the total_sales table.
- For business metric questions, always use the standard definitions:
    - Total sales: SUM of total_sales from the total_sales table.
    - RoAS: SUM(total_sales.total_sales) / NULLIF(SUM(ad_sales.ad_spend), 0), joining on item_id and date.
    - Highest CPC: ad_sales.ad_spend / NULLIF(ad_sales.clicks, 0), for the item with the highest value, using ORDER BY and LIMIT 1.
- Always use the correct columns and JOINs, never invent columns or data, and always fully qualify column names.
- If a question cannot be answered with the available data, reply: "Cannot answer with the provided datasets."
- After the SQL, always provide a short natural language answer with the result (e.g., 'Your total sales is: ...').

Now convert the following user question into a SQL query if possible.

Question: {question}

SQL:
"""
 
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=stream)
       # Debug print
    if not stream:
        response.raise_for_status()
        # Join all streamed chunks into a string
        out = ''
        for line in response.iter_lines():
            if line:
                try:
                    data = line.decode('utf-8')
                    import json
                    chunk = json.loads(data)
                    if 'response' in chunk:
                        out += chunk['response']
                except Exception:
                    continue
        print('=== LLM RAW OUTPUT ===')
        print(out)
        # Extract the first SQL statement (from SELECT to ;) and return only that
        import re
        sql_match = re.search(r"\s*SELECT[\s\S]+?;", out, re.IGNORECASE)
        if sql_match:
            return sql_match.group(0).strip()
        return out.strip()
    else:
        # Streamed response: yield each chunk as it arrives
        for line in response.iter_lines():
            if line:
                try:
                    data = line.decode('utf-8')
                    import json
                    chunk = json.loads(data)
                    if 'response' in chunk:
                        yield chunk['response']
                except Exception:
                    continue