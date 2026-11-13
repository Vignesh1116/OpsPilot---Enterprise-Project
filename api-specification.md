# OpsPilot – REST API Specification (v1)

All endpoints are prefixed with `/api/v1`. Requests and responses use standard `application/json`.
Authentication uses `Authorization: Bearer <JWT_ACCESS_TOKEN>`.

---

## 1. Authentication & Session (`/api/v1/auth`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticate with email/password, return access & refresh JWTs | Public |
| `POST` | `/auth/refresh` | Refresh expired access token using refresh token | Public |
| `POST` | `/auth/logout` | Invalidate refresh token session | Authenticated |
| `GET` | `/auth/me` | Fetch active user profile, company info, and role permissions | Authenticated |
| `PUT` | `/auth/password` | Update current user password | Authenticated |

---

## 2. Organization, Facilities & Departments (`/api/v1/organizations`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/organizations/company` | Retrieve active company profile | `company:read` |
| `PUT` | `/organizations/company` | Update company metadata & tax details | `company:update` |
| `GET` | `/organizations/locations` | List all operating locations (Coimbatore, Tiruppur, etc.) | `locations:read` |
| `POST` | `/organizations/locations` | Register a new operating facility | `locations:create` |
| `GET` | `/organizations/locations/{id}` | Get facility details | `locations:read` |
| `PUT` | `/organizations/locations/{id}` | Update facility details | `locations:update` |
| `GET` | `/organizations/departments` | List company departments | `departments:read` |
| `POST` | `/organizations/departments` | Create new department | `departments:create` |

---

## 3. User Management & RBAC (`/api/v1/users`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/users` | Paginated list of users with role, location, and department filters | `users:read` |
| `POST` | `/users` | Create/onboard a new employee/technician | `users:create` |
| `GET` | `/users/{id}` | Retrieve user profile & assigned roles | `users:read` |
| `PUT` | `/users/{id}` | Update user details, role assignments, or active status | `users:update` |
| `GET` | `/roles` | List available roles and assigned permissions | `roles:read` |
| `POST` | `/roles` | Create custom operational role | `roles:create` |
| `GET` | `/permissions` | List all system permission codes | `roles:read` |

---

## 4. Asset Management (`/api/v1/assets`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/assets` | Search & filter assets by location, category, status, and criticality | `assets:read` |
| `POST` | `/assets` | Register a new asset with tag, category, and purchase details | `assets:create` |
| `GET` | `/assets/{id}` | Retrieve complete asset record including maintenance summary | `assets:read` |
| `PUT` | `/assets/{id}` | Update asset specifications, location, or status | `assets:update` |
| `POST` | `/assets/{id}/decommission` | Decommission an asset with rationale | `assets:decommission` |
| `GET` | `/assets/categories` | List asset taxonomies and depreciation rules | `assets:read` |
| `POST` | `/assets/categories` | Create new asset category | `assets:create` |

---

## 5. Preventive Maintenance & Schedules (`/api/v1/maintenance`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/maintenance/schedules` | List active preventive maintenance schedules | `maintenance:read` |
| `POST` | `/maintenance/schedules` | Create recurring maintenance schedule for an asset | `maintenance:create` |
| `GET` | `/maintenance/schedules/{id}` | Get schedule details | `maintenance:read` |
| `PUT` | `/maintenance/schedules/{id}` | Update schedule frequency or lead time | `maintenance:update` |
| `POST` | `/maintenance/schedules/{id}/generate-work-order` | Manually trigger a preventive work order from schedule | `maintenance:trigger` |
| `GET` | `/maintenance/history` | Historical audit of all completed maintenance executions | `maintenance:read` |

---

## 6. Work Orders & Execution (`/api/v1/work-orders`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/work-orders` | Paginated work orders with status, priority, and location filters | `work_orders:read` |
| `POST` | `/work-orders` | Create an issue report or maintenance work order | `work_orders:create` |
| `GET` | `/work-orders/{id}` | Retrieve work order details, comments, history, and parts | `work_orders:read` |
| `PUT` | `/work-orders/{id}` | Edit work order details | `work_orders:update` |
| `POST` | `/work-orders/{id}/assign` | Assign technician and schedule dates | `work_orders:assign` |
| `POST` | `/work-orders/{id}/status` | Transition status (`in_progress`, `on_hold`, `completed`) | `work_orders:update` |
| `POST` | `/work-orders/{id}/comments` | Post an operational update or shift handoff comment | `work_orders:comment` |
| `POST` | `/work-orders/{id}/parts` | Request / requisition spare parts from local inventory | `work_orders:parts` |
| `POST` | `/work-orders/{id}/complete` | Close work order, log actual hours, record maintenance history | `work_orders:complete` |

---

## 7. Inventory & Stock Management (`/api/v1/inventory`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/inventory/items` | Query inventory catalogue with location and low-stock filters | `inventory:read` |
| `POST` | `/inventory/items` | Add new inventory SKU | `inventory:create` |
| `GET` | `/inventory/items/{id}` | Get inventory SKU details and stock balance | `inventory:read` |
| `PUT` | `/inventory/items/{id}` | Update min stock thresholds, bin location, unit cost | `inventory:update` |
| `GET` | `/inventory/low-stock` | Retrieve SKUs falling below minimum reorder thresholds | `inventory:read` |
| `POST` | `/inventory/adjustments` | Manual stock reconciliation adjustment (with audit notes) | `inventory:adjust` |
| `POST` | `/inventory/transfers` | Transfer stock between locations (e.g. Salem Store to Coimbatore) | `inventory:transfer` |
| `GET` | `/inventory/movements` | Immutable audit log of all historical stock movements | `inventory:read` |

---

## 8. Procurement & Vendors (`/api/v1/procurement`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/procurement/vendors` | List approved vendors and suppliers | `vendors:read` |
| `POST` | `/procurement/vendors` | Onboard a new vendor | `vendors:create` |
| `GET` | `/procurement/vendors/{id}` | Get vendor profile and order history | `vendors:read` |
| `PUT` | `/procurement/vendors/{id}` | Update vendor details or rating | `vendors:update` |
| `GET` | `/procurement/purchase-orders` | List purchase orders with status filtering | `procurement:read` |
| `POST` | `/procurement/purchase-orders` | Create draft purchase order with line items | `procurement:create` |
| `GET` | `/procurement/purchase-orders/{id}` | Get PO details and item breakdown | `procurement:read` |
| `POST` | `/procurement/purchase-orders/{id}/approve` | Approve purchase order for vendor dispatch | `procurement:approve` |
| `POST` | `/procurement/goods-receipts` | Create Goods Receipt Note (GRN) & automatically increment stock | `procurement:receive` |
| `GET` | `/procurement/goods-receipts` | Query historical goods receipt notes | `procurement:read` |

---

## 9. System Notifications & Audit Trail (`/api/v1/system`)

| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/system/notifications` | Get user notifications (read/unread) | Authenticated |
| `POST` | `/system/notifications/{id}/read` | Mark specific notification as read | Authenticated |
| `POST` | `/system/notifications/mark-all-read` | Mark all user notifications as read | Authenticated |
| `GET` | `/system/audit-logs` | Query company compliance audit trail with entity filters | `audit:read` |
| `GET` | `/system/health` | Service health check (PostgreSQL & Redis connection status) | Public |
