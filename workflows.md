# OpsPilot – Core Business Workflows

## 1. Asset Lifecycle Management Workflow

```mermaid
stateDiagram-v2
    [*] --> Commissioned: Registered in Inventory & Deployed to Location
    Commissioned --> Operational: Initial Inspection Passed & Scheduled
    Operational --> InMaintenance: Preventive Schedule Due / Incident Logged
    InMaintenance --> Operational: Maintenance Completed & Tested
    InMaintenance --> OutOfService: Critical Failure / Awaiting Replacement Parts
    OutOfService --> InMaintenance: Spare Parts Received & Work Resumed
    Operational --> Decommissioned: End of Economic Lifetime / Scrapped
    OutOfService --> Decommissioned: Beyond Repair
    Decommissioned --> [*]
```

### Steps & Verification
1. **Commissioning**: Asset created with unique company asset tag, assigned to a specific facility (e.g., Coimbatore Factory - Spinning Mill 1), with initial purchase cost and depreciation schedule.
2. **Preventive Alignment**: Asset linked to one or more maintenance schedules (e.g. Monthly spindle bearing lubrication).
3. **Status Transitions**: State shifts from `operational` to `in_maintenance` when a work order starts, locking the asset status. Upon completion and supervisor sign-off, status returns to `operational`.
4. **Decommissioning**: Retains historical work orders, costs, and audit logs without cascading deletion.

---

## 2. Preventive Maintenance & Auto-Work Order Generation

```mermaid
sequenceDiagram
    autonumber
    actor Scheduler as Celery Beat / Cron
    participant MS as Maintenance Schedule Service
    participant WO as Work Order Service
    participant DB as PostgreSQL DB
    participant Notify as Notification Service
    actor Tech as Assigned Technician

    Scheduler->>MS: Run daily check for schedules where next_due_date <= today + lead_time_days
    MS->>DB: Query active schedules
    loop For each due schedule
        MS->>WO: Create Work Order (type='preventive', priority=schedule.priority)
        WO->>DB: Insert work_order & work_order_history
        MS->>DB: Update schedule (last_generated_at=now, calculate next_due_date)
        MS->>Notify: Dispatch alert to Operations Manager and Assigned Tech
    end
    Notify-->>Tech: Push Notification ("Preventive WO-2026-0042 Generated")
```

---

## 3. Work Order Execution & Atomic Spare Parts Requisition

This workflow handles the issue, execution, spare parts deduction, and historical archiving of work orders.

```mermaid
sequenceDiagram
    autonumber
    actor Tech as Maintenance Technician
    participant WO as Work Order Service
    participant Inv as Inventory Service
    participant DB as PostgreSQL (ACID Transaction)
    actor Lead as Operations Manager

    Tech->>WO: Update Work Order status to "in_progress"
    WO->>DB: Record status transition in work_order_history
    Tech->>WO: Requisition spare part (e.g. 2 x SKF Bearing 6204)
    WO->>Inv: Request deduction from Salem Store / Coimbatore Store
    critical Atomic Inventory Deduction
        Inv->>DB: Lock inventory_items row (SELECT FOR UPDATE)
        Inv->>DB: Verify current_stock >= requested_quantity
        Inv->>DB: Deduct current_stock = current_stock - quantity
        Inv->>DB: Insert stock_movements (type='work_order_issue', ref_id=work_order_id)
        Inv->>DB: Insert/update work_order_parts (status='issued')
    end
    Inv-->>WO: Confirmation & Total parts cost updated
    Tech->>WO: Submit Work Order Completion (actual_hours, notes)
    WO->>DB: Insert maintenance_history entry
    WO->>Lead: Notify for final sign-off
    Lead->>WO: Approve & close Work Order (status='completed')
    WO->>DB: Set asset status back to 'operational'
```

---

## 4. Procurement, Purchase Orders & Goods Receipt Note (GRN)

```mermaid
sequenceDiagram
    autonumber
    actor InvExec as Inventory Executive
    actor Mgr as Operations Manager
    participant Proc as Procurement Service
    participant Inv as Inventory Service
    participant DB as PostgreSQL DB
    actor Vendor as Vendor (e.g., Lakshmi Machine Works)

    InvExec->>Proc: Create Draft Purchase Order (items, quantities, unit prices)
    Proc->>DB: Save purchase_orders (status='draft') and purchase_order_items
    InvExec->>Proc: Submit for approval
    Proc->>Mgr: Route approval request
    Mgr->>Proc: Approve Purchase Order
    Proc->>DB: Update status to 'approved'
    Proc->>Vendor: Transmit PO
    Note over Vendor: Vendor ships ordered components with Invoice
    InvExec->>Proc: Create Goods Receipt (GRN) with Invoice details & received quantities
    critical Stock Inwarding
        Proc->>Inv: Increment inventory_items current_stock
        Proc->>DB: Insert stock_movements (type='goods_receipt', ref=PO_id)
        Proc->>DB: Update purchase_order_items (quantity_received)
        Proc->>DB: Update purchase_orders status ('partially_received' or 'received')
    end
    Proc-->>InvExec: GRN Verified & Inventory updated
```

---

## 5. Security & Multi-Tenant Data Isolation Enforcement

```mermaid
flowchart LR
    Req[Incoming HTTP Request] --> JWT[JWT Verification Middleware]
    JWT --> Context[Extract User ID & Company ID]
    Context --> Dep[FastAPI Depends: get_current_active_user]
    Dep --> Service[Domain Service Layer]
    Service --> Repo[Repository Layer]
    Repo --> SQL[(PostgreSQL Query)]
    
    subgraph Isolation Rule
        SQL -.-> Condition["WHERE table.company_id = :current_company_id"]
    end
```

Every query executed by OpsPilot binds `:current_company_id` from the decoded token claims. Even if a malicious or errant payload contains an ID from another tenant, queries fail to find the entity because of the composite predicate `WHERE id = :id AND company_id = :company_id`.
