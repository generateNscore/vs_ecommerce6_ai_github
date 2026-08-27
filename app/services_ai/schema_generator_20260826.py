from app.database import Base
# This import is REQUIRED to register your tables on Base.metadata
# import app.models

def generate_db_schema() -> str:
    lines = []
    for table in Base.metadata.tables.values():
        if table.name not in ['customers','categories','products','orders','order_items']:
            continue
        lines.append(f"Table {table.name}:")
        for col in table.columns:
            desc = f" - {col.name} ({col.type})"
            if col.primary_key: desc += " PK"
            if col.foreign_keys:
                fk = list(col.foreign_keys)[0]
                desc += f" FK -> {fk.column.table.name}.{fk.column.name}"
            lines.append(desc)

    lines.append("""
Relationships:
- customer 1--N orders (orders.customer_id)
- category 1--N products (products.category_id)
- order 1--N order_items (order_items.order_id)
- product 1--N order_items (order_items.product_id)

Business Rules:
- 매출/수익 = SUM(order_items.quantity * order_items.unit_price)
- orders 테이블에는 total_amount가 없음. order_items에서 계산해야 함
- 날짜 필터는 orders.order_date 사용
""")
    return "\n".join(lines)

# Cache it once at startup
DB_SCHEMA = generate_db_schema()