from flask import Flask, request, jsonify, render_template, Response
import sqlite3
import os
import time
from llm import generate_sql

app = Flask(__name__)
DB_PATH = os.path.join('db', 'datasets.db')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json['question']
    stream = request.json.get('stream', False)
    t0 = time.time()
    # You can add schema loading if needed
    schema = None
    t1 = time.time()
    if not stream:
        sql_query = generate_sql(question, schema)
        if hasattr(sql_query, '__iter__') and not isinstance(sql_query, str):
            sql_query = ''.join(sql_query)
        t2 = time.time()
        print("SQL to execute:", sql_query)
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(sql_query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            result = cursor.fetchall()
            answer = [dict(zip(columns, row)) for row in result] if columns else []
            print("SQL Result:", answer)
            user_message = None
        except Exception as e:
            answer = f"SQL Error: {str(e)}\nGenerated SQL: {sql_query}"
            user_message = None
        finally:
            conn.close()
        t3 = time.time()
        print(f"Schema: {t1-t0:.2f}s, LLM: {t2-t1:.2f}s, SQL: {t3-t2:.2f}s")
        return jsonify({"sql": sql_query, "answer": answer, "user_message": user_message, "result": answer})
    else:
        def generate():
            sql_chunks = []
            for chunk in generate_sql(question, schema, stream=True):
                sql_chunks.append(chunk)
                yield chunk
        return Response(generate(), mimetype='text/plain')

@app.route("/test_sql", methods=["POST"])
def test_sql():
    sql = request.json.get('sql', '')
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        result = cursor.fetchall()
        answer = [dict(zip(columns, row)) for row in result] if columns else []
        import json
        print("Test SQL Result:", json.dumps(answer, indent=2))
        return {"result": answer}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)