from services.v1.auth_services import AuthServices


class AuthController:
    @staticmethod
    async def register_controller(data, db):
        return await AuthServices.register_serv(data, db)

    @staticmethod
    async def login_controller(data, db):
        return await AuthServices.login_serv(data, db)
