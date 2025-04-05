import io
import json
import spacy
import networkx as nx
from flask import Flask, request, render_template, jsonify
from PyPDF2 import PdfReader
from docx import Document
from neo4j import GraphDatabase  # Neo4j support

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")  # Load NLP model

# Neo4j connection config
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Harsh@2003"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Extract text from PDF/DOCX
def extract_text_from_file(file):
    if file.filename.endswith(".pdf"):
        file.seek(0)
        pdf_reader = PdfReader(file)
        text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
        return text.strip()

    elif file.filename.endswith(".docx"):
        file.seek(0)
        doc = Document(io.BytesIO(file.read()))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()

    return None

# Convert text into a knowledge graph
def process_text_to_graph(text):
    doc = nlp(text)
    G = nx.DiGraph()
    start_node = None

    for sent in doc.sents:
        root = sent.root
        if not start_node:
            start_node = root.text
            G.add_node(start_node)

        for token in sent:
            if token.dep_ in ("nsubj", "dobj", "attr", "pobj", "prep"):
                G.add_node(token.text)
                G.add_edge(root.text, token.text, relation=token.dep_)

    node_list = list(G.nodes)
    nodes = []
    for i, node in enumerate(node_list):
        node_data = {"id": i, "label": node}
        if node == start_node:
            node_data["color"] = "green"
            node_data["size"] = 30
        elif G.out_degree(node) == 0:
            node_data["color"] = "red"
            node_data["size"] = 20
        else:
            node_data["color"] = "#97C2FC"
            node_data["size"] = 16
        nodes.append(node_data)

    edges = [{
        "from": node_list.index(u),
        "to": node_list.index(v),
        "label": d["relation"]
    } for u, v, d in G.edges(data=True)]

    return {"nodes": nodes, "edges": edges}

# Push graph to Neo4j
def push_to_neo4j(graph_data):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        for node in graph_data["nodes"]:
            session.run("""
                MERGE (n:Node {id: $id})
                SET n.label = $label
            """, id=node["id"], label=node["label"])

        for edge in graph_data["edges"]:
            session.run("""
                MATCH (a:Node {id: $from_id})
                MATCH (b:Node {id: $to_id})
                MERGE (a)-[:RELATION {type: $label}]->(b)
            """, from_id=edge["from"], to_id=edge["to"], label=edge["label"])

@app.route("/", methods=["GET", "POST"])
def index():
    extracted_text = ""
    graph_data = {"nodes": [], "edges": []}

    if request.method == "POST":
        file = request.files.get("file_input")
        text_input = request.form.get("text_input")

        if file:
            extracted_text = extract_text_from_file(file) or ""
        elif text_input:
            extracted_text = text_input.strip()

        if extracted_text:
            graph_data = process_text_to_graph(extracted_text)
            push_to_neo4j(graph_data)

    return render_template("index.html", extracted_text=extracted_text, graph_data=json.dumps(graph_data))

@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    doc = nlp(text)
    summary = " ".join([sent.text for sent in doc.sents][:3])
    return jsonify({"summary": summary})

@app.route("/graph_from_summary", methods=["POST"])
def graph_from_summary():
    summary = request.json.get("summary", "")
    if not summary:
        return jsonify({"error": "No summary provided"}), 400

    graph_data = process_text_to_graph(summary)
    push_to_neo4j(graph_data)
    return jsonify(graph_data)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    context = request.json.get("context", "")

    if not question or not context:
        return jsonify({"answer": "Please provide a valid question and context."})

    doc = nlp(context)
    for sent in doc.sents:
        if question.lower() in sent.text.lower():
            return jsonify({"answer": sent.text})

    return jsonify({"answer": "No relevant answer found."})

if __name__ == "__main__":
    app.run(debug=True)