from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Whitechain
    WHITECHAIN_RPC_URL: str = "https://rpc.testnet.whitechain.io"
    WHITECHAIN_CHAIN_ID: int = 1874
    USDT_CONTRACT_ADDRESS: str = "0xcedfB56113143d55b2358b8CFbB0dEB5Ad2f55a7"

    # Smart Contracts
    PAYMENT_PROCESSOR_ADDRESS: Optional[str] = None
    REFUND_MANAGER_ADDRESS: Optional[str] = None

    # API
    SECRET_KEY: str
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Webhook
    WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
