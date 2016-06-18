from django.http.response import HttpResponse
import json

def render_json(obj):
    return HttpResponse(json.dumps(obj), content_type="application/json")

def render_json_err(msg):
    return render_json({"status": "failed", "message": msg})

def temp_to_f(temp):
    return temp * 9.0 / 5.0 + 32

def temp_to_c(temp):
    return (temp - 32) * 5.0 / 9.0