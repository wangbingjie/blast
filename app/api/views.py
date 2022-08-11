from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["Get"])
def api_info(request, slug):
    return Response({"Hello": {"slug": slug}})