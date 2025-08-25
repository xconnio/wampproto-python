import json
import subprocess

from wampproto.types import SessionDetails


class JoinerWampprotoCli:
    def __init__(self, realm: str):
        self._realm = realm
        self._session_details: SessionDetails | None = None

    def run_command(self, command: str) -> str:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 0, result.stderr.decode()
        return result.stdout.decode().strip()

    def send_hello(self) -> str:
        hello = f"wampproto message hello {self._realm} anonymous -e foo=bar -r callee=true --serializer json"

        return self.run_command(hello)

    def receive(self, data: str):
        return self.process_data(data)

    def process_data(self, data: str):
        msg = json.loads(data)
        if msg[0] == 2:
            self._session_details = SessionDetails(
                msg[1], self._realm, msg[2].get("authid", ""), msg[2].get("authrole", "")
            )
            return None
        else:
            raise ValueError("received unknown message")

    def get_session_details(self) -> SessionDetails:
        if self._session_details is None:
            raise ValueError("session is not setup yet")

        return self._session_details
