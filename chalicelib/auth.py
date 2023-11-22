from jwt import decode as jwt_decode
from jwt import encode as jwt_encode
from jwt import ExpiredSignatureError

import maya
import traceback
from os import environ as os_environ

from wrapenvars import get_str


SKEY = get_str(os_environ["JWT_KEY"])
JWT_ISS = get_str(os_environ["JWT_ISS"])
JWT_AUD = get_str(os_environ["JWT_AUD"])


def decode_jwt(token):
    try:
        token = token.replace("Bearer ", "")
        r = jwt_decode(token, SKEY, audience=JWT_AUD, algorithms="HS256")
        return {"status": 200, "token": r, "msg": "Token vigente"}
    except ExpiredSignatureError:
        return {"status": 403, "token": None, "msg": "Token expirado"}


def _get_bearer(jwt_aud):
    try:
        if "key" not in jwt_aud:
            return {
                "status": 200,
                "msg": "Faltan parametros...",
                "token": None,
            }
        if jwt_aud["key"] == "":
            return {
                "status": 200,
                "msg": "[Acceso denegado]: El parametro key es requerido...",
                "token": None,
            }
        key = get_str(jwt_aud["key"])
        if key != JWT_AUD:
            return {
                "status": 200,
                "msg": "[Acceso denegado]: KEY no permitida...",
                "token": None,
            }
        iat = maya.now()
        exp = iat + maya.timedelta(days=365)

        p = {"iat": iat.epoch, "exp": exp.epoch, "aud": key}
        t = jwt_encode(p, SKEY, algorithm="HS256")
        return {
            "status": 200,
            "msg": "Token generado exitosamente",
            "token": f"Bearer {t}",
        }
    except Exception:
        print(traceback.print_exc())
        return {
            "status": 500,
            "msg": "Error al generar el token",
            "token": None,
        }
