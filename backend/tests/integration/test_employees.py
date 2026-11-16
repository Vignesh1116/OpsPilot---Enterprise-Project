import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.auth import Role, User, UserRole
from app.models.organization import Company, CompanyLocation, Department


@pytest.fixture
async def setup_employee_data(db_session: AsyncSession):
    # Roles
    roles = {}
    for code in ["COMPANY_ADMIN", "OPERATIONS_MANAGER", "MAINTENANCE_TECHNICIAN", "EMPLOYEE"]:
        r = Role(id=uuid.uuid4(), code=code, name=code.replace("_", " ").title(), is_system_role=True)
        db_session.add(r)
        roles[code] = r

    # Company A
    comp_a = Company(
        id=uuid.uuid4(),
        name="Coimbatore Textiles Ltd",
        slug="coimbatore-tex",
        code="CBE-TEX",
        address="Avanashi Rd",
        city="Coimbatore",
        state="Tamil Nadu",
        country="India",
        postal_code="641018",
        phone="+91-422-2000000",
        email="hq@coimbatoretextiles.com",
        tax_id="33AAAAA0000A1Z5",
        is_active=True,
    )
    db_session.add(comp_a)

    # Company B
    comp_b = Company(
        id=uuid.uuid4(),
        name="Salem Spares Ltd",
        slug="salem-spares",
        code="SLM-SP",
        address="Junction Main Rd",
        city="Salem",
        state="Tamil Nadu",
        country="India",
        postal_code="636005",
        phone="+91-427-2000000",
        email="hq@salemspares.com",
        tax_id="33CCCCC2222C1Z8",
        is_active=True,
    )
    db_session.add(comp_b)
    await db_session.flush()

    # Location in Company A
    loc_a = CompanyLocation(
        id=uuid.uuid4(),
        company_id=comp_a.id,
        name="Coimbatore - Main Factory",
        code="CBE-MF01",
        type="factory",
        address="Avanashi Rd",
        city="Coimbatore",
        state="Tamil Nadu",
        postal_code="641004",
        is_active=True,
    )
    db_session.add(loc_a)

    # Department in Company A
    dept_a = Department(
        id=uuid.uuid4(),
        company_id=comp_a.id,
        name="Maintenance & Utilities",
        code="MAINT",
        description="Plant maintenance",
        is_active=True,
    )
    db_session.add(dept_a)

    # Location in Company B
    loc_b = CompanyLocation(
        id=uuid.uuid4(),
        company_id=comp_b.id,
        name="Salem - Spare Parts Store",
        code="SLM-SP01",
        type="spare_parts_store",
        address="Junction Rd",
        city="Salem",
        state="Tamil Nadu",
        postal_code="636005",
        is_active=True,
    )
    db_session.add(loc_b)
    await db_session.flush()

    # Admin User A
    admin_a = User(
        id=uuid.uuid4(),
        company_id=comp_a.id,
        location_id=loc_a.id,
        department_id=dept_a.id,
        email="admin@coimbatoretextiles.com",
        password_hash=get_password_hash("Password123!"),
        first_name="Admin",
        last_name="Vignesh",
        designation="Operations Director",
        is_active=True,
        is_verified=True,
    )
    db_session.add(admin_a)
    await db_session.flush()

    db_session.add(UserRole(user_id=admin_a.id, role_id=roles["COMPANY_ADMIN"].id))
    await db_session.commit()

    token_a = create_access_token(admin_a.id, {"company_id": str(comp_a.id), "roles": ["COMPANY_ADMIN"]})

    return {
        "comp_a": comp_a,
        "comp_b": comp_b,
        "loc_a": loc_a,
        "dept_a": dept_a,
        "loc_b": loc_b,
        "admin_a": admin_a,
        "token_a": token_a,
    }


@pytest.mark.asyncio
async def test_employee_crud_and_validation(client: AsyncClient, setup_employee_data):
    token_a = setup_employee_data["token_a"]
    loc_a = setup_employee_data["loc_a"]
    dept_a = setup_employee_data["dept_a"]
    loc_b = setup_employee_data["loc_b"]

    # 1. Attempt to create employee with location from another company (Should Fail)
    invalid_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "email": "alien.tech@coimbatoretextiles.com",
            "password": "SecurePassword123!",
            "first_name": "Alien",
            "last_name": "Tech",
            "location_id": str(loc_b.id),  # Belongs to Company B!
            "role_codes": ["MAINTENANCE_TECHNICIAN"],
        },
    )
    assert invalid_res.status_code == 422
    assert "location" in invalid_res.json()["detail"].lower()

    # 2. Valid Employee Creation with Location and Department
    create_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "email": "murugan.tech@coimbatoretextiles.com",
            "password": "SecurePassword123!",
            "first_name": "Murugan",
            "last_name": "Subramanian",
            "phone": "+91-9876543210",
            "designation": "Senior Maintenance Technician",
            "location_id": str(loc_a.id),
            "department_id": str(dept_a.id),
            "role_codes": ["MAINTENANCE_TECHNICIAN"],
        },
    )
    assert create_res.status_code == 201
    emp = create_res.json()
    assert emp["email"] == "murugan.tech@coimbatoretextiles.com"
    assert emp["location_name"] == "Coimbatore - Main Factory"
    assert emp["department_name"] == "Maintenance & Utilities"
    assert "MAINTENANCE_TECHNICIAN" in emp["roles"]

    # 3. View Employee Details
    get_res = await client.get(
        f"/api/v1/users/{emp['id']}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["full_name"] == "Murugan Subramanian"

    # 4. Update Employee
    update_res = await client.put(
        f"/api/v1/users/{emp['id']}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "designation": "Lead Maintenance Specialist",
            "phone": "+91-9999988888",
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["designation"] == "Lead Maintenance Specialist"

    # 5. Search and Filter Employees
    search_res = await client.get(
        "/api/v1/users?search=Murugan",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert search_res.status_code == 200
    items = search_res.json()
    assert len(items) == 1
    assert items[0]["email"] == "murugan.tech@coimbatoretextiles.com"

    # 6. Deactivate Employee
    status_res = await client.patch(
        f"/api/v1/users/{emp['id']}/status",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"is_active": False},
    )
    assert status_res.status_code == 200
    assert status_res.json()["is_active"] is False
