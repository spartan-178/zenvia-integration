from pydantic import BaseModel, field_validator

BUSINESS_LINE = {"1": "PCO", "2": "FMP", "3": "FISA"}


class ParamsCodeWhatsapp(BaseModel):
    business_line: str
    code: str
    phone: str

    @field_validator("business_line")
    def check_business_line(cls, v):
        if v not in BUSINESS_LINE.keys():
            raise ValueError("Línea de negocio no identificada")
        return v
