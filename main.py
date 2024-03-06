import asyncio
import aiohttp

from bs4 import BeautifulSoup

import ssl

sslcontext = ssl.create_default_context()
sslcontext.check_hostname = False
sslcontext.verify_mode = ssl.CERT_NONE


async def fetch_data(session, week):
    url = ('https://www.nstu.ru/studies/schedule/'
           f'schedule_classes/schedule?group=АВТ-343&week={week}')
    async with session.get(url, ssl=sslcontext) as response:
        return await response.text()


async def process_info(data, info_i, time):
    info_i = info_i.strip()
    if '\n' in info_i:
        info_i = info_i.replace('\n', ' ')
    else:
        dic.append({'Дата': '-'.join(data.text.split('.')),
                    'Предмет': info_i,
                    'Время': time})
        return

    if '·' in info_i.split(' '):
        name_obj = info_i.split(' ')
        dic.append({'Дата': '-'.join(data.text.split('.')),
                    'Предмет': ' '.join(name_obj[0:name_obj.index('·')]).strip(),
                    'Время': time,
                    'Тип': name_obj[-2]})
    else:
        name_obj = info_i.split(' ')
        dic.append({'Дата': '-'.join(data.text.split('.')),
                    'Предмет': ' '.join(name_obj[0:name_obj.index('')]).strip(),
                    'Время': time})


async def scrape_data(week):
    async with aiohttp.ClientSession() as session:
        html = await fetch_data(session, week)
        code = BeautifulSoup(html, 'html.parser')

        all_obj = code.find_all('div', class_='schedule__table-row', attrs={'data-empty': True})

        if all_obj:
            for obj in all_obj:
                data = obj.find('span', class_='schedule__table-date')
                info = obj.find_all('div', class_='schedule__table-row')

                for i in range(len(info)):
                    info_i = info[i].find('div', class_='schedule__table-item').text
                    if len(info_i) != 34:
                        try:
                            time = info[i].find('div', class_='schedule__table-time').text
                            await process_info(data, info_i, time)
                        except AttributeError:
                            continue


async def main():
    tasks = [scrape_data(week) for week in range(1, 19)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    dic = []

    asyncio.run(main())

    print(dic)
