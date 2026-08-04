from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from schemas.odoo import (
    OdooLead,
    OdooContact,
    OdooProduct,
    OdooQuote,
    OdooActivity,
    OdooMeeting,
    OdooSalesDashboard
)


class OdooConnectorInterface(ABC):
    """
    Abstract base class defining the contract for Odoo operations.
    Implementations (XML-RPC, REST, GraphQL) must conform to this interface.
    """

    @abstractmethod
    def get_leads(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooLead]:
        pass

    @abstractmethod
    def create_lead(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_lead(self, lead_id: int, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def delete_lead(self, lead_id: int) -> bool:
        pass

    @abstractmethod
    def search_contacts(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooContact]:
        pass

    @abstractmethod
    def get_products(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooProduct]:
        pass

    @abstractmethod
    def get_quotes(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooQuote]:
        pass

    @abstractmethod
    def create_activity(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def schedule_meeting(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_sales_dashboard(self) -> OdooSalesDashboard:
        pass
