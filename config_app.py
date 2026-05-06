from dataclasses import asdict, dataclass
import os

from dotenv import load_dotenv


@dataclass
class AppConfig:
    client_name: str
    client_business: str
    target_country: str
    anthropic_model: str
    max_search_results: int
    max_pages_to_read: int


def load_config() -> AppConfig:
    load_dotenv()
    return AppConfig(
        client_name=os.getenv("CLIENT_NAME", "Bubbles"),
        client_business=os.getenv(
            "CLIENT_BUSINESS",
            "Retail and e-commerce business operations",
        ),
        target_country=os.getenv("TARGET_COUNTRY", "Sweden"),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "8")),
        max_pages_to_read=int(os.getenv("MAX_PAGES_TO_READ", "5")),
    )


def as_dict(config: AppConfig) -> dict:
    return asdict(config)


if __name__ == "__main__":
    print(as_dict(load_config()))
