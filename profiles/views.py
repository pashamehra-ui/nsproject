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
