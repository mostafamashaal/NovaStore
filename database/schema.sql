--======================================
--M1.3 Schema Implementation
--Identity
--======================================

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(30) NOT NULL 
        CHECK (role IN ('customer', 'support_agent', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()    
);

--======================================
--Customer Profile
--======================================

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE 
        REFERENCES users(id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
-- Products
--======================================

CREATE TABLE products (
    id UUID NOT NULL PRIMARY KEY,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL 
        CHECK(price >= 0),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

);

--======================================
--Inventory
--======================================

CREATE TABLE inventory (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL UNIQUE 
        REFERENCES products(id),
    available_quantity INTEGER NOT NULL 
        CHECK (available_quantity >=0),
    reserved_quantity INTEGER NOT NULL 
        CHECK (reserved_quantity >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
-- Orders
--======================================

CREATE TABLE orders (
    id UUID PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id UUID NOT NULL 
        REFERENCES customers(id),
    status VARCHAR(30) NOT NULL 
        CHECK ( 
            status IN ( 
                'processing',
                 'shipped',
                 'in_transit',
                  'delivered',
                   'cancelled'
                   )
               ),
    total_amount NUMERIC(12,2) NOT NULL 
        CHECK (total_amount >=0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
--Order Items
--======================================

CREATE TABLE order_items (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL 
        REFERENCES orders(id),
    product_id UUID NOT NULL 
        REFERENCES products(id),
    quantity INTEGER NOT NULL 
        CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL
        CHECK (unit_price >=0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================
-- Order Status History
-- ============================================

CREATE TABLE order_status_history (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL
        REFERENCES orders(id),
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    changed_by_user_id UUID
        REFERENCES users(id),
    changed_by_type VARCHAR(30) NOT NULL
        CHECK (
            changed_by_type IN (
                'customer',
                'support_agent',
                'admin',
                'ai',
                'system'
            )
        ),
    changed_at TIMESTAMPTZ NOT NULL
);

-- ============================================
-- Payments
-- ============================================
 CREATE TABLE payments (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL
        REFERENCES orders(id),
    provider VARCHAR(100) NOT NULL,
    transaction_reference VARCHAR(255) NOT NULL,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL,
    amount NUMERIC(12,2) NOT NULL
        CHECK (amount >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================
-- Shipments
-- ============================================

CREATE TABLE shipments (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL
        REFERENCES orders(id),
    carrier VARCHAR(100) NOT NULL,
    tracking_number VARCHAR(255),
    status VARCHAR(30) NOT NULL
        CHECK (
            status IN (
                'pending',
                'shipped',
                'in_transit',
                'delivered'
            )
        ),
    estimated_delivery DATE,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================
-- Conversations
-- ============================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL
        REFERENCES customers(id),
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
--Messages
--======================================

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL
        REFERENCES conversations(id),
    sender_type VARCHAR(30) NOT NULL
        CHECK (
            sender_type IN (
                'customer',
                'support_agent',
                'ai',
                'system',
                'tool'
            )
        ),
    sender_user_id UUID
        REFERENCES users(id),
    content TEXT NOT NULL
        CHECK (length(trim(content)) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
--Tickets
--======================================

CREATE TABLE tickets (
    id UUID PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id UUID NOT NULL
        REFERENCES customers(id),
    conversation_id UUID
        REFERENCES conversations(id),
    assigned_agent_id UUID
        REFERENCES users(id),
    category VARCHAR(50) NOT NULL
        CHECK (
            category IN (
                'refund',
                'complaint',
                'damaged_order',
                'technical',
                'shipping'
            )
        ),
    priority VARCHAR(20) NOT NULL
        CHECK (
            priority IN (
                'low',
                'medium',
                'high',
                'urgent'
            )
        ),
    status VARCHAR(30) NOT NULL
        CHECK (
            status IN (
                'open',
                'in_progress',
                'waiting_customer',
                'resolved',
                'closed'
            )
        ),
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

--======================================
--Refundes
--======================================
CREATE TABLE refunds (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL
        REFERENCES orders(id),
    customer_id UUID NOT NULL
        REFERENCES customers(id),
    ticket_id UUID
        REFERENCES tickets(id),
    amount NUMERIC(12,2) NOT NULL
        CHECK (amount >= 0),
    reason TEXT NOT NULL,
    status VARCHAR(30) NOT NULL
        CHECK (
            status IN (
                'requested',
                'pending_approval',
                'approved',
                'rejected',
                'processing',
                'completed',
                'failed'
            )
        ),
    requested_by UUID
        REFERENCES users(id),
    approved_by UUID
        REFERENCES users(id),
    requested_at TIMESTAMPTZ NOT NULL,
    decided_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

--======================================
--Documents
--======================================

CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    source VARCHAR(255) NOT NULL,
    uploaded_by UUID NOT NULL
        REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
--Document Chunks
--======================================

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL
        REFERENCES documents(id)
        ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

--======================================
--Agent Runs
--======================================

CREATE TABLE agent_runs (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL
        REFERENCES conversations(id),
    customer_id UUID NOT NULL 
        REFERENCES customers(id),
    status VARCHAR(30) NOT NULL
        CHECK (
            status IN (
                'running',
                'waiting_approval',
                'completed',
                'failed',
                'cancelled'
            )
        ),
    model VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    estimated_cost NUMERIC(12,6)
);

--======================================
--Tool Calls
--======================================

CREATE TABLE tool_calls (
    id UUID PRIMARY KEY,
    agent_run_id UUID NOT NULL
        REFERENCES agent_runs(id),
    tool_name VARCHAR(100) NOT NULL,
    arguments JSONB NOT NULL,
    result JSONB,
    status VARCHAR(30) NOT NULL,
    error_message TEXT,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

--======================================
--Approvls
--======================================

CREATE TABLE approvals (
    id UUID PRIMARY KEY,
    agent_run_id UUID NOT NULL
        REFERENCES agent_runs(id),
    tool_call_id UUID
        REFERENCES tool_calls(id),
    ticket_id UUID
        REFERENCES tickets(id),
    action VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL
        CHECK (
            status IN (
                'pending',
                'approved',
                'rejected',
                'expired'
            )
        ),
    requested_at TIMESTAMPTZ NOT NULL,
    decided_at TIMESTAMPTZ,
    decided_by UUID
        REFERENCES users(id),
    reason TEXT
);

--======================================
--Audit Logs
--======================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    actor_user_id UUID
        REFERENCES users(id),
    actor_type VARCHAR(30) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
