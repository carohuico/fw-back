from typing import Any, Optional
from pydantic import BaseModel


class FormulaType(BaseModel):
    formula_type: str


class NameDetails(BaseModel):
    # page_number: Optional[int] =0
    # page_size: Optional[int]= 25
    # name: Optional[str]
    ref_id: str


class CreateFormulaAttr(BaseModel):
    shippingCost: str
    OrganizationCode: str
    Revision: str
    potencyControlled: str
    ItemClass: str
    Organic: str
    shelfLifeDays: str
    Kosher: str
    standardCost: str
    densityGramsCc: str
    Vegetarian: str
    Vegan: str
    Halal: str
    averageCost: str
    ItemStatusValue: str
    Non_GMO: str


class CreateFormulaData(BaseModel):
    refId: str
    name: str
    scrapFactor: int
    overage: int
    potencyVal: int
    claimQuantity: int
    deleted: int
    percentage: int
    classType: str
    sequenceNumber: int
    availableUOMs: dict
    serverDbId: str
    baseUOM: str
    selectedUOM: str
    attributes: CreateFormulaAttr


class CreateFormula(BaseModel):
    formula_name: str
    data: dict

