from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from src.api.schemas.customer import CustomerResponse


def test_customer_response_from_attributes():
    customer_id = uuid4()
    created_at = datetime.now(timezone.utc)

    customer = SimpleNamespace(
        id=customer_id,
        user_id=uuid4(),
        first_name="Ahmed",
        last_name="Ali",
        phone=None,
        created_at=created_at,
    )

    response = CustomerResponse.model_validate(customer)

    assert response.id == customer_id
    assert response.first_name == "Ahmed"
    assert response.last_name == "Ali"
    assert response.phone is None
    assert response.created_at == created_at
    assert not hasattr(response, "user_id")
