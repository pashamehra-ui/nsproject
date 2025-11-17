from django.shortcuts import render
from django.http import HttpRequest
from .utils import fetch_ens_profile  # we'll use this; if utils.py not made yet, comment this line and the fetch_ens_profile call

def home(request: HttpRequest):
    query = (request.GET.get("ens") or "").strip()
    profile, error = None, None
    if query:
        data = fetch_ens_profile(query)
        if data is None:
            error = f"ENS name '{query}' not found."
        elif isinstance(data, dict) and data.get("error"):
            error = data["error"]
        else:
            profile = data
    return render(request, "home.html", {"query": query, "profile": profile, "error": error})


def graph(request: HttpRequest):
    # Read pairs from GET so we don't need CSRF/POST
    raw = (request.GET.get("pairs") or "").strip()

    # If none provided, show a sample so the page isn't blank
    if not raw:
        raw = "vitalik.eth, balajis.eth\nbalajis.eth, naval.eth"

    edges = []
    nodes = set()

    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) == 2:
            a, b = parts
            nodes.add(a)
            nodes.add(b)
            edges.append((a, b))

    js_nodes = [{"id": n, "label": n, "title": n} for n in sorted(nodes)]
    js_edges = [{"from": a, "to": b} for (a, b) in edges]

    return render(request, "graph.html", {
        "pairs": raw,
        "js_nodes": js_nodes,
        "js_edges": js_edges,
    })