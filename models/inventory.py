"""
Inventory Management Models
Handles inventory tracking, staff assignments, and low stock alerts
"""
from database import db
from datetime import datetime
from decimal import Decimal
import uuid

class InventoryLocation(db.Model):
    """Physical locations/warehouses for inventory"""
    
    __tablename__ = 'inventory_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Address Information
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Nigeria')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Manager/Staff Assignment
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', backref='managed_locations')
    inventory_items = db.relationship('InventoryItem', backref='location', lazy='dynamic')
    stock_movements = db.relationship('StockMovement', backref='stock_location', lazy='dynamic')
    staff_assignments = db.relationship('StaffLocationAssignment', backref='assigned_location', lazy='dynamic')
    
    def __repr__(self):
        return f'<InventoryLocation {self.name}>'

class StaffLocationAssignment(db.Model):
    """Staff assignments to specific inventory locations/areas"""
    
    __tablename__ = 'staff_location_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    
    # Assignment Details
    role = db.Column(db.String(50))  # manager, supervisor, clerk, etc.
    permissions = db.Column(db.JSON)  # List of permissions for this location
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('User', backref='location_assignments')
    
    def __repr__(self):
        return f'<StaffLocationAssignment {self.staff.full_name} -> {self.assigned_location.name}>'

class InventoryItem(db.Model):
    """Inventory tracking for all products across locations"""
    
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Product Information
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    jewelry_item_id = db.Column(db.Integer, db.ForeignKey('jewelry_items.id'))
    automobile_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    
    # Location
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    
    # Stock Information
    current_stock = db.Column(db.Integer, default=0, nullable=False)
    reserved_stock = db.Column(db.Integer, default=0)
    available_stock = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=2)  # Default low stock threshold
    max_stock_level = db.Column(db.Integer)
    
    # Cost Information
    unit_cost = db.Column(db.Numeric(10, 2))
    total_value = db.Column(db.Numeric(12, 2))
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, discontinued
    
    # Timestamps
    last_counted = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='inventory_items')
    jewelry_item = db.relationship('JewelryItem', backref='inventory_items')
    automobile = db.relationship('Vehicle', backref='inventory_items')
    stock_movements = db.relationship('StockMovement', backref='inventory_item', lazy='dynamic')
    low_stock_alerts = db.relationship('LowStockAlert', backref='inventory_item', lazy='dynamic')
    
    def __repr__(self):
        return f'<InventoryItem {self.get_item_name()} at {self.location.name}>'
    
    def get_item_name(self):
        """Get the name of the associated item"""
        if self.product:
            return self.product.name
        elif self.jewelry_item:
            return self.jewelry_item.name
        elif self.automobile:
            return f"{self.automobile.make.name} {self.automobile.model.name}"
        return "Unknown Item"
    
    def get_item_sku(self):
        """Get the SKU of the associated item"""
        if self.product:
            return self.product.sku
        elif self.jewelry_item:
            return getattr(self.jewelry_item, 'sku', 'N/A')
        elif self.automobile:
            return getattr(self.automobile, 'vin', 'N/A')
        return "N/A"
    
    def get_item_description(self):
        """Get the description of the associated item"""
        if self.product:
            return self.product.description or self.product.short_description
        elif self.jewelry_item:
            return getattr(self.jewelry_item, 'description', '')
        elif self.automobile:
            return f"{self.automobile.year} {self.automobile.make.name} {self.automobile.model.name}"
        return ""
    
    def get_item_category(self):
        """Get the category of the associated item"""
        if self.product and self.product.category:
            return self.product.category.name
        elif self.jewelry_item:
            return getattr(self.jewelry_item, 'category', 'Jewelry')
        elif self.automobile:
            return "Automobile"
        return "Uncategorized"
    
    def get_item_price(self):
        """Get the selling price of the associated item"""
        if self.product:
            return self.product.price
        elif self.jewelry_item:
            return getattr(self.jewelry_item, 'price', None)
        elif self.automobile:
            return getattr(self.automobile, 'price', None)
        return None
    
    @property
    def is_low_stock(self):
        """Check if item is at or below reorder point"""
        return self.available_stock <= self.reorder_point
    
    @property
    def is_out_of_stock(self):
        """Check if item is completely out of stock"""
        return self.available_stock <= 0
    
    def update_available_stock(self):
        """Calculate and update available stock"""
        self.available_stock = max(0, self.current_stock - self.reserved_stock)
        return self.available_stock

class StockMovement(db.Model):
    """Track all stock movements (in, out, transfers, adjustments)"""
    
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # References
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Movement Details
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, transfer, adjustment, sale, return
    quantity = db.Column(db.Integer, nullable=False)
    
    # Reference Information
    reference_type = db.Column(db.String(50))  # order, purchase, transfer, adjustment
    reference_id = db.Column(db.String(50))
    
    # Additional Information
    notes = db.Column(db.Text)
    unit_cost = db.Column(db.Numeric(10, 2))
    
    # Balances after movement
    stock_before = db.Column(db.Integer)
    stock_after = db.Column(db.Integer)
    
    # Timestamps
    movement_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} for {self.inventory_item.get_item_name()}>'

class LowStockAlert(db.Model):
    """Low stock alerts for inventory management"""
    
    __tablename__ = 'low_stock_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # References
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    
    # Alert Details
    alert_level = db.Column(db.String(20), default='low')  # low, critical, out_of_stock
    current_stock = db.Column(db.Integer, nullable=False)
    reorder_point = db.Column(db.Integer, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    acknowledged_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    acknowledged_by = db.relationship('User', backref='acknowledged_alerts')
    
    def __repr__(self):
        return f'<LowStockAlert {self.alert_level} for {self.inventory_item.get_item_name()}>'
    
    @property
    def is_critical(self):
        """Check if alert is critical (less than 2 items)"""
        return self.current_stock < 2

class InventoryAudit(db.Model):
    """Inventory audit/cycle count records"""
    
    __tablename__ = 'inventory_audits'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # References
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Audit Details
    audit_type = db.Column(db.String(20), default='cycle_count')  # cycle_count, full_audit
    status = db.Column(db.String(20), default='in_progress')  # planned, in_progress, completed, cancelled
    
    # Date Information
    scheduled_date = db.Column(db.Date)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Summary
    total_items_counted = db.Column(db.Integer, default=0)
    discrepancies_found = db.Column(db.Integer, default=0)
    total_value_difference = db.Column(db.Numeric(12, 2), default=0)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    auditor = db.relationship('User', backref='conducted_audits')
    audit_items = db.relationship('InventoryAuditItem', backref='audit', lazy='dynamic')
    
    def __repr__(self):
        return f'<InventoryAudit {self.audit_type} at {self.location.name}>'

class InventoryAuditItem(db.Model):
    """Individual items counted during inventory audit"""
    
    __tablename__ = 'inventory_audit_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # References
    audit_id = db.Column(db.Integer, db.ForeignKey('inventory_audits.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    
    # Count Information
    system_count = db.Column(db.Integer, nullable=False)
    physical_count = db.Column(db.Integer, nullable=False)
    variance = db.Column(db.Integer, nullable=False)
    
    # Cost Information
    unit_cost = db.Column(db.Numeric(10, 2))
    value_variance = db.Column(db.Numeric(10, 2))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    counted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_item = db.relationship('InventoryItem', backref='audit_items')
    
    def __repr__(self):
        return f'<InventoryAuditItem {self.inventory_item.get_item_name()} variance: {self.variance}>'