from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

def order_count(db: Session, city: str = None, category = None):
    if city is None and category is None:
        return db.execute(text("SELECT COUNT(*) FROM order_items")).scalar()
    elif category is None:
        query = text("""SELECT COUNT(oi.id)
                        FROM customers c
                        JOIN orders o ON o.customer_id = c.id
                        JOIN order_items oi ON oi.order_id = o.id
                        WHERE c.city = :city""")
        return db.execute(query, {"city": city}).scalar()
    elif city is None:
        query = text("""SELECT COUNT(oi.id)
                        FROM categories cat
                        JOIN products p ON p.category_id = cat.id
                        JOIN order_items oi ON oi.product_id = p.id
            WHERE cat.name = :category""")
        return db.execute(query, {"category": category}).scalar()
    else:
        query = text("""SELECT COUNT(oi.id)
                        FROM customers c
                        JOIN orders o ON o.customer_id = c.id
                        JOIN order_items oi ON oi.order_id = o.id
                        JOIN products p ON p.id = oi.product_id
                        JOIN categories cat ON cat.id = p.category_id
                        WHERE c.city = :city
                        AND cat.name = :category""")
        return db.execute(query, {"city": city, "category": category}).scalar()


def customer_count(db, city=None):
    if city is None:
        query = text("SELECT COUNT(*) FROM customers")
        return db.execute(query).scalar()
    else:
        query = text("""SELECT COUNT(*) 
                        FROM customers c 
                        WHERE c.city = :city""")
        return db.execute(query, {"city": city}).scalar()



def total_sales(db, city=None, category=None, year=None):
    # city별, category별, year별 총 매출액
    if year is None:
        if city is None and category is None:
            query = text("SELECT SUM(quantity*unit_price) FROM order_items")
            return db.execute(query).scalar()

        elif category is None: # city 값이 주어진 경우
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM customers c
                            JOIN orders o ON o.customer_id = c.id
                            JOIN order_items oi ON oi.order_id = o.id
                            WHERE c.city = :city""")
            return db.execute(query, {"city": city}).scalar()

        elif city is None: # category값만 주어진 경우
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM categories cat
                            JOIN products p ON p.category_id = cat.id
                            JOIN order_items oi ON oi.product_id = p.id
                            WHERE cat.name = :category""")
            return db.execute(query, {"category": category}).scalar()

        else: # city값과 category값 둘다 주어진 경우
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM customers c
                            JOIN orders o ON o.customer_id = c.id
                            JOIN order_items oi ON oi.order_id = o.id
                            JOIN products p ON p.id = oi.product_id
                            JOIN categories cat ON cat.id = p.category_id
                            WHERE c.city = :city
                              AND cat.name = :category""")
            return db.execute(query, {"city": city, "category": category}).scalar()
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        if city is None and category is None:
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM customers c
                            JOIN orders o ON o.customer_id = c.id
                            JOIN order_items oi ON oi.order_id = o.id
                            WHERE o.order_date >= :start_date
                              AND o.order_date < :end_date""")
            return db.execute(query, {"start_date": start_date, "end_date": end_date}).scalar()
        elif category is None:  # city 값이 주어진 경우
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM customers c
                            JOIN orders o ON o.customer_id = c.id
                            JOIN order_items oi ON oi.order_id = o.id
                            WHERE c.city = :city
                              AND o.order_date >= :start_date
                              AND o.order_date < :end_date""")
            return db.execute(query, {"city": city, "start_date": start_date, "end_date": end_date}).scalar()
        elif city is None:  # category 값이 주어진 경우
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM customers c
                            JOIN orders o ON o.customer_id = c.id
                            JOIN order_items oi ON oi.order_id = o.id
                            JOIN products p ON p.id = oi.product_id
                            JOIN categories cat ON cat.id = p.category_id
                            WHERE cat.name = :category
                              AND o.order_date >= :start_date
                              AND o.order_date < :end_date""")
            return db.execute(query, {"category": category, "start_date": start_date, "end_date": end_date}).scalar()
        else:
            query = text("""SELECT SUM(oi.quantity * oi.unit_price)
                            FROM customers c
                            JOIN orders o ON o.customer_id = c.id
                            JOIN order_items oi ON oi.order_id = o.id
                            JOIN products p ON p.id = oi.product_id
                            JOIN categories cat ON cat.id = p.category_id
                            WHERE c.city = :city
                              AND cat.name = :category
                              AND o.order_date >= :start_date
                              AND o.order_date < :end_date""")
            return db.execute(query, {"city": city, "category": category, "start_date": start_date, "end_date": end_date}).scalar()



def category_sales(db, city=None):
    query = text("SELECT name FROM categories")

    return {item['name']: total_sales(db, city, item['name']) for item in db.execute(query).mappings().all()}



def yearly_sales(db):
    query = text("SELECT DISTINCT EXTRACT(YEAR FROM order_date)::int AS order_year FROM orders ORDER BY order_year")

    return {year: total_sales(db, None, None, year) for year in db.execute(query).scalars()}



def top_category(db, city=None):
    sales_categories = category_sales(db, city)
    top_sales = max(sales_categories.values())

    for key, value in sales_categories.items():
        if value == top_sales:
            return key


def city_sales(db, category=None):
    query = text("SELECT DISTINCT city FROM customers")
    city_list = [item['city'] for item in db.execute(query).mappings().all()]

    return {city: total_sales(db, city, category) for city in city_list}



def monthly_sales(db, city = None):
    table_exists = db.execute(text("""
                                   SELECT EXISTS (SELECT
                                                  FROM pg_tables
                                                  WHERE schemaname = 'public'
                                                    AND tablename = 'customers');
                                   """)).scalar()

    if not table_exists:
        return {"months": [0], 'sales': [0]}

    if city is None:
        query = text("""SELECT TO_CHAR(DATE_TRUNC('month', o.order_date), 'YYYY-MM') AS year_month,
                        SUM(oi.quantity * oi.unit_price) AS total_sales
                        FROM orders o
                        JOIN order_items oi ON oi.order_id = o.id
                        GROUP BY DATE_TRUNC('month', o.order_date)
                        ORDER BY year_month""")
        results = db.execute(query).mappings().all()
    else:
        query = text("""SELECT TO_CHAR(DATE_TRUNC('month', o.order_date), 'YYYY-MM') AS year_month,
                        SUM(oi.quantity * oi.unit_price) AS total_sales
                        FROM customers c
                        JOIN orders o ON o.customer_id = c.id
                        JOIN order_items oi ON oi.order_id = o.id
                        WHERE c.city = :city
                        GROUP BY DATE_TRUNC('month', o.order_date)
                        ORDER BY year_month""")
        results = db.execute(query, {"city": city}).mappings().all()

    return {"months": [item['year_month'] for item in results],
            'sales': [item['total_sales'] for item in results]}


def piechart_categories(db, city=None):
    table_exists = db.execute(text("""
                                   SELECT EXISTS (SELECT
                                                  FROM pg_tables
                                                  WHERE schemaname = 'public'
                                                    AND tablename = 'customers');
                                   """)).scalar()

    if not table_exists:
        return {"None": 0}

    return category_sales(db, city)


def barchart_cities(db, category=None):
    table_exists = db.execute(text("""
                                   SELECT EXISTS (SELECT
                                                  FROM pg_tables
                                                  WHERE schemaname = 'public'
                                                    AND tablename = 'customers');
                                   """)).scalar()

    if not table_exists:
        return {"None": 0}
    return city_sales(db, category)


def dashboard_summary(db, city=None, category=None):
    table_exists = db.execute(text("""
                                   SELECT EXISTS (SELECT
                                                  FROM pg_tables
                                                  WHERE schemaname = 'public'
                                                    AND tablename = 'customers');
                                   """)).scalar()

    if table_exists:
        # Your logic when the table exists
        return {
            "sales": total_sales(db, city, category),
            "orders": order_count(db, city, category),
            "customers": customer_count(db, city),
            "top_category": top_category(db, city)
        }
    else:
        return {
            "sales": 0,
            "orders": 0,
            "customers": 0,
            "top_category": "None"
        }


def analyse(db):
    from app.models import Order, OrderItem # Customer, Category, Product,
    # customers = db.query(Customer).all() # 사용하지 않아도 되는 것 같음.
    # categories = db.query(Category).all() # 사용하지 않아도 되는 것 같음.
    # products = db.query(Product).all() # 사용하지 않아도 되는 것 같음.
    orders = db.query(Order).all()
    order_items = db.query(OrderItem).all()

    city = 'Seoul' # ['Seoul', 'Incheon', 'Seoul']
    category = 'mobile' # ['Home Theater', 'mobile', 'drink']
    print('계산결과: order_count(db): ', order_count(db))
    print('계산결과: python_order_count(db)', len(order_items))

    print(f'계산결과: order_count(db, {city}): ', order_count(db, city)) # ok
    ordersN = []
    for oi in order_items:
        if oi.order.customer.city == city:
            ordersN.append(oi)
    print(f'계산결과: python_order_count(db, {city})', len(ordersN))  # ok

    print(f'계산결과: order_count(db, None, {category}): ', order_count(db, None, category)) # ok
    ordersN = []
    for oi in order_items:
        if oi.product.category.name == category:
            ordersN.append(oi)
    print(f'계산결과: python_order_count(db, None, {category})', len(ordersN)) # ok

    print(f'계산결과: order_count(db, {city}, {category}): ', order_count(db, city, category)) # ok
    ordersN = []
    for oi in order_items:
        if oi.product.category.name == category and oi.order.customer.city == city:
            ordersN.append(oi)
    print(f'계산결과: python_order_count(db, {city}, {category})', len(ordersN)) # ok

    print(f'계산결과: total_sales(db, {city}): ', total_sales(db, city)) # ok
    ordersN = []
    for oi in order_items:
        if oi.order.customer.city == city:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, {city})', sum(ordersN)) # ok

    print(f'계산결과: total_sales(db, None, {category}): ', total_sales(db, None, category)) # ok
    ordersN = []
    for oi in order_items:
        if oi.product.category.name == category:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, None, {category})', sum(ordersN)) # ok

    print(f'계산결과: total_sales(db, {city}, {category}): ', total_sales(db, city, category)) # ok
    ordersN = []
    for oi in order_items:
        if oi.product.category.name == category and oi.order.customer.city == city:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, {city}, {category})', sum(ordersN)) # ok

    year = 2025
    print(f'계산결과: total_sales(db, None, None, {year}): ', total_sales(db, None, None, year)) # ok
    ordersN = []
    for oi in order_items:
        if oi.order.order_date.year == year:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, None, None, {year})', sum(ordersN)) # ok

    print(f'계산결과: total_sales(db, {city}, None, {year}): ', total_sales(db, city, None, year)) # ok
    ordersN = []
    for oi in order_items:
        if oi.order.order_date.year == year and oi.order.customer.city == city:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, {city}, None, {year})', sum(ordersN)) # ok

    print(f'계산결과: total_sales(db, None, {category}, {year}): ', total_sales(db, None, category, year)) # ok
    ordersN = []
    for oi in order_items:
        if oi.order.order_date.year == year and oi.product.category.name == category:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, None, {category}, {year})', sum(ordersN)) # ok

    print(f'계산결과: total_sales(db, {city}, {category}, {year}): ', total_sales(db, city, category, year)) # ok
    ordersN = []
    for oi in order_items:
        if oi.order.order_date.year == year and oi.product.category.name == category and oi.order.customer.city == city:
            ordersN.append(oi.quantity * oi.unit_price)
    print(f'파이썬 계산결과: total_sales(db, {city}, {category}, {year})', sum(ordersN)) # ok


    print('계산결과: yearly_sales', yearly_sales(db)) # ok
    years = set([o.order_date.year for o in orders])
    yearsSales = {}
    for year in years:
        ordersN = []
        for oi in order_items:
            if oi.order.order_date.year == year:
                ordersN.append(oi.quantity * oi.unit_price)
        yearsSales[year] = sum(ordersN)
    print('파이썬 계산결과: yearly_sales(db)', yearsSales) # ok


    cities = set([o.customer.city for o in orders])
    print('계산 결과 city_sales(db):', city_sales(db)) # ok
    citySales = {}
    for city in cities:
        ordersN = []
        for oi in order_items:
            if oi.order.customer.city == city:
                ordersN.append(oi.quantity * oi.unit_price)
        citySales[city] = sum(ordersN)
    print('파이썬 계산결과: city_sales(db)', citySales) # ok

    print(f'계산 결과 city_sales(db, {category}):', city_sales(db, category)) # ok
    citySales = {}
    for city in cities:
        ordersN = []
        for oi in order_items:
            if oi.order.customer.city == city and oi.product.category.name == category:
                ordersN.append(oi.quantity * oi.unit_price)
        citySales[city] = sum(ordersN)
    print(f'파이썬 계산결과: city_sales(db, {category})', citySales) # ok

    print('계산 결과 monthly_sales(db, city = None): ', monthly_sales(db))
    months = {month: sum(oi.quantity*oi.unit_price for oi in order_items if oi.order.order_date.strftime('%Y-%m') == month) for month in sorted(set([o.order_date.strftime('%Y-%m') for o in orders]))}
    print(months)

    print(f'계산 결과 monthly_sales(db, city = {city}): ', monthly_sales(db, city))
    months = {month: sum(oi.quantity*oi.unit_price for oi in order_items if oi.order.order_date.strftime('%Y-%m') == month and oi.order.customer.city == city) for month in sorted(set([o.order_date.strftime('%Y-%m') for o in orders]))}
    print(months)