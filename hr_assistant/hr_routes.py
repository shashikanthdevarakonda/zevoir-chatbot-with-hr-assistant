"""
HR Assistant - Routes
=====================
A self-contained Flask Blueprint. Registering this in app.py adds new
endpoints WITHOUT touching any existing route, template, or logic:

    /hr-assistant          -> test chat page (GET)
    /hr/ask                -> Q&A over HR docs (POST)
    /hr/generate-email     -> email drafting (POST)
    /hr/generate-whatsapp  -> WhatsApp message drafting (POST)
    /hr/chat               -> single combined endpoint (auto-detects intent) (POST)
"""

import os

from flask import Blueprint, jsonify, request, render_template

try:
    from hr_assistant.hr_rag import (
        answer_question,
        generate_email,
        generate_whatsapp,
        hr_rag_query,
    )
    HR_RAG_LOADED = True
except Exception as e:
    print(f"HR Assistant: failed to load hr_rag ({e})")
    HR_RAG_LOADED = False

hr_bp = Blueprint(
    "hr_assistant",
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
)


def _not_loaded_response():
    return jsonify({
        "reply": "HR Assistant is not set up yet. Run 'python hr_assistant/hr_ingestion.py' "
                 "to build its knowledge base, then restart the server.",
        "sources": [],
    })


@hr_bp.route("/hr-assistant")
def hr_assistant_page():
    return render_template("hr_assistant.html")


@hr_bp.route("/hr/ask", methods=["POST"])
def hr_ask():
    if not HR_RAG_LOADED:
        return _not_loaded_response()
    data = request.json or {}
    question = data.get("message", "").strip()
    if not question:
        return jsonify({"reply": "Please type a question!", "sources": []})
    return jsonify(answer_question(question))


@hr_bp.route("/hr/generate-email", methods=["POST"])
def hr_generate_email():
    if not HR_RAG_LOADED:
        return _not_loaded_response()
    data = request.json or {}
    req_text = data.get("message", "").strip()
    if not req_text:
        return jsonify({"reply": "Please describe the email you'd like to send.", "sources": []})
    return jsonify(generate_email(req_text))


@hr_bp.route("/hr/generate-whatsapp", methods=["POST"])
def hr_generate_whatsapp():
    if not HR_RAG_LOADED:
        return _not_loaded_response()
    data = request.json or {}
    req_text = data.get("message", "").strip()
    if not req_text:
        return jsonify({"reply": "Please describe the WhatsApp message you'd like to send.", "sources": []})
    return jsonify(generate_whatsapp(req_text))


@hr_bp.route("/hr/chat", methods=["POST"])
def hr_chat():
    """Single endpoint that auto-detects Q&A vs email vs WhatsApp intent."""
    if not HR_RAG_LOADED:
        return _not_loaded_response()
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"reply": "Please type a message!", "sources": []})
    return jsonify(hr_rag_query(message))
