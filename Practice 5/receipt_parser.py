import re
import json

text = open("raw.txt", "r", encoding="utf-8").read()

# 1) Цены — только строки вида "308,00"
price_pattern = re.compile(r'^\d[\d ]*,\d{2}$', re.MULTILINE)
prices = price_pattern.findall(text)

# превращаем "1 526,00" → 1526.00
prices = [float(p.replace(' ', '').replace(',', '.')) for p in prices]

# 2) Названия товаров
name_pattern = re.compile(r'^\d+\.\s*\n(.+)', re.MULTILINE)
names = name_pattern.findall(text)
names = [n.strip() for n in names]

# 3) Итог
total_pattern = re.compile(r'ИТОГО:\s*([\d ]+,\d{2})')
total_match = total_pattern.search(text)
total = total_match.group(1).replace(' ', '') if total_match else None

# 4) Дата/время
dt_pattern = re.compile(r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s*\d{2}:\d{2}:\d{2})')
dt = dt_pattern.search(text)
datetime = dt.group(1) if dt else None

# 5) Оплата
pay_pattern = re.compile(r'Банковская карта:\s*([\d ]+,\d{2})')
pay = pay_pattern.search(text)
payment = pay.group(1).replace(' ', '') if pay else None

data = {
    "products": names,
    "prices": prices,
    "total_calculated": sum(prices),
    "total_on_receipt": total,
    "datetime": datetime,
    "payment": payment
}

print(json.dumps(data, indent=4, ensure_ascii=False))