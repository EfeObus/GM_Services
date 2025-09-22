# Database Schema

**GM Services Platform Database Schema Documentation**  
**Version 1.0**  
**Last Updated:** January 1, 2024

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Tables](#core-tables)
3. [Service-Specific Tables](#service-specific-tables)
4. [System Tables](#system-tables)
5. [Relationships and Constraints](#relationships-and-constraints)
6. [Indexes and Performance](#indexes-and-performance)
7. [Data Types and Constraints](#data-types-and-constraints)
8. [Migration History](#migration-history)
9. [Backup and Recovery](#backup-and-recovery)

## Schema Overview

The GM Services database schema is designed to support a multi-service business platform with the following key principles:

- **Normalization**: 3NF compliance for data integrity
- **Scalability**: Partitioning and indexing for performance
- **Flexibility**: JSON columns for service-specific data
- **Auditability**: Comprehensive audit trails
- **Security**: Encrypted sensitive data storage

### Database Information

- **Database Engine**: PostgreSQL 14+
- **Character Set**: UTF-8
- **Collation**: en_US.UTF-8
- **Time Zone**: UTC
- **Total Tables**: 45+
- **Estimated Size**: 10GB+ (production)

## Core Tables

### Users and Authentication

#### users
Core user information and authentication data.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    profile_image VARCHAR(500),
    
    -- Security fields
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_login TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- MFA fields
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(32),
    backup_codes TEXT[], -- Encrypted backup codes
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_phone_format CHECK (phone IS NULL OR phone ~ '^\+?[1-9]\d{1,14}$')
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### user_profiles
Extended user profile information.

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Address information
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Nigeria',
    
    -- Business information
    company_name VARCHAR(255),
    job_title VARCHAR(100),
    industry VARCHAR(100),
    
    -- Preferences
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'Africa/Lagos',
    currency VARCHAR(3) DEFAULT 'NGN',
    notification_preferences JSONB DEFAULT '{}',
    
    -- Social media
    linkedin_url VARCHAR(500),
    twitter_handle VARCHAR(50),
    website_url VARCHAR(500),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_country ON user_profiles(country);
CREATE INDEX idx_user_profiles_city ON user_profiles(city);
```

### Roles and Permissions

#### roles
User role definitions.

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_role_name_format CHECK (name ~ '^[a-z_]+$')
);

-- Default roles
INSERT INTO roles (name, display_name, description, is_system_role) VALUES
('customer', 'Customer', 'Regular platform user', TRUE),
('staff', 'Staff Member', 'GM Services staff member', TRUE),
('admin', 'Administrator', 'System administrator', TRUE),
('super_admin', 'Super Administrator', 'Full system access', TRUE);
```

#### permissions
System permissions for granular access control.

```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_permission_name_format CHECK (name ~ '^[a-z_]+$'),
    UNIQUE(resource, action)
);

-- Sample permissions
INSERT INTO permissions (name, resource, action, description) VALUES
('view_services', 'services', 'view', 'View service requests'),
('create_services', 'services', 'create', 'Create service requests'),
('manage_users', 'users', 'manage', 'Manage user accounts'),
('view_reports', 'reports', 'view', 'View system reports'),
('manage_payments', 'payments', 'manage', 'Manage payment transactions');
```

#### user_roles
Many-to-many relationship between users and roles.

```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_expires_at ON user_roles(expires_at) WHERE expires_at IS NOT NULL;
```

#### role_permissions
Many-to-many relationship between roles and permissions.

```sql
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
```

## Service-Specific Tables

### Service Requests

#### service_requests
Core service request table.

```sql
CREATE TABLE service_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Status and priority
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    priority VARCHAR(10) DEFAULT 'normal' NOT NULL,
    urgency_level INTEGER DEFAULT 1 CHECK (urgency_level BETWEEN 1 AND 5),
    
    -- Financial information
    estimated_cost DECIMAL(12,2),
    final_cost DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'NGN',
    
    -- Assignment
    assigned_to INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE,
    
    -- Scheduling
    preferred_date DATE,
    preferred_time TIME,
    scheduled_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Location (if applicable)
    location_type VARCHAR(20), -- 'pickup', 'delivery', 'on_site'
    location_address TEXT,
    location_coordinates POINT,
    
    -- Service-specific data (JSON for flexibility)
    service_data JSONB DEFAULT '{}',
    internal_notes TEXT,
    customer_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_service_type CHECK (service_type IN (
        'automotive', 'hotel', 'logistics', 'rental', 'gadgets',
        'loans', 'jewelry', 'car_service', 'paperwork',
        'creative_services', 'web_development'
    )),
    CONSTRAINT chk_status CHECK (status IN (
        'pending', 'confirmed', 'in_progress', 'completed',
        'cancelled', 'on_hold', 'failed'
    )),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    CONSTRAINT chk_costs CHECK (
        (estimated_cost IS NULL OR estimated_cost >= 0) AND
        (final_cost IS NULL OR final_cost >= 0)
    )
);

-- Indexes
CREATE INDEX idx_service_requests_user_id ON service_requests(user_id);
CREATE INDEX idx_service_requests_service_type ON service_requests(service_type);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_priority ON service_requests(priority, created_at);
CREATE INDEX idx_service_requests_assigned_to ON service_requests(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at);
CREATE INDEX idx_service_requests_location ON service_requests USING GIST(location_coordinates) WHERE location_coordinates IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX idx_service_requests_user_status ON service_requests(user_id, status);
CREATE INDEX idx_service_requests_type_status ON service_requests(service_type, status);
CREATE INDEX idx_service_requests_active ON service_requests(status, created_at) 
    WHERE status IN ('pending', 'confirmed', 'in_progress');
```

#### service_status_history
Track status changes for audit trail.

```sql
CREATE TABLE service_status_history (
    id SERIAL PRIMARY KEY,
    service_request_id INTEGER NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by INTEGER REFERENCES users(id),
    reason TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_status_values CHECK (
        previous_status IS NULL OR previous_status IN (
            'pending', 'confirmed', 'in_progress', 'completed',
            'cancelled', 'on_hold', 'failed'
        )
    ),
    CONSTRAINT chk_new_status_values CHECK (new_status IN (
        'pending', 'confirmed', 'in_progress', 'completed',
        'cancelled', 'on_hold', 'failed'
    ))
);

CREATE INDEX idx_service_status_history_service_id ON service_status_history(service_request_id);
CREATE INDEX idx_service_status_history_created_at ON service_status_history(created_at);
```

### Automotive Services

#### vehicles
Vehicle information for automotive services.

```sql
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Vehicle identification
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    vin VARCHAR(17) UNIQUE,
    license_plate VARCHAR(20),
    
    -- Vehicle details
    color VARCHAR(30),
    fuel_type VARCHAR(20) DEFAULT 'petrol',
    transmission VARCHAR(15) DEFAULT 'manual',
    engine_size VARCHAR(10),
    mileage INTEGER,
    
    -- Registration information
    registration_number VARCHAR(50),
    registration_expiry DATE,
    insurance_provider VARCHAR(100),
    insurance_expiry DATE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_year CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    CONSTRAINT chk_vin_format CHECK (vin IS NULL OR LENGTH(vin) = 17),
    CONSTRAINT chk_fuel_type CHECK (fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid', 'lpg')),
    CONSTRAINT chk_transmission CHECK (transmission IN ('manual', 'automatic', 'cvt'))
);

CREATE INDEX idx_vehicles_user_id ON vehicles(user_id);
CREATE INDEX idx_vehicles_make_model ON vehicles(make, model);
CREATE INDEX idx_vehicles_vin ON vehicles(vin) WHERE vin IS NOT NULL;
CREATE INDEX idx_vehicles_active ON vehicles(is_active) WHERE is_active = TRUE;
```

#### vehicle_services
Track vehicle service history.

```sql
CREATE TABLE vehicle_services (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    service_request_id INTEGER REFERENCES service_requests(id),
    
    service_type VARCHAR(50) NOT NULL,
    description TEXT,
    cost DECIMAL(10,2),
    mileage_at_service INTEGER,
    
    service_date DATE NOT NULL,
    next_service_due DATE,
    next_service_mileage INTEGER,
    
    -- Service provider
    provider_name VARCHAR(100),
    provider_contact VARCHAR(20),
    
    -- Parts and labor
    parts_cost DECIMAL(10,2) DEFAULT 0,
    labor_cost DECIMAL(10,2) DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_service_type_automotive CHECK (service_type IN (
        'oil_change', 'brake_service', 'tire_rotation', 'engine_tune',
        'transmission_service', 'battery_replacement', 'inspection',
        'repair', 'maintenance', 'cleaning', 'other'
    )),
    CONSTRAINT chk_costs_non_negative CHECK (
        cost IS NULL OR cost >= 0,
        parts_cost >= 0,
        labor_cost >= 0
    )
);

CREATE INDEX idx_vehicle_services_vehicle_id ON vehicle_services(vehicle_id);
CREATE INDEX idx_vehicle_services_service_date ON vehicle_services(service_date);
CREATE INDEX idx_vehicle_services_type ON vehicle_services(service_type);
```

### Hotel and Hospitality

#### hotel_bookings
Hotel and accommodation bookings.

```sql
CREATE TABLE hotel_bookings (
    id SERIAL PRIMARY KEY,
    service_request_id INTEGER REFERENCES service_requests(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    -- Booking details
    property_name VARCHAR(255),
    property_type VARCHAR(50) DEFAULT 'hotel',
    room_type VARCHAR(100),
    
    -- Dates and guests
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_nights INTEGER GENERATED ALWAYS AS (check_out_date - check_in_date) STORED,
    number_of_adults INTEGER DEFAULT 1,
    number_of_children INTEGER DEFAULT 0,
    
    -- Pricing
    room_rate DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'NGN',
    
    -- Special requests
    special_requests TEXT,
    dietary_requirements TEXT,
    accessibility_needs TEXT,
    
    -- Booking status
    booking_status VARCHAR(20) DEFAULT 'pending',
    confirmation_number VARCHAR(50),
    
    -- Location
    property_address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_dates CHECK (check_out_date > check_in_date),
    CONSTRAINT chk_guests CHECK (number_of_adults > 0 AND number_of_children >= 0),
    CONSTRAINT chk_property_type CHECK (property_type IN (
        'hotel', 'resort', 'apartment', 'guesthouse', 'lodge', 'hostel'
    )),
    CONSTRAINT chk_booking_status CHECK (booking_status IN (
        'pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show'
    ))
);

CREATE INDEX idx_hotel_bookings_user_id ON hotel_bookings(user_id);
CREATE INDEX idx_hotel_bookings_check_in ON hotel_bookings(check_in_date);
CREATE INDEX idx_hotel_bookings_status ON hotel_bookings(booking_status);
CREATE INDEX idx_hotel_bookings_location ON hotel_bookings(city, state);
```

### Financial Services

#### loan_applications
Loan application tracking.

```sql
CREATE TABLE loan_applications (
    id SERIAL PRIMARY KEY,
    service_request_id INTEGER REFERENCES service_requests(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    -- Loan details
    loan_type VARCHAR(50) NOT NULL,
    loan_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    loan_purpose TEXT,
    requested_term_months INTEGER,
    
    -- Applicant information
    employment_status VARCHAR(50),
    monthly_income DECIMAL(10,2),
    existing_debts DECIMAL(10,2) DEFAULT 0,
    credit_score INTEGER,
    
    -- Application status
    application_status VARCHAR(20) DEFAULT 'submitted',
    approved_amount DECIMAL(12,2),
    approved_rate DECIMAL(5,4),
    approved_term_months INTEGER,
    
    -- Decision information
    decision_date DATE,
    decision_reason TEXT,
    reviewed_by INTEGER REFERENCES users(id),
    
    -- Risk assessment
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    risk_factors JSONB DEFAULT '[]',
    
    -- Documentation
    documents_submitted JSONB DEFAULT '[]',
    documents_verified BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_loan_type CHECK (loan_type IN (
        'personal', 'business', 'auto', 'mortgage', 'student', 'payday'
    )),
    CONSTRAINT chk_amounts CHECK (
        loan_amount > 0 AND
        (approved_amount IS NULL OR approved_amount > 0) AND
        (monthly_income IS NULL OR monthly_income >= 0) AND
        existing_debts >= 0
    ),
    CONSTRAINT chk_employment_status CHECK (employment_status IN (
        'employed_full_time', 'employed_part_time', 'self_employed',
        'unemployed', 'student', 'retired'
    )),
    CONSTRAINT chk_application_status CHECK (application_status IN (
        'submitted', 'under_review', 'approved', 'rejected',
        'withdrawn', 'expired'
    ))
);

CREATE INDEX idx_loan_applications_user_id ON loan_applications(user_id);
CREATE INDEX idx_loan_applications_status ON loan_applications(application_status);
CREATE INDEX idx_loan_applications_type ON loan_applications(loan_type);
CREATE INDEX idx_loan_applications_amount ON loan_applications(loan_amount);
```

## System Tables

### Payments and Transactions

#### payments
Payment transaction records.

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    service_request_id INTEGER REFERENCES service_requests(id),
    
    -- Payment details
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    payment_method VARCHAR(50) NOT NULL,
    gateway VARCHAR(50) NOT NULL,
    
    -- Gateway information
    gateway_transaction_id VARCHAR(255),
    gateway_reference VARCHAR(255),
    gateway_response JSONB DEFAULT '{}',
    
    -- Payment status
    status VARCHAR(20) DEFAULT 'pending',
    failure_reason TEXT,
    
    -- Metadata
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_payment_method CHECK (payment_method IN (
        'card', 'bank_transfer', 'wallet', 'cash', 'crypto'
    )),
    CONSTRAINT chk_gateway CHECK (gateway IN (
        'stripe', 'paypal', 'paystack', 'flutterwave', 'razorpay'
    )),
    CONSTRAINT chk_payment_status CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded'
    ))
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_service_request_id ON payments(service_request_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_gateway ON payments(gateway);
CREATE INDEX idx_payments_gateway_transaction_id ON payments(gateway_transaction_id);
CREATE INDEX idx_payments_created_at ON payments(created_at);
```

#### payment_methods
Stored payment methods for users.

```sql
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Method details
    type VARCHAR(20) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Card information (encrypted)
    card_last_four VARCHAR(4),
    card_brand VARCHAR(20),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    
    -- Bank account information (encrypted)
    bank_name VARCHAR(100),
    account_last_four VARCHAR(4),
    account_type VARCHAR(20),
    
    -- Status and preferences
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Gateway references
    gateway_customer_id VARCHAR(255),
    gateway_payment_method_id VARCHAR(255),
    
    -- Metadata
    nickname VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_payment_method_type CHECK (type IN ('card', 'bank_account', 'wallet')),
    CONSTRAINT chk_card_exp CHECK (
        (type != 'card') OR 
        (card_exp_month BETWEEN 1 AND 12 AND card_exp_year >= EXTRACT(YEAR FROM CURRENT_DATE))
    )
);

CREATE INDEX idx_payment_methods_user_id ON payment_methods(user_id);
CREATE INDEX idx_payment_methods_default ON payment_methods(user_id, is_default) WHERE is_default = TRUE;
CREATE INDEX idx_payment_methods_active ON payment_methods(is_active) WHERE is_active = TRUE;
```

### Communication and Notifications

#### messages
System messaging between users.

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id),
    recipient_id INTEGER REFERENCES users(id),
    service_request_id INTEGER REFERENCES service_requests(id),
    
    -- Message content
    subject VARCHAR(255),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'user',
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- Attachments
    attachments JSONB DEFAULT '[]',
    
    -- Threading
    thread_id INTEGER REFERENCES messages(id),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_message_type CHECK (message_type IN (
        'user', 'system', 'notification', 'alert'
    )),
    CONSTRAINT chk_sender_recipient CHECK (
        sender_id IS NOT NULL OR message_type = 'system'
    )
);

CREATE INDEX idx_messages_recipient ON messages(recipient_id, created_at);
CREATE INDEX idx_messages_sender ON messages(sender_id, created_at);
CREATE INDEX idx_messages_service_request ON messages(service_request_id);
CREATE INDEX idx_messages_unread ON messages(recipient_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_messages_thread ON messages(thread_id) WHERE thread_id IS NOT NULL;
```

#### notifications
System notifications to users.

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification content
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    
    -- Action data
    action_url VARCHAR(500),
    action_data JSONB DEFAULT '{}',
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- Delivery
    delivery_methods VARCHAR(100)[], -- ['email', 'sms', 'push', 'in_app']
    delivered_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_notification_type CHECK (type IN (
        'service_update', 'payment_confirmation', 'system_alert',
        'promotional', 'reminder', 'welcome', 'security'
    ))
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id, created_at);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_expires ON notifications(expires_at) WHERE expires_at IS NOT NULL;
```

### File Management

#### file_uploads
Track uploaded files.

```sql
CREATE TABLE file_uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    service_request_id INTEGER REFERENCES service_requests(id),
    
    -- File information
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64), -- SHA-256 hash for deduplication
    
    -- File metadata
    description TEXT,
    file_category VARCHAR(50),
    is_public BOOLEAN DEFAULT FALSE,
    is_temporary BOOLEAN DEFAULT FALSE,
    
    -- Security
    virus_scan_status VARCHAR(20) DEFAULT 'pending',
    virus_scan_result TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_file_size CHECK (file_size > 0),
    CONSTRAINT chk_virus_scan_status CHECK (virus_scan_status IN (
        'pending', 'clean', 'infected', 'failed'
    ))
);

CREATE INDEX idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX idx_file_uploads_service_request ON file_uploads(service_request_id);
CREATE INDEX idx_file_uploads_hash ON file_uploads(file_hash);
CREATE INDEX idx_file_uploads_category ON file_uploads(file_category);
CREATE INDEX idx_file_uploads_temporary ON file_uploads(is_temporary, created_at) WHERE is_temporary = TRUE;
```

## Relationships and Constraints

### Foreign Key Relationships

```sql
-- User-centric relationships
ALTER TABLE user_profiles ADD CONSTRAINT fk_user_profiles_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_roles ADD CONSTRAINT fk_user_roles_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE service_requests ADD CONSTRAINT fk_service_requests_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Service relationships
ALTER TABLE service_status_history ADD CONSTRAINT fk_status_history_service 
    FOREIGN KEY (service_request_id) REFERENCES service_requests(id) ON DELETE CASCADE;

ALTER TABLE payments ADD CONSTRAINT fk_payments_service 
    FOREIGN KEY (service_request_id) REFERENCES service_requests(id) ON DELETE SET NULL;

-- File relationships
ALTER TABLE file_uploads ADD CONSTRAINT fk_file_uploads_service 
    FOREIGN KEY (service_request_id) REFERENCES service_requests(id) ON DELETE SET NULL;
```

### Check Constraints

```sql
-- Email format validation
ALTER TABLE users ADD CONSTRAINT chk_users_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Phone number validation
ALTER TABLE users ADD CONSTRAINT chk_users_phone_format 
    CHECK (phone IS NULL OR phone ~ '^\+?[1-9]\d{1,14}$');

-- Date validations
ALTER TABLE hotel_bookings ADD CONSTRAINT chk_hotel_dates 
    CHECK (check_out_date > check_in_date);

-- Amount validations
ALTER TABLE payments ADD CONSTRAINT chk_payments_amount_positive 
    CHECK (amount > 0);

ALTER TABLE loan_applications ADD CONSTRAINT chk_loan_amounts 
    CHECK (loan_amount > 0 AND monthly_income >= 0);
```

### Unique Constraints

```sql
-- User uniqueness
ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);

-- Role-permission uniqueness
ALTER TABLE role_permissions ADD CONSTRAINT uq_role_permissions 
    UNIQUE (role_id, permission_id);

-- User-role uniqueness
ALTER TABLE user_roles ADD CONSTRAINT uq_user_roles 
    UNIQUE (user_id, role_id);

-- Payment method default uniqueness (only one default per user)
CREATE UNIQUE INDEX uq_payment_methods_default 
    ON payment_methods(user_id) 
    WHERE is_default = TRUE;
```

## Indexes and Performance

### Primary Indexes

```sql
-- High-traffic query indexes
CREATE INDEX idx_service_requests_user_status_created 
    ON service_requests(user_id, status, created_at);

CREATE INDEX idx_payments_user_status_created 
    ON payments(user_id, status, created_at);

CREATE INDEX idx_notifications_user_unread_created 
    ON notifications(user_id, is_read, created_at) 
    WHERE is_read = FALSE;
```

### Partial Indexes

```sql
-- Index only active records
CREATE INDEX idx_users_active_email 
    ON users(email) 
    WHERE is_active = TRUE;

CREATE INDEX idx_service_requests_active 
    ON service_requests(status, created_at) 
    WHERE status IN ('pending', 'confirmed', 'in_progress');

-- Index only unread notifications
CREATE INDEX idx_notifications_unread_by_type 
    ON notifications(user_id, type, created_at) 
    WHERE is_read = FALSE;
```

### Composite Indexes

```sql
-- Common query patterns
CREATE INDEX idx_service_requests_type_status_date 
    ON service_requests(service_type, status, created_at);

CREATE INDEX idx_payments_gateway_status_date 
    ON payments(gateway, status, created_at);

CREATE INDEX idx_messages_recipient_thread_date 
    ON messages(recipient_id, thread_id, created_at);
```

### Full-Text Search Indexes

```sql
-- Full-text search for service requests
ALTER TABLE service_requests ADD COLUMN search_vector tsvector;

CREATE INDEX idx_service_requests_search 
    ON service_requests USING gin(search_vector);

-- Update search vector trigger
CREATE OR REPLACE FUNCTION update_service_request_search_vector()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.service_type, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_service_request_search_vector
    BEFORE INSERT OR UPDATE ON service_requests
    FOR EACH ROW EXECUTE FUNCTION update_service_request_search_vector();
```

## Data Types and Constraints

### Custom Types and Enums

```sql
-- Status enums
CREATE TYPE service_status AS ENUM (
    'pending', 'confirmed', 'in_progress', 'completed',
    'cancelled', 'on_hold', 'failed'
);

CREATE TYPE payment_status AS ENUM (
    'pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded'
);

CREATE TYPE user_status AS ENUM (
    'active', 'inactive', 'suspended', 'pending_verification'
);

-- Priority levels
CREATE TYPE priority_level AS ENUM ('low', 'normal', 'high', 'urgent');

-- Service types
CREATE TYPE service_type AS ENUM (
    'automotive', 'hotel', 'logistics', 'rental', 'gadgets',
    'loans', 'jewelry', 'car_service', 'paperwork',
    'creative_services', 'web_development'
);
```

### JSON Schema Validation

```sql
-- Service data JSON schema validation
ALTER TABLE service_requests ADD CONSTRAINT chk_service_data_schema
    CHECK (
        service_data IS NULL OR 
        jsonb_typeof(service_data) = 'object'
    );

-- Notification preferences schema
CREATE OR REPLACE FUNCTION validate_notification_preferences(prefs jsonb)
RETURNS boolean AS $$
BEGIN
    RETURN (
        prefs IS NULL OR (
            jsonb_typeof(prefs) = 'object' AND
            (prefs ? 'email' IS FALSE OR jsonb_typeof(prefs->'email') = 'boolean') AND
            (prefs ? 'sms' IS FALSE OR jsonb_typeof(prefs->'sms') = 'boolean') AND
            (prefs ? 'push' IS FALSE OR jsonb_typeof(prefs->'push') = 'boolean')
        )
    );
END;
$$ LANGUAGE plpgsql;

ALTER TABLE user_profiles ADD CONSTRAINT chk_notification_preferences_schema
    CHECK (validate_notification_preferences(notification_preferences));
```

## Migration History

### Version Control

```sql
-- Migration tracking table
CREATE TABLE schema_migrations (
    version VARCHAR(14) PRIMARY KEY,
    dirty BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sample migration records
INSERT INTO schema_migrations (version, dirty) VALUES
('20240101000001', FALSE), -- Initial schema
('20240101000002', FALSE), -- Add user profiles
('20240101000003', FALSE), -- Add service requests
('20240101000004', FALSE), -- Add payment system
('20240101000005', FALSE); -- Add file uploads
```

### Migration Scripts

#### Migration 20240101000001 - Initial Schema

```sql
-- Create initial users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create roles and permissions
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Backup and Recovery

### Backup Strategy

```sql
-- Create backup user with minimal privileges
CREATE USER backup_user WITH PASSWORD 'secure_backup_password';
GRANT CONNECT ON DATABASE gmservices TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO backup_user;

-- Backup script (to be run via cron)
/*
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Full database backup
pg_dump -h localhost -U backup_user -d gmservices \
    --format=custom --compress=9 \
    --file="$BACKUP_DIR/gmservices_full_$(date +%Y%m%d_%H%M%S).backup"

# Schema-only backup
pg_dump -h localhost -U backup_user -d gmservices \
    --schema-only --format=plain \
    --file="$BACKUP_DIR/gmservices_schema_$(date +%Y%m%d_%H%M%S).sql"

# Data-only backup
pg_dump -h localhost -U backup_user -d gmservices \
    --data-only --format=custom --compress=9 \
    --file="$BACKUP_DIR/gmservices_data_$(date +%Y%m%d_%H%M%S).backup"
*/
```

### Point-in-Time Recovery

```sql
-- Enable WAL archiving in postgresql.conf
/*
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
max_wal_senders = 3
checkpoint_timeout = 15min
*/

-- Create base backup
/*
SELECT pg_start_backup('base_backup_$(date +%Y%m%d)');
-- Copy data directory
SELECT pg_stop_backup();
*/
```

### Data Retention Policies

```sql
-- Cleanup old audit records (keep 2 years)
DELETE FROM service_status_history 
WHERE created_at < CURRENT_DATE - INTERVAL '2 years';

-- Archive old completed service requests (keep 5 years)
CREATE TABLE service_requests_archive (LIKE service_requests INCLUDING ALL);

INSERT INTO service_requests_archive
SELECT * FROM service_requests 
WHERE status = 'completed' 
AND completed_at < CURRENT_DATE - INTERVAL '5 years';

DELETE FROM service_requests 
WHERE status = 'completed' 
AND completed_at < CURRENT_DATE - INTERVAL '5 years';

-- Cleanup temporary files (keep 7 days)
DELETE FROM file_uploads 
WHERE is_temporary = TRUE 
AND created_at < CURRENT_DATE - INTERVAL '7 days';
```

---

## Performance Monitoring

### Database Statistics

```sql
-- Monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Monitor slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Maintenance Scripts

```sql
-- Regular maintenance function
CREATE OR REPLACE FUNCTION perform_maintenance()
RETURNS void AS $$
BEGIN
    -- Update table statistics
    ANALYZE;
    
    -- Rebuild fragmented indexes
    REINDEX DATABASE gmservices;
    
    -- Vacuum full on heavily updated tables
    VACUUM FULL users;
    VACUUM FULL service_requests;
    VACUUM FULL payments;
    
    -- Log maintenance completion
    INSERT INTO system_logs (level, message, created_at)
    VALUES ('INFO', 'Database maintenance completed', CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- Schedule via pg_cron (if available)
SELECT cron.schedule('maintenance', '0 2 * * 0', 'SELECT perform_maintenance();');
```

---

**Schema Version:** 1.0  
**Last Updated:** January 1, 2024  
**Next Review:** April 1, 2024  
**Maintainer:** Database Team  
**Approved By:** CTO, Lead Developer