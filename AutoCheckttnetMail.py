# coding=utf8
# #################
# 作者: ts6075
# 開始日期: 20190309
# 程式目的: 爬取文筆信箱是否有新Email
# 版本記錄
# v1.0 - 20190309 - 初版
# v1.1 - 20190312 - 修正寫檔編碼問題
# v1.2 - 20190426 - 修改為只讀取未讀Email
# v1.3 - 20190427 - 加入LineNotify功能
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
    # 預設是utf-8, 但open的encoding會因平台不同而不同
    # 所以建議還是加一下 encoding='utf8'
    # #################
    f = open('./文筆/' + fileName, mode, encoding='utf8')  # Create and Open file
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
logMsg = ''           # 記錄待寫入之訊息 (記錄Email資訊)
newEmail = bool(0)    # 記錄是否有新信件, True:有, False:無
for ele in list_search:
    # #################
    # # 解析每個欄位   #
    # 0:checkbox, 1:Re Mail, 2:主題, 3:寄件者, 4:國家/地區, 5:日期, 6:標記
    # #################
    ele = ele.select('td')

    # #################
    # # 只顯示未讀Email #
    # mail1: 未讀
    # mail2: 已讀
    # mail3: 已回覆
    # #################
    ele_status = ele[1].select_one('img').get('src')          # 取得Email狀態
    ele_status = ele_status.split('/')[-1]                    # 取得img檔名, 用/切割路徑, 取最後一個元素即為檔名

    if (ele_status == "mail1.gif"):                           # 只讀取未讀Email
        for e in ele[2:6]:                                    # 2 <= 讀取 < 6
            e = e.text.replace(' ', '').replace('\r', '').replace('\n', '')
            logMsg += e + '\t'
        logMsg += '\n'
        newEmail = bool(1)                                    # 表示有新信件

# #################
# # 若本次執行沒有新Email,就刪除整個資料夾 #
# #################
if (not newEmail):
    if (os.path.exists('./文筆')):  # 判斷資料夾是否存在
        shutil.rmtree('./文筆')     # Delete folder
        print('\n本次執行沒有新的Email')
else:
    print(logMsg)
    writeTxt('文筆信件.txt', logMsg, 'a')                          # 寫入查詢結果

    # #################
    # # 發送LineNotify訊息 #
    # #################
    notify_Post_Url = 'https://notify-api.line.me/api/notify'      # Line API網址
    notify_token = 'Bearer myToken'                                # 文筆群組
    lineMsg = '\n' + '通知：' + str(t_today) + '有新郵件！\n'
    lineMsg += '==========\n' + logMsg
    headers = {'Authorization': notify_token}
    FormData = {'message': lineMsg}
    res = requests.post(notify_Post_Url, headers=headers, params=FormData)
