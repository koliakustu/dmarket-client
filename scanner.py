import database
from dmarket.client import DMarketClient
from dmarket.models import OfferItem

def populate_items(client: DMarketClient, category_path: str | None = None, update_offers: bool = True) -> None:
    offers: list[OfferItem] = []
    cursor: str | None = None

    while True:
        response = client.get_market_offers(category_path=category_path, limit=100, cursor=cursor)
        offers.extend(response.items)
        cursor = response.cursor
        if not cursor:
            break

    items_dict = {}
    for offer in offers:
        item_tuple = (offer.title, offer.category_path)
        price = offer.price
        if item_tuple not in items_dict:
            items_dict[item_tuple] = {}
        if price not in items_dict[item_tuple]:
            items_dict[item_tuple][price] = 0

        items_dict[item_tuple][price] += 1

    database.add_items(list(items_dict.keys()))

    if update_offers:
        for item_tuple, prices_dict in items_dict.items():
            database.update_offers(item_tuple[0], prices_dict)

