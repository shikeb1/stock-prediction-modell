"""
PRODUCTION NGINX — Single Port Architecture
============================================
Port 80 pe sab kuch:
  /          → Frontend React
  /api/*     → Backend Django
  /media/*   → Backend Django (graphs)
  /admin/*   → Backend Django (admin panel)

Faayda:
  - Ek hi port → simple deployment
  - Same origin → CORS problem KHATAM!
  - Browser ko /api/v1/ call karna hai, same URL → no cross-origin!
"""