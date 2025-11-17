# from model.v1.user_model import Role  # Adjust model if you're testing with Role
# from helpers.v1.helpers import fetchRecord, deleteRole, deletePermission
from model.v1.user_model import User  # Adjust import to your model
from helpers.v1.helpers import IDGeneration

from model.v1.permission_model import Permission


def test_user_id_generation_high_ids(db_session):
    # Add a dummy user with a very high ID
    test_user = User(id=99999, email="dummyuser@123.com", username="DummyUser")
    db_session.add(test_user)
    db_session.commit()

    # Now userID() should return 100000
    new_id = IDGeneration.userID(db_session)
    assert new_id == 100000
    db_session.query(User).filter_by(id=99999).delete()
    db_session.commit()
