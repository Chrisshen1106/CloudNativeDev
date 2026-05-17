import pytest
from app import create_app
from models import db, Equipment, User
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        user = User.query.first()
        assert user is not None, "DB 裡沒有任何 User，無法建立測試資料"

        equipment = Equipment(
            idUser=user.idUser,
            name='__TEST_OPTIMISTIC_LOCK__',
            status='in_use',
            version=0,
        )
        db.session.add(equipment)
        db.session.commit()
        asset_id = equipment.idEquipment

        token = create_access_token(identity=str(user.idUser),
                                    additional_claims={'role': 'admin'})
        yield app.test_client(), token, asset_id

        # 測試結束後清掉，不污染真實資料
        Equipment.query.filter_by(idEquipment=asset_id).delete()
        db.session.commit()


def put(client, token, asset_id, payload):
    return client.put(
        f'/api/assets/{asset_id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )


def test_update_success(client):
    c, token, asset_id = client
    res = put(c, token, asset_id, {'name': 'Updated Laptop', 'version': 0})
    assert res.status_code == 200
    assert res.get_json() == {'success': True}


def test_version_increments_after_update(client):
    c, token, asset_id = client
    put(c, token, asset_id, {'name': 'v1', 'version': 0})

    res = put(c, token, asset_id, {'name': 'v2', 'version': 1})
    assert res.status_code == 200


def test_conflict_returns_409_with_asset(client):
    c, token, asset_id = client
    res = put(c, token, asset_id, {'name': 'Stale Update', 'version': 99})
    assert res.status_code == 409

    body = res.get_json()
    assert body['success'] is False
    assert 'content' in body
    assert body['content']['version'] == 0


def test_conflict_asset_contains_latest_data(client):
    c, token, asset_id = client
    put(c, token, asset_id, {'name': 'Someone Else', 'version': 0})

    res = put(c, token, asset_id, {'name': 'My Change', 'version': 0})
    assert res.status_code == 409

    asset = res.get_json()['content']
    assert asset['name'] == 'Someone Else'
    assert asset['version'] == 1


def test_missing_version_returns_400(client):
    c, token, asset_id = client
    res = put(c, token, asset_id, {'name': 'No Version'})
    assert res.status_code == 400


def test_stale_update_does_not_overwrite(client):
    c, token, asset_id = client
    put(c, token, asset_id, {'name': 'Correct Update', 'version': 0})

    put(c, token, asset_id, {'name': 'Overwrite Attempt', 'version': 0})

    # 直接查 DB，避免 GET endpoint 去 join 尚未建立的 Form 表
    eq = Equipment.query.get(asset_id)
    assert eq.name == 'Correct Update'
