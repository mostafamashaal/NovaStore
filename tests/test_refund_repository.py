from unittest.mock import MagicMock
from uuid import uuid4

from src.models.refund import Refund
from src.repositories.refund_repository import RefundRepository


def test_refund_repository_list_by_order():
    session = MagicMock()
    order_id = uuid4()
    refunds = [
        MagicMock(spec=Refund),
        MagicMock(spec=Refund),
    ]
    session.scalars.return_value.all.return_value = refunds

    repository = RefundRepository(session)

    result = repository.list_by_order(order_id)

    assert result == refunds
    session.scalars.assert_called_once()

    statement = session.scalars.call_args.args[0]
    assert order_id in statement.compile().params.values()
