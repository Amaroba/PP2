import re
import json

text = open("raw.txt", "r", encoding="utf-8").read()

# 1) Prices (все денежные значения)
price_pattern = re.compile(r'\d[\d ]*,\d{2}')
prices = price_pattern.findall(text)
prices = [float(p.replace(' ', '')) for p in prices]

# 2) Product names
# Берём строки с точкой в конце номера и название после неё
name_pattern = re.compile(r'\d+\.\s*\n(.+)', re.MULTILINE)
names = name_pattern.findall(text)
names = [n.strip() for n in names]

# 3) Total amount
total_pattern = re.compile(r'ИТОГО:\s*([\d ]+,\d{2})')
total_match = total_pattern.search(text)
total = total_match.group(1).replace(' ', '') if total_match else None

# 4) Date & time
dt_pattern = re.compile(r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s*\d{2}:\d{2}:\d{2})')
dt = dt_pattern.search(text)
datetime = dt.group(1) if dt else None

# 5) Payment method
pay_pattern = re.compile(r'Банковская карта:\s*([\d ]+,\d{2})')
payment = pay_pattern.search(text)
payment_method = payment.group(1).replace(' ', '') if payment else None

# Structured output
data = {
    "products": names,
    "prices": prices,
    "total_calculated": sum(prices),
    "total_on_receipt": total,
    "datetime": datetime,
    "payment": payment_method
}

print(json.dumps(data, indent=4, ensure_ascii=False))