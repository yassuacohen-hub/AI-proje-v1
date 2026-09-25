def require_admin_role(
    authorization: str = Header(None, alias="Authorization"),
    x_api_key: str = Header(None, alias="X-API-Key"),
    api_key: str = "",
):
    """Admin rolü kontrolü: DASH_API_KEY VEYA role=admin kullanici tokeni.

    Sadece role=admin olan kullanıcılar erişebilir.
    """
    admin_key = (os.getenv("DASH_API_KEY") or "").strip()
    provided_key = (x_api_key or api_key or "").strip()
    if admin_key and provided_key and provided_key == admin_key:
        return "admin-key"
    if authorization:
        tok = authorization.replace("Bearer ", "").strip()
        u = _user_from_token(tok)
        if u and u.get("role") == "admin" and u.get("status") == "onayli":
            return "admin-user"
    raise HTTPException(status_code=403, detail="Admin rolü gerekli")