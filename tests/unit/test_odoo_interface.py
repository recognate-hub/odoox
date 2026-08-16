from odoo.interface import OdooConnectorInterface


class DummyConnector(OdooConnectorInterface):
    def get_leads(self, domain=None, limit=100):
        return super().get_leads(domain, limit)

    def create_lead(self, data):
        return super().create_lead(data)

    def update_lead(self, lead_id, data):
        return super().update_lead(lead_id, data)

    def delete_lead(self, lead_id):
        return super().delete_lead(lead_id)

    def search_contacts(self, domain=None, limit=100):
        return super().search_contacts(domain, limit)

    def create_contact(self, data):
        return super().create_contact(data)

    def get_products(self, domain=None, limit=100):
        return super().get_products(domain, limit)

    def create_product(self, data):
        return super().create_product(data)

    def get_quotes(self, domain=None, limit=100):
        return super().get_quotes(domain, limit)

    def create_quote(self, data):
        return super().create_quote(data)

    def create_activity(self, data):
        return super().create_activity(data)

    def schedule_meeting(self, data):
        return super().schedule_meeting(data)

    def get_sales_dashboard(self):
        return super().get_sales_dashboard()

    def create_invoice(self, data):
        return super().create_invoice(data)

    def send_email(self, data):
        return super().send_email(data)

    def search_read_records(self, model, domain=None, fields=None, limit=100):
        return super().search_read_records(model, domain, fields, limit)

    def create_record(self, model, data):
        return super().create_record(model, data)

    def update_record(self, model, record_id, data):
        return super().update_record(model, record_id, data)

    def get_installed_apps(self):
        return super().get_installed_apps()

    def get_model_fields(self, model):
        return super().get_model_fields(model)


def test_interface_methods():
    dummy = DummyConnector()
    
    assert dummy.get_leads() is None
    assert dummy.create_lead({}) is None
    assert dummy.update_lead(1, {}) is None
    assert dummy.delete_lead(1) is None
    
    assert dummy.search_contacts() is None
    assert dummy.create_contact({}) is None
    
    assert dummy.get_products() is None
    assert dummy.create_product({}) is None
    
    assert dummy.get_quotes() is None
    assert dummy.create_quote({}) is None
    
    assert dummy.create_activity({}) is None
    assert dummy.schedule_meeting({}) is None
    assert dummy.get_sales_dashboard() is None
    
    assert dummy.create_invoice({}) is None
    assert dummy.send_email({}) is None
    
    assert dummy.search_read_records("model") is None
    assert dummy.create_record("model", {}) is None
    assert dummy.update_record("model", 1, {}) is None
    
    assert dummy.get_installed_apps() is None
    assert dummy.get_model_fields("model") is None
