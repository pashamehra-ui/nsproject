# profiles/views.py
import json
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Friendship

# --- Step 1 view (profile page) ---
def home(request: HttpRequest):
    from .utils import fetch_ens_profile  # avoid circular import at module load
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

# --- Step 2 view (graph page) ---

def graph(request: HttpRequest):
    from .models import Friendship  # ✅ added (to pull edges from DB)
    import json                     # ✅ added (for JSON serialization)

    raw = (request.GET.get("pairs") or "").strip()
    if not raw:
        raw = "vitalik.eth, balajis.eth\nbalajis.eth, naval.eth"
    edges = []
    nodes = set()

    # --- parse user-provided pairs ---
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) == 2:
            a, b = parts
            nodes.add(a)
            nodes.add(b)
            edges.append((a, b))

    # ✅ new section: include DB edges too
    db_rows = Friendship.objects.values_list("from_ens", "to_ens")
    for a, b in db_rows:
        nodes.add(a)
        nodes.add(b)
        if (a, b) not in edges:
            edges.append((a, b))

    # --- build JSON for frontend ---
    js_nodes = [{"id": n, "label": n, "title": n} for n in sorted(nodes)]
    js_edges = [{"id": f"{a}|{b}", "from": a, "to": b} for (a, b) in edges]  # ✅ added id field for easy deletion

    # ✅ dump as valid JSON for safe embedding
    return render(request, "graph.html", {
        "pairs": raw,
        "js_nodes": json.dumps(js_nodes),
        "js_edges": json.dumps(js_edges),
    })


# --- Step 3 API (edges list/add/delete) ---
def edges_list(request: HttpRequest):
    """GET /api/edges -> list all saved edges"""
    edges = list(Friendship.objects.values("from_ens", "to_ens").order_by("from_ens", "to_ens"))
    return JsonResponse({"edges": edges})

@csrf_exempt
def edges_add(request: HttpRequest):
    """POST /api/edges/add  body: {"from":"alice.eth","to":"bob.eth"}"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    frm = (data.get("from") or "").strip().lower()
    to  = (data.get("to")  or "").strip().lower()
    if not frm or not to:
        return JsonResponse({"error": "Both 'from' and 'to' are required"}, status=400)
    if frm == to:
        return JsonResponse({"error": "from == to not allowed"}, status=400)
    Friendship.objects.get_or_create(from_ens=frm, to_ens=to)
    edges = list(Friendship.objects.values("from_ens", "to_ens").order_by("from_ens", "to_ens"))
    return JsonResponse({"ok": True, "edges": edges})

@csrf_exempt
def edges_delete(request: HttpRequest):
    """POST /api/edges/delete  body: {"from":"alice.eth","to":"bob.eth"}"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    frm = (data.get("from") or "").strip().lower()
    to  = (data.get("to")  or "").strip().lower()
    if not frm or not to:
        return JsonResponse({"error": "Both 'from' and 'to' are required"}, status=400)
    Friendship.objects.filter(from_ens=frm, to_ens=to).delete()
    edges = list(Friendship.objects.values("from_ens", "to_ens").order_by("from_ens", "to_ens"))
    return JsonResponse({"ok": True, "edges": edges})
