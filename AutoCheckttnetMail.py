# coding=utf8
# #################
# 作者: ts6075
# 開始日期: 20190309
# 程式目的: 爬取文筆信箱是否有新Email
# 版本記錄
# v1.0 - 20190309 - 初版
# #################
# #################
# # 爬蟲所用       #
# #################
import datetime                # 日期
import requests                # 網頁呼叫
from bs4 import BeautifulSoup  # 爬取網頁
import os                      # 寫檔用
import shutil                  # 刪除資料夾


# #################
# # 寫入txt       #
# fileName -------- 檔名
# msg ------------- 寫入文字
# mode ------------ 寫入模式(w:覆寫檔案, a:接續寫入)
# #################
def writeTxt(fileName, msg, mode):
    if (not os.path.exists('./文筆')):    # 判斷資料夾是否存在
        os.makedirs('./文筆')             # Create folder

    # #################
    # # 開檔,設定編碼,寫檔,關檔 #
    # #################
    f = open('./文筆/' + fileName, mode)  # Create and Open file
    f.write(msg)                         # Write file
    f.close()                            # Close file
    return


# ################################## 主程式 從此開始#################
# #################
# # 取得csrf_token #
# #################
Login_Get_Url = 'https://tw.ttnet.net/login.html'      # login網址,取得csrf_token用
ses = requests.Session()                               # 建立Session
res = ses.get(Login_Get_Url)
soup = BeautifulSoup(res.text, 'lxml')                 # 取得html並存入soup
csrf_token = soup.select_one('input[name=csrf_token]').get('value')

# #################
# # 登入帳號設定   #
# #################
Login_Post_Url = 'https://tw.ttnet.net/account/login'  # login網址,登入Post用
headers = {'User-Agent': 'Mozilla/5.0'}
FormData = {
    'csrf_token': csrf_token,
    'username': '輸入帳號',
    'password': '輸入密碼',
    'validateShow': '0',
    'nextUrl': 'https://tw.ttnet.net/mails/inbox'
}

# #################
# # 登入帳號       #
# #################
res = ses.post(Login_Post_Url, data=FormData, headers=headers)
headers = res.request.headers                 # 登入並取得新的headers

# #################
# # 找出收件匣第一頁所有Email(前20封) #
# #################
soup = BeautifulSoup(res.text, 'lxml')        # 取得html並存入soup
list_search = soup.select('[id=ps_chks] tr')  # 取得Email清單

# #################
# # Log記錄       #
# #################
t_today = datetime.date.today()                              # 今天日期
print('程式執行日期:' + str(t_today))
writeTxt('文筆信件.txt', '-----------', 'a')
writeTxt('文筆信件.txt', '程式執行日期:' + str(t_today), 'a')
writeTxt('文筆信件.txt', '-----------\n', 'a')

# #################
# # 解析每封Email  #
# #################
newEmail = bool(0)    # 記錄是否有新信件, True:有, False:無
for ele in list_search:
    # #################
    # # 解析每個欄位   #
    # 0:checkbox, 1:Re Mail, 2:主題, 3:寄件者, 4:國家/地區, 5:日期, 6:標記
    # #################
    ele = ele.select('td')

    # #################
    # # 只顯示指定日期以後Email #
    # #################
    ele_Date = ele[5].text                                    # 取得Email日期
    ele_Date = ele_Date.replace(' ', '').replace('\r\n', '')  # 去除空白
    ele_Date = ele_Date.split('-')                            # 切成 0:年, 1:月, 2:日
    ele_Year = int(ele_Date[0])                               # 取得 年

    if (ele_Year >= 2019):                                    # 只讀取2019年以後
        for e in ele[2:6]:                                    # 2 <= 讀取 < 6
            e = e.text.replace(' ', '').replace('\r', '').replace('\n', '')
            print(e)
            writeTxt('文筆信件.txt', e + '\t', 'a')
        writeTxt('文筆信件.txt', '\n', 'a')
        newEmail = bool(1)                                    # 表示有新信件

# #################
# # 若本次執行沒有新Email,就刪除整個資料夾 #
# #################
if (not newEmail):
    if (os.path.exists('./文筆')):  # 判斷資料夾是否存在
        shutil.rmtree('./文筆')     # Delete folder
        print('\n本次執行沒有新的Email')
