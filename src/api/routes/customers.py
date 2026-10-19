from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.customer import CustomerResponse
from src.api.schemas.order import (
    OrderDetailResponse,
    OrderSummaryResponse,
)
from src.api.schemas.order_status_history import (
    OrderStatusHistoryResponse,
)
from src.api.schemas.refund import RefundResponse
from src.api.schemas.shipment import ShipmentResponse
from src.api.schemas.ticket import TicketCreateRequest, TicketResponse
from src.db.dependencies import get_db
from src.models.user import User
from src.repositories.customer_repository import CustomerRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.refund_repository import RefundRepository
from src.repositories.shipment_repository import ShipmentRepository
from src.repositories.ticket_repository import TicketRepository
from src.security.dependencies import get_current_user
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.refund_service import RefundService
from src.services.shipment_service import ShipmentService
from src.services.ticket_service import TicketService


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


@router.get("/me/orders", response_model=list[OrderSummaryResponse])
def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderSummaryResponse]:
    """Return the authenticated customer's order history."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    order_repository = OrderRepository(db)
    order_service = OrderService(order_repository)

    return order_service.list_orders_for_customer(customer.id)


@router.get(
    "/me/orders/{order_id}",
    response_model=OrderDetailResponse,
)
def read_my_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderDetailResponse:
    """Return an order and its items if it belongs to the current customer."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    order_repository = OrderRepository(db)
    order_service = OrderService(order_repository)

    order = order_service.get_order_for_customer(
        order_id=order_id,
        customer_id=customer.id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


@router.get(
    "/me/orders/{order_id}/history",
    response_model=list[OrderStatusHistoryResponse],
)
def read_my_order_status_history(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderStatusHistoryResponse]:
    """Return status history for an order owned by the current customer."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    order_repository = OrderRepository(db)
    order_service = OrderService(order_repository)

    history = order_service.get_status_history_for_customer(
        order_id=order_id,
        customer_id=customer.id,
    )

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return history


@router.get(
    "/me/orders/{order_id}/shipments",
    response_model=list[ShipmentResponse],
)
def list_my_order_shipments(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ShipmentResponse]:
    """Return shipment tracking information for the customer's order."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    order_repository = OrderRepository(db)
    shipment_repository = ShipmentRepository(db)
    shipment_service = ShipmentService(
        order_repository=order_repository,
        shipment_repository=shipment_repository,
    )

    shipments = shipment_service.list_shipments_for_customer(
        order_id=order_id,
        customer_id=customer.id,
    )

    if shipments is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return shipments


@router.get(
    "/me/orders/{order_id}/refunds",
    response_model=list[RefundResponse],
)
def list_my_order_refunds(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RefundResponse]:
    """Return refund history for an order owned by the current customer."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    order_repository = OrderRepository(db)
    refund_repository = RefundRepository(db)
    refund_service = RefundService(
        order_repository=order_repository,
        refund_repository=refund_repository,
    )

    refunds = refund_service.list_refunds_for_customer(
        order_id=order_id,
        customer_id=customer.id,
    )

    if refunds is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return refunds


@router.get(
    "/me/tickets",
    response_model=list[TicketResponse],
)
def list_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TicketResponse]:
    """Return support tickets belonging to the authenticated customer."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    ticket_repository = TicketRepository(db)
    ticket_service = TicketService(ticket_repository)

    return ticket_service.list_tickets_for_customer(customer.id)


@router.post(
    "/me/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_ticket(
    ticket_data: TicketCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketResponse:
    """Create a support ticket for the authenticated customer."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    ticket_repository = TicketRepository(db)
    ticket_service = TicketService(ticket_repository)

    return ticket_service.create_ticket_for_customer(
        customer_id=customer.id,
        ticket_data=ticket_data,
    )


@router.get(
    "/me/tickets/{ticket_id}",
    response_model=TicketResponse,
)
def read_my_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketResponse:
    """Return a support ticket only if it belongs to the current customer."""
    customer_repository = CustomerRepository(db)
    customer_service = CustomerService(customer_repository)

    customer = customer_service.get_customer_by_user_id(current_user.id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    ticket_repository = TicketRepository(db)
    ticket_service = TicketService(ticket_repository)

    ticket = ticket_service.get_ticket_for_customer(
        ticket_id=ticket_id,
        customer_id=customer.id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket
