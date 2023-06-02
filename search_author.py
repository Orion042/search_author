#!/usr/bin/env python
import sqlite3
import sys
import argparse
import os
import uuid
from tabulate import tabulate

count_author = 0

def check_wrong(num):
    if (num in [1, 2, 3, 4, 9, 10, -1]):
        return True
    else:
        return False

def user_select():
    print("=== コマンド入力 ===")
    while True:
        print("名前検索 : 1")
        print("タグ検索 : 2")
        print("表示 : 3")
        print("更新 : 4")
        print("追加 : 9")
        print("終了 : 10")
        print("削除 : -1")
        num = int(input("入力 ---> "))
        print("============")
        if (check_wrong(num)):
            break
        print("== 1, 2, 3, 4, 9, 10, -1の値を入力してください ==")
    return num

def show_count_author(num):
    print("\n===========================")
    print("登録数 : ", num)
    print("===========================")

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--tablefmt", type=str, default="grid", help="表示する形式を入力 (simple, plain, grid, pipe, orgtbl)")

    args = parser.parse_args()

    return args

def init_DB():
    path = os.getcwd()

    db_file = path + "\\author_db.db"

    if not os.path.isfile(db_file):
        print("DB file not found")
        print("Create new DB file ? [Y/N]")
        user = input("--> ")
        if(user.lower() in ["no", "n"]):
            sys.exit()
    conn = sqlite3.connect(db_file)

    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS author (author_id varchar(100) PRIMARY KEY, jp_name varchar(100) NOT NULL,en_name varchar(100) NOT NULL,book text)")
    cur.execute("CREATE TABLE IF NOT EXISTS tag (author_id varchar(100) NOT NULL, tag varchar(100))")

    return conn, cur

def strip_tag(tags):
    return tags.split(",")


def search_authorNameDB(conn, cur, args):
    user_count = 0
    headers = ["日本語名", "英語名"]
    table_data = list()

    name = input("検索したい作家名 ---> ")
    for row in cur.execute("SELECT jp_name,en_name from author WHERE jp_name like ? OR en_name like ?",("%" + name + "%","%" + name + "%")):
        table_data.append([row[0], row[1]])
        user_count += 1

    if (user_count != 0):
        result=tabulate(table_data, headers, tablefmt=args.tablefmt.lower())
        print("")
        print(result)
    else:
        print("\n===========================")
        print("      該当なし")
        print("===========================")

def list_to_string(tag_list):
    return ", ".join(tag_list)

def show_tagDB(conn, cur):

    tag_list = []
    
    for row in cur.execute("SELECT tag From tag ORDER BY tag ASC"):
        tag_list.append(row[0])

    print("タグ一覧 : " + str(sorted(list(set(tag_list)))))

def search_tagDB(conn, cur, args):
    headers = ["日本語名", "英語名", "タグ名"]
    table_data = list()

    show_tagDB(conn, cur)

    search_tag = input("検索したいタグを入力 (複数の場合はカンマ区切り) ---> ")

    search_tag = search_tag.replace(", ",",")

    array_tag = strip_tag(search_tag)

    author_tmp_jpName = ""
    author_tmp_enName = ""
    author_tmp_tag = []
    count_row = 0

    for row in cur.execute("SELECT * FROM author INNER JOIN tag ON author.author_id = tag.author_id WHERE tag.tag IN ({})".format(','.join('?'*len(array_tag))), array_tag):
        
        if count_row == 0:
            author_tmp_jpName = row[1]
            author_tmp_enName = row[2]
            count_row += 1

        if author_tmp_jpName == row[1]:
            author_tmp_tag.append(row[5])
        else:
            table_data.append([author_tmp_jpName, author_tmp_enName, list_to_string(author_tmp_tag)])
            author_tmp_jpName = row[1]
            author_tmp_enName = row[2]
            author_tmp_tag = []
            author_tmp_tag.append(row[5])
            
    table_data.append([author_tmp_jpName, author_tmp_enName, list_to_string(author_tmp_tag)])

    if count_row > 0:
        result=tabulate(table_data, headers, tablefmt=args.tablefmt.lower())
        print("")
        print(result)
    else:
        print("\n===========================")
        print("      該当なし")
        print("===========================")

def show_DB(conn, cur, args):
    global count_author

    print("名前順 : 1")
    print("登録順 : 2")
    num = int(input("入力 ---> "))
    headers = ["日本語名", "英語名"]
    table_data = list()

    if (num == 1):
        for row in cur.execute("SELECT jp_name,en_name from author ORDER BY jp_name"):
            table_data.append([row[0], row[1]])
            count_author += 1

        print("")
        result=tabulate(table_data, headers, tablefmt=args.tablefmt.lower())
        print(result)
        show_count_author(count_author)
    elif (num == 2):
        for row in cur.execute("SELECT jp_name,en_name from author"):
            table_data.append([row[0], row[1]])
            count_author += 1

        print("")
        result=tabulate(table_data, headers, tablefmt=args.tablefmt.lower())
        print(result)
        show_count_author(count_author)
    else:
        print("入力エラー")
        sys.exit()

def update_DB(conn, cur, args):
    print("日本語名の修正 : 1, 英語名の修正 : 2, タグ追加修正 : 3")
    update_select = int(input("--> "))

    if (update_select == 1):
        update_jp_author = input("変更したい作者名を入力(英語名) --> ")
        new_jp_author = input("新しい日本語名を入力 --> ")
        update_check = input(update_jp_author + " の日本語名を " + new_jp_author + " に変更 [Y/N] : ")

        if(update_check.lower() in ["yes", "y"]):
            cur.execute("UPDATE author SET jp_name = ? WHERE en_name = ?",(new_jp_author, update_jp_author))
            conn.commit()
        else:
            print("変更キャンセル")
            sys.exit()
    elif (update_select == 2):
        update_en_author = input("変更したい作者名(日本語) --> ")
        new_en_author = input("新しい英語名を入力 --> ")
        update_check = input(update_en_author + " の英語名を " + new_en_author + " に変更 [Y/N] : ")

        if(update_check.lower() in ["yes", "y"]):
            cur.execute("UPDATE author SET en_name = ? WHERE jp_name = ?",(new_en_author, update_en_author))
            conn.commit()
        else:
            print("変更キャンセル")
            sys.exit()
    elif (update_select == 3):
        jp_name_list = list()
        count_same_author = 0
        author_id = ""

        update_tag_author_name = input("変更したい作者名を入力(日本語) --> ")
        for row in cur.execute("SELECT author_id, jp_name from author WHERE jp_name like ?", (f'%{update_tag_author_name}%',)):
            author_id = row[0]
            jp_name_list.append(row[1])
            count_same_author += 1
        if(count_same_author > 1):
            print("複数の作者がいます")
            print(jp_name_list)
            sys.exit()

        old_headers = ["タグ一覧"]
        table_data_old_tag = list()

        for row in cur.execute("SELECT tag from tag WHERE author_id = ?", (author_id,)):
            table_data_old_tag.append(row)

        if len(table_data_old_tag) < 1:
            print("タグなし")
        else:
            result=tabulate(table_data_old_tag, old_headers, tablefmt=args.tablefmt.lower())
            print("")
            print(result)
        cur.execute("DELETE FROM tag WHERE author_id = ?", (author_id,))
        conn.commit()

        new_tag = input("新しくタグを追加(全て新規入力, カンマ区切り) ---> ")

        if len(new_tag) == 0:
            sys.exit()

        array_tag = strip_tag(new_tag)

        tag_info = list()

        for i in range(len(array_tag)):
            tag_info.append((author_id, array_tag[i]))

        cur.executemany("INSERT INTO tag VALUES (?,?)",tag_info)
        conn.commit()

    else:
        print("入力エラー")
        sys.exit()

def check_same_author(conn, cur, name):

    count = 0

    for row in cur.execute("SELECT author_id from author WHERE jp_name = ?",(name,)):
        count += 1

    if count == 0:
        return False
    else:
        return True


def insert_DB(conn, cur):
    authorID = str(uuid.uuid4())

    print("\n===== 作家名登録 =====")
    jpName = input("日本語名 ---> ")
    enName = input("英語名   ---> ")

    jpName = jpName.replace("　", " ")

    book_text = input("本に関する内容(空白可) ---> ")
    if (len(jpName) < 1) or (len(enName) < 1):
        print("")
        print("**********************")
        print("名前が入力されていません")
        print("**********************")
        sys.exit()
    tags = input("著者に関するタグ(半角カンマ区切りで入力、空白可) ---> ")

    check_result = check_same_author(conn, cur, jpName)
    
    if check_result:
        print("既に存在しています")
        sys.exit()

    tag_info = list()

    check_tag = True

    if tags == "":
        check_tag = False

    tags = tags.replace(", ", ",")

    array_tag = strip_tag(tags)

    for i in range(len(array_tag)):
        tag_info.append((authorID, array_tag[i]))

    try:
        cur.execute("INSERT INTO author VALUES (?,?,?,?)",(authorID, jpName, enName, book_text))
        if check_tag:
            cur.executemany("INSERT INTO tag VALUES (?,?)",tag_info)
        conn.commit()
    except:
        print("")
        print("*********")
        print("挿入エラー")
        print("*********")
        sys.exit()

def delete_DB(conn, cur):
    delete_name = input("削除したい名前を入力 --> ")
    check_delete = input(delete_name + "の情報を削除 [Y/N] : ")
    author_id = ""
    jp_name_list = list()

    if check_delete.lower() in ["yes", "y"]:
        count_author = 0
        for row in cur.execute("SELECT author_id, jp_name from author WHERE jp_name like ?", (f'%{delete_name}%',)):
            author_id = row[0]
            jp_name_list.append(row[1])
            count_author += 1
        if(count_author > 1):
            print("複数の作者がいます")
            print(jp_name_list)
            sys.exit()
        cur.execute("DELETE FROM tag WHERE author_id = ?", (author_id,))
        cur.execute("DELETE FROM author WHERE author_id = ?",(author_id,))
        conn.commit()
        print("done")

def check_args(args):
    if not args.tablefmt.lower() in ["simple", "plain", "grid", "pipe", "orgtbl"]:
        print("コマンドライン引数に問題があります")
        print("設定可能な表示形式 : simple, plain, grid, pipe, orgtbl")
        sys.exit()

def operate_DB(conn, cur, number, args):
    if(number == 10):
        sys.exit()
    elif(number == 1):
        search_authorNameDB(conn, cur, args)
    elif(number == 2):
        search_tagDB(conn, cur, args)
    elif(number == 3):
        show_DB(conn, cur, args)
    elif(number == 4):
        update_DB(conn, cur, args)
    elif(number == 9):
        insert_DB(conn, cur)
    elif(number == -1):
        delete_DB(conn, cur)

def main():

    args = get_args()

    check_args(args)

    conn, cur = init_DB()

    number = user_select()

    operate_DB(conn, cur, number, args)

    conn.close()

if __name__ == "__main__":
    main()