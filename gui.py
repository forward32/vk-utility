# -*- coding: utf-8 -*-

import sys
import vk
from PyQt4 import QtCore, QtGui
import threading
#######################################################################################################################
#######################################################################################################################
class AuthForm(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("Авторизация")
        self.setWindowIcon(QtGui.QIcon("icon.jpg"))

        # set form to center of screen
        geom = QtGui.QApplication.desktop().screenGeometry()
        x = (geom.width()-self.width()) / 2
        y = (geom.height()-self.height()) / 2
        self.move(x,y)

        lbl_login = QtGui.QLabel("Логин:")
        lbl_pass = QtGui.QLabel("Пароль:")
        lbl_id = QtGui.QLabel("ID страницы:")
        edt_login = QtGui.QLineEdit()
        edt_pass = QtGui.QLineEdit()
        edt_id = QtGui.QLineEdit()
        edt_pass.setEchoMode(QtGui.QLineEdit.Password)
        btn_ok = QtGui.QPushButton("Принять")
        btn_cancel = QtGui.QPushButton("Отменить")

        grid = QtGui.QGridLayout(self)
        grid.addWidget(lbl_login, 0, 0)
        grid.addWidget(edt_login, 0, 1)
        grid.addWidget(lbl_pass, 1, 0)
        grid.addWidget(edt_pass, 1, 1)
        grid.addWidget(lbl_id, 2, 0)
        grid.addWidget(edt_id, 2, 1)
        grid.addWidget(btn_ok, 3, 0)
        grid.addWidget(btn_cancel, 3, 1)

        btn_ok.clicked.connect(lambda:self.to_ok_clicked(edt_login.text(), edt_pass.text(), edt_id.text()))
        btn_cancel.clicked.connect(self.to_cancel_clicked)

    def to_ok_clicked(self, user_name, pass_name, id_name):
        if user_name != "" and pass_name != "" and id_name != "":
            loader = vk.Loader()
            val = loader.autorize(user_name, pass_name, id_name)
            if val == -1:
                QtGui.QMessageBox.warning(self, "Ошибка авторизации", ("Неверный ввод данных.\n"
                                                 "Проверьте правильность ввода данных и повторите попытку."))
                return
			
            auth.hide()
			
            mainForm.musicForm.loader = loader
            mainForm.searchForm.loader = loader			
            mainForm.musicForm.set_music_content()
            mainForm.show()
        else:
            QtGui.QMessageBox.warning(self, "Неверный ввод", "Все поля должны быть заполнены.")

    def to_cancel_clicked(self):
        sys.exit(0)
#######################################################################################################################
#######################################################################################################################
class OneItem(QtGui.QWidget):
    def __init__(self, track_name, duration):
        QtGui.QWidget.__init__(self)
        self.track = track_name

        lbl_icon = QtGui.QLabel(self)
        lbl_icon.setGeometry(0,0,30,20)
        pix = QtGui.QPixmap("track.png")
        scalled_pix = pix.scaled(lbl_icon.width(), lbl_icon.height(), QtCore.Qt.KeepAspectRatio)
        lbl_icon.setPixmap(scalled_pix)

        lbl_name = QtGui.QLabel(self)
        lbl_name.setText(self.track)
        lbl_name.setGeometry(50,0,350,20)

        lbl_duration = QtGui.QLabel(self)
        lbl_duration.setText(duration)
        lbl_duration.setGeometry(420,0,30,20)

        self.chbox = QtGui.QCheckBox(self)
        self.chbox.setGeometry(460,0,40,20)
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

        layout_btns = QtGui.QHBoxLayout()
        layout_btns.addWidget(self.btn_save)
        layout_btns.addWidget(self.btn_save_all)
        layout_btns.addWidget(btn_cancel)
        layout_btns.addWidget(btn_exit)

        self.layout_form = QtGui.QVBoxLayout(self)
        self.layout_form.addLayout(layout_lbl,)
        self.layout_form.addLayout(layout_lst)
        self.layout_form.addLayout(layout_btns)


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
                custom_item = OneItem(elem[0], elem[1])
                lst_item = QtGui.QListWidgetItem()
                self.lst_widgets.addItem(lst_item)
                self.lst_widgets.setItemWidget(lst_item, custom_item)
                self.track_dict[counter] = elem[2] # saved url to track
                counter += 1
        self.lbl_count.setText("Всего треков: " + str(len(all_music)))

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

        self.music.work = True
        val = self.music.load_tracks_from_list(lst, dir, self.lbl_progress)
        if val == -1:
            QtGui.QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении\n. "
                                                      "Убедитесь в существовании выбраной папки.")

        self.btn_save_all.setEnabled(True)
        self.btn_save.setEnabled(True)
#######################################################################################################################
#######################################################################################################################
class SearchMusic(QtGui.QWidget):
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

        lbl_search = QtGui.QLabel("Поиск треков: ")
        edt_search = QtGui.QLineEdit()
        btn_search = QtGui.QPushButton("Найти")
        btn_search.clicked.connect(lambda :self.find_tracks(edt_search.text()))
        layout_search = QtGui.QHBoxLayout()
        layout_search.addWidget(lbl_search)
        layout_search.addWidget(edt_search)
        layout_search.addWidget(btn_search)

        self.lbl_count = QtGui.QLabel("Найдено треков: 0")
        btn_update = QtGui.QPushButton("Найти еще")
        btn_update.clicked.connect(lambda:self.to_find_more_click(edt_search.text()))
        layout_lbl = QtGui.QHBoxLayout()
        layout_lbl.addWidget(self.lbl_count)
        layout_lbl.addWidget(btn_update)
        layout_lbl.addWidget(self.lbl_progress)

        btn_exit = QtGui.QPushButton("Выйти")
        btn_exit.clicked.connect(self.to_exit_clicked)
        self.btn_save = QtGui.QPushButton("Скачать выделенные")
        self.btn_save.clicked.connect(self.to_save_clicked)
        self.btn_save_all = QtGui.QPushButton("Скачать все")
        self.btn_save_all.clicked.connect(self.to_save_all_clicked)
        btn_cancel = QtGui.QPushButton("Отменить загрузку")
        btn_cancel.clicked.connect(self.to_cancel_clicked)

        layout_btns = QtGui.QHBoxLayout()
        layout_btns.addWidget(self.btn_save)
        layout_btns.addWidget(self.btn_save_all)
        layout_btns.addWidget(btn_cancel)
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
               custom_item = OneItem(elem[0], elem[1])
               lst_item = QtGui.QListWidgetItem()
               self.lst_widgets.addItem(lst_item)
               self.lst_widgets.setItemWidget(lst_item, custom_item)
               self.track_dict[counter] = elem[2] # saved url to track
               counter += 1
        self.lbl_count.setText("Всего треков: " + str(len(all_music)))

    def find_tracks(self, search_word):
        val = self.music.search_by_name(search_word, self.loader.app.access_token)
        if val == -1:
            return

        lst = self.music.get_list_for_gui()
        self.set_music_content(lst)

    def to_find_more_click(self, search_word):
        if search_word != "":
            self.music.offset += self.music.max_sound_count
            self.find_tracks(search_word)

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
        tabs.addTab(self.musicForm, "Музыка со страницы")

        self.searchForm = SearchMusic()
        tabs.addTab(self.searchForm, "Поиск музыки")

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