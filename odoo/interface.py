from abc import ABC, abstractmethod
from typing import Any

from schemas.odoo import (
    OdooContact,
    OdooLead,
    OdooProduct,
    OdooQuote,
    OdooSalesDashboard,
)


class OdooConnectorInterface(ABC):
    """
    Abstract base class defining the contract for Odoo operations.
    Implementations (XML-RPC, REST, GraphQL) must conform to this interface.
    """

    @abstractmethod
    def get_leads(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooLead]:
        pass

    @abstractmethod
    def create_lead(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_lead(self, lead_id: int, data: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def delete_lead(self, lead_id: int) -> bool:
        pass

    @abstractmethod
    def search_contacts(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooContact]:
        pass

    @abstractmethod
    def get_products(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooProduct]:
        pass

    @abstractmethod
    def get_quotes(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooQuote]:
        pass

    @abstractmethod
    def create_activity(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def schedule_meeting(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_sales_dashboard(self) -> OdooSalesDashboard:
        pass
