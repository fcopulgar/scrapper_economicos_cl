import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import webbrowser


def main():
    max_price = float(input("Max price CLP > ").replace('.', ''))
    min_price = float(input("Min price CLP > ").replace('.', ''))
    min_built = int(input("Min metros construidos m2 > ").replace('.', ''))
    min_terrace = int(input("Min terraza m2 > ").replace('.', ''))
    url_economicos = 'https://www.economicos.cl/rm/propiedades?idComuna=39&operacion=Venta&estacionamientos=1&age=7dd&pagina={page}'
    url_uf = 'https://mindicador.cl/api'
    uf = float(get_page(url_uf).json()["uf"]["valor"])
    print(uf)
    url = url_economicos.format(page=0)
    page = get_page(url)
    if page.status_code != 200:
        print("[!] ERROR: {}".format(page.status_code))
        exit()
    soup = BeautifulSoup(page.content, 'html.parser')
    max_pages = get_max_pages(soup)
    for page_number in range(max_pages):
        print("[i] PAGE {} / {}".format(page_number+1, max_pages))
        url_page = url_economicos.format(page=page_number)
        page = get_page(url_page)
        soup = BeautifulSoup(page.content, 'html.parser')

        mydivs = soup.findAll("div", {"class": "result row-fluid"})
        for div in mydivs:
            try:
                price_tag = div.find("li", {"class": "ecn_precio"})
                url_prop = "{}{}".format(get_hostname(url), div.find("a")["href"])
                price = price_tag.getText().replace(".", "").replace(" ", "").replace("\n", "").replace("\t", "")
                float_price = format_price(price, uf)
                if max_price > float_price > min_price:
                    page_prop = get_page(url_prop)
                    soup_prop = BeautifulSoup(page_prop.content, 'html.parser')
                    m2_built = get_m2_built(soup_prop)
                    m2_land = get_m2_land(soup_prop)
                    if m2_built > min_built and get_terrace_m2(m2_built, m2_land) > min_terrace:
                        print('{} ({})'.format(url_prop, int(float_price)))
                        print('m2 construidos: {}'.format(m2_built))
                        print('m2 terreno: {}'.format(m2_land))
                        webbrowser.open(url_prop)

            except Exception as e:
                pass


def get_page(url: str):
    page = requests.get(url=url)
    return page


def get_hostname(url: str) -> str:
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    return result


def get_max_pages(soup):
    text = soup.find("a", {"href": "#tab1"}).getText()
    print(text)
    max_pages = int(text.split(" ")[-2])
    return max_pages


def get_prop_specs(soup, text):
    try:
        div_table = soup.find("div", {"id": "specs"})
        li_obj = div_table.findAll("li")
        for li in li_obj:
            if text in li.getText():
                return li.getText().split()[-1]
        return None
    except Exception as e:
        return None


def get_m2_built(soup):
    try:
        m2 = int(get_prop_specs(soup, "construidos"))
        if m2 > 1000:
            return m2/1000
        else:
            return m2
    except Exception as e:
        return 0


def get_m2_land(soup):
    try:
        m2 = int(get_prop_specs(soup, "terreno"))
        if m2 > 1000:
            return m2/1000
        else:
            return m2
    except Exception as e:
        return 0


def get_terrace_m2(m2_built, m2_land):
    if m2_land == 0:
        return 0
    return m2_land - m2_built


def format_price(price: str, uf: float) -> float:
    if "UF" in price.upper():
        return float(price.replace("UF", ""))*uf
    else:
        return float(price)


if __name__ == '__main__':
    main()

