import json

def parse_interfaces():
    with open("sample-data.json") as f:
        data = json.load(f)

    print("Interface Status")
    print("=" * 80)
    print(f"{'DN':50} {'Description':20} {'Speed':8} {'MTU':6}")
    print("-" * 80)

    for item in data["imdata"]: # Словарь и ключ,item словарь
        attributes = item["l1PhysIf"]["attributes"] #Тоже ключ, и внутри словарь
        # Берем конкретные значения
        dn = attributes["dn"]
        descr = attributes["descr"]
        speed = attributes["speed"]
        mtu = attributes["mtu"]

        print(f"{dn:50} {descr:20} {speed:8} {mtu:6}")


parse_interfaces()
