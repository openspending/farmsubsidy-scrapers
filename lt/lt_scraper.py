import asyncio
import csv
import time
import os

import lxml.html
from playwright.async_api import async_playwright
import httpx
from tqdm import tqdm
import pandas as pd


YEAR = 2021
BASE_URL = 'https://portal.nma.lt/nma-portal/pages/fas_search'
PROGRAM_NAME = 'KP13'



async def get_session():
    
    headers = None

    async def find_data_request(request):
        nonlocal headers

        if request.method == 'GET' and request.url == BASE_URL:
            print("Found request")
            headers = await request.all_headers()
            headers = headers.copy()
            

    async with async_playwright() as p:
        print("Launch browser")
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        page.set_default_navigation_timeout(120_000)

        await page.goto(BASE_URL)
        # page.on("response", lambda response: print("<<", response.status, response.url))
        await page.wait_for_load_state(state="networkidle")
        await page.locator(f"a[href=\"javascript:submitForm('{PROGRAM_NAME}');\"]").click()
        await page.wait_for_load_state(state="networkidle")

        page.on("request", lambda request: print(">>", request.method, request.url))
        page.on("request", find_data_request)
        await page.goto(BASE_URL)

        headers.pop("content-length", None)
        return headers


class EndOfPagination(Exception):
    pass


SUBSIDY_TYPES = {
    0: 'EAGF',
    1: 'EAGF - other',
    2: 'EAFRD',
}

def get_data_items(root):
    table = root.xpath('//table[1]')
    if not table:
        raise EndOfPagination
    table = table[0]
    trs = table.xpath('.//tr')
    base = None
    for tr in trs:
        tds = tr.xpath('./td')
        if tr.attrib.get('id'):
            base = {
                'year': YEAR,
                'country': 'LT',
                'currency': 'EUR',
                'recipient_id': tr.attrib.get('id'),
                'recipient_name': tds[0].text_content(),
                'recipient_location': '%s, %s' % (
                    tds[2].text_content().replace('rajonas', '').strip(),
                    tds[1].text_content().replace('apskritis', '').strip(),
                )
            }
        else:
            subsidy_name = tds[3].text_content()
            for i in range(3):
                amount = float(tds[4 + i].text_content().replace(',', '.'))
                if amount > 0:
                    subsidy = dict(base)
                    subsidy.update({
                        'scheme': '%s (%s)' % (subsidy_name, SUBSIDY_TYPES[i]),
                        'amount': amount
                    })
                    yield subsidy


def download_offset(page_num, headers):
    post_data = {
        "pa": "pl",
        "pTipas": "p",
        "psl_nr": str(page_num),
        "programos_kodas": PROGRAM_NAME,
        "fin_metai": str(YEAR),
        "pareiskejas": "",
        "apskritis": "",
        "savivaldybe": "",
        "priemone": "",
        "t_suma": "",
        "k_suma": "",
        "v_suma": "",
        "b_suma": "",
        "action": "Ieškoti",
    }
    response = httpx.post(BASE_URL, headers=headers.copy(), data=post_data, timeout=120)
    with open("page.html", "w") as f:
        f.write(response.text)
    root = lxml.html.fromstring(response.text)
    yield from get_data_items(root)

OFFSET_FILE = 'lt_offset.txt'

def update_offset(offset):
    with open(OFFSET_FILE, 'w') as f:
        f.write(str(offset))


def read_offset():
    if not os.path.exists(OFFSET_FILE):
        return 1
    with open(OFFSET_FILE, 'r') as f:
        return int(f.read())

def main():
    headers = asyncio.run(get_session())
    print("Headers:", headers)
    output_filename = f'lt_{YEAR}.csv.gz'
    if os.path.exists(output_filename):
        df = pd.read_csv(output_filename)
    else:
        df = pd.DataFrame()
    page_num = read_offset()
    while True:
        print("Downloading page", page_num)
        try:
            df = pd.concat([df, pd.DataFrame(list(download_offset(page_num, headers)))])
            df.to_csv(output_filename, index=False, compression='gzip')
            page_num += 1
            update_offset(page_num)
        except EndOfPagination:
            print("End of pagination")
            break
        except Exception as e:
            print(e)
            time.sleep(30)
            headers = asyncio.run(get_session())


if __name__ == '__main__':
    main()
