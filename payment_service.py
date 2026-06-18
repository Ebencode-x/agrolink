"""
payment_service.py — AgroLink Tanzania
=======================================
Provider-agnostic payment layer.

PROVIDER sasa hivi: AzamPay (sandbox — inapatikana bila application)
PROVIDER baadaye:   Selcom  (ukipata credentials, badilisha .env tu)

.env variables zinazohitajika:
    PAYMENT_PROVIDER=azampay          # au "selcom" baadaye
    AZAMPAY_APP_NAME=AgroLink
    AZAMPAY_CLIENT_ID=...             # kutoka AzamPay sandbox dashboard
    AZAMPAY_CLIENT_SECRET=...
    AZAMPAY_BASE_URL=https://sandbox.azampay.co.tz

    # Selcom (unazijaza ukipata response kutoka info@selcom.net)
    # PAYMENT_PROVIDER=selcom
    # SELCOM_API_KEY=...
    # SELCOM_API_SECRET=...
    # SELCOM_BASE_URL=https://apigw.selcom.net

Workflow ya malipo:
    1. initiate_payment()  → mnunuzi analipa (MNO push)
    2. [callback kutoka provider] → verify_payment()
    3. release_escrow()    → mkulima anapewa pesa
"""

import os
import hmac
import hashlib
import base64
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
import requests

logger = logging.getLogger(__name__)


# ── Exceptions ────────────────────────────────────────────────────────────────

class PaymentError(Exception):
    """Raised wakati payment initiation inashindwa."""
    pass

class PaymentVerificationError(Exception):
    """Raised wakati callback verification inashindwa."""
    pass


# ══════════════════════════════════════════════════════════════════════════════
# BASE PROVIDER
# ══════════════════════════════════════════════════════════════════════════════

class BasePaymentProvider:
    """
    Interface ambayo kila provider lazima ifuate.
    Ukiongeza provider mpya (e.g. M-Pesa, Tigo Pesa moja kwa moja),
    inherit class hii na implement methods zote tatu.
    """

    def initiate(self, amount_tzs: int, msisdn: str, reference: str,
                 description: str) -> dict:
        """
        Anzisha malipo — tuma push request kwa simu ya mnunuzi.
        Returns: {"success": bool, "provider_ref": str, "message": str}
        """
        raise NotImplementedError

    def verify(self, payload: dict, headers: dict) -> dict:
        """
        Thibitisha callback kutoka provider (signature check).
        Returns: {"success": bool, "reference": str, "status": str}
        """
        raise NotImplementedError

    def disburse(self, amount_tzs: int, msisdn: str, reference: str,
                 description: str) -> dict:
        """
        Tuma pesa kwa mkulima baada ya order kukamilika.
        Returns: {"success": bool, "provider_ref": str, "message": str}
        """
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════════════
# AZAMPAY PROVIDER (sandbox inapatikana sasa hivi)
# ══════════════════════════════════════════════════════════════════════════════

class AzamPayProvider(BasePaymentProvider):
    """
    AzamPay Tanzania — sandbox inafanya kazi bila application.
    Docs: https://developerdocs.azampay.co.tz
    """

    def __init__(self):
        self.app_name     = os.getenv("AZAMPAY_APP_NAME", "AgroLink")
        self.client_id    = os.getenv("AZAMPAY_CLIENT_ID", "")
        self.client_secret= os.getenv("AZAMPAY_CLIENT_SECRET", "")
        self.base_url     = os.getenv(
            "AZAMPAY_BASE_URL", "https://sandbox.azampay.co.tz"
        )
        self._token: Optional[str] = None

    def _get_token(self) -> str:
        """
        Rudisha bearer token.
        Sandbox: tumia AZAMPAY_TOKEN moja kwa moja (portal inakupa tayari).
        Production: itabadilishwa kuomba token kwa Client ID/Secret.
        """
        if self._token:
            return self._token

        # Sandbox token kutoka .env (AZAMPAY_TOKEN)
        env_token = os.getenv("AZAMPAY_TOKEN", "")
        if env_token:
            self._token = env_token
            logger.info("AzamPay: kutumia token kutoka .env")
            return self._token

        # Production fallback — OAuth2 flow
        url = "https://authenticator.azampay.co.tz/AppRegistration/GenerateToken"
        payload = {
            "appName":      self.app_name,
            "clientId":     self.client_id,
            "clientSecret": self.client_secret,
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self._token = data["data"]["accessToken"]
            return self._token
        except Exception as e:
            logger.error(f"AzamPay token error: {e}")
            raise PaymentError("Imeshindwa kupata token ya malipo. Jaribu tena.")

    def initiate(self, amount_tzs: int, msisdn: str, reference: str,
                 description: str) -> dict:
        """
        MNO checkout — inatuma USSD push kwa simu ya mnunuzi.
        msisdn format: "255712345678" (bila +, bila 0 mwanzoni)
        """
        token = self._get_token()
        url   = f"{self.base_url}/azampay/mno/checkout"

        # Gundua MNO kutoka namba
        mno = self._detect_mno(msisdn)

        payload = {
            "accountNumber": msisdn,
            "amount":        str(amount_tzs),
            "currency":      "TZS",
            "externalId":    reference,
            "provider":      mno,
            "additionalProperties": {
                "description": description
            }
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        }

        # ── Mock mode kwa sandbox (PAYMENT_MOCK=true) ──────────────────────
        if os.getenv("PAYMENT_MOCK", "true").lower() == "true":
            logger.info(f"[MOCK] Payment simulated: {amount_tzs} TZS → {msisdn}")
            return {
                "success":      True,
                "provider_ref": f"MOCK-{reference}",
                "message":      "Ombi la malipo limetumwa. Angalia simu yako na uthibitishe.",
            }
        # ── Production flow ──────────────────────────────────────────────────
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            data = resp.json()

            if resp.status_code == 200 and data.get("success"):
                return {
                    "success":      True,
                    "provider_ref": data.get("transactionId", reference),
                    "message":      "Ombi la malipo limetumwa. Angalia simu yako.",
                }
            else:
                msg = data.get("message", "Imeshindwa. Jaribu tena.")
                logger.warning(f"AzamPay initiate failed: {data}")
                return {"success": False, "provider_ref": None, "message": msg}

        except requests.Timeout:
            return {
                "success": False,
                "provider_ref": None,
                "message": "Mtandao umechelewa. Jaribu tena baada ya dakika moja."
            }
        except Exception as e:
            logger.error(f"AzamPay initiate exception: {e}")
            raise PaymentError("Hitilafu ya mfumo wa malipo.")

    def verify(self, payload: dict, headers: dict) -> dict:
        """
        Thibitisha callback ya AzamPay.
        AzamPay hutuma POST kwa /payments/callback na JSON body.
        """
        # AzamPay sandbox haitumi signature — production itatumia HMAC
        # Hapa tunakagua fields muhimu tu
        required = {"transactionId", "utilityref", "amount", "paymentStatus"}
        if not required.issubset(payload.keys()):
            raise PaymentVerificationError("Callback payload haina fields zote.")

        status = payload.get("paymentStatus", "").upper()
        return {
            "success":   status == "SUCCESS",
            "reference": payload.get("utilityref", ""),
            "status":    status,
            "provider_ref": payload.get("transactionId", ""),
        }

    def disburse(self, amount_tzs: int, msisdn: str, reference: str,
                 description: str) -> dict:
        """
        Tuma pesa kwa mkulima (disbursement).
        Sandbox: inasimulate tu — production itahitaji B2B endpoint.
        """
        # TODO: Implement AzamPay B2B disbursement ukipata production access
        # Kwa sasa sandbox haisupport disbursement — tunasimulate success
        logger.info(f"[SANDBOX] Disbursement simulated: {amount_tzs} TZS → {msisdn}")
        return {
            "success":      True,
            "provider_ref": f"SIM-{reference}",
            "message":      f"[Sandbox] Malipo ya {amount_tzs:,} TZS yamesimulishwa.",
        }

    @staticmethod
    def _detect_mno(msisdn: str) -> str:
        """
        Gundua mtoa huduma (MNO) kutoka namba ya simu.
        Inatumika kwa AzamPay provider field.
        """
        prefix_map = {
            # Vodacom M-Pesa
            ("255744", "255745", "255746", "255747",
             "255748", "255749", "255765", "255766",
             "255767", "255768", "255769"): "Mpesa",
            # Tigo Pesa
            ("255711", "255712", "255713", "255714",
             "255715", "255716", "255717", "255718",
             "255719", "255671", "255672", "255673"): "TigoPesa",
            # Airtel Money
            ("255780", "255781", "255782", "255783",
             "255784", "255785", "255786", "255787",
             "255788", "255789"): "Airtel",
            # Halotel
            ("255621", "255622", "255623", "255624",
             "255625", "255626", "255627", "255628",
             "255629"): "Halopesa",
        }
        for prefixes, mno in prefix_map.items():
            if any(msisdn.startswith(p) for p in prefixes):
                return mno
        return "Mpesa"  # default


# ══════════════════════════════════════════════════════════════════════════════
# SELCOM PROVIDER (placeholder — unajaza ukipata credentials)
# ══════════════════════════════════════════════════════════════════════════════

class SelcomProvider(BasePaymentProvider):
    """
    Selcom Tanzania — unajaza implementation hii ukipata response
    kutoka info@selcom.net

    Selcom inatumia HMAC-SHA256 signature kwa kila request:
    Authorization: SELCOM {api_key}
    Digest-Method: HS256
    Digest: base64(hmac_sha256(signed_fields, api_secret))
    Timestamp: ISO8601
    Signed-Fields: field1,field2,...
    """

    def __init__(self):
        self.api_key    = os.getenv("SELCOM_API_KEY", "")
        self.api_secret = os.getenv("SELCOM_API_SECRET", "")
        self.base_url   = os.getenv(
            "SELCOM_BASE_URL", "https://apigw.selcom.net"
        )
        self.vendor     = os.getenv("SELCOM_VENDOR", "")

    def _build_headers(self, signed_fields: dict) -> dict:
        """
        Jenga Selcom authentication headers.
        signed_fields: dict ya fields zinazotakiwa kusainiwa (order inaweza kuathiri digest)
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
        fields_str = ",".join(signed_fields.keys())
        values_str = "&".join(
            f"{k}={v}" for k, v in signed_fields.items()
        )
        digest = base64.b64encode(
            hmac.new(
                self.api_secret.encode(),
                values_str.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        return {
            "Content-Type":   "application/json",
            "Authorization":  f"SELCOM {self.api_key}",
            "Digest-Method":  "HS256",
            "Digest":         digest,
            "Timestamp":      timestamp,
            "Signed-Fields":  fields_str,
        }

    def initiate(self, amount_tzs: int, msisdn: str, reference: str,
                 description: str) -> dict:
        """
        Selcom Pesalink checkout.
        TODO: Implement ukipata Selcom credentials na endpoint docs.
        """
        # Placeholder — itafanywa kazi ukipata credentials
        logger.warning("Selcom provider: credentials hazijawekwa bado.")
        raise PaymentError(
            "Selcom integration bado haijawezeshwa. "
            "Tafadhali wasiliana na msimamizi."
        )

    def verify(self, payload: dict, headers: dict) -> dict:
        raise PaymentError("Selcom verify: bado haijawezeshwa.")

    def disburse(self, amount_tzs: int, msisdn: str, reference: str,
                 description: str) -> dict:
        raise PaymentError("Selcom disburse: bado haijawezeshwa.")


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT SERVICE  (hii ndiyo app.py itatumia)
# ══════════════════════════════════════════════════════════════════════════════

class PaymentService:
    """
    Kiungo kati ya AgroLink routes na payment providers.
    App.py itatumia class hii tu — haijui kuhusu AzamPay au Selcom.

    Usage:
        from payment_service import PaymentService
        svc = PaymentService()

        # Anzisha malipo
        result = svc.initiate_payment(
            order=order,
            msisdn="255712345678"
        )

        # Kutoka callback route
        result = svc.handle_callback(request.json, request.headers)

        # Baada ya order kukamilika
        result = svc.release_escrow(escrow=escrow, seller_msisdn="255712345678")
    """

    def __init__(self):
        provider_name = os.getenv("PAYMENT_PROVIDER", "azampay").lower()
        if provider_name == "selcom":
            self.provider = SelcomProvider()
            self.provider_name = "Selcom"
        else:
            self.provider = AzamPayProvider()
            self.provider_name = "AzamPay"
        logger.info(f"PaymentService initialized with provider: {self.provider_name}")

    def initiate_payment(self, order, msisdn: str) -> dict:
        """
        Anzisha malipo kwa order iliyoidhinishwa (status=approved).

        Args:
            order: Order model instance (status lazima iwe 'approved')
            msisdn: Namba ya simu ya mnunuzi, format "255XXXXXXXXX"

        Returns:
            {"success": bool, "message": str, "reference": str}
        """
        # Safisha msisdn
        msisdn = self._normalize_msisdn(msisdn)

        # Tengeneza reference ya kipekee
        reference = f"AGR-{order.id}-{uuid.uuid4().hex[:8].upper()}"

        description = (
            f"AgroLink: Malipo ya order #{order.id} — "
            f"{order.quantity_kg}kg @ {order.price_tzs:,} TZS"
        )

        logger.info(
            f"Initiating payment: order={order.id}, "
            f"amount={order.price_tzs}, msisdn={msisdn[:7]}***"
        )

        result = self.provider.initiate(
            amount_tzs  = order.price_tzs,
            msisdn      = msisdn,
            reference   = reference,
            description = description,
        )

        result["reference"] = reference
        return result

    def handle_callback(self, payload: dict, headers: dict) -> dict:
        """
        Shughulikia callback kutoka payment provider.
        Itatumika kwenye /payments/callback route.

        Returns:
            {"success": bool, "reference": str, "status": str}
        """
        try:
            return self.provider.verify(payload, headers)
        except PaymentVerificationError as e:
            logger.error(f"Callback verification failed: {e}")
            return {"success": False, "reference": "", "status": "FAILED"}

    def release_escrow(self, escrow, seller_msisdn: str,
                       commission_rate: float = 0.05) -> dict:
        """
        Toa pesa kutoka escrow kwa mkulima baada ya order kukamilika.

        commission_rate: 0.05 = 5% ya platform (inaweza kubadilishwa)

        Returns:
            {"success": bool, "seller_amount": int, "platform_fee": int}
        """
        total       = escrow.amount_tzs
        platform_fee= int(total * commission_rate)
        seller_amt  = total - platform_fee

        seller_msisdn = self._normalize_msisdn(seller_msisdn)

        logger.info(
            f"Releasing escrow {escrow.reference}: "
            f"total={total}, seller={seller_amt}, fee={platform_fee}"
        )

        result = self.provider.disburse(
            amount_tzs  = seller_amt,
            msisdn      = seller_msisdn,
            reference   = f"DIS-{escrow.reference}",
            description = f"AgroLink: Malipo yako — order #{escrow.id}",
        )

        result["seller_amount"] = seller_amt
        result["platform_fee"]  = platform_fee
        return result

    @staticmethod
    def _normalize_msisdn(msisdn: str) -> str:
        """
        Badilisha namba yoyote ya TZ kuwa format "255XXXXXXXXX".
        0712345678 → 255712345678
        +255712345678 → 255712345678
        """
        msisdn = msisdn.strip().replace(" ", "").replace("-", "")
        if msisdn.startswith("+"):
            msisdn = msisdn[1:]
        if msisdn.startswith("0"):
            msisdn = "255" + msisdn[1:]
        return msisdn


# ── Singleton (import moja, instance moja) ───────────────────────────────────
_payment_service: Optional[PaymentService] = None

def get_payment_service() -> PaymentService:
    """Rudisha singleton ya PaymentService."""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService()
    return _payment_service
