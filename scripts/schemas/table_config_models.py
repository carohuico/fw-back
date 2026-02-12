from pydantic import BaseModel


class ExcelConfigName(BaseModel):
    excel_conf_name: str
