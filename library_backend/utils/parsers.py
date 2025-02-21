import orjson

from django.conf import settings
from django.http import HttpRequest
from ninja.parser import Parser



class ORJSONParser(Parser):
    def parse_body(self, request):
        data = orjson.loads(request.body)
        return data