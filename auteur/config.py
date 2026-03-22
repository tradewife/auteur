"""AUTEUR configuration — loads from environment / .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API keys
    fal_key: str = ""
    kie_api_key: str = ""
    gemini_api_key: str = ""

    # Browser automation
    browser_use_enabled: bool = False
    browser_use_api_key: str = ""
    browser_executable_path: str = ""
    browser_storage_state_dir: Path = Path("./.browser_state")
    browser_artifact_dir: Path = Path("./output/browser_ops")

    # Output
    auteur_output_dir: Path = Path("./output")

    # x402 payment gate
    x402_enabled: bool = False
    auteur_wallet: str = ""
    shot_price_usdc: str = "100000000000000"  # 0.0001 ETH in wei
    base_sepolia_rpc: str = "https://sepolia.base.org"
    auteur_contract_address: str = ""  # 0xAUTEUR.sol address for spend() calls
    deployer_private_key: str = ""  # For onchain spend() settlement

    @property
    def has_browser_use(self) -> bool:
        return self.browser_use_enabled and (
            bool(self.browser_use_api_key) or bool(self.gemini_api_key)
        )

    @property
    def has_fal(self) -> bool:
        return bool(self.fal_key)

    @property
    def has_kie(self) -> bool:
        return bool(self.kie_api_key)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def x402_configured(self) -> bool:
        return self.x402_enabled and bool(self.auteur_wallet)

    @property
    def can_settle(self) -> bool:
        return bool(self.deployer_private_key) and bool(self.auteur_contract_address)


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
