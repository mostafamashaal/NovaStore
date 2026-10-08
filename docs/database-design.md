# NovaStore AI Customer Operations Platform

## Database Design Specification

**Version:** V1  
**Status:** Implemented and Validated
**Database:** PostgreSQL + pgvector

---

## 1. Overview

NovaStore is a fictional e-commerce company selling laptops,
phones, monitors, and accessories.

The database supports the AI Customer Operations Platform responsible for:

- Customer accounts and authentication
- Products and inventory
- Orders, payments, and shipments
- Customer conversations and support tickets
- Refund workflows
- Knowledge documents and RAG
- AI agent execution and tool calls
- Human approval workflows
- Audit and operational logging

---

## 2. Design Goals

The database should provide:

1. Strong relational integrity.
2. Clear separation between business entities.
3. Historical records for important state changes.
4. Support for AI-agent observability.
5. Support for human-in-the-loop workflows.
6. Secure handling of customer and operational data.
7. Efficient lookup of common business queries.
8. A design that is simple enough for V1 but extensible for V2.

---

## 3. Core Design Principles

### 3.1 Separation of Concerns

Authentication data is separated from customer profile data.

Business entities are separated into independent tables rather than being stored in one large table.

### 3.2 Technical IDs vs Business IDs

Internal primary keys use UUIDs.

Customer-facing identifiers use business-friendly values such as:

- `NS-10452` for orders
- `TKT-2026-00124` for tickets

### 3.3 Money

Financial values use PostgreSQL `NUMERIC` rather than floating-point types.

Examples:

- `NUMERIC(10,2)` for product prices
- `NUMERIC(12,2)` for order/payment/refund amounts

### 3.4 Time

Server-side event timestamps use `TIMESTAMPTZ`.

This avoids ambiguity when systems or users operate across different time zones.

### 3.5 Security Boundary

The LLM/AI agent is not a security boundary.

Authorization is enforced by the backend before sensitive data is returned or business actions are executed.

For example, an agent cannot retrieve another customer's order merely because an LLM generated a valid-looking request.

### 3.6 Sensitive Data

The database must never store:

- Plain-text passwords
- Raw card numbers
- CVV/PIN values
- API keys
- Other secrets

Passwords are stored only as secure password hashes.

### 3.7 Scope Control

V1 intentionally avoids unnecessary complexity.

Examples of features deferred to V2:

- Multiple warehouses
- Database-managed dynamic policy engine
- Advanced ticket event tables
- Multi-agent architecture
- Dedicated vector database
- Real external shipping/payment integrations
- Voice/WhatsApp channels

---

# 4. Entity Relationship Overview

```text
                         ┌──────────────┐
                         │    USERS     │
                         └──────┬───────┘
                                │
                              1 │ 0..1
                                │
                         ┌──────▼───────┐
                         │  CUSTOMERS   │
                         └──────┬───────┘
                                │
                 ┌──────────────┼─────────────────┐
                 │              │                 │
                 │              │                 │
                 ▼              ▼                 ▼
              ORDERS      CONVERSATIONS        TICKETS
                 │              │                 │
        ┌────────┼──────┐       │            ┌────┴─────┐
        │        │      │       │            │          │
        ▼        ▼      ▼       ▼            ▼          ▼
 ORDER_ITEMS PAYMENTS SHIPMENTS MESSAGES   REFUNDS   AGENT...
        │
        ▼
    PRODUCTS
        │
        ▼
   INVENTORY

ORDERS
   │
   ▼
ORDER_STATUS_HISTORY

DOCUMENTS
   │
   ▼
DOCUMENT_CHUNKS
   │
   ▼
 EMBEDDINGS

CONVERSATIONS
      │
      ▼
  AGENT_RUNS
      │
      ├───────────────┐
      ▼               ▼
 TOOL_CALLS       APPROVALS

AUDIT_LOGS
```

---

# 5. Tables

The V1 database contains **19 tables**:

1. `users`
2. `customers`
3. `products`
4. `inventory`
5. `orders`
6. `order_items`
7. `order_status_history`
8. `payments`
9. `shipments`
10. `conversations`
11. `messages`
12. `tickets`
13. `refunds`
14. `documents`
15. `document_chunks`
16. `agent_runs`
17. `tool_calls`
18. `approvals`
19. `audit_logs`

---

---

# 6. Identity and Users

## 6.1 users

Stores system identities and authentication information.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `email` | VARCHAR(255) | No | Unique login identifier |
| `password_hash` | TEXT | No | Secure password hash |
| `role` | VARCHAR(30) | No | `customer`, `support_agent`, `admin` |
| `is_active` | BOOLEAN | No | Default `true` |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationships

- One `users` record can have zero or one `customers` record.
- `users` may also act as support agents or admins.

### Important Constraints

- `email` must be unique.
- `role` should have a `CHECK` constraint.
- Passwords must never be stored in plain text.

---

## 6.2 customers

Stores customer-specific profile information.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `user_id` | UUID | No | FK → `users.id`, UNIQUE |
| `first_name` | VARCHAR(100) | No | Customer first name |
| `last_name` | VARCHAR(100) | No | Customer last name |
| `phone` | VARCHAR(30) | Yes | Optional phone number |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationship

```text
users 1 ─── 0..1 customers
```

`user_id` is unique because one authentication account maps to at most one customer profile in V1.

---

# 7. Commerce

## 7.1 products

Stores the products available in the NovaStore catalog.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `sku` | VARCHAR(100) | No | Unique business identifier |
| `name` | VARCHAR(255) | No | Product name |
| `description` | TEXT | Yes | Optional product description |
| `category` | VARCHAR(100) | No | Product category |
| `price` | NUMERIC(10,2) | No | Current product price, must be >= 0 |
| `is_active` | BOOLEAN | No | Default `true` |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Design Decision

- `id` is the technical primary key used internally by the database.
- `sku` is the business identifier used to identify a product in business operations.
- `sku` must be unique.
- Product price must never be negative.

---

## 7.2 inventory

Stores the current inventory state for each product.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `product_id` | UUID | No | FK → `products.id`, UNIQUE |
| `available_quantity` | INTEGER | No | Available stock, must be >= 0 |
| `reserved_quantity` | INTEGER | No | Reserved stock, must be >= 0 |
| `updated_at` | TIMESTAMPTZ | No | Last inventory update |

### Relationship

```text
products 1 ─── 1 inventory
```

### Design Decision

- V1 uses one inventory record per product.
- `product_id` is unique, so each product has exactly one inventory record.
- `available_quantity` represents stock currently available for purchase.
- `reserved_quantity` represents stock temporarily reserved for orders.
- Both quantities must never be negative.

### V2 Consideration

In V2, inventory can be expanded to support multiple warehouses or locations.

For example:

```text
products
   │
   ├── warehouse A inventory
   ├── warehouse B inventory
   └── warehouse C inventory
```

---

## 7.3 orders

Stores customer orders and their current lifecycle status.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `order_number` | VARCHAR(50) | No | Unique business order identifier |
| `customer_id` | UUID | No | FK → `customers.id` |
| `status` | VARCHAR(30) | No | Current order status |
| `total_amount` | NUMERIC(12,2) | No | Total order amount, must be >= 0 |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationship

```text
customers 1 ─── many orders
```

### Allowed Order Statuses

The V1 order lifecycle supports:

- `processing`
- `shipped`
- `in_transit`
- `delivered`
- `cancelled`

The allowed values should be enforced consistently by both:

- The database constraint.
- The backend business logic.

### Design Decision

- `id` is the technical primary key.
- `order_number` is the business-facing order identifier.
- `order_number` must be unique.
- `customer_id` identifies the customer who owns the order.
- `status` represents the current state of the order.
- Historical status changes are stored separately in `order_status_history`.

---

## 7.4 order_items

Stores the individual products included in each order.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `order_id` | UUID | No | FK → `orders.id` |
| `product_id` | UUID | No | FK → `products.id` |
| `quantity` | INTEGER | No | Quantity purchased, must be > 0 |
| `unit_price` | NUMERIC(10,2) | No | Product price at the time of purchase |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationships

```text
orders 1 ─── many order_items

products 1 ─── many order_items
```

### Important Design Decision

`unit_price` stores the product price **at the time the order was placed**.

It must not depend on the current value of `products.price`.

For example:

```text
Product current price:     $1,200
Order purchase price:      $1,050
```

The `order_items.unit_price` should remain `$1,050` even if the product price later changes.

This preserves the historical financial information of the order.

### Constraints

- `quantity` must be greater than `0`.
- `unit_price` must be greater than or equal to `0`.
- `order_id` must reference an existing order.
- `product_id` must reference an existing product.

---

## 7.5 order_status_history

Stores the complete history of order status changes.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `order_id` | UUID | No | FK → `orders.id` |
| `old_status` | VARCHAR(30) | Yes | Previous order status |
| `new_status` | VARCHAR(30) | No | New order status |
| `changed_by_user_id` | UUID | Yes | FK → `users.id` |
| `changed_by_type` | VARCHAR(30) | No | Who or what changed the status |
| `changed_at` | TIMESTAMPTZ | No | Time of status change |

### Relationship

```text
orders 1 ─── many order_status_history
```

### Allowed `changed_by_type` Values

- `customer`
- `support_agent`
- `admin`
- `ai`
- `system`

### Design Decisions

- `old_status` may be `NULL` for the first status transition.
- `new_status` represents the new state of the order.
- `changed_by_user_id` identifies the user responsible for the change when applicable.
- For AI or system-generated changes, `changed_by_user_id` may be `NULL`.
- Every status transition should create a new history record.

### Example

```text
Order #NS-1001

processing
    │
    ▼
shipped
    │
    ▼
in_transit
    │
    ▼
delivered
```

The history table allows the system to answer:

- When was the order shipped?
- Who changed the status?
- What was the previous status?
- How did the order reach its current state?

---

## 7.6 payments

Stores payment transactions associated with orders.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `order_id` | UUID | No | FK → `orders.id` |
| `provider` | VARCHAR(100) | No | Payment provider |
| `transaction_reference` | VARCHAR(255) | No | External transaction identifier |
| `method` | VARCHAR(50) | No | Payment method |
| `status` | VARCHAR(30) | No | Current payment status |
| `amount` | NUMERIC(12,2) | No | Payment amount |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationship

```text
orders 1 ─── many payments
```

### Design Decisions

- An order may have multiple payment records.
- `transaction_reference` identifies the transaction at the external payment provider.
- `amount` must be greater than or equal to `0`.
- Payment status should be controlled by the database and backend business logic.

### Security Requirements

The system must **never** store:

- Raw card numbers
- CVV/CVC codes
- Payment PINs
- Other sensitive payment credentials

Only safe payment metadata and provider transaction references should be stored.

---

## 7.7 shipments

Stores shipment and delivery information for orders.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `order_id` | UUID | No | FK → `orders.id` |
| `carrier` | VARCHAR(100) | No | Shipping carrier |
| `tracking_number` | VARCHAR(255) | Yes | Carrier tracking number |
| `status` | VARCHAR(30) | No | Current shipment status |
| `estimated_delivery` | DATE | Yes | Expected delivery date |
| `shipped_at` | TIMESTAMPTZ | Yes | Actual shipment time |
| `delivered_at` | TIMESTAMPTZ | Yes | Actual delivery time |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationship

```text
orders 1 ─── many shipments
```

### Design Decisions

- An order may have multiple shipment records.
- `tracking_number` may be `NULL` before a carrier is assigned.
- `estimated_delivery` may be `NULL` when the carrier has not provided an estimate.
- `shipped_at` remains `NULL` until the order is actually shipped.
- `delivered_at` remains `NULL` until delivery is completed.

### Shipment Lifecycle

```text
pending
   │
   ▼
shipped
   │
   ▼
in_transit
   │
   ▼
delivered
```

The exact shipment status values should be enforced consistently by the database and backend.

---

# 8. Customer Operations

## 8.1 conversations

Stores customer conversations with the NovaStore support system.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `customer_id` | UUID | No | FK → `customers.id` |
| `status` | VARCHAR(30) | No | Current conversation status |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationship

```text
customers 1 ─── many conversations
```

### Design Decision

A **conversation** represents the communication thread between a customer and the NovaStore support system.

A conversation is **not the same as a ticket**.

- `conversation` → communication and message history.
- `ticket` → structured customer support issue that can be assigned, prioritized, and resolved.

This separation allows a conversation to exist without creating a support ticket.
---

## 8.2 messages

Stores individual messages exchanged within a customer conversation.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `conversation_id` | UUID | No | FK → `conversations.id` |
| `sender_type` | VARCHAR(30) | No | Type of message sender |
| `sender_user_id` | UUID | Yes | FK → `users.id` |
| `content` | TEXT | No | Message content |
| `created_at` | TIMESTAMPTZ | No | Message creation time |

### Relationships

```text
conversations 1 ─── many messages

users 1 ─── many messages
```

### Sender Types

The `sender_type` identifies who or what generated the message.

Allowed values:

- `customer`
- `support_agent`
- `ai`
- `system`
- `tool`

### Design Decisions

- Human senders should have their actual `sender_user_id`.
- AI-generated messages may have `sender_user_id = NULL`.
- System-generated messages may have `sender_user_id = NULL`.
- Tool-generated messages may have `sender_user_id = NULL`.
- `conversation_id` must reference an existing conversation.
- Messages are ordered chronologically using `created_at`.
- Message content must not be empty.
- The `sender_type` value should be validated by both the database constraint and backend business logic.

### Message Flow

```text
Customer
   │
   ▼
Conversation
   │
   ▼
Message
   │
   ├── Customer Message
   ├── AI Message
   ├── Support Agent Message
   ├── System Message
   └── Tool Message
```

### Example

A typical conversation may contain:

```text
Customer:
"Where is my order?"

AI:
"Let me check your order status."

Tool:
"Order #NS-1001 → in_transit"

AI:
"Your order is currently in transit."
```

The `messages` table stores each of these messages as separate records while maintaining their relationship to the same conversation.

---

## 8.3 tickets

Stores structured customer support issues that require tracking, assignment, and resolution.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `ticket_number` | VARCHAR(50) | No | Unique business ticket identifier |
| `customer_id` | UUID | No | FK → `customers.id` |
| `conversation_id` | UUID | Yes | FK → `conversations.id` |
| `assigned_agent_id` | UUID | Yes | FK → `users.id` |
| `category` | VARCHAR(50) | No | Type of support issue |
| `priority` | VARCHAR(20) | No | Ticket priority |
| `status` | VARCHAR(30) | No | Current ticket status |
| `subject` | VARCHAR(255) | No | Ticket subject |
| `description` | TEXT | No | Detailed description of the issue |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |
| `resolved_at` | TIMESTAMPTZ | Yes | Time when the ticket was resolved |

### Relationships

```text
customers 1 ─── many tickets

conversations 1 ─── 0..many tickets

users 1 ─── 0..many tickets
         │
         └── assigned support agent
```

### Ticket Categories

The V1 system supports the following ticket categories:

- `refund`
- `complaint`
- `damaged_order`
- `technical`
- `shipping`

The category identifies the primary type of customer issue.

### Ticket Priorities

The V1 system supports four priority levels:

- `low`
- `medium`
- `high`
- `urgent`

Priority determines how quickly the support team should handle the ticket.

### Ticket Statuses

The V1 ticket lifecycle supports:

- `open`
- `in_progress`
- `waiting_customer`
- `resolved`
- `closed`

A typical ticket lifecycle is:

```text
open
  │
  ▼
in_progress
  │
  ├───────────────┐
  ▼               ▼
waiting_customer  resolved
  │                 │
  │                 ▼
  └──────────────► closed
```

### Design Decisions

- `ticket_number` is the business-facing identifier and must be unique.
- `id` is the technical primary key used internally by the database.
- Every ticket belongs to a customer through `customer_id`.
- `conversation_id` is optional because not every support issue must originate from an existing conversation.
- `assigned_agent_id` is optional because a newly created ticket may not yet be assigned to a support agent.
- `assigned_agent_id` should reference a user whose role allows support-agent operations.
- `resolved_at` remains `NULL` until the ticket reaches the `resolved` state.
- The ticket status must be validated by both database constraints and backend business logic.
- The ticket priority must also be validated by both database constraints and backend business logic.

### Conversation and Ticket Separation

A conversation and a ticket serve different purposes:

```text
Conversation
    │
    ├── Messages
    └── Communication history

Ticket
    │
    ├── Category
    ├── Priority
    ├── Assigned Agent
    ├── Status
    └── Resolution
```

A conversation may exist without a ticket.

A ticket may optionally reference a conversation through `conversation_id`.

This separation allows NovaStore to distinguish between normal customer communication and issues that require formal support workflows.

### Example

A customer sends:

```text
"ممكن أعرف ليه الطلب بتاعي لسه موصلش؟"
```

The AI system may create a ticket:

```text
Ticket Number: NS-T-1001
Category: shipping
Priority: high
Status: open
Assigned Agent: NULL
```

After assignment:

```text
Ticket Number: NS-T-1001
Category: shipping
Priority: high
Status: in_progress
Assigned Agent: Support Agent
```

After resolving the issue:

```text
Ticket Number: NS-T-1001
Category: shipping
Priority: high
Status: resolved
Resolved At: 2026-10-05T20:00:00
```
---

## 8.4 refunds

Stores customer refund requests and tracks the complete refund lifecycle.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `order_id` | UUID | No | FK → `orders.id` |
| `customer_id` | UUID | No | FK → `customers.id` |
| `ticket_id` | UUID | Yes | FK → `tickets.id` |
| `amount` | NUMERIC(12,2) | No | Refund amount, must be >= 0 |
| `reason` | TEXT | No | Reason for the refund |
| `status` | VARCHAR(30) | No | Current refund status |
| `requested_by` | UUID | Yes | FK → `users.id` |
| `approved_by` | UUID | Yes | FK → `users.id` |
| `requested_at` | TIMESTAMPTZ | No | Time when refund was requested |
| `decided_at` | TIMESTAMPTZ | Yes | Time when refund request was approved or rejected |
| `completed_at` | TIMESTAMPTZ | Yes | Time when refund was completed |

### Relationships

```text
orders 1 ─── many refunds

customers 1 ─── many refunds

tickets 1 ─── many refunds

users 1 ─── many refunds
         │
         ├── requested_by
         └── approved_by
```

### Refund Statuses

The V1 refund lifecycle supports:

- `requested`
- `pending_approval`
- `approved`
- `rejected`
- `processing`
- `completed`
- `failed`

A typical refund lifecycle is:

```text
requested
    │
    ▼
pending_approval
    │
    ├───────────────┐
    ▼               ▼
approved          rejected
    │
    ▼
processing
    │
    ├───────────────┐
    ▼               ▼
completed         failed
```

### Design Decisions

- `order_id` identifies the order associated with the refund.
- `customer_id` identifies the customer requesting the refund.
- `ticket_id` is optional because a refund request may or may not originate from a support ticket.
- `amount` represents the specific amount being refunded.
- `amount` must never be negative.
- `requested_by` identifies the user who initiated the refund request when applicable.
- `approved_by` identifies the user who approved the refund when human approval is required.
- `approved_by` remains `NULL` when the refund is rejected, has not yet been reviewed, or does not require human approval.
- `decided_at` remains `NULL` until the refund request is approved or rejected.
- `completed_at` remains `NULL` until the refund is successfully completed.
- Refund status must be validated by both database constraints and backend business logic.

### Why Refunds Are a Separate Entity

Refunds are modeled as a separate table instead of storing refund information directly inside `orders`.

This allows NovaStore to support:

- Multiple refunds for the same order.
- Partial refunds.
- Refund approval workflows.
- Refund rejection.
- Refund processing and completion tracking.
- Failed refunds.
- Auditability of refund operations.

For example:

```text
Order #NS-1001
Total: $1,000

Refund 1:
Amount: $200
Status: completed

Refund 2:
Amount: $150
Status: processing
```

The order can therefore have multiple refund records while preserving the complete refund history.

### Human Approval

Some refunds may require human approval based on business rules.

For example:

```text
Customer
   │
   ▼
Refund Request
   │
   ▼
AI Agent
   │
   ▼
Check Refund Policy
   │
   ├── Automatically Allowed
   │
   └── Human Approval Required
              │
              ▼
        Support Agent
              │
        ┌─────┴─────┐
        ▼           ▼
     Approved     Rejected
        │
        ▼
   Process Refund
```

The `approvals` table will later store the detailed human approval workflow for actions that require explicit authorization.

---

# 9. Knowledge and RAG

## 9.1 documents

Stores documents used as a knowledge source for the AI and RAG system.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `title` | VARCHAR(255) | No | Document title |
| `file_name` | VARCHAR(255) | No | Original file name |
| `document_type` | VARCHAR(50) | No | Type of knowledge document |
| `source` | VARCHAR(255) | No | Document source |
| `uploaded_by` | UUID | No | FK → `users.id` |
| `created_at` | TIMESTAMPTZ | No | Default `now()` |
| `updated_at` | TIMESTAMPTZ | No | Default `now()` |

### Relationship

```text
users 1 ─── many documents
```

### Example Documents

Documents may include:

- Refund policy
- Shipping policy
- Warranty policy
- Return policy
- Product manuals

### Design Decisions

- Each uploaded knowledge document is stored as a separate record.
- `uploaded_by` identifies the user who uploaded the document.
- The original file name is preserved for traceability.
- Documents are later divided into smaller chunks for RAG processing.
- The `source` field identifies where the document originated.

---

## 9.2 document_chunks

Stores smaller text chunks extracted from documents for retrieval and semantic search.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `document_id` | UUID | No | FK → `documents.id` |
| `chunk_index` | INTEGER | No | Position of the chunk within the document |
| `content` | TEXT | No | Text content of the chunk |
| `embedding` | VECTOR | No | Vector embedding used for similarity search |
| `metadata` | JSONB | Yes | Additional chunk metadata |
| `created_at` | TIMESTAMPTZ | No | Chunk creation time |

### Relationship

```text
documents 1 ─── many document_chunks
```

### Constraints

The combination of `document_id` and `chunk_index` should be unique:

```text
UNIQUE(document_id, chunk_index)
```

This prevents duplicate chunk positions within the same document.

### Delete Behavior

`ON DELETE CASCADE` is acceptable because document chunks have no independent business meaning outside their parent document.

If a document is deleted, its chunks should also be deleted.

### Vector Dimension

The vector dimension should be selected after the embedding model has been finalized.

The database design should not hard-code a vector dimension before the embedding model is chosen.

### RAG Role

The `embedding` column stores the numerical representation of the chunk that enables semantic similarity search.

The system can use these embeddings to retrieve relevant policy or knowledge content before generating an AI response.

---

# 10. AI Agent and Observability

## 10.1 agent_runs

Stores individual executions of the AI agent.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `conversation_id` | UUID | No | FK → `conversations.id` |
| `customer_id` | UUID | No | FK → `customers.id` |
| `status` | VARCHAR(30) | No | Current agent run status |
| `model` | VARCHAR(100) | No | AI model used |
| `started_at` | TIMESTAMPTZ | No | Agent execution start time |
| `completed_at` | TIMESTAMPTZ | Yes | Agent execution completion time |
| `error_message` | TEXT | Yes | Error information if execution fails |
| `input_tokens` | INTEGER | Yes | Number of input tokens |
| `output_tokens` | INTEGER | Yes | Number of output tokens |
| `estimated_cost` | NUMERIC(12,6) | Yes | Estimated AI execution cost |

### Relationships

```text
conversations 1 ─── many agent_runs

customers 1 ─── many agent_runs
```

### Agent Run Statuses

The V1 system supports:

- `running`
- `waiting_approval`
- `completed`
- `failed`
- `cancelled`

### Design Decisions

The `agent_runs` table provides observability into AI executions.

It supports:

- Debugging
- Execution tracking
- Latency analysis
- Token usage tracking
- Cost estimation
- AI evaluation
- Failure analysis

Each agent execution should create a separate `agent_runs` record.

---

## 10.2 tool_calls

Stores every tool invocation made during an AI agent run.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `agent_run_id` | UUID | No | FK → `agent_runs.id` |
| `tool_name` | VARCHAR(100) | No | Name of the tool being called |
| `arguments` | JSONB | No | Tool input arguments |
| `result` | JSONB | Yes | Tool execution result |
| `status` | VARCHAR(30) | No | Tool call status |
| `error_message` | TEXT | Yes | Error information if the tool fails |
| `latency_ms` | INTEGER | Yes | Tool execution latency |
| `created_at` | TIMESTAMPTZ | No | Tool call creation time |

### Relationship

```text
agent_runs 1 ─── many tool_calls
```

### Design Decisions

- `arguments` uses `JSONB` because different tools require different input structures.
- `result` uses `JSONB` because different tools can return different structures.
- Tool calls must be associated with the agent run that initiated them.
- `latency_ms` allows tool performance to be measured.
- Failed tool calls should store an error message when available.

### Example

```text
Agent Run
   │
   ▼
Tool Call
   │
   ├── tool_name: get_order
   ├── arguments: {"order_number": "NS-1001"}
   ├── result: {"status": "in_transit"}
   └── status: completed
```

---

## 10.3 approvals

Stores human approval requests for AI actions that require authorization.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `agent_run_id` | UUID | No | FK → `agent_runs.id` |
| `tool_call_id` | UUID | Yes | FK → `tool_calls.id` |
| `ticket_id` | UUID | Yes | FK → `tickets.id` |
| `action` | VARCHAR(100) | No | Action requiring approval |
| `status` | VARCHAR(30) | No | Approval status |
| `requested_at` | TIMESTAMPTZ | No | Approval request time |
| `decided_at` | TIMESTAMPTZ | Yes | Decision time |
| `decided_by` | UUID | Yes | FK → `users.id` |
| `reason` | TEXT | Yes | Approval or rejection reason |

### Relationships

```text
agent_runs 1 ─── many approvals

tool_calls 1 ─── 0..many approvals

tickets 1 ─── 0..many approvals

users 1 ─── many approvals
```

### Approval Statuses

The V1 system supports:

- `pending`
- `approved`
- `rejected`
- `expired`

### Example Action

```text
action = create_refund
```

### Design Decisions

The approval system allows the AI agent to pause execution when a sensitive action requires human authorization.

Example:

```text
AI Agent
   │
   ▼
Sensitive Action
   │
   ▼
Approval Required
   │
   ▼
Approval Record
   │
   ├── Approved
   │
   └── Rejected
```

If approved, the agent workflow can resume.

If rejected, the agent must not execute the protected action.

---

# 11. Audit and Security

## 11.1 audit_logs

Stores security and business audit events.

| Column | Type | Null | Constraints / Purpose |
|---|---|---:|---|
| `id` | UUID | No | Primary key |
| `actor_user_id` | UUID | Yes | FK → `users.id` |
| `actor_type` | VARCHAR(30) | No | Type of actor |
| `action` | VARCHAR(100) | No | Action that occurred |
| `entity_type` | VARCHAR(100) | No | Type of affected entity |
| `entity_id` | UUID | Yes | Identifier of affected entity |
| `metadata` | JSONB | Yes | Additional event information |
| `created_at` | TIMESTAMPTZ | No | Event creation time |

### Relationship

```text
users 1 ─── many audit_logs
```

### Example Audit Events

Examples include:

- `refund_requested`
- `refund_approved`
- `order_cancelled`
- `ticket_assigned`
- `document_uploaded`
- `user_role_changed`

### Polymorphic Entity Reference

The combination of:

```text
entity_type
entity_id
```

allows an audit record to refer to different entity types.

For example:

```text
entity_type = "order"
entity_id   = "..."
```

or:

```text
entity_type = "refund"
entity_id   = "..."
```

The application layer is responsible for validating that the referenced entity exists.

### Design Decisions

- Audit logs should be append-only from the application perspective.
- Existing audit records should not normally be modified or deleted.
- Sensitive business actions should generate audit events.
- `metadata` allows additional context to be stored without changing the table schema for every new audit event.

---

# 12. Relationships

## 12.1 Identity Relationships

```text
users 1 ─── 0..1 customers
```

One user account can have zero or one customer profile.

---

## 12.2 Commerce Relationships

```text
customers 1 ─── many orders

orders 1 ─── many order_items

products 1 ─── many order_items

products 1 ─── 1 inventory

orders 1 ─── many payments

orders 1 ─── many shipments

orders 1 ─── many order_status_history
```

---

## 12.3 Customer Operations Relationships

```text
customers 1 ─── many conversations

conversations 1 ─── many messages

customers 1 ─── many tickets

tickets many ─── 1 support agent

orders 1 ─── many refunds

customers 1 ─── many refunds

tickets 1 ─── many refunds
```

The relationship between tickets and refunds is optional because not every ticket results in a refund.

---

## 12.4 RAG Relationships

```text
documents 1 ─── many document_chunks
```

Each document can contain multiple chunks.

---

## 12.5 AI Relationships

```text
conversations 1 ─── many agent_runs

agent_runs 1 ─── many tool_calls

agent_runs 1 ─── many approvals

tool_calls 1 ─── 0..many approvals
```

---

## 12.6 Audit Relationships

```text
users 1 ─── many audit_logs
```

Audit logs use `entity_type` and `entity_id` to identify the affected business entity.

---

# 13. Index Strategy

Indexes should be created for columns that are frequently used for:

- Lookups
- Filtering
- Joins
- Sorting
- Relationship traversal

## 13.1 Identity Indexes

```text
users(email)

customers(user_id)
```

`users.email` supports login and customer lookup.

`customers.user_id` supports mapping an authenticated user to a customer profile.

---

## 13.2 Product Indexes

```text
products(sku)
```

The SKU is frequently used to identify products.

---

## 13.3 Order Indexes

```text
orders(order_number)

orders(customer_id)

orders(status)
```

These indexes support:

- Order lookup by order number.
- Retrieving a customer's orders.
- Filtering orders by status.

---

## 13.4 Order Item Indexes

```text
order_items(order_id)

order_items(product_id)
```

These indexes support retrieving:

- Items belonging to an order.
- Orders containing a specific product.

---

## 13.5 Shipment Indexes

```text
shipments(order_id)

shipments(tracking_number)
```

These indexes support order shipment lookup and tracking-number searches.

---

## 13.6 Conversation and Message Indexes

```text
conversations(customer_id)

messages(conversation_id, created_at)
```

The composite message index supports chronological retrieval of messages within a conversation.

---

## 13.7 Ticket Indexes

```text
tickets(customer_id)

tickets(assigned_agent_id)

tickets(status)
```

These indexes support:

- Customer ticket lookup.
- Agent workload retrieval.
- Filtering tickets by status.

---

## 13.8 Refund Indexes

```text
refunds(order_id)
```

This supports retrieving refund history for an order.

---

## 13.9 RAG Indexes

```text
document_chunks(document_id)
```

The vector index should be added only after:

- The embedding model is finalized.
- The vector dimension is finalized.
- The similarity metric is finalized.

The vector indexing strategy should therefore be selected after the embedding architecture is confirmed.

---

## 13.10 Agent Observability Indexes

```text
agent_runs(conversation_id)

tool_calls(agent_run_id)
```

These indexes support tracing an AI workflow from a conversation to its agent runs and tool calls.

---

## 13.11 Audit Indexes

```text
audit_logs(entity_id)
```

This supports retrieving audit events related to a specific business entity.

### Indexing Principle

Do not blindly index every column.

Every index introduces:

- Additional storage requirements.
- Additional write cost.
- Additional update cost.
- Maintenance overhead.

Indexes should therefore be added based on actual query patterns.

---

# 14. Constraints

## 14.1 Uniqueness Constraints

The following values must be unique:

```text
users.email

customers.user_id

products.sku

inventory.product_id

orders.order_number

tickets.ticket_number

(document_id, chunk_index)
```

The combination of `document_id` and `chunk_index` must be unique so that each document has only one chunk at each position.

---

## 14.2 Quantity Constraints

The following quantities must never be negative:

```text
inventory.available_quantity >= 0

inventory.reserved_quantity >= 0
```

Order item quantities must be greater than zero:

```text
order_items.quantity > 0
```

---

## 14.3 Money Constraints

The following monetary values must be non-negative:

```text
products.price >= 0

orders.total_amount >= 0

order_items.unit_price >= 0

refunds.amount >= 0

payments.amount >= 0
```

---

## 14.4 Foreign Key Constraints

Foreign keys must enforce the existence of referenced records.

Examples:

```text
orders.customer_id
    → customers.id

order_items.order_id
    → orders.id

order_items.product_id
    → products.id

inventory.product_id
    → products.id
```

Foreign key constraints protect the structural integrity of the database.

---

# 15. Delete and Cascade Strategy

Deletion behavior must be designed carefully because NovaStore contains important business and financial data.

## 15.1 Appropriate Cascade

The following cascade is acceptable:

```text
documents
    │
    └── document_chunks
```

If a document is deleted, its chunks can be deleted automatically because the chunks have no independent business meaning.

Example:

```text
DELETE document
      │
      ▼
DELETE related document_chunks
```

---

## 15.2 Business Data

Important business records should generally not be destructively deleted through cascading relationships.

For example:

```text
customers
   │
   └── orders
          │
          ├── payments
          ├── shipments
          └── refunds
```

Deleting a customer must not automatically delete historical orders, payments, shipments, or refunds.

### Design Decision

For important business data, prefer:

- Deactivation
- Retention policies
- Archiving
- Soft-delete strategies where appropriate

instead of destructive cascading deletion.

---

# 16. Business Logic vs Database Constraints

The database should enforce structural integrity, while the backend should enforce complex business rules.

## 16.1 Database Constraints

The database should enforce rules such as:

```text
quantity > 0

price >= 0

email is unique

foreign key exists
```

These are structural rules that should remain true regardless of which application interacts with the database.

---

## 16.2 Backend Business Rules

Complex business rules should be implemented in the backend.

Examples:

```text
An order can be cancelled only while it is processing.

A refund can be requested only if the order satisfies the refund policy.

A refund may be allowed only within 14 days.

Only eligible products can be refunded.

Refunds above $500 require human approval.
```

### Design Decision

Business rules should not be embedded entirely inside database constraints.

Keeping business workflows in the backend makes the database:

- Easier to reuse.
- Easier to test.
- Easier to evolve.
- Independent from a specific application workflow.

The database should protect data integrity, while the backend controls business behavior.

---

# 17. Authorization

Authorization must be enforced by the backend.

The AI agent must never be treated as a security boundary.

## 17.1 Ownership Verification

For customer-owned resources, the backend should follow this flow:

```text
Authenticated User
        │
        ▼
Customer ID
        │
        ▼
Requested Order
        │
        ▼
Verify Ownership
        │
   ┌────┴────┐
   ▼         ▼
 Allow      Reject
```

The backend must verify that the requested order belongs to the authenticated customer.

---

## 17.2 Example

If Customer A asks:

```text
"Show me Customer B's order."
```

The AI model's decision is irrelevant to authorization.

The backend must perform:

```text
Authenticated Customer
        │
        ▼
Requested Order
        │
        ▼
Ownership Check
        │
        ▼
Customer does not own order
        │
        ▼
DENY
```

### Critical Security Principle

The LLM is not an authorization mechanism.

Even if the AI decides that an action is acceptable, the backend must independently verify:

- User identity.
- Resource ownership.
- Role permissions.
- Action permissions.
- Business rules.

---

# 18. RAG Data Flow

The RAG system allows the AI agent to answer questions using trusted NovaStore knowledge.

## 18.1 Document Ingestion

```text
Admin uploads document
        │
        ▼
documents
        │
        ▼
Document Processing
        │
        ▼
Chunking
        │
        ▼
document_chunks
        │
        ▼
Embedding Generation
        │
        ▼
embedding VECTOR
```

The document is converted into chunks and each chunk receives an embedding.

---

## 18.2 Query Flow

When a customer asks a knowledge-based question:

```text
Customer Question
        │
        ▼
Question Embedding
        │
        ▼
Vector Similarity Search
        │
        ▼
Top-K Relevant Chunks
        │
        ▼
LLM
        │
        ▼
Grounded Response
```

The retrieved chunks provide the factual context used by the LLM.

---

## 18.3 Grounding Rule

If the system cannot find sufficient evidence in the knowledge base:

```text
Customer Question
        │
        ▼
Knowledge Search
        │
        ▼
No Sufficient Evidence
        │
        ├── Do not invent policy
        │
        └── State that knowledge is insufficient
                    or escalate to a human
```

### Critical RAG Principle

The AI must not invent company policies when the knowledge base does not provide supporting evidence.

---

# 19. Agent Execution

The AI agent follows a controlled execution workflow.

## 19.1 Order Status Example

```text
Customer
    │
    ▼
Conversation
    │
    ▼
Agent Run
    │
    ▼
Intent Detection
    │
    ▼
get_order Tool
    │
    ▼
Authorization Check
    │
    ▼
Policy Check
    │
    ▼
cancel_order Tool
    │
    ▼
Database Update
    │
    ▼
Verification
    │
    ▼
Final Response
```

### Execution Trace

The complete workflow can be traced through:

```text
conversation
      │
      ▼
agent_run
      │
      ▼
tool_call
      │
      ▼
database operation
```

If human approval is required:

```text
agent_run
      │
      ▼
tool_call
      │
      ▼
approval
      │
      ▼
Human Decision
      │
      ▼
Resume Workflow
```

### Design Decision

The AI agent should not directly bypass backend workflows.

Every sensitive operation should pass through deterministic backend validation.

---

# 20. Refund Approval

Refunds are an example of a sensitive AI-assisted workflow.

## 20.1 Refund Workflow

```text
Customer
    │
    ▼
Refund Request
    │
    ▼
Agent Run
    │
    ▼
Get Order
    │
    ▼
Verify Ownership
    │
    ▼
Check Refund Policy
    │
    ▼
Refund Amount = $850
    │
    ▼
Human Approval Required
    │
    ▼
Approval Record
    │
    ▼
Support Agent
    │
    ├───────────────┐
    ▼               ▼
 Approve          Reject
    │               │
    ▼               ▼
Resume Agent      Stop Workflow
Workflow
    │
    ▼
Execute Refund
    │
    ▼
Verify Result
    │
    ▼
Customer Response
```

---

## 20.2 Tables Involved

The refund approval workflow uses:

```text
conversations

agent_runs

tool_calls

refunds

approvals

audit_logs
```

Each table provides a different responsibility:

| Table | Responsibility |
|---|---|
| `conversations` | Customer communication |
| `agent_runs` | AI execution tracking |
| `tool_calls` | Tool invocation tracking |
| `refunds` | Refund business entity |
| `approvals` | Human authorization |
| `audit_logs` | Security and business audit trail |

---

# 21. Security

Security must be enforced across authentication, authorization, data storage, AI tools, and audit logging.

## 21.1 Authentication

The system must use secure password hashing.

Passwords must never be stored in plain text.

```text
User Password
      │
      ▼
Secure Password Hashing
      │
      ▼
password_hash
```

The database stores only the resulting secure password hash.

---

## 21.2 Authorization

Authorization must verify:

- User identity.
- Resource ownership.
- User role.
- Action permissions.
- Business rules.

The backend remains the final authority for protected operations.

---

## 21.3 Sensitive Data

The system must never log or store sensitive credentials such as:

- Passwords.
- API keys.
- Raw payment credentials.
- Authentication tokens.
- CVV/CVC codes.
- Payment PINs.

---

## 21.4 AI Tool Security

Tool arguments and tool results must be reviewed for sensitive information before being stored in `tool_calls`.

For example:

```text
AI Agent
   │
   ▼
Tool Arguments
   │
   ▼
Sensitive Data Check
   │
   ├── Safe → Store
   │
   └── Sensitive → Redact / Do Not Store
```

---

## 21.5 Audit Logging

Sensitive actions should generate audit records.

Examples include:

- Refund approval.
- Order cancellation.
- User role changes.
- Document uploads.
- Ticket assignment.

These events should be recorded in `audit_logs`.

---

# 22. V1 Scope

The V1 architecture intentionally keeps the system simple and focused.

## 22.1 Business Policies

Business policies are implemented in backend configuration or application code.

A dedicated database policy engine is not included in V1.

```text
Backend
   │
   └── Business Policies
```

---

## 22.2 Inventory

V1 uses one inventory record per product.

```text
products 1 ─── 1 inventory
```

Multiple warehouses are deferred to V2.

---

## 22.3 Support History

Major support and business actions are tracked through:

```text
audit_logs
```

A dedicated ticket-event history table is not required in V1.

---

## 22.4 Vector Search

PostgreSQL with `pgvector` is used for vector storage and similarity search.

```text
PostgreSQL
    │
    └── pgvector
           │
           └── document embeddings
```

A separate vector database is not required in V1.

---

## 22.5 Agent Architecture

V1 uses:

```text
Single AI Agent
       │
       ▼
Deterministic Backend Workflows
```

A multi-agent architecture is deferred to a future version.

---

## 22.6 Deployment Architecture

V1 uses a monolithic backend architecture.

```text
NovaStore Application
        │
        ├── API
        ├── Business Logic
        ├── AI Agent
        ├── Tool Layer
        └── Database
```

Microservices are not required for V1.

---

# 23. V2 Possibilities

The following capabilities may be introduced in future versions when justified by actual requirements.

## 23.1 Possible V2 Tables and Features

- `warehouses`
- `inventory_movements`
- `ticket_events`
- `business_rules`
- `policy_versions`
- `notification_logs`
- `agent_memory`
- `evaluation_cases`
- `model_versions`
- Dedicated analytics tables
- Multiple communication channels
- External payment integrations
- External shipping integrations
- Multi-agent architecture
- Dedicated vector infrastructure

### Design Principle

V2 features should only be introduced when there is a clear business or technical justification.

The V1 architecture should remain intentionally simple rather than prematurely implementing infrastructure that is not yet required.

---

# 24. Final V1 Architecture

The final V1 database architecture can be summarized as follows:

```text
                         ┌──────────────┐
                         │    USERS     │
                         └──────┬───────┘
                                │
                              1 │ 0..1
                                │
                         ┌──────▼───────┐
                         │  CUSTOMERS   │
                         └──────┬───────┘
                                │
                 ┌──────────────┼─────────────────┐
                 │              │                 │
                 ▼              ▼                 ▼
              ORDERS      CONVERSATIONS        TICKETS
                 │              │                 │
        ┌────────┼──────┐       │            ┌────┴─────┐
        │        │      │       │            │          │
        ▼        ▼      ▼       ▼            ▼          ▼
 ORDER_ITEMS PAYMENTS SHIPMENTS MESSAGES   REFUNDS   AGENT...
        │
        ▼
    PRODUCTS
        │
        ▼
   INVENTORY

ORDERS
   │
   ▼
ORDER_STATUS_HISTORY

DOCUMENTS
   │
   ▼
DOCUMENT_CHUNKS
   │
   ▼
 EMBEDDINGS

CONVERSATIONS
      │
      ▼
  AGENT_RUNS
      │
      ├───────────────┐
      ▼               ▼
 TOOL_CALLS       APPROVALS

AUDIT_LOGS
```

### V1 Architecture Principles

The architecture provides:

- Customer identity and authentication.
- Product and inventory management.
- Order management.
- Payment and shipment tracking.
- Customer conversations.
- Support ticket management.
- Refund workflows.
- Knowledge base and RAG.
- AI agent execution tracking.
- Tool execution tracking.
- Human approval workflows.
- Security and audit logging.

The architecture intentionally avoids unnecessary complexity while providing a strong foundation for future expansion.

---

# 25. Definition of Done

The V1 database design is considered complete when the following requirements have been satisfied.

## 25.1 Database Design Checklist

- [x] Business entities identified.
- [x] Relationships defined.
- [x] ERD designed.
- [x] 19 V1 tables defined.
- [x] Columns defined.
- [x] Data types selected.
- [x] Primary key relationships defined.
- [x] Foreign key relationships defined.
- [x] Nullability considered.
- [x] Database constraints defined.
- [x] Index strategy defined.
- [x] Cascade strategy defined.
- [x] Security considerations documented.
- [x] RAG storage designed.
- [x] AI agent observability designed.
- [x] Human approval workflow designed.
- [x] V1 and V2 scope documented.

## 25.2 V1 Database Design Status

```text
Database Design
       │
       ▼
   Completed
       │
       ├── Identity
       ├── Commerce
       ├── Customer Operations
       ├── Knowledge / RAG
       ├── AI Agent
       ├── Observability
       ├── Approvals
       └── Audit / Security
```

The V1 database design has been implemented in PostgreSQL, validated against the actual database schema, populated with seed data, and verified through database tests.

The V1 database is now considered implemented and validated, and is ready for the next application development phase.