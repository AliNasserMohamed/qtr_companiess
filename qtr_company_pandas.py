import time

from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import aiohttp
import asyncio

csv_file = open("qtr_company.csv", "w", encoding="utf-8", newline='')
writer = csv.writer(csv_file)
writer.writerow(
    ["name", "desc", "section_name", "address", "website", "phone", "tel", "whats", "email", "city", "link","added"])


class WebScraper(object):
    def __init__(self, urls,sections):
        self.urls = urls
        self.sections=sections
        self.all_data = []
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.main())

    def get_post_data(self, data, link,section_name):
        try:
            product_soup = BeautifulSoup(data, features="html.parser")
            name = product_soup.find("h3", class_="panel-title").text
            desc, website, address, phone, whats, tel, email, city,added = None, None, None, None, None, None, None, None,None
            ps = product_soup.find("div", id="site_info").find_all("p")
            for p in ps:
                if "رابط الشركة" in p.text:
                    website = p.find("a")["href"]
                elif "وصف الشركة" in p.text:
                    desc = p.text
                elif "عنوان الشركة" in p.text:
                    address = p.text
                elif "الهاتف" in p.text:
                    phone = p.text.split("fax")[0].replace("Tel", "").replace("الهاتف", "").replace("tel", "").replace(
                        "هاتف", "").replace("ephoneNumber(s)", "").replace("ephoneNumber(s)", "")
                    phone = phone.split("Fax")[0].split("Mobile")[0].split("فاكس")[0]
                    phone = phone.replace(":", "").replace("		", "").replace("+", "00").replace("- Hotline",
                                                                                                      "").replace(
                        "هاتف", "").replace("Calluson", "").replace("ephoneNumber(s)", "")
                elif "البريد الاكتروني" in p.text:
                    email = p.text.replace("البريد الاكتروني", "")
                elif "المدينة" in p.text:
                    city = p.text.replace("المدينة", "")
                elif "تاريخ الإضافة:" in p.text:
                    added = p.text.replace("تاريخ الإضافة:", "")
            ass = product_soup.find("div", id="site_info").find_all("a")
            for a in ass:
                # print(a.text)
                if "إتصل" in a.text:
                    phone = a["href"].replace("tel", "").replace(":", "")
                elif "واتس أب" in a.text:
                    whats = a["href"].replace("tel", "").replace(":", "")
                elif "عبر الهاتف " in a.text:
                    tel = a["href"].replace("tel", "").replace(":", "")
                elif "الأيميل " in a.text:
                    email = a["href"].replace("mailto", "").replace(":", "")
            data_list = [name, desc, section_name, address, website, phone, tel, whats, email, city, link,added]
            writer.writerow(data_list)
        except:
            print("pass", link)

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                text = await response.read()
                return text, url
        except Exception as e:
            print(str(e))

    async def main(self):
        tasks = []
        headers_post = {
            "host": "qtr.company",
            "connection": "keep-alive",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en;q=0.9",
            "cookie": "PHPSESSID=7e4cdfcbce6fb850f4a36d8c6917ed89; _ga=GA1.2.1205744864.1679311474; _gid=GA1.2.1750024913.1679311474"
        }
        async with aiohttp.ClientSession(headers=headers_post) as session:
            for url in self.urls:
                tasks.append(asyncio.ensure_future(self.fetch(session, url)))

            htmls = await asyncio.gather(*tasks)
            self.all_data.extend(htmls)

            # Storing the raw HTML data.
            conter = 0
            for html, link,section_name in zip(htmls, self.urls,self.sections):

                if html is not None:
                    conter += 1
                    print("\t\t we are getting ", conter)
                    # self.master_dict[url] = {'Raw Html': html[0], 'Title': html[2]}
                    # print(html[0])
                    self.get_post_data(html[0], link,section_name)
                else:
                    continue


df=pd.read_excel("qtr_companies_.xlsx")

url = "https://qtr.company/categories.php"

sections_links =df["link"].to_list()
section_names =df["section_name"].to_list()
print("all_sections", len(section_names))
section_c = 0
start=0
step=100
end=len(section_names)
for i in range(start,end,step):
    print(" scraping",i+step)
    WebScraper(sections_links[i:i+step],section_names[i:i+step])
    time.sleep(10)


