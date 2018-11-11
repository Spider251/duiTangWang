'https://www.duitang.com/napi/blog/list/by_search/?kw=%E6%A0%A1%E8%8A%B1&start=0&limit=1000'
#'https://www.duitang.com/search/?kw=%E6%A0%A1%E8%8A%B1&type=feed'

import requests
import urllib.parse
import threading

#设置最大线程锁——————监控有10条线程，超过10条就暂停——没上锁就烧cpu或电脑死机
thread_lock = threading.BoundedSemaphore(value=10)

#通过url获取数据
def get_page(url):
    #requests.get自带json转码
    page = requests.get(url)
    page = page.content
    #将bytes转成字符串
    page = page.decode('utf-8')
    return page
#label是字符串  譬如搜校花等关键字
def pages_from_duitang(label):
    pages = []
    url = 'https://www.duitang.com/napi/blog/list/by_search/?kw={}&start={}&limit=1000'
    #将中文转成url编码(ASCII)
    label = urllib.parse.quote(label)
    for index in range(0, 2380, 100):
        u = url.format(label,index)
        print(u)
        page = get_page(u)
        pages.append(page)
    return pages



def findall_in_page(page,startpart,endpart):#查找字符串头和尾切片
    all_strings = []
    end = 0
    while page.find(startpart,end) !=-1:#从end开始找 找不到返回-1结果，找到就死循环
        start = page.find(startpart,end)+len(startpart)
        end = page.find(endpart,start)
        string = page[start:end]#切片
        all_strings.append(string)
    return all_strings

def pic_urls_from_pages(pages):
    pic_urls = []
    for page in pages:#遍历36个页面
        urls = findall_in_page(page,'path":"','"')#取头，取尾
        pic_urls.extend(urls)#extend：将一个列表所有的元素添加到元素的后面
        print(pic_urls)
    return pic_urls

def download_pics(url,n):
    r = requests.get(url)
    path = 'pics/'+str(n)+'.jpg'
    with open(path,'wb') as f:
        f.write(r.content)
        #每张图片下载完了，解锁
        thread_lock.release()

def main(label):
    pages = pages_from_duitang(label)
    pic_urls = pic_urls_from_pages(pages)
    n = 0
    for url in pic_urls:
        n += 1
        print("正在下载第{}张图片！".format(n))
        #上锁
        thread_lock.acquire()
        t = threading.Thread(target=download_pics,args=(url,n))
        t.start()
main('校花')


