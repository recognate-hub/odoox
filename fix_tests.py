def process(filepath):
    with open(filepath, "r") as f:
        data = f.read()
    data = data.replace(
        '== "Test Lead"', '== "<untrusted_crm_data>Test Lead</untrusted_crm_data>"'
    )
    data = data.replace(
        '== "Alpha Corp"', '== "<untrusted_crm_data>Alpha Corp</untrusted_crm_data>"'
    )
    data = data.replace(
        '== "Lead 1"', '== "<untrusted_crm_data>Lead 1</untrusted_crm_data>"'
    )
    data = data.replace(
        '== "Found Lead"', '== "<untrusted_crm_data>Found Lead</untrusted_crm_data>"'
    )
    data = data.replace(
        '== "John Doe"', '== "<untrusted_crm_data>John Doe</untrusted_crm_data>"'
    )
    data = data.replace(
        '== "Product A"', '== "<untrusted_crm_data>Product A</untrusted_crm_data>"'
    )
    data = data.replace(
        '== "S00001"', '== "<untrusted_crm_data>S00001</untrusted_crm_data>"'
    )
    with open(filepath, "w") as f:
        f.write(data)


process("tests/unit/test_crm_service.py")
process("tests/unit/test_repository.py")
