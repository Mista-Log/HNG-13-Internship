from time import timezone
import requests
import random
from django.conf import settings
from datetime import datetime
from .models import Country, RefreshStatus
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont
import os


COUNTRIES_API = 'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies'
EXCHANGE_API = 'https://open.er-api.com/v6/latest/USD'




def fetch_countries_data(timeout=10):
    r = requests.get(COUNTRIES_API, timeout=timeout)
    r.raise_for_status()
    return r.json()




def fetch_exchange_rates(timeout=10):
    r = requests.get(EXCHANGE_API, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    # expected structure: { 'result': 'success', 'rates': {...} }
    rates = data.get('rates')
    if rates is None:
        raise ValueError('Malformed exchange API response')
    return rates




def generate_estimated_gdp(population, exchange_rate):
    if population is None or exchange_rate in (None, 0):
        return None
    multiplier = random.randint(1000, 2000)
    return (population * multiplier) / exchange_rate




def generate_summary_image(total, top_five, timestamp):
    # Create a simple PNG. Keep it basic so no complex fonts required.
    width, height = 1200, 630
    image = Image.new('RGB', (width, height), color=(255,255,255))
    draw = ImageDraw.Draw(image)


    # Use default font
    try:
        font = ImageFont.truetype('arial.ttf', size=24)
        title_font = ImageFont.truetype('arial.ttf', size=36)
    except Exception:
        font = ImageFont.load_default()
        title_font = font


    # Title
    draw.text((40,40), f"Countries Summary", font=title_font, fill=(0,0,0))
    draw.text((40,100), f"Total countries: {total}", font=font, fill=(0,0,0))
    draw.text((40,140), f"Last refreshed: {timestamp}", font=font, fill=(0,0,0))


    y = 200
    draw.text((40,y-30), "Top 5 by estimated GDP:", font=font, fill=(0,0,0))
    for i, c in enumerate(top_five, start=1):
        name = c.name
        gdp = f"{c.estimated_gdp:.2f}" if c.estimated_gdp is not None else 'N/A'
        draw.text((40,y), f"{i}. {name} — {gdp}", font=font, fill=(0,0,0))
        y += 32


    file_path = os.path.join(settings.CACHE_DIR, 'summary.png')
    image.save(file_path)
    return file_path

@transaction.atomic
def refresh_and_cache_all():
    # This function fetches external data and updates DB in a single transaction.
    # It will raise exceptions if external API calls fail.
    countries_json = fetch_countries_data()
    rates = fetch_exchange_rates()


    updated_count = 0
    for item in countries_json:
        name = item.get('name')
        capital = item.get('capital')
        region = item.get('region')
        population = item.get('population') or 0
        flag_url = item.get('flag')
        currencies = item.get('currencies') or []


        currency_code = None
        exchange_rate = None
        estimated_gdp = None


        if currencies and len(currencies) > 0:
            # take first currency code
            first = currencies[0]
            # currency may be {'code':'NGN', 'name': 'Nigerian Naira', 'symbol':'₦'}
            currency_code = first.get('code')
            if currency_code:
                # Try to find rate; rates are keyed by code maybe like 'NGN'
                exchange_rate = rates.get(currency_code)
                if exchange_rate in (None,):
                    exchange_rate = None
                if exchange_rate not in (None,):
                    estimated_gdp = generate_estimated_gdp(population, exchange_rate)
                else:
                    estimated_gdp = None
        else:
            # no currency array
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0


        # Upsert by case-insensitive name
        obj, created = Country.objects.update_or_create(
            name__iexact=name,
            defaults={
                'name': name,
                'capital': capital,
                'region': region,
                'population': population,
                'currency_code': currency_code,
                'exchange_rate': exchange_rate,
                'estimated_gdp': estimated_gdp,
                'flag_url': flag_url,
                'last_refreshed_at': timezone.now(),
            }
        )
        updated_count += 1


    # Update RefreshStatus (single record). Create or update.
    status, _ = RefreshStatus.objects.get_or_create(id=1)
    status.last_refreshed_at = timezone.now()
    status.total_countries = Country.objects.count()
    status.save()


    # Generate summary image
    top5 = Country.objects.exclude(estimated_gdp__isnull=True).order_by('-estimated_gdp')[:5]
    image_path = generate_summary_image(status.total_countries, top5, status.last_refreshed_at.isoformat())


    return {'total': status.total_countries, 'last_refreshed_at': status.last_refreshed_at, 'image_path': image_path}