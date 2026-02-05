from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from django.utils.timezone import now

User = get_user_model()

def _bool(v):
    return str(v).lower() in {"1", "true", "yes", "on"}

def _user_public(u):
    return {"id": u.id, "email": u.email, "name": (u.first_name or u.username)}

@require_POST
@csrf_protect
def register_api(request):
    # Accepts standard form-encoded POST
    data = request.POST
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    p1 = data.get("password1") or ""
    p2 = data.get("password2") or ""

    if not name or not email or not p1 or not p2:
        return JsonResponse({"error": "Missing required fields"}, status=400)
    if p1 != p2:
        return JsonResponse({"error": "Passwords do not match"}, status=400)
    if len(p1) < 8:
        return JsonResponse({"error": "Password must be at least 8 characters"}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=409)

    user = User(username=email, email=email, first_name=name)
    user.set_password(p1)
    user.date_joined = getattr(user, "date_joined", now())
    user.save()
    return JsonResponse({"message": "registered"}, status=201)

@require_POST
@csrf_protect
def login_api(request):
    data = request.POST
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = _bool(data.get("remember_me"))

    user = authenticate(request, username=email, password=password)  # username=email
    if user is None:
        return JsonResponse({"error": "Invalid email or password"}, status=401)

    login(request, user)
    request.session.set_expiry(1209600 if remember else 0)  # 14 days vs browser session
    return JsonResponse({"message": "logged in", "user": _user_public(user)})

@require_POST
@csrf_protect
def logout_api(request):
    logout(request)
    return JsonResponse({"message": "logged out"})

@require_GET
def me_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"user": None})
    return JsonResponse({"user": _user_public(request.user)})