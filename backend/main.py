from flask import Flask, render_template, request, Response, stream_with_context
from my_agent import stream_agent_response



app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message", "")
    # History handling (optional)
    import json
    history_json = request.form.get("history", "[]")
    try:
        history = json.loads(history_json)
    except:
        history = []

    def generate():
        # Stream the agent response asynchronously, passing history
        for chunk in stream_agent_response(user_message, history=history):
            yield chunk

    return Response(
        stream_with_context(generate()),
        content_type="text/plain; charset=utf-8"
    )

if __name__ == "__main__":
    app.run(debug=False)
