import uuid
from datetime import timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.auth import Role, User, UserRole
from app.models.organization import Company


@pytest.fixture
async def setup_auth_data(db_session: AsyncSession):
    """Seed test database with two companies, roles, and users with different roles."""
    # 1. Create System Roles
    roles = {}
    for code in [
        "COMPANY_ADMIN",
        "OPERATIONS_MANAGER",
        "MAINTENANCE_TECHNICIAN",
        "INVENTORY_EXECUTIVE",
        "EMPLOYEE",
    ]:
        role = Role(
            id=uuid.uuid4(),
            code=code,
            name=code.replace("_", " ").title(),
            is_system_role=True,
        )
        db_session.add(role)
        roles[code] = role

    # 2. Create Company A (Coimbatore HQ)
    company_a = Company(
        id=uuid.uuid4(),
        name="Coimbatore Textiles Ltd",
        slug="coimbatore-textiles",
        code="CBE-TEX",
        address="Avanashi Road",
        city="Coimbatore",
        state="Tamil Nadu",
        country="India",
        postal_code="641018",
        phone="+91-422-2550000",
        email="info@coimbatoretextiles.com",
        tax_id="33AAAAA0000A1Z5",
        is_active=True,
    )
    db_session.add(company_a)

    # 3. Create Company B (Madurai Spinning Mills - Isolated Tenant)
    company_b = Company(
        id=uuid.uuid4(),
        name="Madurai Spinning Mills Ltd",
        slug="madurai-spinning",
        code="MDU-SPIN",
        address="Alagar Kovil Road",
        city="Madurai",
        state="Tamil Nadu",
        country="India",
        postal_code="625002",
        phone="+91-452-2550000",
        email="info@maduraispinning.com",
        tax_id="33BBBBB1111B1Z9",
        is_active=True,
    )
    db_session.add(company_b)

    await db_session.flush()

    # 4. Create Users for Company A
    admin_user = User(
        id=uuid.uuid4(),
        company_id=company_a.id,
        email="admin@coimbatoretextiles.com",
        password_hash=get_password_hash("AdminSecurePassword123!"),
        first_name="Admin",
        last_name="Vignesh",
        designation="Chief Operating Officer",
        is_active=True,
        is_verified=True,
    )
    db_session.add(admin_user)

    employee_user = User(
        id=uuid.uuid4(),
        company_id=company_a.id,
        email="employee@coimbatoretextiles.com",
        password_hash=get_password_hash("EmployeePassword123!"),
        first_name="Ramesh",
        last_name="Kumar",
        designation="Junior Technician",
        is_active=True,
        is_verified=True,
    )
    db_session.add(employee_user)

    disabled_user = User(
        id=uuid.uuid4(),
        company_id=company_a.id,
        email="disabled@coimbatoretextiles.com",
        password_hash=get_password_hash("DisabledPassword123!"),
        first_name="Suresh",
        last_name="Rajan",
        designation="Former Operator",
        is_active=False,
        is_verified=True,
    )
    db_session.add(disabled_user)

    # 5. Create User for Company B (Isolated tenant)
    other_tenant_user = User(
        id=uuid.uuid4(),
        company_id=company_b.id,
        email="admin@maduraispinning.com",
        password_hash=get_password_hash("OtherAdminPassword123!"),
        first_name="Murugan",
        last_name="P",
        designation="Plant Manager",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_tenant_user)

    await db_session.flush()

    # Assign roles
    db_session.add(UserRole(user_id=admin_user.id, role_id=roles["COMPANY_ADMIN"].id))
    db_session.add(UserRole(user_id=employee_user.id, role_id=roles["EMPLOYEE"].id))
    db_session.add(UserRole(user_id=disabled_user.id, role_id=roles["EMPLOYEE"].id))
    db_session.add(UserRole(user_id=other_tenant_user.id, role_id=roles["COMPANY_ADMIN"].id))

    await db_session.commit()

    return {
        "company_a": company_a,
        "company_b": company_b,
        "admin_user": admin_user,
        "employee_user": employee_user,
        "disabled_user": disabled_user,
        "other_tenant_user": other_tenant_user,
    }


@pytest.mark.asyncio
async def test_valid_login(client: AsyncClient, setup_auth_data):
    """Test valid login returns access and refresh tokens without password hash."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@coimbatoretextiles.com",
            "password": "AdminSecurePassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@coimbatoretextiles.com"
    assert "COMPANY_ADMIN" in data["user"]["roles"]
    # Verify password hash is never leaked
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


@pytest.mark.asyncio
async def test_invalid_login_wrong_password(client: AsyncClient, setup_auth_data):
    """Test login with incorrect password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@coimbatoretextiles.com",
            "password": "WrongPasswordAttempt!",
        },
    )
    assert response.status_code == 401
    assert response.json()["title"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_invalid_login_non_existent_user(client: AsyncClient, setup_auth_data):
    """Test login with non-existent user returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@coimbatoretextiles.com",
            "password": "SomePassword123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_disabled_account_login_rejected(client: AsyncClient, setup_auth_data):
    """Test deactivated account cannot log in."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "disabled@coimbatoretextiles.com",
            "password": "DisabledPassword123!",
        },
    )
    assert response.status_code == 401
    assert "disabled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unauthorized_endpoint_without_token(client: AsyncClient, setup_auth_data):
    """Test protected endpoints reject requests without token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_rejected(client: AsyncClient, setup_auth_data):
    """Test that expired JWT access token is rejected with 401."""
    admin = setup_auth_data["admin_user"]
    expired_token = create_access_token(
        subject=admin.id,
        claims={"company_id": str(admin.company_id), "type": "access"},
        expires_delta=timedelta(seconds=-10),  # expired 10 seconds ago
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_disabled_account_with_valid_token_rejected(client: AsyncClient, setup_auth_data):
    """Test that active tokens for disabled users are rejected upon database check."""
    disabled = setup_auth_data["disabled_user"]
    valid_format_token = create_access_token(
        subject=disabled.id,
        claims={"company_id": str(disabled.company_id), "type": "access"},
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {valid_format_token}"},
    )
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower() or "disabled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_insufficient_permission_for_user_creation(client: AsyncClient, setup_auth_data):
    """Test that an Employee cannot create users (requires COMPANY_ADMIN)."""
    # 1. Login as employee
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "employee@coimbatoretextiles.com",
            "password": "EmployeePassword123!",
        },
    )
    token = login_res.json()["access_token"]

    # 2. Attempt to create a user
    create_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "new.tech@coimbatoretextiles.com",
            "password": "NewTechSecurePassword123!",
            "first_name": "Karthik",
            "last_name": "S",
            "role_codes": ["MAINTENANCE_TECHNICIAN"],
        },
    )
    assert create_res.status_code == 403
    assert create_res.json()["title"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_admin_user_registration_and_activation(client: AsyncClient, setup_auth_data):
    """Test authorized admin can register users and update their activation status."""
    # 1. Login as COMPANY_ADMIN
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@coimbatoretextiles.com",
            "password": "AdminSecurePassword123!",
        },
    )
    token = login_res.json()["access_token"]

    # 2. Create new user
    create_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "inventory.lead@coimbatoretextiles.com",
            "password": "InventoryLeadPassword123!",
            "first_name": "Priya",
            "last_name": "M",
            "designation": "Inventory Lead",
            "role_codes": ["INVENTORY_EXECUTIVE"],
        },
    )
    assert create_res.status_code == 201
    new_user = create_res.json()
    assert new_user["email"] == "inventory.lead@coimbatoretextiles.com"
    assert new_user["is_active"] is True
    assert "INVENTORY_EXECUTIVE" in new_user["roles"]

    # 3. Deactivate new user
    deactivate_res = await client.patch(
        f"/api/v1/users/{new_user['id']}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"is_active": False},
    )
    assert deactivate_res.status_code == 200
    assert deactivate_res.json()["is_active"] is False


@pytest.mark.asyncio
async def test_cross_company_access_prevention(client: AsyncClient, setup_auth_data):
    """Test that Admin from Company A cannot view or mutate users belonging to Company B."""
    # 1. Login as Admin of Company A
    login_a = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@coimbatoretextiles.com",
            "password": "AdminSecurePassword123!",
        },
    )
    token_a = login_a.json()["access_token"]
    user_b = setup_auth_data["other_tenant_user"]

    # 2. Try to fetch user from Company B using Company A's token
    res = await client.get(
        f"/api/v1/users/{user_b.id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res.status_code == 404  # Not found within caller's company isolation scope

    # 3. Try to deactivate user from Company B using Company A's token
    patch_res = await client.patch(
        f"/api/v1/users/{user_b.id}/status",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"is_active": False},
    )
    assert patch_res.status_code == 404
