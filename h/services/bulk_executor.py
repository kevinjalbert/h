from h.h_api.bulk_api.executor import AutomaticReportExecutor
from h.h_api.enums import DataType
from h.h_api.exceptions import InvalidDeclarationError


class BulkExecutorService:
    def __init__(self, context, request):
        self.db = request.db

    def get_executor(self):
        return AuthorityCheckingExecutor()


class AuthorityCheckingExecutor(AutomaticReportExecutor):
    """A bulk executor which checks the authority."""

    def __init__(self, authority="lms.hypothes.is"):
        self.effective_user = None
        self.authority = authority

    def configure(self, config):
        self._assert_authority("effective user", config.effective_user)

        self.effective_user = config.effective_user

    def execute_batch(self, command_type, data_type, default_config, batch):
        for command in batch:
            self._check_authority(data_type, command.body)

        return super().execute_batch(command_type, data_type, default_config, batch)

    def _assert_authority(self, field, value, embedded=True):
        if embedded and value.endswith(f"@{self.authority}"):
            return

        if value == self.authority:
            return

        raise InvalidDeclarationError(
            f"The {field} '{value}' does not match the expected authority"
        )

    def _check_authority(self, data_type, body):
        if data_type == DataType.USER:
            self._assert_authority("id", body.id)
            self._assert_authority(
                "authority", body.attributes["authority"], embedded=False
            )

        elif data_type == DataType.GROUP:
            self._assert_authority("groupid", body.attributes["groupid"])
            self._assert_authority("query groupid", body.meta["query"]["groupid"])

        elif data_type == DataType.GROUP_MEMBERSHIP:
            self._assert_authority(
                "member id", body.relationships["member"]["data"]["id"]
            )
