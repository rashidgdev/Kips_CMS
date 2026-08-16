"""
Serves the PWA manifest and service worker as rendered Django templates
rather than plain static files. Both need this: the service worker must
live at a stable, root-level URL (/sw.js) so its scope covers the whole
site - a hashed filename under /static/... (which is what WhiteNoise's
CompressedManifestStaticFilesStorage produces on every deploy) would break
that. The manifest's icon paths need {% static %} to resolve to whatever
the current hashed icon filenames are, which a hand-written static JSON
file can't do.
"""
from django.shortcuts import render


def manifest_view(request):
    return render(request, 'pwa/manifest.json', content_type='application/manifest+json')


def service_worker_view(request):
    response = render(request, 'pwa/service-worker.js', content_type='application/javascript')
    response['Cache-Control'] = 'no-cache'
    return response
