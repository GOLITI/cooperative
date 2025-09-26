# Mapping des champs réels du modèle Product
# Champs que nous utilisons dans les serializers vs champs réels

# Champs CORRECTS du modèle Product:
# - name
# - code (pas sku)
# - barcode
# - description
# - category (ForeignKey vers ProductCategory)
# - unit (ForeignKey vers Unit)
# - current_stock
# - min_stock_level (pas minimum_stock)
# - max_stock_level (pas maximum_stock) 
# - selling_price
# - purchase_price (pas cost_price)
# - member_price
# - product_type
# - specifications
# - image
# - weight
# - dimensions
# - origin
# - quality_grade
# - expiry_tracking
# - lot_tracking
# - is_active
# - created_at
# - updated_at

# Champs INCORRECTS dans nos serializers:
# sku -> code
# cost_price -> purchase_price
# minimum_stock -> min_stock_level
# maximum_stock -> max_stock_level
# quantity_in_stock -> current_stock
# unit_price -> selling_price