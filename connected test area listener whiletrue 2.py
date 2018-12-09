# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 17:57:17 2018

@author: jen yang
"""
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import threading
from queue import Queue

cred = credentials.Certificate("C:/Users/jen yang/Downloads/eatwhere-3090c-firebase-adminsdk-cokd5-5ed99f0c43.json")
firebase_admin.initialize_app(cred, {    'databaseURL': 'https://eatwhere-3090c.firebaseio.com/'})

import ast
import numpy
import geopy.distance



from math import sin, cos, sqrt, atan2, radians

def all_shops_in_range(max_dist,pin_coords,shopdict):   
    potential_shops = []
    #print(pin_coords)
    lat1 = pin_coords['latitude']
    lon1 = pin_coords['longitude']
    #print('parsing shops')
    for shop in shopdict:  
        #print(shop)
        actualshop = ast.literal_eval(shop)
        #print(type(actualshop))
        shopnem = list(actualshop.keys())[0]
        #print(shopnem)
        #print(actualshop)
        shop_lat = actualshop[shopnem]["location"]["latitude"]
        shop_long = actualshop[shopnem]["location"]["longitude"]
        shopcoords = (shop_lat,shop_long)
        point_coords = (lat1,lon1)
        distance = geopy.distance.distance(shopcoords, point_coords).m
        print("Result:",shopnem, distance)
        if  distance <= max_dist:
            potential_shops.append(actualshop)
            print("shop in range")
    return potential_shops

def price_filter(D,potential_shops):
    global_list = []
    counter = 1
    for i in D:
        ava_shops = []
        ava_cuisines = []
        print(counter,i)
        counter+=1
        ahem = list(i.values())
        pricecollection = (list(ahem[0]["priceList"].values()))
        maxlst = []
        minlst = []
        for h in pricecollection:
            if type(h)==dict:
                maxlst.append(h['maxPrice'])
                minlst.append(h['minPrice'])
        maxlst.sort()
        minlst.sort()
        if ((len(maxlst))%2 == 0):
            print("even number")
            print(len(maxlst))
            a = len(maxlst)/2
            a= int(a)
            max_median = (maxlst[a-1] + maxlst[a])/2
            print(max_median)
        else:
            print("odd number")
            a = int((len(maxlst)-1)/2 )
            if a == 0.5:
                print(a)
                a = 0
                max_median = maxlst[a]
            else:
                max_median = maxlst[a]
        minprice = minlst[0]
        #print((list(i.keys())[0],'minprice = ',minprice, 'max_median = ', max_median))
        pricedestination = db.reference("Sessions/"+list(i.keys())[0]+"/"+"priceList")
        pricedestination.update({"aggregated prices":(('minprice = ',minprice),('max_median = ', max_median))})
        
        for shop in potential_shops:
            print("yeet")
            print(shop)
            print(type(shop))
            print("preeent")
            shop_name = list(shop.keys())[0]
            print(shop_name)
            shop_range = shop[shop_name]["price"]
            yeet = shop_range.split("-")
            shop_avg = (float(yeet[1])+float(yeet[0]))/2
            print(shop_avg)
            if minprice<=shop_avg<=max_median:
                print("SHOP FOUND",minprice, max_median)
                ava_shops.append(shop)
                print(shop[shop_name])
                ava_cuisines.append(shop[shop_name]["cuisine"])
            else:
                print("SHOP NOT IN RANGE",minprice, max_median)
        avacuisines = list(set(ava_cuisines))
        signaldestination = db.reference("Sessions/"+list(i.keys())[0])
        signaldestination.update({"signal":{"go_to_cuisine":True,"go_to_result":False,"start":True}})
        #signaldestination.update({"go_to_cuisines" : True})
        ava_cuisinedestination = db.reference("Sessions/"+list(i.keys())[0])
        ava_cuisinedestination.update({"avaCuisineList":avacuisines})
        ava_shops.insert(0,list(i.keys())[0])
        print("shopslist>>>>>",ava_shops)
        global_list.append(ava_shops)
    return (global_list,avacuisines)

def cuisine_filter(alluserprefs,glob_list):
    print("alluserprefs", alluserprefs)
    for session in alluserprefs:
        print("session",session)
        session_preferences = []
        session_name = list(alluserprefs.keys())[0]
        print("session_name", session_name)
        for user in list(alluserprefs[session_name]["cuisineList"].keys()):
            print(user)
            if user != str(0):
                print(alluserprefs[session_name]["cuisineList"][user])
                for cooisine in (list(alluserprefs[session_name]["cuisineList"][user].keys())):
                    print(cooisine)
                    print(alluserprefs[session_name]["cuisineList"][user][cooisine])
                    omegalul = alluserprefs[session_name]["cuisineList"][user][cooisine]
                    if omegalul == True:
                        session_preferences.append(cooisine)
            else:
                print("node 0; ignoring node 0...")
        print(session_preferences)
        valuedicti = {}
        collective = list(set(session_preferences))
        for foodtaip in collective:
            multiplier = session_preferences.count(foodtaip)
            valuedicti[foodtaip] = multiplier
        final_list =  []
        bigL = []
        print("oY", glob_list)
        for session in glob_list:
            for i in range (1, len(session)-1,1):
                session_name = session[0]
                for item in session:
                    if type(item)!= str:
                        score = 1
                        shop_nemu = list(item.keys())[0]
                        print("watisurnem", shop_nemu)
                        print(item)
                        shop_cuisine = item[shop_nemu]["cuisine"]
                        print("shop_cuisine",shop_cuisine)
                        if type(shop_cuisine) == list:
                            for damnitferrell in shop_cuisine:
                                print("damnit ferrell...",damnitferrell)
                                if damnitferrell in valuedicti:
                                    print("morescore!")
                                    score = score * valuedicti[damnitferrell]
                                    print("score", score)
                                else:
                                    print("this shouldnt be happunin")
                        else:
                            if shop_cuisine in valuedicti:
                                print("morescore!")
                                score = score * valuedicti[shop_cuisine]
                                print("score",score)
                        final_list.append((score,item))
                final_list.sort(key=lambda x:x[0],reverse = True)
        
                    
# =============================================================================
#             for i in range (1,len(session[1])-1,1):
#                 print(session[i])
#                 shop_name = list(session[i].keys())[0]
#                 shop_category = (session[i])[shop_name]['cuisine']
#                 truthlist = []
#                 if type(shop_category) == list:
#                     for j in shop_category:
#                         if j not in session_preferences:
#                             print(j,session_preferences)
#                             truthlist.append(False)
#                         else:
#                             truthlist.append(True)
#                         print(truthlist)
#                         if False not in truthlist:
#                             final_list.append(i)
#                 else:
#                     print('yo what',shop_category)
#                     if shop_category not in session_preferences:
#                         print(j,session_preferences)
#                         truthlist.append(False)
#                     else:
#                         truthlist.append(True) 
#                     if False not in truthlist:
#                         final_list.append(session[i])
# =============================================================================
        print("check step," ,final_list)
#        for h in final_list:
#            tempname = (list(h.keys())[0])
#            ahah = h[tempname]
#            ahah["name"] = tempname
#            bigL.append(ahah)
#        print(session_name)
        finaldestination = db.reference("Sessions/"+session_name)
        finaldestination.update({"resultList":final_list})
        #finaldestination.update({"resultList":bigL})
        signaldestination = db.reference("Sessions/"+session_name)
        signaldestination.update({"signal":{"go_to_cuisine":True,"go_to_result":True,"start":True}})
    return final_list
    

def listener(d1,d2):
    previousSessions = set(d1.keys())
    currentSessions = set(d2.keys())
    newSessions = []
    removedSessions = []
    price1 = []
    price2 = []
    cuisines1 = []
    cuisines2 = []
    signal1 =[]
    signal2 = []    
    users1 = []
    users2 = []
    status1= []
    status2 = []
    updated_statuses = []
    updated_priceLists = []
    updated_cuisineLists = []
    updated_signalLists = []
    radiusgroup = {}
    updated_sessions = []
    print(previousSessions)
    print(currentSessions)
    for i in previousSessions:
        cuisinestemplist1 = []
        pricetemplist1 = []
        signaltemplist1 = []
        userstemplist1 = []
        print("previousSessions,",i)
        if i not in currentSessions:
            removedSessions.append((i,d1[i]))
        #print(d1[i])
        for j in d1[i]:
            #print (j)
            if j == "cuisineList":
#                print("entered",j)
#                print (j,d1[i][j] )
                cuisinestemplist1.append(d1[i][j])
            elif j == "priceList":
#                print("entered",j)
#                print(i,j,d1[i][j])
                pricetemplist1.append(d1[i][j])
#                print(pricetemplist1)
            elif j == "signal":
#                print("entered",j)
#                print (j,d1[i][j] )
                signaltemplist1.append(d1[i][j])
            elif j == "users":
#                print("entered",j)
#                print (j,d1[i][j] )
                userstemplist1.append(d1[i][j])
            elif j == "status":
                session_status = d1[i][j]
                status1.append((i,{"status":session_status}))
#        print("CHECKING", cuisinestemplist1)
        if cuisinestemplist1 != []:
            cuisines1.append((i,{"cuisineList":cuisinestemplist1[0]}))
        else:
            cuisines1.append((i,{"cuisineList":["none"]}))
        if pricetemplist1 != []:
            price1.append((i,{"priceList":pricetemplist1[0]}))
        else:
            price1.append((i,{"priceList":["none"]}))
        if signaltemplist1 != []:
            signal1.append((i,{"signal":signaltemplist1[0]}))
        else:
            signal1.append((i,{"signal":["none"]}))
        users1.append((i,{"users":userstemplist1[0]}))
    print("done with previousSessions")
    for I in currentSessions:
        cuisinestemplist2 = []
        pricetemplist2 = []
        signaltemplist2 = []
        userstemplist2 = []
#        print("currentSessions,",I)
        #print("currentSessions,",I)
        if i not in previousSessions:
            newSessions.append((I,d2[I]))
        for j in d2[I]:
            #print (j)
            if j == "cuisineList":
                cuisinestemplist2.append(d2[I][j])
            elif j == "priceList":
                pricetemplist2.append(d2[I][j])
            elif j == "signal":
                signaltemplist2.append(d2[I][j])
            elif j == "users":
                userstemplist2.append(d2[I][j])
            elif j == "status":
                session_status = d2[I][j]
                status2.append((I,{"status":session_status}))
            elif j == "radius":
#                print(print("entered",j))
#                print (j,d1[i][j])
                session_radius = j,d2[I][j]
                radiusgroup[I] = session_radius
#        current_prices = list(zip(pricetemplist2[0].keys(),pricetemplist2[0].values()))
        if cuisinestemplist2 != []:
            cuisines2.append((I,{"cuisineList":cuisinestemplist2[0]}))
        else:
            cuisines2.append((I,{"cuisineList":["none"]}))
        if pricetemplist1 != []:
            price2.append((I,{"priceList":pricetemplist2[0]}))
        else:
            price2.append((I,{"priceList":["none"]}))
        if signaltemplist1 != []:
            signal2.append((I,{"signal":signaltemplist2[0]}))
        else:
            signal2.append((I,{"signal":["none"]}))
        users2.append((I,{"users":userstemplist2[0]}))
    print("done with currentSessions")
#    print("checking price 1")
    for h in price2:
        for k in price1:
#            print("checking price 2")
#            print(h,k)
            if h[0] == k[0]:
#                print("yes", h[0],k[0])
                if h[1] == k[1]:
                    pass
#                    print("no change in price")
                else:
#                    print("got change in price")
                    updated_priceLists.append({h[0]:h[1]})
#            else:
#                print("no," , h[0],k[0])
#    print("checking cuisines 1")
    for h in cuisines2:
        for k in cuisines1:
#            print("checking cuisines 2")
#            print(h,k)
            if h[0] == k[0]:
#                print("yes", h[0],k[0])
#                print("there should be one more check here for cuisines")
                if h[1] == k[1]:
                    pass
#                    print("no change in prefs")
                else:
#                    print("got change in prefs")
                    updated_cuisineLists.append({h[0]:h[1]})
#            else:
#                print("no," , h[0],k[0])
                
#    print("checking signals 1")
    for h in signal2:
        for k in signal1:
#            print("checking signals 2")
#            print(h,k)
            if h[0] == k[0]:
#                print("yes," , h[0],k[0])
                if h[1] == k[1]:
                    pass
#                   print("no change in signals")
                else:
#                    print("got change in signals")
                    updated_signalLists.append({h[0]:h[1]})
#            else:
#                print("no,", h[0],k[0])
    for h in status2:
#        print(h)
        session_name = h[0]
        for k in status1:
           # print("checker")
           # print(h,k)
           # print(h[1],k[1])
            if h[0]==k[0]:
           #     print("this session")
                if h[1]["status"] == k[1]["status"]:
           #             print("no updates")
                        pass
                else:
                        print("updated status")
                        updated_statuses.append((session_name,{"status":h[1]["status"]}))
    return newSessions,removedSessions,updated_priceLists, updated_cuisineLists, updated_signalLists,users2,updated_statuses,radiusgroup,updated_sessions

mainref = db.reference('Sessions')
shopsDB = [line.rstrip('\n') for line in open('C:/Users/jen yang/Downloads/testdb.txt')]
print(shopsDB)

ongoing_sessions = {}
try:
    counter = 0
    olddb = mainref.get()
    print(olddb)

    print("start")
    while True:         
        print(counter)
        counter += 1
        print(counter)
        newdb = mainref.get()
#        print("database: this >>>> {}".format(newdb))
#        print("previous database: this >>>> {}".format(olddb))
        if newdb == olddb:
            print("idleidle")
            pass    
        else:
            print("new!")
            newSessions,removedSessions,updated_priceLists, updated_cuisineLists, updated_signalsLists,users2,updated_statuses,radiusgroup,updated_sessions = listener(olddb,newdb)
            olddb = newdb  #updates old list
            for i in newSessions,removedSessions,updated_priceLists, updated_cuisineLists, updated_signalsLists,users2,updated_statuses,radiusgroup,updated_sessions:
                print(i)
#            Q1.put(removedSessions)
            for j in updated_statuses:
                print("UPDATED STATUS",j)
                session_nem = j[0]
                if j[1]["status"] == "open":
                    max_dist = radiusgroup[session_nem][1]
                    pin_coords = newdb[session_nem]["location"]
                    potential_shops = all_shops_in_range(max_dist,pin_coords,shopsDB)
                    ongoing_sessions[j[0]]=potential_shops
                    print("ongoing_sessions",ongoing_sessions)
                    print("radius assigning complete")
                    sessionresultsreference = db.reference("Sessions/"+session_nem)
                    sessionresultsreference.update({"resultList":potential_shops})
                    ongoing_sessions[session_nem] = potential_shops
            for j in updated_priceLists:
                updated_session_name = list(j.keys())[0]
                for k in users2:
                    if k[0] == updated_session_name:
                        those_users_dict = k[1]
                inter1 = list(those_users_dict.values())
                print(len(inter1[0]))
                if (len(list(j[updated_session_name]["priceList"]))-1) == len(inter1[0]):
                    print("all price!, number users:",len(inter1[0].values()))
                    print("all price!, users:",inter1[0].values())
                    print("all price!, number price:",len(list(j[updated_session_name]["priceList"])))
                    print("BLEH",list(j[updated_session_name]["priceList"]))
                    print(updated_priceLists)
                    print("ongoing_sessions",ongoing_sessions)
                    glob_shops,ava_cuisines = price_filter(updated_priceLists,ongoing_sessions[updated_session_name])
                    if glob_shops == {}:
                        glob_shops = {0:0}
                    if ava_cuisines == {}:
                        ava_cuisines = {0:0}
                    print("glob_shops", glob_shops)
                    print("ava_cuisines",ava_cuisines)
            for k in updated_cuisineLists:
                updated_session_name = list(k.keys())[0]
                for f in users2:
                    if f[0] == updated_session_name:
                        those_users_dict = f[1]
                inter2 = list(those_users_dict.values())
                if (len(list(k[updated_session_name]["cuisineList"]))-1) == len(inter2[0]):
                    print("all prefs!, number of users:", (len(list(k[updated_session_name]["cuisineList"]))))
                    final_results = cuisine_filter(k,glob_shops)
                    print("final_results",final_results)
                 
#            Q3.put(updated_cuisineLists)
#==============================================================================
except (KeyboardInterrupt,SystemExit):
    print ("killing workers")
    #for i in range (num_price_checker_threads):         
        #Q2.put(None)
    print ("workers killed; killing server")
    raise