import pytest

class InitApiClient:

    @pytest.fixture(autouse=True)
    def init_apiclient(self,api_client):
            self.api_client=api_client