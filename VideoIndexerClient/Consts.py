import os
from dataclasses import dataclass

@dataclass
class Consts:
    ApiVersion: str
    ApiEndpoint: str
    AzureResourceManager: str
    AccountName: str
    ResourceGroup: str
    SubscriptionId: str
    Location: str

    def __post_init__(self):
        self.AccountName = os.getenv('AccountName', self.AccountName)
        self.ResourceGroup = os.getenv('ResourceGroup', self.ResourceGroup)
        self.SubscriptionId = os.getenv('SubscriptionId', self.SubscriptionId)

        if self.AccountName is None or self.AccountName == '' \
            or self.ResourceGroup is None or self.ResourceGroup == '' \
            or self.SubscriptionId is None or self.SubscriptionId == '':
            raise ValueError('Please Fill In SubscriptionId, Account Name and Resource Group on the Constant Class!')