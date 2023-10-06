import json
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import re


def get_soup(url):
    headers_gen = Headers(os='win', browser='chrome')
    hh = requests.get(url, headers=headers_gen.generate())
    hh_html = hh.text
    hh_soup = BeautifulSoup(hh_html, 'lxml')
    vacancies_list = hh_soup.find_all("div", class_="vacancy-serp-item__layout")
    return vacancies_list, headers_gen


def soup_info(vacancies_list, headers_gen):
    parsed_data = []
    parsed_salary = []
    for vacancy in vacancies_list:
        a_tag = vacancy.find('a')
        link = a_tag["href"]
        vacancy_description = requests.get(link, headers=headers_gen.generate()).text
        vacancy_soup = BeautifulSoup(vacancy_description, "lxml")
        vacancy_keys = vacancy_soup.find_all("span", class_="bloko-tag__section bloko-tag__section_text")

        reg_ex = r'Flask?.+|Django?.+'
        res = re.findall(reg_ex, str(vacancy_keys))
        if len(res) > 0:
            company = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary').text
            city = vacancy.find('div', attrs={'data-qa':'vacancy-serp__vacancy-address'}, class_='bloko-text').text
            a_tag = vacancy.find('a')
            abs_link = a_tag["href"]
            salary_tag = vacancy.find('span', class_='bloko-header-section-2')
            if salary_tag is not None:
                salary = salary_tag.text
            else:
                salary = 'Зарплата не указана.'
            data = {
                    "link": abs_link,
                    "company": company,
                    "city": city.split()[0].strip(','),
                    "salary": salary
                    }
            parsed_data.append(data)

            if '$' in salary:
                parsed_salary.append(data)
    return parsed_data, parsed_salary


hh_url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
v_list, h_gen = get_soup(hh_url)
data, doll_salary = soup_info(v_list, h_gen)

jstr = json.dumps(data, ensure_ascii=False, indent=4)
jstr_dollars = json.dumps(doll_salary, ensure_ascii=False, indent=4)


print(f'Vacancies-json: {jstr}\nVacancies with salary in dollars:{jstr_dollars}')

with open('hh.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False)
