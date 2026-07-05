from pydantic import AliasPath, BaseModel, Field

class OfferItem(BaseModel):
    created_at: str = Field(alias="createdAt")
    offer_id: str = Field(alias="offerId")
    price_cents: int = Field(alias="priceCents")
    locked: bool
    title: str = Field(validation_alias=AliasPath("attributes", "title"))
    category_path: str = Field(validation_alias=AliasPath("attributes", "categoryPath"))
    tradable: bool = Field(validation_alias=AliasPath("attributes", "tradable"))

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


