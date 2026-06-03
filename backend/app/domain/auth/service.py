"""
Auth domain — Service (business logic).
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.auth.models import User, UserRole
from app.domain.auth.repository import UserRepository
from app.domain.auth.schemas import (
    LoginRequest, RegisterRequest, AdminCreateUserRequest, UserUpdateRequest, ChangePasswordRequest,
    UserResponse, UserAssignableResponse, TokenResponse,
)
from app.shared.security import hash_password, verify_password, create_access_token
from app.shared.exceptions import (
    NotFoundException, AlreadyExistsException, UnauthorizedException, BadRequestException,
)


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.db = db

    # ── Auth ──────────────────────────────────────────────
    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    def register(self, payload: RegisterRequest) -> UserResponse:
        if self.repo.email_exists(payload.email):
            raise AlreadyExistsException("User", "email", payload.email)

        user = self.repo.create({
            "name": payload.name,
            "email": payload.email,
            "hashed_password": hash_password(payload.password),
            # Public self-registration is always commercial to avoid privilege escalation.
            "role": UserRole.COMMERCIAL,
            "phone": payload.phone,
        })
        return UserResponse.model_validate(user)

    def admin_create_user(self, payload: AdminCreateUserRequest) -> UserResponse:
        """Admin creates a user with any role and optional account_id."""
        if self.repo.email_exists(payload.email):
            raise AlreadyExistsException("User", "email", payload.email)

        user = self.repo.create({
            "name": payload.name,
            "email": payload.email,
            "hashed_password": hash_password(payload.password),
            "role": payload.role,
            "phone": payload.phone,
            "account_id": payload.account_id,
        })
        return UserResponse.model_validate(user)

    # ── Users CRUD ────────────────────────────────────────
    def get_user(self, user_id: int) -> UserResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return UserResponse.model_validate(user)

    def list_users(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[UserResponse], int]:
        users = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [UserResponse.model_validate(u) for u in users], total

    def list_assignable_users(self) -> List[UserAssignableResponse]:
        users = self.repo.get_assignable_users()
        return [UserAssignableResponse.model_validate(user) for user in users]

    def update_user(self, user_id: int, payload: UserUpdateRequest) -> UserResponse:
        if payload.email and self.repo.email_exists(payload.email, exclude_id=user_id):
            raise AlreadyExistsException("User", "email", payload.email)

        data = payload.model_dump(exclude_unset=True)
        user = self.repo.update(user_id, data)
        if not user:
            raise NotFoundException("User", user_id)
        return UserResponse.model_validate(user)

    def change_password(self, user_id: int, payload: ChangePasswordRequest) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        if not verify_password(payload.old_password, user.hashed_password):
            raise BadRequestException("Current password is incorrect")
        self.repo.update(user_id, {"hashed_password": hash_password(payload.new_password)})

    def delete_user(self, user_id: int) -> None:
        from app.domain.leads.models import Lead
        from app.domain.deals.models import Deal
        from app.domain.tickets.models import Ticket, TicketMessage
        from app.domain.activities.models import Activity
        from app.domain.audit.models import AuditLog
        from app.domain.accounts.models import Account

        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        # Block deletion if user created tickets (FK ON DELETE RESTRICT)
        ticket_count = self.db.query(Ticket).filter(Ticket.created_by == user_id).count()
        if ticket_count > 0:
            raise BadRequestException(
                f"Cannot delete user #{user_id}: {ticket_count} ticket(s) reference this user as creator. "
                "Reassign or delete those tickets first."
            )

        # SET NULL on all nullable FK references (matching ON DELETE SET NULL)
        self.db.query(Account).filter(Account.owner_user_id == user_id).update(
            {"owner_user_id": None}, synchronize_session=False
        )
        self.db.query(Lead).filter(Lead.owner_user_id == user_id).update(
            {"owner_user_id": None}, synchronize_session=False
        )
        self.db.query(Deal).filter(Deal.owner_user_id == user_id).update(
            {"owner_user_id": None}, synchronize_session=False
        )
        self.db.query(Ticket).filter(Ticket.assigned_to == user_id).update(
            {"assigned_to": None}, synchronize_session=False
        )
        self.db.query(Activity).filter(Activity.created_by == user_id).update(
            {"created_by": None}, synchronize_session=False
        )
        self.db.query(AuditLog).filter(AuditLog.actor_user_id == user_id).update(
            {"actor_user_id": None}, synchronize_session=False
        )
        self.db.query(TicketMessage).filter(TicketMessage.author_user_id == user_id).update(
            {"author_user_id": None}, synchronize_session=False
        )
        self.db.flush()

        if not self.repo.delete(user_id):
            raise NotFoundException("User", user_id)
