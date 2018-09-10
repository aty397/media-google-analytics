#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import sys

import click
import MySQLdb


# SHORTCODE_REX = re.compile(r'\[(\?)(\w+)[^]]*]')
SHORTCODE_REX = re.compile(r'\[(\\?)(\w+)[^]]*]')


@click.command()
@click.option('--host', default='127.0.0.1')
@click.option('--db', required=True)
@click.option('--user', default='root')
@click.option('--password', default='')

def main(host, db, user, password):
    connection = MySQLdb.connect(host=host, db=db, user=user, passwd=password)

    cursor = connection.cursor()

    # count total
    cursor.execute('SELECT COUNT(*) FROM wp_posts')
    total = cursor.fetchall()[0][0]

    # dump all post content
    # pub dateでソートして最新50件取ってくる
    cursor.execute("select ID,post_date,post_title from wp_posts where post_status = 'publish' and post_type in ('post', 'page') order by post_date desc limit 50")
    count = 0
    for post_id, post_date,post_title in cursor:
        count += 1
        # if (count % 1000) == 0:
        #     print(f'{count:6d} / {total:d}', file=sys.stderr)
        
        #GAで検索できる形(ルートからのパス)に変換
        post_id = get_posturl_from_postid_for_bijin (post_id)
        
        #時間部分を削除
        post_date = post_date.strftime("%Y-%m-%d-%H")

        print(post_id,post_date,post_title)
        # for mo in SHORTCODE_REX.finditer(post_content):
        #     is_end, shortcodename = mo.groups()
        #     # print(post_id, is_end, shortcodename)
        #     print(post_id, shortcodename)


def get_posturl_from_postid_for_bijin (postid):
    result = '/archives/'+ str(postid)
    return result

if __name__ == '__main__':
    main()

