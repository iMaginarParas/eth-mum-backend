from web3 import Web3
from web3.exceptions import TransactionNotFound
from typing import Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WHITECHAIN_RPC_URL))
        self.chain_id = settings.WHITECHAIN_CHAIN_ID
        self.usdt_address = settings.USDT_CONTRACT_ADDRESS

    def is_connected(self) -> bool:
        """Check if connected to Whitechain RPC"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction details"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            return dict(tx)
        except TransactionNotFound:
            logger.warning(f"Transaction not found: {tx_hash}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transaction: {e}")
            return None

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction receipt"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except TransactionNotFound:
            logger.warning(f"Transaction receipt not found: {tx_hash}")
            return None
        except Exception as e:
            logger.error(f"Error fetching receipt: {e}")
            return None

    def verify_payment_transaction(
        self,
        tx_hash: str,
        expected_payment_id: str,
        expected_merchant: str,
        expected_amount: int
    ) -> bool:
        """Verify a payment transaction matches expected parameters"""
        try:
            receipt = self.get_transaction_receipt(tx_hash)
            if not receipt:
                return False

            # Check transaction was successful
            if receipt.get('status') != 1:
                logger.warning(f"Transaction failed: {tx_hash}")
                return False

            # Check contract address matches payment processor
            if receipt.get('to', '').lower() != settings.PAYMENT_PROCESSOR_ADDRESS.lower():
                logger.warning(f"Invalid contract address in tx: {tx_hash}")
                return False

            # Parse logs for PaymentCompleted event
            payment_processor_abi = [
                {
                    "anonymous": False,
                    "inputs": [
                        {"indexed": True, "name": "paymentId", "type": "bytes32"},
                        {"indexed": True, "name": "merchant", "type": "address"},
                        {"indexed": True, "name": "customer", "type": "address"},
                        {"indexed": False, "name": "amount", "type": "uint256"},
                        {"indexed": False, "name": "token", "type": "address"},
                        {"indexed": False, "name": "timestamp", "type": "uint256"}
                    ],
                    "name": "PaymentCompleted",
                    "type": "event"
                }
            ]

            contract = self.w3.eth.contract(
                address=settings.PAYMENT_PROCESSOR_ADDRESS,
                abi=payment_processor_abi
            )

            # Get PaymentCompleted events from receipt
            payment_events = contract.events.PaymentCompleted().process_receipt(receipt)

            if not payment_events:
                logger.warning(f"No PaymentCompleted event found in tx: {tx_hash}")
                return False

            # Verify event parameters
            event = payment_events[0]['args']
            payment_id_bytes = self.w3.to_bytes(hexstr=expected_payment_id)

            if event['paymentId'] != payment_id_bytes:
                logger.warning(f"Payment ID mismatch in tx: {tx_hash}")
                return False

            if event['merchant'].lower() != expected_merchant.lower():
                logger.warning(f"Merchant address mismatch in tx: {tx_hash}")
                return False

            if event['amount'] != expected_amount:
                logger.warning(f"Amount mismatch in tx: {tx_hash}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error verifying payment transaction: {e}")
            return False

    def convert_to_token_amount(self, amount_str: str, decimals: int = 6) -> int:
        """Convert human-readable amount to token amount with decimals"""
        from decimal import Decimal
        amount = Decimal(amount_str)
        return int(amount * (10 ** decimals))

    def convert_from_token_amount(self, amount: int, decimals: int = 6) -> str:
        """Convert token amount to human-readable string"""
        from decimal import Decimal
        return str(Decimal(amount) / (10 ** decimals))


blockchain_service = BlockchainService()
