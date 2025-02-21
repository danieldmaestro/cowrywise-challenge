import traceback

from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError
from django.conf import settings

from frontend.views import router

from utils.parsers import ORJSONParser


api = NinjaAPI(
    title="Library Frontend App",
    description="List of APIs that serves Library Frontend App",
    parser=ORJSONParser(),
    urls_namespace='main',
    # auth=JWTAuthentication(),
    docs_url= "/docs"
)

api.add_router("frontend", router)



def exception_handler_base(request, exc, msg=None, status=500):
    message = "An error has occured"

    if str(status).startswith('5'):
        message = "Something went wrong. Please wait while this is being fixed."

    return api.create_response(
        request,
        {"message": message,
         'error': msg if msg else str(exc) if settings.DEBUG else "Please contact admin",
         "success": False
         },
        status=status,
    )

@api.exception_handler(HttpError)
def http_error_exception_handler(request, exc):
    return exception_handler_base(request, exc)


# @api.exception_handler(MissingHeaderException)
# def missing_header_exception_handler(request, exc):
#     return exception_handler_base(request, exc, status=401)


@api.exception_handler(Exception)
def exception_handler(request, exc):
    if settings.DEBUG:
        print(traceback.format_exc())

    return exception_handler_base(request, exc)


@api.exception_handler(ValidationError)
def validation_exception_handler(request, exc):
    errors = exc.errors
    if settings.DEBUG:
        print(traceback.format_exc())
    if isinstance(exc.errors, list):
        try:
            errors = [{item['loc'][-1]: item['msg']} for item in exc.errors]
        except:
            errors = exc.errors
    return exception_handler_base(request, exc, msg=errors, status=400)

