from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.customer import CustomerResponse
from src.db.dependencies import get_db
from src.models.user import User
from src.repositories.customer_repository import CustomerRepository
from src.security.dependencies import get_current_user
from src.services.customer_service import CustomerService


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/me", response_model=CustomerResponse)
def read_my_customer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    """Return the authenticated user's customer profile."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    return customer
