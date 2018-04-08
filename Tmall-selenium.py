#!./usr/bin/env.python
# -*- coding: utf-8 -*-
# 使用selenium抓取天猫搜索结果页数据
# 其实搜索结果页的数据并没有使用异步加载，使用requests抓取也是可以的，selenium的优势在于抓取异步加载的数据和需要鼠标键盘的交互操作
# 想再提高效率可以使用多线程和配置headless的chrome来抓取

import time,csv
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

page_num = 0

# 当前文件目录下，新建一个csv文件，写入标题行，以便后期追加写入数据
with open('result.csv', 'w', encoding='utf-8', newline='') as result:
    item_info = csv.writer(result)
    item_info.writerow(['商品链接', '商品图片', '商品价格', '商品标题', '店铺名称', '店铺链接', '商品销量'])


def search_for(url, keyword, timeout):
    driver = webdriver.Chrome(executable_path=r'D:\Panson\scrapystudy\Scripts\drivers\chromedriver.exe')
    driver.get(url=url)  # url='https://yao.tmall.com/'
    try:
        # 获取输入框
        # 使用显式等待定位输入框，找到就立刻执行下一步，找不到就默认每隔0.5秒再查找一次，直至超时报错
        search = WebDriverWait(driver=driver, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, '//input[@id="mq"]')))  # timeout=10
        # print(search)
        # 直接定位
        # search2 = driver.find_element_by_id("mq")
        # print(search2)
        # 清空输入框
        search.clear()
        # 输入关键字
        # search.send_keys(keyword)  # keyword='减肥药'
        # 直接一步输入关键字回车，不用分开写代码
        search.send_keys(keyword + Keys.RETURN)
        # 可以不获取搜索按钮，直接在搜索框回车即可
        # search.send_keys(Keys.RETURN)
        # 获取搜索按钮
        # button = WebDriverWait(driver=driver, timeout=5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mallSearch"]/form/fieldset/div[@class="mallSearch-input clearfix"]/button')))
        # # 点击搜索
        # button.click()
    except TimeoutException:
        print('超时错误')
    # 使用显式等待不会报抓不到元素的错误，只会报查找超时错误
    # except NoSuchElementException:
    #     print('找不到元素错误')
    except ElementClickInterceptedException:
        print('点击错误')
    except WebDriverException:
        print('未知错误')
        driver.quit()
    # 顺利跳转到搜索结果页
    # 开始抓取数据
    crawl(driver)


def crawl(driver):
    global page_num
    page_num += 1
    try:
        WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="product  "]/div[@class="product-iWrap"]')))
        # print(product_info)
        # print(type(product_info))
        response = Selector(text=driver.page_source)
        products = response.xpath('//div[@class="product  "]/div[@class="product-iWrap"]')
        for product in products:
            detail_url = product.xpath('.//div[@class="productImg-wrap"]/a/@href').extract_first()
            img = product.xpath('.//div[@class="productImg-wrap"]/a/img/@src').extract_first()
            price = ''.join(product.xpath('.//p[@class="productPrice"]/em//text()').extract())  # 拼接“¥”符号与价格
            title = product.xpath('.//p[@class="productTitle"]/a/@title').extract_first()
            shop = ''.join(product.xpath('.//a[@class="productShop-name"]//text()').extract()).strip()  # 防止搜索高亮标签影响，拼接列表并去除换行符
            shop_url = product.xpath('.//a[@class="productShop-name"]/@href').extract_first()
            status = product.xpath('.//p[@class="productStatus"]/span/em/text()').extract_first(default="0")
            # '追加'模式，把抓取数据写入csv文件保存
            with open('result.csv', 'a', encoding='utf-8', newline='') as f:
                item = csv.writer(f)
                item.writerow([detail_url, img, price, title, shop, shop_url, status])
            print('商品链接：' + detail_url + '\n'
                  '商品图片：' + img + '\n'
                  '商品价格：' + price + '\n'
                  '商品标题：' + title + '\n'
                  '店铺名称：' + shop + '\n'
                  '店铺链接：' + shop_url + '\n'
                  '商品销量：' + status + '\n\n'
                  )
        # for product in product_info:
        #     url = product.find_element_by_class_name('productImg').get_attribute('href')
        #     img = product.find_element_by_xpath('//div[@class="productImg-wrap"]/a/img').get_attribute('src')
        #     price = product.find_element_by_class_name('productPrice').text
        #     title = product.find_element_by_class_name('productTitle').text
        #     shop = product.find_element_by_class_name('productShop-name').text
        #     status = product.find_element_by_xpath('//p[@class="productStatus"]/span/em') # 有些会显示这个元素，有些没有这个元素，导致循环出错，能否通过设定默认值解决？
        #     if status:
        #         salse = status
        #     else:
        #         salse = 0
        #     # print(url+'\n\n', img+'\n\n', price+'\n\n', title+'\n\n', shop+'\n\n', status+'\n\n')
        #     print(salse + '\n\n')
    except TimeoutException:
        print('定位元素超时')
    except NoSuchElementException:
        print('找不到元素错误')
    except ElementClickInterceptedException:
        print('点击错误')
    except WebDriverException:
        print('未知错误')
        driver.quit()
# 翻页循环抓取
    try:
        next_page = driver.find_element_by_link_text('下一页>>')
        # print(type(next_page), '\n', next_page)
        # 点击下一页
        next_page.click()
        # 抓取下一页
        # 抓取函数
        crawl(driver)
    # 末页为不可点击的b标签
    except NoSuchElementException:
        print('抓取完毕或找不到定位元素,共抓取', page_num, '页数据')
        # time.sleep(60)
        # driver.quit()


if __name__ == "__main__":
    search_for(url='https://www.tmall.com/', keyword='减肥药', timeout=10)
