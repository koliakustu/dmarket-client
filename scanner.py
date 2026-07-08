import time
import database
from dmarket.client import DMarketClient
from dmarket.models import *

def populate_items(client: DMarketClient, title: str | None = None, category_path: str | None = None, update_offers: bool = True) -> None:
    offers: list[OfferItem] = []
    cursor: str | None = None

    while True:
        response = client.get_market_offers(title=title, category_path=category_path, limit=100, cursor=cursor)
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

def sync_item_offers(client: DMarketClient, title: str) -> None:
    offers_dict: dict[int, int] = {}
    cursor: str | None = None

    while True:
        offers_response: MarketplaceOffersResponse = client.get_market_offers(title=title, limit=100, cursor=cursor)
        for offer in offers_response.items:
            price = offer.price
            if price in offers_dict:
                offers_dict[price] += 1
            else:
                offers_dict[price] = 1
        cursor = offers_response.cursor
        if not cursor:
            break
    database.update_offers(title, offers_dict)

def sync_item_orders(client: DMarketClient, title: str) -> None:
    orders_response: TargetsByTitleResponse = client.get_targets_by_title(title=title)
    orders_dict: dict[int, int] = {}
    for order in orders_response.orders:
        orders_dict[order.price] = order.amount

    database.update_orders(title, orders_dict)

def sync_item_sales(client: DMarketClient, title: str, days_limit: int = 30) -> None:
    seconds_in_day = 86400
    cutoff_timestamp = int(time.time()) - (days_limit * seconds_in_day)

    last_known_date = database.get_last_sale_date(title)
    if last_known_date:
        stop_timestamp = max(last_known_date, cutoff_timestamp)
    else:
        stop_timestamp = cutoff_timestamp

    sales: list[tuple[int, int, int]] = []
    offset = 0
    while True:
        sales_response: ItemSalesHistoryResponse = client.get_item_sales_history(title=title, limit=100, offset=offset)
        if not sales_response.sales:
            break
        for sale in sales_response.sales:
            if sale.date <= stop_timestamp:
                break
            sales.append((sale.date, sale.price, 1 if sale.operation_type == "Target" else 0))
        offset += len(sales_response.sales)

    database.update_sales(title, sales)

def sync_item_data(client: DMarketClient, title: str) -> None:
    database.touch_item_timestamp(title)
    sync_item_offers(client=client, title=title)
    sync_item_orders(client=client, title=title)
    sync_item_sales(client=client, title=title)


