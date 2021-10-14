import json
import time
import os
from lib import sql
from lib import cp
from lib import message
from lib import nodered

DEBUG = False

iteration = 0

cwd = os.getcwd()
jsonconf = cwd + '/config.json'

with open(jsonconf, 'r') as datajson:
    data_2 = json.load(datajson)
APP_ID = data_2['APP_DATA']['app_id']

seconds = int(sql.q_appconfig(APP_ID)['SECONDS'])

##begin loop
while True:
    json_l_out = []


    #pull list of tracking numbers to be checked
    tp_pull = sql.q_post_tracking()
    tracking_nums = tp_pull[0]
    tracking_count = tp_pull[1]

    for i in range(tracking_count):
        json_d_out = {}

        sql_pin = tracking_nums[i]['pin']
        sql_service = tracking_nums[i]['service']
        sql_c_status = tracking_nums[i]['c_status']
        sql_p_status = tracking_nums[i]['p_status']
        sql_delivered = bool(tracking_nums[i]['delivered'])
        sql_c_city = tracking_nums[i]['c_city']
        sql_p_city = tracking_nums[i]['p_city']

        #pull tracking # details from CP website
        cp_pull = cp.cp_pull(sql_pin)
        cp_header = cp_pull[0]
        cp_detail = cp_pull[1]
        if len(cp_detail) == 0:
            a = {}
            a['status'] = cp_header['status']
            cp_detail.append(a)

        cp_pin = cp_header['pin']
        cp_service = cp_header['prod']
        cp_c_status = cp_detail[0]['status']
        try: cp_p_status = cp_detail[1]['status']
        except: cp_p_status = None
        cp_delivered = cp_header['delivered']
        try: cp_c_city = cp_detail[0]['location']
        except: cp_c_city = None
        try: cp_p_city = cp_detail[1]['location']
        except: cp_p_city = None


        if sql_service != cp_service:
            sql.u_post_tracking(sql_pin,cp_service,'SERVICE')
            if DEBUG: print('UPDATED SERVICE')

        if sql_c_status != cp_c_status:
            sql.u_post_tracking(sql_pin,cp_c_status,'C_STATUS')
            json_d_out['pin'] = sql_pin
            json_d_out['c_status'] = cp_c_status
            json_d_out['p_status'] = sql_c_status
            json_d_out['destination'] = cp_header['destination']
            json_d_out['c_city'] = cp_c_city
            if DEBUG: print('UPDATED C_STATUS')

        if sql_p_status != cp_p_status and len(cp_detail)>1:
            sql.u_post_tracking(sql_pin,cp_p_status,'P_STATUS')
            if DEBUG: print('UPDATED P_STATUS')

        if sql_delivered != cp_delivered:
            sql.u_post_tracking(sql_pin,cp_delivered,'DELIVERED')
            if DEBUG: print('UPDATED Delivered')

        if sql_c_city != cp_c_city:
            sql.u_post_tracking(sql_pin,cp_c_city,'C_CITY')
            if DEBUG: print('UPDATED Current City')

        if sql_p_city != cp_p_city and len(cp_detail)>1 and cp_p_city != cp_c_city:
            sql.u_post_tracking(sql_pin,cp_p_city,'P_CITY')
            if DEBUG: print('UPDATED Previous City')

        if json_d_out:
            json_l_out.append(json_d_out.copy())

        if DEBUG:
            print("")
            print(f"CP Header: {cp_header}")
            print(f"CP Detail: {cp_detail}")

    if json_l_out:
        #print(json_l_out)
        nr_msg = message.status(json_l_out)
        #print(nr_msg)
        nodered.nr_msg_out(nr_msg)
        

    if DEBUG: print(f"SQL Pull: {tracking_nums}")
    print(iteration)
    iteration += 1
    time.sleep(seconds)
