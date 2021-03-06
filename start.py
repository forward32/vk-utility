# -*- coding: utf-8 -*-
import sys
import vk
from PyQt4 import QtCore, QtGui
import threading
from time import sleep
import socket
import webbrowser
import os
import shutil
#######################################################################################################################
#######################################################################################################################
WORK = True # flag for thread authorization
STATUS = -1 # authorization status
PREVIEW_FOLDER = ".preview"
def static_auth_thread(loader, user, pass_):
    global WORK
    global STATUS
    WORK = True
    STATUS = loader.autorize(user, pass_)
    WORK = False
#######################################################################################################################
#######################################################################################################################
class AuthForm(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("Авторизация")
        self.setWindowIcon(QtGui.QIcon("icon.jpg"))

        # set form to center of screen
        geom = QtGui.QApplication.desktop().screenGeometry()
        x = (geom.width()-self.width()/2) / 2
        y = (geom.height()-self.height()/2) / 2
        self.move(x,y)

        lbl_login = QtGui.QLabel("Логин:")
        lbl_pass = QtGui.QLabel("Пароль:")
        edt_login = QtGui.QLineEdit()
        edt_pass = QtGui.QLineEdit()
        edt_pass.setEchoMode(QtGui.QLineEdit.Password)
        btn_ok = QtGui.QPushButton("Принять")
        btn_cancel = QtGui.QPushButton("Отменить")
        self.lbl_progress = QtGui.QLabel()

        grid = QtGui.QGridLayout()
        grid.addWidget(lbl_login, 0, 0)
        grid.addWidget(edt_login, 0, 1)
        grid.addWidget(lbl_pass, 1, 0)
        grid.addWidget(edt_pass, 1, 1)
        grid.addWidget(btn_ok, 2, 0)
        grid.addWidget(btn_cancel, 2, 1)

        layout_progress = QtGui.QVBoxLayout(self)
        layout_progress.addLayout(grid)
        layout_progress.addWidget(self.lbl_progress)

        btn_ok.clicked.connect(lambda:self.to_ok_clicked(edt_login.text(), edt_pass.text()))
        btn_cancel.clicked.connect(self.to_cancel_clicked)

    def check_connection(self):
        try:
            socket.gethostbyaddr('www.yandex.ru')
        except socket.gaierror:
            return False
        return True

    def to_ok_clicked(self, user_name, pass_name):
        if not self.check_connection():
            QtGui.QMessageBox.warning(self, "Предупреждение", "Отсутствует соединение с интернетом.")
            return
        
        if user_name != "" and pass_name != "":
            loader = vk.Loader()
            thr = threading.Thread(target=static_auth_thread, args=(loader, user_name, pass_name))
            thr.start()
            # wait while authorize
            while WORK==True:
                for i in range(5):
                    QtGui.QApplication.processEvents()
                    self.lbl_progress.setText("Авторизуюсь" + '.'*i)
                    sleep(0.4)
					
            if STATUS == -1:
                QtGui.QMessageBox.warning(self, "Ошибка авторизации", ("Неверный ввод данных.\n"
                                                 "Проверьте правильность ввода данных и повторите попытку."))
                self.lbl_progress.setText("")
                return
				
            auth.close()
            mainForm.musicForm.loader = loader
            mainForm.searchForm.loader = loader
            mainForm.imageForm.loader = loader
            mainForm.musicForm.edt_page.setText(loader.id)
            mainForm.imageForm.edt_page.setText(loader.id)
            mainForm.musicForm.set_music_content()
            mainForm.imageForm.set_image_content()
            mainForm.show()
        else:
            QtGui.QMessageBox.warning(self, "Неверный ввод", "Все поля должны быть заполнены.")

    def to_cancel_clicked(self):
        sys.exit(0)
#######################################################################################################################
#######################################################################################################################
class OneItem(QtGui.QWidget):
    def __init__(self, track_name, duration, url):
        QtGui.QWidget.__init__(self)
        self.track = track_name
        self.url = url

        self.btn_play = QtGui.QPushButton(self)
        self.btn_play.setGeometry(0,0,50,30)
        pix = QtGui.QPixmap("play.png")
        scalled_pix = pix.scaled(self.btn_play.width(), self.btn_play.height(), QtCore.Qt.KeepAspectRatio)
        icon = QtGui.QIcon(pix)
        self.btn_play.setIcon(icon)
        self.btn_play.clicked.connect(self.play_track_in_browser)

        lbl_name = QtGui.QLabel(self)
        lbl_name.setText(self.track)
        lbl_name.setGeometry(80,0,350,30)

        lbl_duration = QtGui.QLabel(self)
        lbl_duration.setText(duration)
        lbl_duration.setGeometry(450,0,40,30)

        self.chbox = QtGui.QCheckBox(self)
        self.chbox.setGeometry(510,0,40,30)

    def play_track_in_browser(self):
        if self.url != "":
            webbrowser.open(self.url)
#######################################################################################################################
#######################################################################################################################
class OnePictureItem(QtGui.QWidget):
    def __init__(self, img_url, img_path):
        QtGui.QWidget.__init__(self)
        self.url = img_url

        lbl_preview = QtGui.QLabel(self)
        lbl_preview.setGeometry(0,0,100,100)
        pix = QtGui.QPixmap(img_path)
        scalled_pix = pix.scaled(lbl_preview.width(), lbl_preview.height())
        lbl_preview.setPixmap(scalled_pix)

        lbl_line = QtGui.QLabel(self)
        lbl_line.setText("-----------------------------------------------------------------------")
        lbl_line.setGeometry(100,40,300,20)

        self.btn_show = QtGui.QPushButton(self)
        self.btn_show.setGeometry(400,30,60,40)
        pix = QtGui.QPixmap("show.png")
        scalled_pix = pix.scaled(self.btn_show.width(), self.btn_show.height(), QtCore.Qt.KeepAspectRatio)
        icon = QtGui.QIcon(pix)
        self.btn_show.setIcon(icon)
        self.btn_show.clicked.connect(self.show_img_in_browser)

        self.chbox = QtGui.QCheckBox(self)
        self.chbox.setGeometry(470,30,40,40)

    def show_img_in_browser(self):
        if self.url != "":
            webbrowser.open(self.url)
#######################################################################################################################
#######################################################################################################################
class UserMusic(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.track_dict = {}
        self.music = vk.Music_loader()
        self.loader = vk.Loader()
        self.setGeometry(600,300,600,500)
        self.lbl_progress = QtGui.QLabel("")

        self.lst_widgets = QtGui.QListWidget()
        self.lst_widgets.setGeometry(50,50,500,400)

        layout_lst = QtGui.QHBoxLayout()
        layout_lst.addWidget(self.lst_widgets)

        self.lbl_count = QtGui.QLabel("Всего треков: 0")
        self.btn_sync = QtGui.QPushButton("Синхронизировать")
        self.btn_sync.clicked.connect(self.sync)
        layout_lbl = QtGui.QHBoxLayout()
        layout_lbl.addWidget(self.lbl_count)
        layout_lbl.addWidget(self.btn_sync)
        layout_lbl.addWidget(self.lbl_progress)

        btn_exit = QtGui.QPushButton("Выйти")
        btn_exit.clicked.connect(self.to_exit_clicked)
        self.btn_save = QtGui.QPushButton("Скачать выделенные")
        self.btn_save.clicked.connect(self.to_save_clicked)
        self.btn_save_all = QtGui.QPushButton("Скачать все")
        self.btn_save_all.clicked.connect(self.to_save_all_clicked)
        btn_cancel = QtGui.QPushButton("Отменить загрузку")
        btn_cancel.clicked.connect(self.to_cancel_clicked)
        btn_uncheck = QtGui.QPushButton("Убрать выделение")
        btn_uncheck.clicked.connect(self.uncheck)

        lbl_page = QtGui.QLabel("Текущая страница:")
        self.edt_page = QtGui.QLineEdit()
        self.btn_page = QtGui.QPushButton("Обновить контент")
        self.btn_page.clicked.connect(lambda:self.update_page_content(self.edt_page.text()))
        layout_page = QtGui.QHBoxLayout()
        layout_page.addWidget(lbl_page)
        layout_page.addWidget(self.edt_page)
        layout_page.addWidget(self.btn_page)

        layout_btns = QtGui.QHBoxLayout()
        layout_btns.addWidget(self.btn_save)
        layout_btns.addWidget(self.btn_save_all)
        layout_btns.addWidget(btn_cancel)
        layout_btns.addWidget(btn_uncheck)
        layout_btns.addWidget(btn_exit)

        self.layout_form = QtGui.QVBoxLayout(self)
        self.layout_form.addLayout(layout_lbl,)
        self.layout_form.addLayout(layout_lst)
        self.layout_form.addLayout(layout_page)
        self.layout_form.addLayout(layout_btns)

    def sync(self):
        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для синхронизации музыки"))
        if dirName != "":
            old = os.getcwd()
            os.chdir(dirName)
            # getting available tracks list
            all_tracks = []
            for i in range(self.lst_widgets.count()):
                wgt = self.lst_widgets.itemWidget(self.lst_widgets.item(i))
                all_tracks.append(wgt.track+'.mp3')
            files = [f for f in os.listdir(dirName) if os.path.isfile(f)]
            diff = list(set(all_tracks) - set(files))
            for_removing = list(set(files) - set(all_tracks))

            for_loading = []
            for i in range(self.lst_widgets.count()):
                wgt = self.lst_widgets.itemWidget(self.lst_widgets.item(i))
                if wgt.track+'.mp3' in diff:
                    for_loading.append([wgt.track, self.track_dict[i]])

            if len(for_loading) or len(for_removing) > 0:
                if len(for_loading) > 0:
                    msg = "Будет загружено новых треков: "+str(len(for_loading)) + ".\nДождитесь окончания загрузки."
                    QtGui.QMessageBox.information(self, "Синхронизация", msg)
                    if dirName != "":
                        os.chdir(old)
                        thr = threading.Thread(target=self.load_tracks, args=(for_loading, dirName))
                        thr.start()
                if len(for_removing) > 0:
                    msg = "Будет удалено треков из папки: "+str(len(for_removing)) + ".\nПричина-их нет на сервере ВК."
                    QtGui.QMessageBox.information(self, "Синхронизация", msg)
                    for i in range(len(for_removing)):
                        os.remove(for_removing[i])
            else:
                QtGui.QMessageBox.information(self, "Синхронизация", "Синхронизация не требуется.")

            os.chdir(old)

    def update_page_content(self, id_name):
        self.loader.app.uid = self.loader.get_uid(id_name, self.loader.app.access_token)
        if self.loader.app.uid == -1:
            QtGui.QMessageBox.warning(self, "Ошибка доступа", "Не могу получить данные с указанной страницы.")
            return
        self.loader.id = id_name
        self.lbl_progress.setText("Обновляются данные. Это займет какое-то время.")
        self.btn_save.setEnabled(False)
        self.btn_save_all.setEnabled(False)
        self.lst_widgets.clear()
        self.lbl_count.setText("Всего треков:")
        QtGui.QApplication.processEvents()
        if self.set_music_content() == -1:
            self.lbl_count.setText("Всего треков: 0")
            self.lbl_progress.setText("")
            self.btn_save.setEnabled(True)
            self.btn_save_all.setEnabled(True)
            

    # all_music: 1 - track name; 2 - duration (min:sec); 3 - url
    def set_music_content(self):
        self.lst_widgets.clear()

        val = self.music.get(self.loader.app.uid, self.loader.app.access_token)
        if val == -1:
            return -1
 
        all_music = self.music.get_list_for_gui()
        counter = 0
        for elem in all_music:
            if len(elem) == 3:
                custom_item = OneItem(elem[0], elem[1], elem[2])
                lst_item = QtGui.QListWidgetItem()
                lst_item.setSizeHint(QtCore.QSize(lst_item.sizeHint().width(), 30))
                self.lst_widgets.addItem(lst_item)
                self.lst_widgets.setItemWidget(lst_item, custom_item)
                self.track_dict[counter] = elem[2] # saved url to track
                counter += 1

        self.lbl_count.setText("Всего треков: " + str(len(all_music)))
        self.btn_save.setEnabled(True)
        self.btn_save_all.setEnabled(True)
        self.lbl_progress.setText("")
        global WORK
        WORK = False

    def to_save_clicked(self):
        for_loading = []
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            if wgt.chbox.isChecked():
                for_loading.append([wgt.track, self.track_dict[i]])

        if len(for_loading) == 0:
            QtGui.QMessageBox.warning(self, "Ошибка выбора", "Не выбран ни один трек.")
            return

        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения"))
        if dirName != "":
            thr = threading.Thread(target=self.load_tracks, args=(for_loading, dirName))
            thr.start()

    def to_save_all_clicked(self):
        for_loading = []
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            for_loading.append([wgt.track, self.track_dict[i]])

        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения"))
        if dirName != "":
            thr = threading.Thread(target=self.load_tracks, args=(for_loading, dirName))
            thr.start()

    def to_cancel_clicked(self):
        self.music.work = False

    def to_exit_clicked(self):
        self.music.work = False
        QtGui.QMessageBox.information(self, "Внимание", "Не завершайте работу приложения аварийно.\n"
                                                        "Программа завершится в течении нескольких секунд.")
        self.lst_widgets.clear()
        mainForm.close()

    def load_tracks(self, lst, dir):
        self.btn_save_all.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_sync.setEnabled(False)

        self.music.work = True
        val = self.music.load_tracks_from_list(lst, dir, self.lbl_progress)
        if val == -1:
            QtGui.QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении\n. "
                                                      "Убедитесь в существовании выбраной папки.")

        self.btn_save_all.setEnabled(True)
        self.btn_save.setEnabled(True)
        self.btn_sync.setEnabled(True)

    def uncheck(self):
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            if wgt.chbox.isChecked():
                wgt.chbox.setChecked(False)
#######################################################################################################################
#######################################################################################################################
class SearchMusic(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.track_dict = {}
        self.music = vk.Music_loader()
        self.loader = vk.Loader()
        self.old_search_word = ""
        self.setGeometry(600,300,600,500)
        self.lbl_progress = QtGui.QLabel("")

        self.lst_widgets = QtGui.QListWidget()
        self.lst_widgets.setGeometry(50,50,500,400)

        layout_lst = QtGui.QHBoxLayout()
        layout_lst.addWidget(self.lst_widgets)

        lbl_search = QtGui.QLabel("Поиск треков: ")
        edt_search = QtGui.QLineEdit()
        btn_search = QtGui.QPushButton("Найти (найти еще)")
        btn_search.clicked.connect(lambda :self.find_tracks(edt_search.text()))
        layout_search = QtGui.QHBoxLayout()
        layout_search.addWidget(lbl_search)
        layout_search.addWidget(edt_search)
        layout_search.addWidget(btn_search)

        self.lbl_count = QtGui.QLabel("Найдено треков: 0")
        layout_lbl = QtGui.QHBoxLayout()
        layout_lbl.addWidget(self.lbl_count)
        layout_lbl.addWidget(self.lbl_progress)

        btn_exit = QtGui.QPushButton("Выйти")
        btn_exit.clicked.connect(self.to_exit_clicked)
        self.btn_save = QtGui.QPushButton("Скачать выделенные")
        self.btn_save.clicked.connect(self.to_save_clicked)
        self.btn_save_all = QtGui.QPushButton("Скачать все")
        self.btn_save_all.clicked.connect(self.to_save_all_clicked)
        btn_cancel = QtGui.QPushButton("Отменить загрузку")
        btn_cancel.clicked.connect(self.to_cancel_clicked)
        btn_uncheck = QtGui.QPushButton("Убрать выделение")
        btn_uncheck.clicked.connect(self.uncheck)

        layout_btns = QtGui.QHBoxLayout()
        layout_btns.addWidget(self.btn_save)
        layout_btns.addWidget(self.btn_save_all)
        layout_btns.addWidget(btn_cancel)
        layout_btns.addWidget(btn_uncheck)
        layout_btns.addWidget(btn_exit)

        self.layout_form = QtGui.QVBoxLayout(self)
        self.layout_form.addLayout(layout_search)
        self.layout_form.addLayout(layout_lbl,)
        self.layout_form.addLayout(layout_lst)
        self.layout_form.addLayout(layout_btns)

    def load_tracks(self, lst, dir):
        self.btn_save_all.setEnabled(False)
        self.btn_save.setEnabled(False)

        self.music.work = True
        val = self.music.load_tracks_from_list(lst, dir, self.lbl_progress)
        if val == -1:
            QtGui.QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении\n. "
                                                      "Убедитесь в существовании выбраной папки.")

        self.btn_save_all.setEnabled(True)
        self.btn_save.setEnabled(True)

    def set_music_content(self, all_music):
        self.lst_widgets.clear()
        counter = 0
        for elem in all_music:
           if len(elem) == 3:
               custom_item = OneItem(elem[0], elem[1], elem[2])
               lst_item = QtGui.QListWidgetItem()
               lst_item.setSizeHint(QtCore.QSize(lst_item.sizeHint().width(), 30))
               self.lst_widgets.addItem(lst_item)
               self.lst_widgets.setItemWidget(lst_item, custom_item)
               self.track_dict[counter] = elem[2] # saved url to track
               counter += 1
        self.lbl_count.setText("Всего треков: " + str(len(all_music)))

    def find_tracks(self, search_word):
        if search_word != self.old_search_word:
            self.music.offset = 0
            self.old_search_word = search_word
        else:
            self.music.offset += self.music.max_sound_count
            
        if self.music.search_by_name(search_word, self.loader.app.access_token) == -1:
            if self.music.offset -2* self.music.max_sound_count >= 0:
                self.music.offset =- 2*self.music.max_sound_count
                if self.music.search_by_name(search_word, self.loader.app.access_token) == -1:
                    self.music.offset -= 2*self.music.max_sound_count
                    return
            else:
                self.music.offset -= 2*self.music.max_sound_count
                return
          
        lst = self.music.get_list_for_gui()
        self.set_music_content(lst)

    def to_save_clicked(self):
        for_loading = []
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            if wgt.chbox.isChecked():
                for_loading.append([wgt.track, self.track_dict[i]])

        if len(for_loading) == 0:
            QtGui.QMessageBox.warning(self, "Ошибка выбора", "Не выбран ни один трек.")
            return

        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения"))
        if dirName != "":
            thr = threading.Thread(target=self.load_tracks, args=(for_loading, dirName))
            thr.start()

    def to_save_all_clicked(self):
        for_loading = []
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            for_loading.append([wgt.track, self.track_dict[i]])

        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения"))
        if dirName != "":
            thr = threading.Thread(target=self.load_tracks, args=(for_loading, dirName))
            thr.start()

    def to_cancel_clicked(self):
        self.music.work = False

    def to_exit_clicked(self):
        self.music.work = False
        QtGui.QMessageBox.information(self, "Внимание", "Не завершайте работу приложения аварийно.\n"
                                                        "Программа завершится в течении нескольких секунд.")
        self.lst_widgets.clear()
        mainForm.close()

    def uncheck(self):
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            if wgt.chbox.isChecked():
                wgt.chbox.setChecked(False)
#######################################################################################################################
#######################################################################################################################
class UserImages(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.dict = {}
        self.photo = vk.Photo_loader()
        self.loader = vk.Loader()
        self.setGeometry(600,300,600,500)
        self.lbl_progress = QtGui.QLabel("")

        self.lst_widgets = QtGui.QListWidget()
        self.lst_widgets.setGeometry(50,50,500,400)

        layout_lst = QtGui.QHBoxLayout()
        layout_lst.addWidget(self.lst_widgets)

        self.lbl_count = QtGui.QLabel("Всего фоток: 0")
        layout_lbl = QtGui.QHBoxLayout()
        layout_lbl.addWidget(self.lbl_count)
        layout_lbl.addWidget(self.lbl_progress)

        btn_exit = QtGui.QPushButton("Выйти")
        btn_exit.clicked.connect(self.to_exit_clicked)
        self.btn_save = QtGui.QPushButton("Скачать выделенные")
        self.btn_save.clicked.connect(self.to_save_clicked)
        self.btn_save_all = QtGui.QPushButton("Скачать все")
        self.btn_save_all.clicked.connect(self.to_save_all_clicked)
        btn_cancel = QtGui.QPushButton("Отменить загрузку")
        btn_cancel.clicked.connect(self.to_cancel_clicked)
        btn_uncheck = QtGui.QPushButton("Убрать выделение")
        btn_uncheck.clicked.connect(self.uncheck)

        lbl_page = QtGui.QLabel("Текущая страница:")
        self.edt_page = QtGui.QLineEdit()
        self.btn_page = QtGui.QPushButton("Обновить контент")
        self.btn_page.clicked.connect(lambda:self.update_page_content(self.edt_page.text()))
        layout_page = QtGui.QHBoxLayout()
        layout_page.addWidget(lbl_page)
        layout_page.addWidget(self.edt_page)
        layout_page.addWidget(self.btn_page)

        layout_btns = QtGui.QHBoxLayout()
        layout_btns.addWidget(self.btn_save)
        layout_btns.addWidget(self.btn_save_all)
        layout_btns.addWidget(btn_cancel)
        layout_btns.addWidget(btn_uncheck)
        layout_btns.addWidget(btn_exit)

        self.layout_form = QtGui.QVBoxLayout(self)
        self.layout_form.addLayout(layout_lbl,)
        self.layout_form.addLayout(layout_lst)
        self.layout_form.addLayout(layout_page)
        self.layout_form.addLayout(layout_btns)

    def update_page_content(self, id_name):
        self.loader.app.uid = self.loader.get_uid(id_name, self.loader.app.access_token)
        if self.loader.app.uid == -1:
            QtGui.QMessageBox.warning(self, "Ошибка доступа", "Не могу получить данные с указанной страницы.")
            return
        self.loader.id = id_name
        self.lbl_progress.setText("Обновляются данные. Это займет какое-то время.")
        self.btn_save.setEnabled(False)
        self.btn_save_all.setEnabled(False)
        self.lst_widgets.clear()
        self.lbl_count.setText("Всего фоток:")
        QtGui.QApplication.processEvents()
        if self.set_image_content() == -1:
            self.lbl_count.setText("Всего фоток: 0")
            self.lbl_progress.setText("")
            self.btn_save.setEnabled(True)
            self.btn_save_all.setEnabled(True)  

    def set_image_content(self):
        #cleaning old data
        self.lst_widgets.clear()
        self.dict = []

        # getting links to images in different resolutions
        val = self.photo.get_all_from_albums(self.loader.app.uid, self.loader.app.access_token, "")
        if val == -1:
            return -1
        else: img_dict_norm = val # links to preview
        val = self.photo.get_all_from_albums(self.loader.app.uid, self.loader.app.access_token, "BIG")
        if val == -1:
            return -1
        else: img_dict_big = val # links for saving (in high resolution)

        # saving images for preview
        self.photo.save_all(PREVIEW_FOLDER, img_dict_norm)

        counter = 0
        for elem in img_dict_big:
            path_to_preview = PREVIEW_FOLDER + "/photo_"+str(counter+1)+".jpeg"
            custom_item = OnePictureItem(elem, path_to_preview)
            lst_item = QtGui.QListWidgetItem()
            lst_item.setSizeHint(QtCore.QSize(lst_item.sizeHint().width(), 110))
            self.lst_widgets.addItem(lst_item)
            self.lst_widgets.setItemWidget(lst_item, custom_item)
            self.dict.append(elem) # saved url to image
            counter += 1
        self.lbl_count.setText("Всего фоток: " + str(len(img_dict_big)))
        self.lbl_progress.setText("")
        self.btn_save.setEnabled(True)
        self.btn_save_all.setEnabled(True)

    def to_save_clicked(self):
        for_loading = []
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            if wgt.chbox.isChecked():
                for_loading.append(["photo_"+str(i+1), self.dict[i]])

        if len(for_loading) == 0:
            QtGui.QMessageBox.warning(self, "Ошибка выбора", "Не выбрана ни одна фотка.")
            return

        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения"))
        if dirName != "":
            thr = threading.Thread(target=self.load_images, args=(for_loading, dirName))
            thr.start()

    def to_save_all_clicked(self):
        for_loading = []
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            for_loading.append(["photo_"+str(i+1), self.dict[i]])

        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения"))
        if dirName != "":
            thr = threading.Thread(target=self.load_images, args=(for_loading, dirName))
            thr.start()

    def to_cancel_clicked(self):
        self.photo.work = False

    def to_exit_clicked(self):
        self.photo.work = False
        QtGui.QMessageBox.information(self, "Внимание", "Не завершайте работу приложения аварийно.\n"
                                                        "Программа завершится в течении нескольких секунд.")
        self.lst_widgets.clear()
        if (os.path.isdir(PREVIEW_FOLDER)):
                shutil.rmtree(PREVIEW_FOLDER)
        mainForm.close()

    def load_images(self, lst, dir):
        self.btn_save_all.setEnabled(False)
        self.btn_save.setEnabled(False)

        self.photo.work = True
        val = self.photo.load_images_from_list(lst, dir, self.lbl_progress)
        if val == -1:
            QtGui.QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении\n. "
                                                      "Убедитесь в существовании выбраной папки.")

        self.btn_save_all.setEnabled(True)
        self.btn_save.setEnabled(True)

    def uncheck(self):
        for i in range(self.lst_widgets.count()):
            item = self.lst_widgets.item(i)
            wgt = self.lst_widgets.itemWidget(item)
            if wgt.chbox.isChecked():
                wgt.chbox.setChecked(False)
#######################################################################################################################
#######################################################################################################################
class MainForm(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("Утилита для ВКонтакте")
        self.setWindowIcon(QtGui.QIcon("icon.jpg"))
        self.setGeometry(600,300,650,500)

        # set form to center of screen
        geom = QtGui.QApplication.desktop().screenGeometry()
        x = (geom.width()-self.width()) / 2
        y = (geom.height()-self.height()) / 2
        self.move(x,y)

        tabs = QtGui.QTabWidget(self)
        tabs.setGeometry(0,0,650,500)

        self.musicForm = UserMusic()
        tabs.addTab(self.musicForm, "Музыка")

        self.searchForm = SearchMusic()
        tabs.addTab(self.searchForm, "Поиск музыки")

        self.imageForm = UserImages()
        tabs.addTab(self.imageForm, "Фото")

        layout_tab = QtGui.QVBoxLayout(self)
        layout_tab.addWidget(tabs)
#######################################################################################################################
#######################################################################################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    auth = AuthForm()
    auth.show()
    mainForm = MainForm()

    sys.exit(app.exec())
