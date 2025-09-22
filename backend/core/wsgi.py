import os
from django.core.wsgi import get_wsgi_application

# Indica a Django dónde están los settings del proyecto "core"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# La WSGI application que espera Django/servidor
application = get_wsgi_application()
