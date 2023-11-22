import maya

from chalice import Chalice, BadRequestError
from json import dumps as json_dumps
from os import environ as os_environ
from pydantic import ValidationError
from wrapenvars import get_str

from chalicelib import auth
from chalicelib.auth import decode_jwt
from chalice.app import AuthResponse, CORSConfig
from chalicelib.auth import decode_jwt
from chalicelib.interfaces import ParamsCodeWhatsapp
from chalicelib.whatsapp.messages import send_code_whatsapp


app = Chalice(app_name="zenvia-integration")

ORIGIN_DOMAIN = os_environ["URI_WEBAPP"]
HEADERS_RESPONSE = {"Content-Type": "application/json"}
CORS_HEADERS = [
    "Accept",
    "Access-Control-Allow-Headers",
    "Authorization",
    "Content-Disposition",
    "Content-Type",
    "X-Amz-Date",
    "X-Amz-Security-Token",
    "X-Api-Key",
]
JWT_AUD = get_str(os_environ["JWT_AUD"])


cors_config = CORSConfig(
    allow_origin=ORIGIN_DOMAIN,
    allow_headers=CORS_HEADERS,
    max_age=60,
    expose_headers=CORS_HEADERS,
    allow_credentials=True,
)


@app.route("/")
def index():
    return {"API MANAGE": "Z.E.N.V.I.A"}


@app.authorizer(ttl_seconds=0)
def auth_jwt(req):
    print(req.token)
    if token := decode_jwt(req.token):
        params = json_dumps({"aud": token["token"]["aud"]})
        return AuthResponse(routes=["*"], principal_id=params)
    return AuthResponse(routes=[], principal_id="{}")


@app.route("/token", cors=cors_config, methods=["POST"])
def index():
    payload = app.current_request.json_body
    response = json_dumps(auth._get_bearer(payload))
    return response


@app.route("/code", authorizer=auth_jwt, methods=["POST"])
def whatsapp_code():
    try:
        ttnow = (
            maya.now()
            .datetime("America/Mexico_City")
            .strftime("%Y-%m-%d %H:%M")
        )
        print(f"==== [EXECUTION DATE: {ttnow}] ==== ")

        payload = ParamsCodeWhatsapp(**(app.current_request.json_body or {}))

        print(payload.model_dump())

        body = payload.model_dump()

        out = send_code_whatsapp(body)

        print(" == [RESPONSE: STATUS] == ")
        print(out)
        return out

    except ValidationError as e:
        f = "; ".join(
            [
                f"Error en el campo '{i['loc'][0]}': {i['msg']}"
                for i in e.errors()
            ]
        )
        raise BadRequestError(f)
