# -*- coding: utf-8 -*-
from macpath import dirname

import requests
import os
import urllib.request
import shutil
import getpass
####################################################################
class App_data():
    app_id = 4414255
    redirect_url = "http://oauth.vk.com/blank.html"
    response_type = "token"
    display = "wap"
    scope = "photos,audio,video,offline"

    """
    user data
    """
    uid = 0
    access_token = ""

    request = "https://oauth.vk.com/authorize?" \
              "client_id="+str(app_id)+"&" \
              "scope="+scope+"&" \
              "redirect_url="+redirect_url+"&" \
              "display="+display+"&" \
              "response_type="+response_type

    def parse_content(self, content):
        pos_lhref = content.find("action")
        start = content.find("\"", pos_lhref+1) + 1
        stop = content.find("\"", start)
        return content[start:stop]


    def already_in_use(self, content):
        if "action" in content:
            return False
        return True


    def get_access_token(self, url):
        temp_lst = url.split("access_token=")
        if len(temp_lst) >= 2:
            self.access_token = temp_lst[1].split("&")[0]
            return 0
        else:
            return -1


####################################################################
class Loader():
    """
    Returns uid of user by username
    """
    def get_uid(self, user, token):
        parms = "uids="+user
        json = self.send_request("users.get", parms, token)
        if ("response" in json.keys()):
            return json["response"][0]["uid"]
        else:
            return -1


    """
    Returns results of request in a dictionary
    """
    def send_request(self, method, parms, token):
        req = "https://api.vk.com/method/"+str(method)+"?"+\
                  str(parms)+"&access_token="+str(token)
        result = requests.get(req)
        return result.json()


    """
    Process of authorization
    """
    def autorize(self, user, password, id):
        self.app = App_data()
        self.id = id

        # auth part #####
        s = requests.session()
        req = "https://login.vk.com/?act=login&email="+user+"&pass="+password
        s.post(req)
        r = s.get(self.app.request)
        url = ""
        content = r.content.decode("cp866")
        if not self.app.already_in_use(content):
            link = self.app.parse_content(content)
            r = s.get(link)
            url = r.url
        else:
             url = r.url
        val = self.app.get_access_token(url)
        # end auth part #####
        if val == -1:
            return -1

        self.app.uid = self.get_uid(self.id, self.app.access_token)
        if self.app.uid == -1:
            return -1

        return 0

####################################################################
class Photo_loader(Loader):
    def __init__(self):
        self.links = []
        self.aids = []


    """
    Saves links in all available albums of user
    """
    def get_all_from_albums(self, uid, token):
        parms = "uid="+str(uid)
        self.aids = []
        self.aids.append("profile")
        self.aids.append("wall")
        self.aids.append("saved")

        json = self.send_request("photos.getAlbums", parms, token)["response"]

        for elem in json:
            keys = elem.keys()
            if ("aid" in keys):
                self.aids.append(elem["aid"])

        print ("Albums count = " + str(len(self.aids)))
        self.get(uid, token)


    """
    Saves links in all albums by aid
    """
    def get(self, uid, token):
        if (len(self.aids)>0):
            self.links = []
            for elem in self.aids:
                parms = "uid="+str(uid)+"&aid="+str(elem)
                json= self.send_request("photos.get", parms, token)
                if ("response" in json.keys()): json = json["response"]
                else: continue
                for elem in json:
                    keys = elem.keys()
                    if ("src_xbig" in keys):
                        self.links.append(elem["src_xbig"])
                    elif ("src_big" in keys):
                        self.links.append(elem["src_big"])
                    elif ("src" in keys):
                        self.links.append(elem["src"])
            print ("Photos count = " + str(len(self.links)))
			
			
    """
    Saves all photos in links
    """
    def save_all(self, dirname):
        if (len(self.links)>0):
            if (os.path.isdir(dirname)):
                shutil.rmtree(dirname)
            os.mkdir(dirname)
            counter = 1
            for url in self.links:
                name = dirname+"/photo_"+str(counter)+".jpeg"
                print ("Loading " + name + "...")
                urllib.request.urlretrieve(url, name)
                counter += 1
            print ("Saving is complete.")
        else:
            print ("Nothing to save.")
            return


####################################################################
class Music_loader(Loader):
    def __init__(self):
        self.audiolist = []
        self.max_sound_count = 100
        self.work = False


    """
    Returns list of available audio of user
    """
    def get(self, uid, token):
        parms = "uid="+str(uid)
        json = self.send_request("audio.get", parms, token)
        if "response" in json.keys():
            json = json["response"]
            self.audiolist = []
            for elem in json:
                self.audiolist.append([elem["artist"], elem["title"], elem["url"], elem["duration"]])
            return 0
        else:
            return -1


    """
    Saves all tracks in links
    """
    def load_all_audio(self, dirname):
        if (len(self.audiolist) >0 ):
            if (os.path.isdir(dirname)):
                shutil.rmtree(dirname)
            os.mkdir(dirname)
            counter = 0
            for elem in self.audiolist:
                counter += 1
                artist = ""
                if (len(elem[0])>25): artist = elem[0][:25]+"..."
                else: artist = elem[0]
                title = ""
                if (len(elem[1])>25): title = elem[0][:25]+"..."
                else: title = elem[1]

                name = dirname+"/"+artist+"-"+title+".mp3"
                print ("Loading track: " + str(counter) + "...")
                urllib.request.urlretrieve(elem[2], name)
            print ("Saving is complete.")
        else:
            print ("Nothing to load.")
            return


    """
    Loads all tracks from lst;
    lst-structure: one element is list with format: 1 - track name; 2 - url
    """
    def load_tracks_from_list(self, lst, dirName, lbl):
        if os.path.exists(dirName):
            old = os.getcwd()
            os.chdir(dirName)

            cnt = 1
            size = len(lst)
            for elem in lst:
                if self.work:
                    lbl.setText("Скачиваю трек " + str(cnt) + " из " + str(size) + "...")
                    urllib.request.urlretrieve(str(elem[1]), elem[0]+".mp3")
                    cnt += 1
                else:
                    break

            lbl.setText("")
            os.chdir(old)
            return 0

        return -1


    """
    Returns list of tracks provided by audio.search method
    """
    def search_by_name(self, name, token):
        pamrs = "q="+name+"&auto_complete=1&count="+str(self.max_sound_count)
        json = self.send_request("audio.search", pamrs, token)
        if ("response" in json.keys()): json = json["response"]
        else:
            print ("Search not given results.")
            return

        for i in range(1, len(json)):
            self.audiolist.append([json[i]["artist"], json[i]["title"], json[i]["url"], json[i]["duration"]])


    """
    Returns list in format: 1 - track name; 2 - duration; 3 - url
    """
    def get_list_for_gui(self):
        if len(self.audiolist) > 0:
            lst = []
            for elem in self.audiolist:
                tmp_lst = []

                artist = ""
                if (len(elem[0])>25): artist = elem[0][:25]+"..."
                else: artist = elem[0]
                title = ""
                if (len(elem[1])>25): title = elem[0][:25]+"..."
                else: title = elem[1]
                tmp_lst.append(artist+" - " + title)

                dur = float(elem[3]) / 60.0
                tmp_lst.append("%.2f" % dur) # duration

                tmp_lst.append(elem[2]) # url
                lst.append(tmp_lst)

            return lst
        return []

####################################################################
if __name__=="__main__":
    try:
        pass

    except KeyboardInterrupt:
        print ("Normal exit")
