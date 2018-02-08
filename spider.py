#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from fake_useragent import UserAgent
from lxml.html import etree
import sqlite3
from pprint import pprint
import time

# ua = UserAgent()
# ua = ua.random
ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap['phantomjs.page.settings.userAgent'] = (ua)
driver = webdriver.PhantomJS(desired_capabilities=dcap)


def parse_song(list_url):
    driver.get(list_url)
    driver.implicitly_wait(55)
    # ele = driver.find_element_by_id('g_iframe')
    driver.switch_to.frame('g_iframe')
    # pprint(driver.page_source)
    dom_tree = etree.HTML(driver.page_source)
    span_txts = dom_tree.xpath('//table[@class="m-table "]/tbody/tr/td[2]//span[@class="txt"]/a/b/@title')
    song_ids = dom_tree.xpath('//table[@class="m-table "]/tbody/tr/td[1]/div/span[1]/@data-res-id')
    print('共匹配到：{}首歌曲'.format(len(song_ids)))
    for i in zip(span_txts, song_ids):
        song_name = i[0]
        song_id = i[1]
        song_url = 'http://music.163.com/#/song?id={}'.format(song_id)
        yield song_id, song_name, song_url


def parse_comment(song_url):
    driver.get(song_url)
    driver.implicitly_wait(55)
    # ele = driver.find_element_by_id('g_iframe')
    driver.switch_to.frame('g_iframe')
    # print(driver.page_source)
    dom_tree = etree.HTML(driver.page_source)
    itms = dom_tree.xpath('//div[@class="cmmts j-flag"]/div[@class="itm"]')[:15]
    for itm in itms:
        c = itm.xpath('./div[@class="cntwrap"]/div[1]/div//text()')
        author = c[0].replace('“', '-').replace('”', '-').replace('"', '-').replace("'", "-")
        comment = c[1:]
        comment = ''.join(comment)[1:].replace('“', '-').replace('”', '-').replace('"', '-').replace("'", "-")
        date = itm.xpath('./div[@class="cntwrap"]/div[last()]/div[1]/text()')[0]
        # print(author, date, comment)
        yield author, date, comment


def main():
    s_time = time.time()
    count1 = 0
    count2 = 0
    raw_url = 'http://music.163.com/#/playlist?id=81371919'
    conn = sqlite3.connect('music163.db')
    songs = parse_song(raw_url)

    conn.execute(
        'CREATE TABLE IF NOT EXISTS "@@歌曲ID" (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, song_id INTEGER)')

    for song in songs:
        print('*' * 5)
        print(song)
        song_id, song_name, song_url = song[0], song[1], song[2]
        conn.execute('INSERT INTO "@@歌曲ID" (name, song_id) VALUES ("{}",{})'.format(song_name, song_id))
        conn.commit()
        conn.execute(
            'CREATE TABLE IF NOT EXISTS "{}" (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, date TEXT, comment TEXT)'.format(
                song_name))
        song_comment = parse_comment(song_url)
        for info in song_comment:
            print('*' * 10)
            print(info)
            author, date, comment = info[0], info[1], info[2]
            conn.execute(
                'INSERT INTO "{}" (author, date, comment) VALUES ("{}","{}","{}")'.format(song_name, author, date,
                                                                                          comment))
            conn.commit()
            count2 += 1
            print('评论 -' + str(count2) + '- OK')
        count1 += 1
        print('歌曲 -' + str(count1) + '- OK')
    driver.quit()
    conn.close()

    e_time = time.time()
    print('\n耗时：{} s'.format(e_time - s_time))
    print('\n共采集 {} 首歌曲 \ {} 条评论'.format(count1, count2))


def test():
    url = 'http://music.163.com/#/song?id=501133611'
    a = parse_comment(url)
    for i in a:
        print(i)


if __name__ == '__main__':
    main()
    # test()
