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
    def get_leads(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooLead]:
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
    def search_contacts(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooContact]:
        pass

    @abstractmethod
    def create_contact(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_products(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooProduct]:
        pass

    @abstractmethod
    def create_product(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_quotes(
        self, domain: list[Any] | None = None, limit: int = 100, expand_fields: list[str] | None = None
    ) -> list[OdooQuote]:
        """Fetch quotes and sales orders matching a given domain."""
        pass

    @abstractmethod
    def create_quote(self, data: dict[str, Any]) -> int:
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

    @abstractmethod
    def create_invoice(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def send_email(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def search_read_records(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def create_record(self, model: str, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_record(self, model: str, record_id: int, data: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def get_installed_apps(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_model_fields(self, model: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def read_group(
        self, model: str, domain: list[Any], fields: list[str], groupby: list[str], **kwargs
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def archive_record(self, model: str, record_id: int, archive: bool = True) -> bool:
        pass

    @abstractmethod
    def get_attachment(self, attachment_id: int) -> dict[str, Any]:
        pass

    @abstractmethod
    def create_attachment(self, data: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def execute_method(
        self, model: str, method: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None
    ) -> Any:
        pass

    @abstractmethod
    def create_records(self, model: str, data_list: list[dict[str, Any]]) -> list[int]:
        pass

