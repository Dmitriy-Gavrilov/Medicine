from app.exceptions.auth import AdminRoleRequired, DispatcherRoleRequired, WorkerRoleRequired
from app.db.models.user import User, UserRole


class RoleVerifier:
    def __init__(self, user: User):
        self.user = user

    async def verify(self, required_role: UserRole) -> None:
        if required_role == UserRole.ADMIN and self.user.role != UserRole.ADMIN:
            raise AdminRoleRequired()
        elif required_role == UserRole.DISPATCHER and self.user.role not in (UserRole.DISPATCHER, UserRole.ADMIN):
            raise DispatcherRoleRequired()
        elif required_role == UserRole.WORKER and self.user.role not in (UserRole.WORKER, UserRole.ADMIN):
            raise WorkerRoleRequired()
