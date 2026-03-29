# CURRENCY CONVERT
def convert_vnd_to_usd(vnd_amount):
    rate  =  26000  # 1 USD ≈ 24,000 VND

    usd = vnd_amount / rate

    return round(usd, 2)