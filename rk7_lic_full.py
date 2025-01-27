import pywhatkit
import pyautogui
import requests
import time
import fake_useragent
import json
from datetime import date, timedelta, datetime
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import smtplib
import datetime as dt
import os

# commit


url = 'https://l.ucs.ru/ls5api/api/Auth/Login'
url_object = 'https://l.ucs.ru/ls5api/api/Object/GetObjectById'
url_objects = 'https://l.ucs.ru/ls5api/api/Object/GetObjectList'
url_object_order = 'https://l.ucs.ru/ls5api/api/Order/GetOrdersByObjectIdList'
url_application = 'https://l.ucs.ru/ls5api/api/Order/GetOrderByIdRequest'
url_file = 'https://l.ucs.ru/ls5api/api/Order/Generate'
url_end_licence = "https://l.ucs.ru/ls5api/api/Reports/GetObjectWithLicenseEndForReport"
name_file = ''
file_url =''
list_id_rk= []
login = 'lar@solardsoft.ru'
password = '1q2w3e4R!'
password_email = "mart8928716"
send_from = "mva@solardsoft.ru"
send_to = "mva@solardsoft.ru"
today = datetime.now()
dateEnd = today + timedelta(days=15)
# create message object instance 
msg = MIMEMultipart()
# setup the parameters of the message 
subject = f"rkeeepr {today}"
msg['Subject'] = subject
part = MIMEBase('application', "octet-stream")

part.add_header('Content-Disposition', 'attachment; filename="PyWhatKit_DB.txt"')
server = smtplib.SMTP('smtp.timeweb.ru:587')
server.login(send_from, password_email)
user = fake_useragent.UserAgent().random
session = requests.session()
try:
    os.remove("PyWhatKit_DB.txt")
except:
    print("Файл остутствует")

header = {
    "user-agent": user,
}

header_file = {
    "user-agent": user,
    "Content-Type": "application/octet-stream"
}


data_login =  {"RequestObject": {"login": login,
    "pass": password,
    'systemVersion': "v5"}
    }


def main():
    global SessionId, langId
    response = session.post(url, json=data_login, headers=header).json()
    SessionId = response['value']['guid']
    langId = response['value']['langId']
    data_objects_license = {"RequestObject": 
                {'PageNum': 1,
                'PageSize': 500, 
                'dateEnd': str(dateEnd),
                'dateStart': str(today),
                'dealerId': "a6cd6353-cebf-4450-aef5-030cd60aec46",
                'SortOrder': "asc"},
                'SessionId': SessionId,
                'langId': langId}
    response_objects = session.post(url_end_licence, json=data_objects_license, headers=header).json()
    source = response_objects['value']['source']
    list_expiration_of_licenses(source)
    send_log()

def list_expiration_of_licenses(source):
    for s in source:
        id_rk = s['objectId']
        data_object = {"RequestObject": {'PageNum': 1,
                'PageSize': 500, 
                'SortOrder': "asc",
                'objectId': id_rk},
                'SessionId': SessionId,
                'langId': langId}
        response_object = session.post(url_object_order, json=data_object, headers=header).json()
        source_task = response_object['value']['source']
        name_object, number = inforamation_object(id_rk)
        check_and_create_list_application(source_task, name_object, number)

def check_and_create_list_application(source_task, name_object, number):
    for t in source_task:
        num_order = t['num']
        create_order = str(t['createdDate']).split("T")[0]
        create_order = datetime.strptime(create_order, '%Y-%m-%d') + timedelta(days=14)
        check = today < create_order
        list_application = []
        if check:
            if t['paymentStatusName'] == "Не оплачена" and t["statusName"] == "Выставлен счет":
                application = t['id']
                list_application.append(application)
                links_file = creat_list_order(list_application, num_order)
                send_chek(links_file, name_object, number)
            elif t['paymentStatusName'] == "Полностью оплачена":
                print(f'Счет #{num_order} для заведния {name_object} не прошел проверку по оплате')
        else:
            print(f'Счет #{num_order} для заведния {name_object} не прошел проверку по времени')
            break    


def creat_list_order(list_application, num_order):
    if len(list_application) > 1:
        for application in list_application:
            data_application = {"RequestObject": 
                                        {'id': application,
                                            'isReadonly': True,
                                            'PageSize': 500},
                                            'SessionId': SessionId,
                                            'langId': langId}
            response_application = session.post(url_application, json=data_application, headers=header).json()
            response_files = response_application['value']['files']
            link_file = creat_links_order(response_files, num_order)
            if links_file != '':
                links_file = links_file + ' ' + link_file
            else:
                links_file = link_file
        return links_file
    else:
        for application in list_application:
            data_application = {"RequestObject": 
                                        {'id': application,
                                            'isReadonly': True,
                                            'PageSize': 500},
                                            'SessionId': SessionId,
                                            'langId': langId}
            response_application = session.post(url_application, json=data_application, headers=header).json()
            response_files = response_application['value']['files']
            link_file = creat_links_order(response_files, num_order)
            return link_file
            
            

def creat_links_order(response_files, num_order):
    try:
        for idfile in response_files:
            idfile = idfile['id']
            link_file = f"https://l.ucs.ru/ls5api/api/Order/Generate?id={idfile}"
            return link_file
    except:
        print(f'В заяввке {num_order} отсуттвует счет или его нет')



def inforamation_object(id_rk):
    data_object = {"RequestObject":  id_rk,
                                    'SessionId': SessionId,
                                    'langId': langId}
    response_object = session.post(url_object, json=data_object, headers=header).json()
    number = str(response_object['value']['phone'])
    if number.startswith("8"):
        number = number.strip().replace('+', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        number = number[:0] + "7" + number[1:]
    elif number.startswith("+7"):
        number = number.strip().replace('+', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
    name_object = response_object['value']['name'] + " " + response_object['value']['code']
    return name_object, number

def send_chek(links_file, name_object, number):
    file_url = (f'Здравствуйте, {name_object}! Напоминаю Вам об оплате услуг rkeeper.\n'
                'Просьба оплатить счёт в ближайшее время во избежании блокировки программы.\n'
                'Счёт находится по ссылке ниже.\n'
                f'*сслыка(и) на счета:* {links_file}\n'
                'Просьба отправить платёжное поручение после оплаты на почту pp@solardsoft.ru. Это ускорит процесс активации лицензий.\n'
                'Если счёт уже оплачен, по возможности, отправьте платёжное поручение на почту.\n'
                '_*Платёжные поручения, которые будут отправлены в ответном сообщении в WhatsApp не будут рассматриваться.*_\n'
                f'Если вы получили это сообщение ошибочно, просьба написать на почту mva@solardsoft.ru с указанием счёта и номера телефона.  номер телефона: {name_object}, *сслыка(и) на счета:* {links_file}\n')
    for_email = f'Нет номера телефона! \n\n\n{file_url}'
    if number.startswith('7'):
        pywhatkit.sendwhatmsg_instantly(phone_no=f'+{number}', message=file_url, tab_close=True)
        time.sleep(60)
        pyautogui.press("enter")
        pyautogui.press("сtrl+f4")
        print(f'Отправлено клиенту {name_object}')
    else:   
        message=for_email
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(send_from, send_to, msg.as_string())
        print("Счет по {name_object} отправлен на почту mva@solardsoft.ru")


def send_log():
    part.set_payload(open("PyWhatKit_DB.txt", "rb").read())
    encoders.encode_base64(part)
    msg.attach(part)
    server.sendmail(send_from, send_to, msg.as_string())
    server.quit()
    print("Лог отрпавлен mva@solardsoft.ru")
                               
if __name__ == '__main__':
    main()