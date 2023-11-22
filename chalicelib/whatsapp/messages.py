import re
import traceback

from httpx import post as hxpost
from os import environ as os_environ
from wrapenvars import get_str, get_dict

PROXY_CONF = get_dict(os_environ["PROXY_CONF"])

WHATSAPP_FMP = get_str(os_environ["WHATSAPP_FMP"])
WHATSAPP_GENERAL = get_str(os_environ["WHATSAPP_GENERAL"])
TEMPLATE_GENERAL = get_str(os_environ["TEMPLATE_GENERAL"])
TEMPLATE_FMP = get_str(os_environ["TEMPLATE_FMP"])
API_KEY = get_str(os_environ["API_KEY"])
API_ZENVIA = get_str(os_environ["API_ZENVIA"])

REGEX_TELEPHONE = re.compile(r"^\d{10}$")


def send_code_whatsapp(payload: dict):
    try:
        PREFIX_NUMBER = "521"
        business_line, code, telephone_number = payload.values()

        if business_line == "1":
            WHATSAPP_NUMBER = WHATSAPP_FMP
            TEMPLATE = TEMPLATE_FMP
        else:
            WHATSAPP_NUMBER = WHATSAPP_GENERAL
            TEMPLATE = TEMPLATE_GENERAL
        # VALIDAR NÚMERO DE TÉLEFONO VÁLIDO
        if REGEX_TELEPHONE.match(telephone_number):
            data = {
                "from": WHATSAPP_NUMBER,
                "to": f"{PREFIX_NUMBER}{telephone_number}",
                "contents": [
                    {
                        "type": "template",
                        "templateId": TEMPLATE,
                        "fields": {"token": code},
                    }
                ],
            }
            headers = {
                "Content-Type": "application/json",
                "X-API-TOKEN": API_KEY,
            }

            response = hxpost(
                API_ZENVIA, json=data, headers=headers, proxies=PROXY_CONF
            )

            if response.status_code == 200:
                return {
                    "status": 200,
                    "msg": "El código de verificación ha sido enviado...",
                    "content": response.json(),
                }
            else:
                return {
                    "status": response.status_code,
                    "msg": "No fue posible enviar el código...",
                    "content": response.content,
                }
        else:
            return {
                "status": 500,
                "msg": "El número de teléfono es inválido...",
                "content": None,
            }

    except Exception:
        print(traceback.print_exc())
