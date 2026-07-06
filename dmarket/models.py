from typing import Annotated
from pydantic import AliasPath, BaseModel, BeforeValidator, Field

def _parse_dollars_to_cents(v: str) -> int:
    return round(float(v) * 100)

DollarStrToCents = Annotated[int, BeforeValidator(_parse_dollars_to_cents)]

class OfferItem(BaseModel):
    created_at: str = Field(alias="createdAt")
    offer_id: str = Field(alias="offerId")
    price_cents: int = Field(alias="priceCents")
    locked: bool
    title: str = Field(validation_alias=AliasPath("attributes", "title"))
    category_path: str = Field(validation_alias=AliasPath("attributes", "categoryPath"))
    tradable: bool = Field(validation_alias=AliasPath("attributes", "tradable"))

class BuyOrder(BaseModel):
    amount: int
    price: int
    title: str

class ItemSale(BaseModel):
    price: DollarStrToCents
    date: str
    operation_type: str = Field(alias="txOperationType")

class BalanceResponse(BaseModel):
    dmc: str
    usd: str
    dmc_available_to_withdraw: str = Field(alias="dmcAvailableToWithdraw")
    usd_available_to_withdraw: str = Field(alias="usdAvailableToWithdraw")

class UserProfileResponse(BaseModel):
    email: str
    id: str

class MarketplaceOffersResponse(BaseModel):
    items: list[OfferItem]
    total: int
    cursor: str

class TargetsByTitleResponse(BaseModel):
    orders: list[BuyOrder]

class ItemSalesHistoryResponse(BaseModel):
    sales: list[ItemSale]

