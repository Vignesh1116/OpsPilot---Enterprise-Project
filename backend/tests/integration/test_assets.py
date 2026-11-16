import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.auth import Role, User, UserRole
from app.models.organization import Company, CompanyLocation, Department


@pytest.fixture
async def setup_asset_env(db_session: AsyncSession):
    # System Role
    admin_role = Role(id=uuid.uuid4(), code="COMPANY_ADMIN", name="Company Admin", is_system_role=True)
    db_session.add(admin_role)

    # Company A (Coimbatore)
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

    # Company B (Tiruppur Apparel - Isolated Tenant)
    comp_b = Company(
        id=uuid.uuid4(),
        name="Tiruppur Apparels Ltd",
        slug="tiruppur-apparel",
        code="TPR-APP",
        address="Kumaran Rd",
        city="Tiruppur",
        state="Tamil Nadu",
        country="India",
        postal_code="641601",
        phone="+91-421-2000000",
        email="hq@tiruppurapparel.com",
        tax_id="33DDDDD3333D1Z2",
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
        name="Spinning Operations",
        code="SPIN",
        is_active=True,
    )
    db_session.add(dept_a)
    await db_session.flush()

    # User in Company A
    user_a = User(
        id=uuid.uuid4(),
        company_id=comp_a.id,
        location_id=loc_a.id,
        email="admin@coimbatoretextiles.com",
        password_hash=get_password_hash("Password123!"),
        first_name="Admin",
        last_name="Coimbatore",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user_a)

    # User in Company B
    user_b = User(
        id=uuid.uuid4(),
        company_id=comp_b.id,
        email="admin@tiruppurapparel.com",
        password_hash=get_password_hash("Password123!"),
        first_name="Admin",
        last_name="Tiruppur",
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
        "comp_a": comp_a,
        "comp_b": comp_b,
        "loc_a": loc_a,
        "dept_a": dept_a,
        "token_a": token_a,
        "token_b": token_b,
    }


@pytest.mark.asyncio
async def test_asset_lifecycle_qr_and_audit(client: AsyncClient, setup_asset_env):
    token_a = setup_asset_env["token_a"]
    loc_a = setup_asset_env["loc_a"]
    dept_a = setup_asset_env["dept_a"]

    # 1. Create Asset Category
    cat_res = await client.post(
        "/api/v1/assets/categories",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Spinning Machinery",
            "code": "SPIN-MACH",
            "description": "High-speed ring spinning frames and blowroom lines",
            "depreciation_method": "straight_line",
            "expected_lifetime_months": 180,
        },
    )
    assert cat_res.status_code == 201
    category = cat_res.json()
    assert category["code"] == "SPIN-MACH"

    # 2. Register Industrial Asset (LMW Ring Frame LR9/AX)
    today = date.today()
    asset_res = await client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "asset_tag": "AST-CBE-LR9-001",
            "name": "LMW Ring Spinning Frame LR9/AX",
            "model_number": "LR9-AX-1200",
            "serial_number": "LMW-2024-SP-8941",
            "category_id": category["id"],
            "location_id": str(loc_a.id),
            "department_id": str(dept_a.id),
            "status": "operational",
            "critical_level": "critical",
            "purchase_date": today.isoformat(),
            "purchase_cost": 4500000.00,
            "warranty_expiry_date": (today + timedelta(days=730)).isoformat(),
            "expected_lifetime_months": 180,
        },
    )
    assert asset_res.status_code == 201
    asset = asset_res.json()
    assert asset["asset_tag"] == "AST-CBE-LR9-001"
    assert asset["status"] == "operational"
    assert asset["location_name"] == "Coimbatore - Main Factory"
    assert asset["category_name"] == "Spinning Machinery"
    # Verify QR code data URI generated
    assert asset["qr_code_data_uri"] is not None
    assert asset["qr_code_data_uri"].startswith("data:image/png;base64,")

    # 3. Prevent Duplicate Asset Tag within Same Company
    dup_res = await client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "asset_tag": "AST-CBE-LR9-001",
            "name": "Duplicate Ring Frame",
            "category_id": category["id"],
            "location_id": str(loc_a.id),
            "purchase_date": today.isoformat(),
            "purchase_cost": 1000000.00,
        },
    )
    assert dup_res.status_code == 409

    # 4. Update Asset Status to in_maintenance
    update_res = await client.put(
        f"/api/v1/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "status": "in_maintenance",
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "in_maintenance"

    # 5. Verify Asset Audit History Records Status Transition
    history_res = await client.get(
        f"/api/v1/assets/{asset['id']}/history",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert history_res.status_code == 200
    history_logs = history_res.json()
    assert len(history_logs) >= 2  # CREATE and STATUS_CHANGE
    actions = [log["action"] for log in history_logs]
    assert "CREATE" in actions
    assert "STATUS_CHANGE" in actions

    # Verify latest audit log captured transition
    latest_log = history_logs[0]
    assert latest_log["action"] == "STATUS_CHANGE"
    assert latest_log["old_values"]["status"] == "operational"
    assert latest_log["new_values"]["status"] == "in_maintenance"

    # 6. Search and Filter Assets
    search_res = await client.get(
        "/api/v1/assets?search=LR9&status=in_maintenance",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert search_res.status_code == 200
    assert len(search_res.json()) == 1

    # 7. Cross-company Isolation: Company B cannot access Company A's asset
    token_b = setup_asset_env["token_b"]
    isolated_res = await client.get(
        f"/api/v1/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert isolated_res.status_code == 404
