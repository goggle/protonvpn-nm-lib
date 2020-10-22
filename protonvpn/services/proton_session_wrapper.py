from proton.api import ProtonError, Session
from ..logger import logger
from .. import exceptions


class ProtonSessionWrapper():
    """Proton-client wrapper for improved error handling."""
    proton_session = False

    def __init__(
        self, **kwargs
    ):
        self.ERROR_CODE = {
            400: self.handle_400,
            401: self.handle_401,
            403: self.handle_403,
            404: self.handle_404,
            409: self.handle_409,
            422: self.handle_422,
            429: self.handle_429,
            500: self.handle_500,
            501: self.handle_501,
            503: self.handle_503,
        }
        self.user_manager = kwargs.pop("user_manager")
        self.proton_session = Session(**kwargs)

    def api_request(self, *args, **api_kwargs):
        """Wrapper for proton-client api_request.

        Args:
            Takes same arguments as proton-client.
        """
        args = self.flatten_tuple(args)
        logger.info("API Call: {} - {}".format(args, api_kwargs))
        error = False
        try:
            api_response = self.proton_session.api_request(
                *args, **api_kwargs
            )
        except ProtonError as e:
            error = e
        except Exception as e:
            logger.exception("[!] Unknown exception: {}".format(e))
            raise Exception("Unknown error: {}".format(e))

        if not error:
            return api_response

        try:
            result = self.ERROR_CODE[error.code](
                error, args, **api_kwargs
            )
        except KeyError as e:
            raise exceptions.UnhandledAPIError(
                "Unhandled error: {}".format(e)
            )
        else:
            return result

    def authenticate(self, username, password):
        """"Proxymethod for proton-client authenticate.

        Args:
            username (string): protonvpn username
            password (string): protonvpn password
        """
        self.proton_session.authenticate(username, password)

    @staticmethod
    def load(dump, user_manager, TLSPinning=True):
        """Wrapper for proton-client load."""
        api_url = dump['api_url']
        appversion = dump['appversion']
        user_agent = dump['User-Agent']
        proton_session_wrapper = ProtonSessionWrapper(
            api_url=api_url,
            appversion=appversion,
            user_agent=user_agent,
            TLSPinning=TLSPinning,
            user_manager=user_manager
        )

        proton_session_wrapper.proton_session = Session.load(
            dump, TLSPinning=True
        )
        return proton_session_wrapper

    def dump(self):
        """Proxymethod for proton-client dump."""
        return self.proton_session.dump()

    def flatten_tuple(self, _tuple):
        """Recursively flatten tuples."""
        if not isinstance(_tuple, tuple):
            return (_tuple,)
        elif len(_tuple) == 0:
            return ()
        elif isinstance(_tuple[0], dict):
            return self.flatten_tuple(_tuple[1:])
        else:
            return self.flatten_tuple(_tuple[0]) \
                + self.flatten_tuple(_tuple[1:])

    def handle_400(self, error, *args, **kwargs):
        logger.info("Catched 400 error")
        raise exceptions.API400Error(error)

    def handle_401(self, error, *args, **kwargs):
        """Handles access token expiration."""
        logger.info("Catched 401 error")
        logger.info("Refreshing session data")
        self.proton_session.refresh()
        # Store session data
        logger.info("Storing new session data")
        self.user_manager.store_data(
            self.proton_session.dump(),
            self.user_manager.keyring_sessiondata,
            self.user_manager.keyring_service
        )
        logger.info("Calling api_request")
        return self.api_request(*args, **kwargs)

    def handle_403(self, error, *args, **kwargs):
        logger.info("Catched 403 error")
        raise exceptions.API403Error(error)

    def handle_404(self, error, *args, **kwargs):
        logger.info("Catched 404 error")
        raise exceptions.API405Error(error)

    def handle_409(self, error, *args, **kwargs):
        logger.info("Catched 409 error")
        raise exceptions.API409Error(error)

    def handle_422(self, error, *args, **kwargs):
        logger.info("Catched 422 error")
        raise exceptions.API422Error(error)

    def handle_429(self, error, *args, **kwargs):
        logger.info("Catched 429 error")
        raise exceptions.API429Error(error)

    def handle_500(self, error, *args, **kwargs):
        logger.info("Catched 500 error")
        raise exceptions.API500Error(error)

    def handle_501(self, error, *args, **kwargs):
        logger.info("Catched 501 error")
        raise exceptions.API501Error(error)

    def handle_503(self, error, *args, **kwargs):
        logger.info("Catched 504 error")
        raise exceptions.API503Error(error)
