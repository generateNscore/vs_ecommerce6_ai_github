import random
from datetime import datetime #, timedelta
from faker import Faker
from app.services.fake_data import ECommerceWorld
from app.models import Customer, Category, Product, Order, OrderItem

# random.seed(12345)
fake = Faker()


def make_customer_names(customer_count):
    from app.data.names import words

    customer_names = []
    while len(customer_names) < customer_count:
        name = ' '.join(random.sample(words,2))
        if name not in customer_names:
            customer_names.append(name)
    return customer_names


def make_dates(order_count):
    # years = [f"{random.choice(range(2023, 2026))}" for _ in range(order_count)]
    # month_days = [(random.choice(range(1, 13)), random.choice(range(1, 32))) for _ in range(order_count)]
    # hour_mins = [(random.choice(range(10, 20)), random.choice(range(1, 60))) for _ in range(order_count)]
    # for j, (m,d) in enumerate(month_days):
    #     if m in [4, 6, 9, 11] and d>30:
    #         month_days[j] = (m, d-1)
    #     elif m == 2 and d>28:
    #         month_days[j] = (m, 28)
    # return [y+f"-{m:02d}-{d:02d} {h}::{minute:02d}" for y, (m, d), (h, minute) in zip(years, month_days, hour_mins)]
    return [fake.date_time_between(start_date=datetime(2023,1,1), end_date=datetime(2025, 12, 31)) for _ in range(order_count)]

def make_customers_4_db(orders_on_dates):
    customer_in_orders = {}
    for order in orders_on_dates:
        if order['customer'] not in customer_in_orders: customer_in_orders[order['customer']] = []
        customer_in_orders[order['customer']].append(order)

    customers_4_db = {}
    for customer, purchases in customer_in_orders.items():
        # customers_4_db[customer] = sorted(purchase['order_date'] for purchase in purchases)[0].replace('::', '').replace(' ','-')
        customers_4_db[customer] = sorted(purchase['order_date'] for purchase in purchases)[0]


    return customers_4_db


def make_orders_on_dates(order_dates, customer_names, products_list):
    orders_on_dates = []
    for date in order_dates:
        order_tmp = {'customer': random.choice(customer_names), 'order_date': date}
        products2order_tmp = random.choices(population=products_list, weights=[p for _,_,_,p in products_list], k=random.randint(3, 6))
        order_tmp['products'] = list(set(products2order_tmp)) # all elements unique
        # initials = "".join(word[0].upper() for word in order_tmp['customer'].split())
        # order_tmp['order_code'] = "ORD-"+initials+order_tmp['order_date'].replace('::', '').replace(' ','-')
        order_tmp['order_code'] = fake.unique.bothify(text='ORD-######')
        orders_on_dates.append(order_tmp)
    return orders_on_dates


def make_products_list(count):
    from app.data.products import products_dict

    keysN = len(products_dict)
    valuesN = min([len(v) for v in products_dict.values()])

    if count[0] < keysN:
        keys = random.sample(list(products_dict.keys()), count[0])
        if count[1] < valuesN:
            new_products_dict = {k: random.sample(products_dict[k], count[1]) for k in keys}
        else:
            new_products_dict = {k: products_dict[k] for k in keys}
    else:
        if count[1] < valuesN:
            new_products_dict = {k: random.sample(v, count[1]) for k,v in products_dict.items()}
            pass
        else:
            new_products_dict = products_dict

    products_list = []
    for k, product_dict in new_products_dict.items():
        products_list.extend([(k, v[0], v[1], v[2]) for v in product_dict])

    return new_products_dict, products_list


def create_customers(customers_id, city_count):
    from app.data.cities import cities

    if city_count < len(cities):
        cities2search = cities[:city_count]
    else:
        cities2search = cities

    cities = [c for c,_ in cities2search]
    weights = [p for _,p in cities2search]

    customers = []
    # customer_map = {}
    for name, _id in customers_id.items():
        # year, month, day, hNm = _id.split('-')
        # initials = "".join(word[0].upper() for word in name.split())
        # tmp = Customer(name = name,
        #                city = random.choices(population = cities,
        #                                      weights = weights,
        #                                      k=1)[0],
        #                signup_date = _id)
        # customers.append(tmp)
        customers.append(Customer(name = name, city = random.choices(population = cities, weights = weights, k=1)[0], signup_date=_id))
        # customer_map[name] = tmp
    # return customers, customer_map
    return customers

# def create_orders(orders_on_dates,customer_map):
#     orders = []
#     order_map = {}
#     for order in orders_on_dates:
#         tmp = Order(order_date=order['order_date'],
#                     order_code=order['order_code'],
#                     customer=customer_map[order['customer']])
#         orders.append(tmp)
#         order_map[order['order_code']] = tmp
#     return orders, order_map

def create_orders(orders_on_dates, customers):
    orders = []
    # order_map = {}
    for order in orders_on_dates:
        tmp = Order(order_date=order['order_date'],
                    order_code=order['order_code'])
        indx = next((i for i, user in enumerate(customers) if user.name == order['customer']), -1)
        tmp.customer = customers[indx]
        orders.append(tmp)
        # order_map[order['order_code']] = tmp
    # return orders, order_map
    return orders

# def create_order_items(orders_on_dates, order_map, product_map):
#     order_items = []
#     order_item_map = {}
#     for order in orders_on_dates:
#         for product in order['products']:
#             tmp = Order_item(
#                 order=order_map[order['order_code']],
#                 product=product_map[product[1]],
#                 quantity=random.choice(range(1,5)),
#                 unit_price=product[2]
#             )
#             order_items.append(tmp)
#             order_item_map.setdefault(order['order_code'],[]).append(tmp)
#     return order_items, order_item_map

def create_order_items(orders_on_dates, orders, products):
    # print(list(vars(orders[0]).keys()), ' --  Order object attributes') # do not delete this
    # print(list(vars(products[0]).keys()), ' --  Product object attributes')  # do not delete this

    order_items = []
    for j, order in enumerate(orders_on_dates):
        # print(f'{j}-번째 order: ', order, 'products-N: ', len(order['products']))
        for product in order['products']:
            tmp = OrderItem(
                quantity=random.choice(range(1,5)),
                unit_price=product[2]
            )
            idx = next((i for i, item in enumerate(orders) if item.order_code == order['order_code']), -1)
            tmp.order = orders[idx]
            idx = next((i for i, item in enumerate(products) if item.name == product[1]), -1)
            tmp.product = products[idx]
            order_items.append(tmp)
    return order_items


# def create_products(products_dict, category_map):
#     products = []
#     product_map = {}
#     for k, v in products_dict.items():
#         for name, price, popularity in v:
#             tmp = Product(name=name,price=price,category=category_map[k])
#             product_map[name] = tmp
#             products.append(tmp)
#     return products, product_map

def create_products(products_dict, categories):
    products = []
    # product_map = {}
    for k, v in products_dict.items():
        for name, price, popularity in v:
            tmp = Product(name=name,price=price)
            # categories를 차례로 꺼내 name값이 k와 일치하면 그 index를 반환하고 종료하며, 없으면 -1을 반환.
            indx = next((i for i, item in enumerate(categories) if item.name == k), -1)
            tmp.category=categories[indx]
            # product_map[name] = tmp
            products.append(tmp)
    # return products, product_map
    return products

def create_categories(products_dict):
    categories = []
    # category_map = {}
    for k, v in products_dict.items():
        tmp = Category(name=k)
        # category_map[k] = tmp
        categories.append(tmp)
    # return categories, category_map
    return categories


def generate_fake_data(
        customer_count = 10,
        product_count = (4,4),
        order_count = 5,
        city_count=5,
    ):

    products_dict, products_list = make_products_list(product_count)

    customer_names = make_customer_names(customer_count)

    order_dates = make_dates(order_count)

    orders_on_dates = make_orders_on_dates(order_dates, customer_names, products_list)

    customers_4_db = make_customers_4_db(orders_on_dates)

    customers = create_customers(customers_4_db, city_count)

    orders = create_orders(orders_on_dates, customers)

    categories = create_categories(products_dict)

    products = create_products(products_dict, categories)

    order_items = create_order_items(orders_on_dates, orders, products)

    return ECommerceWorld(
        customers = customers,
        categories = categories,
        products = products,
        orders = orders,
        order_items = order_items,
    )


if __name__ == "__main__":
    world = generate_fake_data()
    print([c.name for c in world.customers])
    print([cat.name for cat in world.categories])