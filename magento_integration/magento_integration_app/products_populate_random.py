import random
from django.db import transaction
from magento_integration.magento_integration_app.models import Product, Category

def generate_random_products(num_products):
    categories = Category.objects.all()
    product_names = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    descriptions = ['Lorem ipsum dolor sit amet', 'Consectetur adipiscing elit', 'Sed do eiusmod tempor incididunt', 'Ut labore et dolore magna aliqua']
    prices = [9.99, 19.99, 29.99, 39.99, 49.99]
    magento_skus = ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005']
    sizes = ['S', 'M', 'L', 'XL', 'XXL']

    with transaction.atomic():
        for _ in range(num_products):
            category = random.choice(categories)
            name = random.choice(product_names)
            description = random.choice(descriptions)
            price = random.choice(prices)
            magento_sku = random.choice(magento_skus)
            size = random.choice(sizes)
            stock_quantity = random.randint(0, 100)

            product = Product.objects.create(
                category=category,
                name=name,
                description=description,
                price=price,
                magento_sku=magento_sku,
                size=size,
                stock_quantity=stock_quantity
            )
            product.update_availability()

if __name__ == "__main__":
    num_products_to_generate = 10
    generate_random_products(num_products_to_generate)
    print(f"Added {num_products_to_generate} random products to the database.")
