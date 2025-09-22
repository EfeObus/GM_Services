"""
Gadgets Blueprint
E-commerce functionality for gadgets and accessories
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
from models.ecommerce import Product, ProductCategory, ProductBrand, Order, OrderItem, ShoppingCart, CartItem
from models.gadgets import Smartphone, Laptop, Accessory, ProductImage
from models.user import User
from database import db
from werkzeug.utils import secure_filename
from decimal import Decimal
import json
import os
import uuid
from datetime import datetime

# Create blueprint
gadgets_bp = Blueprint('gadgets', __name__, template_folder='templates')

@gadgets_bp.route('/')
def index():
    """Gadgets home page with all categories"""
    try:
        # Get featured products
        featured_products = Product.query.filter_by(is_featured=True, status='active')\
                                       .join(ProductCategory)\
                                       .filter(ProductCategory.slug.in_(['smartphones', 'laptops', 'accessories']))\
                                       .limit(6).all()
        
        # Get categories
        categories = ProductCategory.query.filter(
            ProductCategory.slug.in_(['smartphones', 'laptops', 'accessories'])
        ).all()
        
        return render_template('gadgets/index.html', 
                             featured_products=featured_products,
                             categories=categories)
    except Exception as e:
        # Database not ready, render with empty data
        return render_template('gadgets/index.html', 
                             featured_products=[],
                             categories=[])

@gadgets_bp.route('/smartphones')
def smartphones():
    """Smartphones listing page"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    try:
        # Get smartphones category
        category = ProductCategory.query.filter_by(slug='smartphones').first()
        if not category:
            flash('Smartphones category not found', 'error')
            return redirect(url_for('gadgets.index'))
        
        # Build query
        query = Product.query.filter_by(category_id=category.id, status='active')\
                           .join(Smartphone)
        
        # Apply filters
        brand_filter = request.args.get('brand')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        os_filter = request.args.get('os')
        
        if brand_filter:
            query = query.join(ProductBrand).filter(ProductBrand.name == brand_filter)
        if price_min:
            query = query.filter(Product.price >= price_min)
        if price_max:
            query = query.filter(Product.price <= price_max)
        if os_filter:
            query = query.filter(Smartphone.operating_system == os_filter)
        
        # Get pagination
        products = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        brands = db.session.query(ProductBrand.name)\
                          .join(Product)\
                          .filter(Product.category_id == category.id)\
                          .distinct().all()
        
        operating_systems = db.session.query(Smartphone.operating_system)\
                                    .join(Product)\
                                    .filter(Product.category_id == category.id)\
                                    .distinct().all()
        
        return render_template('gadgets/smartphones.html',
                             products=products,
                             brands=[b[0] for b in brands],
                             operating_systems=[os[0] for os in operating_systems if os[0]],
                             category=category)
    except Exception as e:
        flash('Error loading smartphones', 'error')
        return redirect(url_for('gadgets.index'))

@gadgets_bp.route('/laptops')
def laptops():
    """Laptops listing page"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    try:
        # Get laptops category
        category = ProductCategory.query.filter_by(slug='laptops').first()
        if not category:
            flash('Laptops category not found', 'error')
            return redirect(url_for('gadgets.index'))
        
        # Build query
        query = Product.query.filter_by(category_id=category.id, status='active')\
                           .join(Laptop)
        
        # Apply filters
        brand_filter = request.args.get('brand')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        use_case_filter = request.args.get('use_case')
        
        if brand_filter:
            query = query.join(ProductBrand).filter(ProductBrand.name == brand_filter)
        if price_min:
            query = query.filter(Product.price >= price_min)
        if price_max:
            query = query.filter(Product.price <= price_max)
        if use_case_filter:
            query = query.filter(Laptop.primary_use_case == use_case_filter)
        
        # Get pagination
        products = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        brands = db.session.query(ProductBrand.name)\
                          .join(Product)\
                          .filter(Product.category_id == category.id)\
                          .distinct().all()
        
        use_cases = db.session.query(Laptop.primary_use_case)\
                            .join(Product)\
                            .filter(Product.category_id == category.id)\
                            .distinct().all()
        
        return render_template('gadgets/laptops.html',
                             products=products,
                             brands=[b[0] for b in brands],
                             use_cases=[uc[0] for uc in use_cases if uc[0]],
                             category=category)
    except Exception as e:
        flash('Error loading laptops', 'error')
        return redirect(url_for('gadgets.index'))

@gadgets_bp.route('/accessories')
def accessories():
    """Accessories listing page"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    try:
        # Get accessories category
        category = ProductCategory.query.filter_by(slug='accessories').first()
        if not category:
            flash('Accessories category not found', 'error')
            return redirect(url_for('gadgets.index'))
        
        # Build query
        query = Product.query.filter_by(category_id=category.id, status='active')\
                           .join(Accessory)
        
        # Apply filters
        brand_filter = request.args.get('brand')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        accessory_type_filter = request.args.get('type')
        
        if brand_filter:
            query = query.join(ProductBrand).filter(ProductBrand.name == brand_filter)
        if price_min:
            query = query.filter(Product.price >= price_min)
        if price_max:
            query = query.filter(Product.price <= price_max)
        if accessory_type_filter:
            query = query.filter(Accessory.accessory_type == accessory_type_filter)
        
        # Get pagination
        products = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        brands = db.session.query(ProductBrand.name)\
                          .join(Product)\
                          .filter(Product.category_id == category.id)\
                          .distinct().all()
        
        accessory_types = db.session.query(Accessory.accessory_type)\
                                  .join(Product)\
                                  .filter(Product.category_id == category.id)\
                                  .distinct().all()
        
        return render_template('gadgets/accessories.html',
                             products=products,
                             brands=[b[0] for b in brands],
                             accessory_types=[at[0] for at in accessory_types if at[0]],
                             category=category)
    except Exception as e:
        flash('Error loading accessories', 'error')
        return redirect(url_for('gadgets.index'))

@gadgets_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Get product-specific details
        smartphone_details = None
        laptop_details = None
        accessory_details = None
        
        if hasattr(product, 'smartphone_details') and product.smartphone_details:
            smartphone_details = product.smartphone_details
        elif hasattr(product, 'laptop_details') and product.laptop_details:
            laptop_details = product.laptop_details
        elif hasattr(product, 'accessory_details') and product.accessory_details:
            accessory_details = product.accessory_details
        
        # Get related products
        related_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.status == 'active'
        ).limit(4).all()
        
        return render_template('gadgets/product_detail.html',
                             product=product,
                             smartphone_details=smartphone_details,
                             laptop_details=laptop_details,
                             accessory_details=accessory_details,
                             related_products=related_products)
    except Exception as e:
        flash('Product not found', 'error')
        return redirect(url_for('gadgets.index'))

@gadgets_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    try:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', 1, type=int)
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'})
        
        product = Product.query.get_or_404(product_id)
        
        if not product.is_in_stock:
            return jsonify({'success': False, 'message': 'Product out of stock'})
        
        # Handle cart for logged-in users
        if current_user.is_authenticated:
            cart = ShoppingCart.query.filter_by(user_id=current_user.id).first()
            if not cart:
                cart = ShoppingCart(user_id=current_user.id)
                db.session.add(cart)
                db.session.flush()
            
            # Check if item already in cart
            cart_item = CartItem.query.filter_by(
                cart_id=cart.id, 
                product_id=product_id
            ).first()
            
            if cart_item:
                cart_item.quantity += quantity
                cart_item.updated_at = datetime.utcnow()
            else:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price
                )
                db.session.add(cart_item)
            
            db.session.commit()
        else:
            # Handle cart for anonymous users using session
            if 'cart' not in session:
                session['cart'] = {}
            
            cart = session['cart']
            product_id_str = str(product_id)
            
            if product_id_str in cart:
                cart[product_id_str]['quantity'] += quantity
            else:
                cart[product_id_str] = {
                    'quantity': quantity,
                    'unit_price': float(product.price),
                    'product_name': product.name
                }
            
            session['cart'] = cart
            session.modified = True
        
        return jsonify({
            'success': True, 
            'message': 'Product added to cart successfully',
            'cart_count': get_cart_count()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error adding to cart'})

@gadgets_bp.route('/cart')
def view_cart():
    """View shopping cart"""
    try:
        cart_items = []
        total_amount = 0
        
        if current_user.is_authenticated:
            cart = ShoppingCart.query.filter_by(user_id=current_user.id).first()
            if cart:
                cart_items = cart.items.all()
                total_amount = cart.total_amount
        else:
            # Handle session cart
            if 'cart' in session:
                for product_id_str, item_data in session['cart'].items():
                    product = Product.query.get(int(product_id_str))
                    if product:
                        cart_items.append({
                            'product': product,
                            'quantity': item_data['quantity'],
                            'unit_price': Decimal(str(item_data['unit_price'])),
                            'total_price': Decimal(str(item_data['unit_price'])) * item_data['quantity']
                        })
                        total_amount += Decimal(str(item_data['unit_price'])) * item_data['quantity']
        
        return render_template('gadgets/cart.html',
                             cart_items=cart_items,
                             total_amount=total_amount)
    except Exception as e:
        flash('Error loading cart', 'error')
        return redirect(url_for('gadgets.index'))

@gadgets_bp.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    try:
        product_id = request.form.get('product_id', type=int)
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'})
        
        if current_user.is_authenticated:
            cart = ShoppingCart.query.filter_by(user_id=current_user.id).first()
            if cart:
                cart_item = CartItem.query.filter_by(
                    cart_id=cart.id, 
                    product_id=product_id
                ).first()
                if cart_item:
                    db.session.delete(cart_item)
                    db.session.commit()
        else:
            # Handle session cart
            if 'cart' in session:
                cart = session['cart']
                product_id_str = str(product_id)
                if product_id_str in cart:
                    del cart[product_id_str]
                    session['cart'] = cart
                    session.modified = True
        
        return jsonify({
            'success': True, 
            'message': 'Item removed from cart',
            'cart_count': get_cart_count()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error removing item'})

def get_cart_count():
    """Get total items in cart"""
    try:
        if current_user.is_authenticated:
            cart = ShoppingCart.query.filter_by(user_id=current_user.id).first()
            return cart.total_items if cart else 0
        else:
            if 'cart' in session:
                return sum(item['quantity'] for item in session['cart'].values())
            return 0
    except:
        return 0

# Template context processor to make cart count available in all templates
@gadgets_bp.context_processor
def inject_cart_count():
    return {'cart_count': get_cart_count()}

@gadgets_bp.route('/search')
def search():
    """Search products"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    if not query:
        return redirect(url_for('gadgets.index'))
    
    try:
        # Search in product names and descriptions
        products = Product.query.filter(
            db.or_(
                Product.name.contains(query),
                Product.description.contains(query),
                Product.short_description.contains(query)
            ),
            Product.status == 'active'
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('gadgets/search_results.html',
                             products=products,
                             query=query)
    except Exception as e:
        flash('Error performing search', 'error')
        return redirect(url_for('gadgets.index'))