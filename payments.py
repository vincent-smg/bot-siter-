"""
Payment provider abstraction.

Right now only MockPaymentProvider exists, which fakes a checkout so the
whole premium flow (buy -> save to DB -> bot picks it up) can be built and
tested before merchant access with TBC/BOG is ready.

When TBC (or BOG) merchant access comes through, add a TBCPaymentProvider
here that implements the same two methods - create_payment() and the
webhook handling - by calling TBC's real /tpay/payments API instead of
faking it. Nothing in app.py needs to change except which provider gets
instantiated, because both providers expose the same interface.
"""

from abc import ABC, abstractmethod


class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, subscription_id: int, amount: float, currency: str, description: str) -> dict:
        """
        Start a payment for the given subscription.
        Must return {"redirect_url": "<where to send the user to pay>"}.
        """
        raise NotImplementedError


class MockPaymentProvider(PaymentProvider):
    """
    Fakes a bank checkout page. Instead of redirecting to TBC/BOG, it
    redirects to our own /premium/mock-pay/<subscription_id> page, which
    shows a fake 'Confirm Payment' button. Clicking it calls the exact
    same internal 'mark this subscription active' logic a real webhook
    would call - so swapping in TBC later only changes how that logic
    gets triggered, not what it does.
    """

    def create_payment(self, subscription_id: int, amount: float, currency: str, description: str) -> dict:
        from flask import url_for
        return {
            "redirect_url": url_for("premium_mock_pay", subscription_id=subscription_id),
        }


# ----------------------------------------------------------------------------
# Example of what the real TBC provider will look like once merchant access
# is approved (left commented out as a reference, not wired up yet):
#
# class TBCPaymentProvider(PaymentProvider):
#     def __init__(self, client_id, client_secret, api_key):
#         self.client_id = client_id
#         self.client_secret = client_secret
#         self.api_key = api_key
#
#     def _get_access_token(self):
#         # POST to https://api.tbcbank.ge/v1/tpay/access-token
#         # with client_id/client_secret, cache the token for ~1 day.
#         ...
#
#     def create_payment(self, subscription_id, amount, currency, description):
#         # POST to https://api.tbcbank.ge/v1/tpay/payments with amount,
#         # currency, and a callback URL that includes subscription_id.
#         # Returns the "approval_url" TBC gives back as redirect_url.
#         ...
# ----------------------------------------------------------------------------


def get_payment_provider():
    """Returns the active payment provider. Swap this when TBC is ready."""
    return MockPaymentProvider()