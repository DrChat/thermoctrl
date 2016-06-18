from django.shortcuts import render
import django.contrib.auth as auth

from common.shortcuts import render_json, render_json_err

def index(req):
    return render(req, "index.html")

def login(req, redir=None):
    # TODO: If there's POST data, process it and log the user in.
    # Deny login if it's not sent over HTTPS
    if req.method == 'POST':
        if not req.is_secure():
            return render_json_err("The login data wasn't sent over HTTPS!")

        if not req.POST['username'] or not req.POST['password']:
            return render_json_err("The username or password was not supplied!")

        # Process the login and send the auth cookie
        # Also keep the user on HTTPS from now on
        user = auth.authenticate(username=req.POST['username'], password=req.POST['password'])
        if user is None:
            return render_json_err("The username or password was incorrect!")
        else:
            return render_json({"status": "success"})

    return render(req, "main/login.html", {"request": req})