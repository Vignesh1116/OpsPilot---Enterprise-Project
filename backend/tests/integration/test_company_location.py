import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.auth import Role, User, UserRole
from app.models.organization import Company


@pytest.fixture
async def setup_org_data(db_session: AsyncSession):
    # Create Role
    admin_role = Role(id=uuid.uuid4(), code="COMPANY_ADMIN", name="Company Admin", is_system_role=True)
    db_session.add(admin_role)

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
        name="Madurai Spinning Mills",
        slug="madurai-spin",
        code="MDU-SPIN",
        address="Alagar Rd",
        city="Madurai",
        state="Tamil Nadu",
        country="India",
        postal_code="625002",
        phone="+91-452-2000000",
        email="hq@maduraispinning.com",
        tax_id="33BBBBB1111B1Z9",
        is_active=True,
    )
    db_session.add(comp_b)
    await db_session.flush()

    # Admin User A
    user_a = User(
        id=uuid.uuid4(),
        company_id=comp_a.id,
        email="admin@coimbatoretextiles.com",
        password_hash=get_password_hash("Password123!"),
        first_name="Admin",
        last_name="A",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user_a)

    # Admin User B
    user_b = User(
        id=uuid.uuid4(),
        company_id=comp_b.id,
        email="admin@maduraispinning.com",
        password_hash=get_password_hash("Password123!"),
        first_name="Admin",
        last_name="B",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user_b)
    await db_session.flush()

    db_session.add(UserRole(user_id=user_a.id, role_id=admin_role.id))
    db_session.add(UserRole(user_id=user_b.id, role_id=admin_role.id))
    await db_session.commit()

    token_a = create_access_token(user_a.id, {"company_id": str(comp_a.id), "roles": ["COMPANY_ADMIN"]})
    token_b = create_access_token(user_b.id, {"company_id": str(comp_b.id), "roles": ["COMPANY_ADMIN"]})

    return {
        "company_a": comp_a,
        "company_b": comp_b,
        "token_a": token_a,
        "token_b": token_b,
    }


@pytest.mark.asyncio
async def test_company_and_location_lifecycle(client: AsyncClient, setup_org_data):
    token_a = setup_org_data["token_a"]

    # 1. Fetch Company Profile
    comp_res = await client.get(
        "/api/v1/organizations/company",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["name"] == "Coimbatore Textiles Ltd"

    # 2. Create Location (Coimbatore - Main Factory)
    loc_res = await client.post(
        "/api/v1/organizations/locations",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Coimbatore - Main Factory",
            "code": "CBE-MF01",
            "type": "factory",
            "address": "124 Avanashi Road, Peelamedu",
            "city": "Coimbatore",
            "state": "Tamil Nadu",
            "postal_code": "641004",
        },
    )
    assert loc_res.status_code == 201
    loc_data = loc_res.json()
    assert loc_data["code"] == "CBE-MF01"

    # 3. Create Department
    dept_res = await client.post(
        "/api/v1/organizations/departments",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Spinning & Weaving Operations",
            "code": "SPIN-OPS",
            "description": "Primary textile production line",
        },
    )
    assert dept_res.status_code == 201
    assert dept_res.json()["code"] == "SPIN-OPS"

    # 4. List Locations
    list_res = await client.get(
        "/api/v1/organizations/locations",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Cross-company isolation: Company B cannot see Company A's location
    token_b = setup_org_data["token_b"]
    isolated_get = await client.get(
        f"/api/v1/organizations/locations/{loc_data['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert isolated_get.status_code == 404
