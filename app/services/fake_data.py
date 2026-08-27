from dataclasses import dataclass
from app.models import Customer, Category, Product, Order, OrderItem

@dataclass
class ECommerceWorld:
  customers: list[Customer]
  categories: list[Category]
  products: list[Product]
  orders: list[Order]
  order_items: list[OrderItem]

  # customer_map: dict # commented this and below 2026-08-01
  # category_map: dict
  # product_map: dict
  # order_map: dict
  # order_item_map: dict


