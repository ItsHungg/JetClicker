from tkinter import ttk, messagebox
import tkinter as tk

import pyautogui
import keyboard

from itertools import permutations, chain
import threading
import json
import time

import platform
import os

__project__ = 'JetClicker'
__version__ = '0.0.2'

__author__ = 'Hung'
__runtime__ = time.strftime('%T')
__rundate__ = time.strftime('%A %d-%b-%Y (%d/%m/%Y)')
__startFlag__ = time.perf_counter()


class Utilities:
    @staticmethod
    def add_default_hotkeys(return_: bool = False):
        if return_:
            return ['+'.join(x for x in i) for i in list(chain.from_iterable(
                permutations(hk.split('+'), r=len(hk.split('+'))) for hk in
                ['ctrl+alt+s', 'ctrl+shift+alt+r', 'ctrl+alt+b']))]
        keyboard.add_hotkey('ctrl+alt+s', root.settings)
        keyboard.add_hotkey('ctrl+shift+alt+r', Utilities.reset_all)
        keyboard.add_hotkey('ctrl+alt+b', root.deiconify)

        Utilities.writelog('Default hotkeys initialized', ('', '\n', True))

    @staticmethod
    def writelog(content: str, built_content: list | tuple | None = None, logType: str = 'INFO',
                 path: str = fr'data\logs\logs.txt',
                 mode: str = 'a',
                 create_separated_file: list = (True, fr'data\logs\logs_{time.strftime("%m-%d-%Y")}.txt')):
        dailylog_content = content
        if built_content:
            if content[2]:
                content = f'[{logType}] {time.strftime("[%D - %T]")}: ' + content + '.'
                dailylog_content = f'[{logType}] {time.strftime("[%T]")}: ' + dailylog_content + '.'
            content = built_content[0] + content
            content += built_content[1]
            dailylog_content = built_content[0] + dailylog_content
            dailylog_content += built_content[1]

        if create_separated_file:
            with open(create_separated_file[1], mode) as daylogwrite:
                daylogwrite.write(dailylog_content)
        with open(path, mode) as logwrite:
            logwrite.write(content)

    @staticmethod
    def reset_all():
        STORAGE.FIXED_POSITIONS = (0, 0)

        STORAGE.General.current_click = 0
        STORAGE.General.total_clicks = 0

        STORAGE.Setting.trigger_hotkey = 'ctrl+c'
        STORAGE.Setting.isTopmost = False
        STORAGE.Setting.isFailsafe = True
        STORAGE.Setting.isAutoPopup = True
        STORAGE.Setting.transparency = 0.5


with open(r'data\data.json', 'r') as read_data:
    try:
        DATA = json.load(read_data)
    except json.decoder.JSONDecodeError as error:
        messagebox.showerror('Decode Error',
                             'Couldn\'t read data.json file.\nPlease check the data file and try again.')
        Utilities.writelog(
            f'Couldn\'t read data.json file.\n\terror message: ({type(error).__name__}) {error}\n\terror id: {id(error)}',
            ('{\n', '\n}\n', True), logType='ERROR')
        quit()

Utilities.writelog(f'Opened {__project__} {__version__}', ('{\n', '\n', True))


class Storage:
    RUNNING = True
    CLICKING = False
    FIXED_POSITIONS = tuple(map(int, DATA[0]['fixed-position']))

    class General:
        total_clicks = DATA[1]['total-clicks']
        current_click = 0

    class Setting:
        ON = False

        trigger_hotkey = DATA[2]['trigger-hotkey']

        isTopmost = DATA[2]['is.topmost']
        isFailsafe = DATA[2]['is.failsafe']
        isAutoPopup = DATA[2]['is.auto-popup']

        transparency = DATA[2]['transparency']


STORAGE = Storage
pyautogui.FAILSAFE = STORAGE.Setting.isFailsafe
pyautogui.PAUSE = 0
Utilities.writelog('Variables initialized', ('', '\n', True))


def save_data(data: list | dict = None):
    if data is None:
        data = [
            {
                'category': 'storage',
                'clicking': STORAGE.CLICKING,
                'fixed-position': STORAGE.FIXED_POSITIONS,
            },
            {
                'category': 'general',
                'total-clicks': STORAGE.General.total_clicks,
                'latest-clicks': STORAGE.General.current_click
            },
            {
                'category': 'settings',
                'trigger-hotkey': STORAGE.Setting.trigger_hotkey,
                'is.topmost': STORAGE.Setting.isTopmost,
                'is.failsafe': STORAGE.Setting.isFailsafe,
                'is.auto-popup': STORAGE.Setting.isAutoPopup,
                'transparency': STORAGE.Setting.transparency
            }
        ]

    with open(r'data\data.json', 'w') as write_data:
        json.dump(data, write_data, indent=2)

    Utilities.writelog('Data saved into data.json', ('', '\n', True))


# noinspection PyTypeChecker,PyMethodMayBeStatic
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f'{__project__} {__version__}')
        self.resizable(False, False)

        # MAIN FRAME
        self.mainFrame = tk.Frame(self)
        self.mainFrame.grid(row=5, column=3, padx=15, pady=15)

        # # MENU FRAME
        self.menuImage = tk.PhotoImage(file=r'assets\textures\menu.png').subsample(20, 20)
        self.menuButton = tk.Button(self, image=self.menuImage, bd=0, bg=self.mainFrame.cget('bg'), cursor='hand2',
                                    command=self.menuActions)
        self.menuButton.grid(row=0, column=0, columnspan=100, rowspan=100, sticky='nw', padx=7, pady=3)

        self.menuFrame = tk.Frame(bg='gray80', width=100)
        self.menuColor = self.menuFrame.cget('bg')

        # # # ALL MENU FRAME
        self.allMenuFrame = tk.Frame(self.menuFrame)
        self.allMenuFrame.grid(row=3, column=3, padx=5, pady=5)

        tk.Button(self.allMenuFrame, image=self.menuImage, bd=0, bg=self.menuColor, activebackground=self.menuColor,
                  cursor='hand2',
                  command=self.menuActions).grid(row=1, column=3, sticky='ew')

        tk.Label(self.allMenuFrame, text='', bg=self.menuColor, font=('Calibri', 1)).grid(row=3, column=3, sticky='ew')
        tk.Frame(self.allMenuFrame, bg='black', height=2).grid(row=4, column=3, sticky='ew')

        # # # SETTING BUTTON
        self.settingImage = tk.PhotoImage(file=r'assets\textures\setting.png').subsample(22, 22)
        self.settingButton = tk.Button(self.allMenuFrame, bg=self.menuColor, activebackground=self.menuColor, bd=0,
                                       image=self.settingImage, cursor='hand2', command=self.settings)
        self.settingButton.grid(row=5, column=3, ipady=7, sticky='nsew')

        # # # INFO BUTTON
        self.infoImage = tk.PhotoImage(file=r'assets\textures\info.png').subsample(19, 19)
        self.infoButton = tk.Button(self.allMenuFrame, bg=self.menuColor, activebackground=self.menuColor, bd=0,
                                    image=self.infoImage, cursor='hand2',
                                    command=lambda: [Utilities.writelog('Opened Credits & Info page', ('', '\n', True)),
                                                     messagebox.showinfo('Credits & Information',
                                                                         f'''CREDITS & INFORMATION of {__project__.upper()}

--- APPLICATION ---
Author: {__author__}
Application name: {__project__}
Application version: {__version__}
Application full-name: {__project__} {__version__}

--- INFORMATION ---
Operating system: {platform.system()}
Full OS name: {platform.platform()}
OS Username: {os.getlogin()}
Python version: {platform.python_version()}

--- STATISTIC ---
Current clicks: {STORAGE.General.current_click}
Total clicks: {STORAGE.General.total_clicks}

--- MISCELLANEOUS ---
Open time: {__runtime__}
Open date: {__rundate__}
Time elapsed: {time.perf_counter() - __startFlag__:.1f}s'''), Utilities.writelog('Closed Credits & Info page',
                                                                                 ('', '\n', True))])
        self.infoButton.grid(row=21, column=3, ipady=7, sticky='sew')

        # # INTERVAL FRAME
        self.intervalFrame = ttk.LabelFrame(self.mainFrame, text='Click interval', labelanchor='n')
        self.intervalFrame.grid(row=3, column=3, ipadx=15, ipady=5, sticky='new', columnspan=3)
        self.intervalFrame.grid_columnconfigure(3, weight=1)

        self._intervalFrame = ttk.Frame(self.intervalFrame)
        self._intervalFrame.grid(row=3, column=3, pady=(5, 0))
        self._intervalFrame.grid_columnconfigure(tuple(range(3, 11)), weight=1)

        self.intervalHourCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                 values=[str(i).zfill(2) for i in range(0, 25)], state='normal',
                                                 validate='key',
                                                 validatecommand=(self.register(self.bindHourChosen), '%P'))
        self.intervalHourCombobox.grid(row=3, column=3)
        self.intervalHourCombobox.set('00')
        ttk.Label(self._intervalFrame, text='hours').grid(row=3, column=4, sticky='w', padx=(1, 6))

        self.intervalMinuteCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                   values=[str(i).zfill(2) for i in range(0, 60)], state='normal',
                                                   validate='key',
                                                   validatecommand=(self.register(self.bindMinuteChosen), '%P'))
        self.intervalMinuteCombobox.grid(row=3, column=5)
        self.intervalMinuteCombobox.current(0)
        ttk.Label(self._intervalFrame, text='mins').grid(row=3, column=6, sticky='w', padx=(1, 6))

        self.intervalSecondCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                   values=[str(i).zfill(2) for i in range(0, 60)], state='normal',
                                                   validate='key',
                                                   validatecommand=(self.register(self.bindSecondChosen), '%P'))
        self.intervalSecondCombobox.grid(row=3, column=7)
        self.intervalSecondCombobox.current(0)
        ttk.Label(self._intervalFrame, text='secs').grid(row=3, column=8, sticky='w', padx=(1, 6))

        self.intervalMillisecondCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                        values=[str(i).zfill(3) for i in range(0, 1000)],
                                                        state='normal', validate='key',
                                                        validatecommand=(
                                                            self.register(self.bindMillisecondChosen), '%P'))
        self.intervalMillisecondCombobox.grid(row=3, column=9)
        self.intervalMillisecondCombobox.current(100)
        ttk.Label(self._intervalFrame, text='millisecs').grid(row=3, column=10, sticky='w', padx=(1, 6))

        self.showInterval = ttk.Label(self._intervalFrame, text='Interval: 00:00:00.100')
        self.showInterval.grid(row=5, column=3, columnspan=8, pady=(5, 0))

        self.intervalWidgets = [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                                self.intervalMillisecondCombobox]
        self.intervals = [i.get() for i in self.intervalWidgets]

        for i in self.intervalWidgets:
            i.bind('<<ComboboxSelected>>', self.bindChosenAll)
            i.bind('<KeyRelease>', self.bindChosenAll)
            i.bind('<FocusIn>', lambda event=i: event.widget.set(''))
            i.bind('<FocusOut>',
                   lambda event=i: event.widget.set(self.intervals[self.intervalWidgets.index(event.widget)]))

        # # CLICK OPTIONS
        self.click_optionFrame = ttk.LabelFrame(self.mainFrame, text='Click options', labelanchor='nw')
        self.click_optionFrame.grid(row=5, column=3, ipadx=15, ipady=5, pady=(5, 0), sticky='nw', padx=(0, 5))
        self.click_optionFrame.grid_columnconfigure(3, weight=1)

        self._click_optionFrame = ttk.Frame(self.click_optionFrame)
        self._click_optionFrame.grid(row=3, column=3, pady=(5, 0))
        self._click_optionFrame.grid_columnconfigure((3, 5), weight=1)

        ttk.Label(self._click_optionFrame, text='Mouse button:').grid(row=3, column=3, padx=(0, 5), pady=(0, 5),
                                                                      sticky='w')
        self.mouseButtonOptionCombobox = ttk.Combobox(self._click_optionFrame, width=7,
                                                      values=['Left', 'Right', 'Middle'], state='readonly')
        self.mouseButtonOptionCombobox.grid(row=3, column=4, pady=(0, 5))
        self.mouseButtonOptionCombobox.current(0)

        ttk.Label(self._click_optionFrame, text='Click type:').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.clickTypeOptionCombobox = ttk.Combobox(self._click_optionFrame, width=7,
                                                    values=['Single', 'Double', 'Triple'], state='readonly')
        self.clickTypeOptionCombobox.grid(row=5, column=4)
        self.clickTypeOptionCombobox.current(0)

        # # CLICK REPEAT
        self.click_repeatFrame = ttk.LabelFrame(self.mainFrame, text='Click repeat', labelanchor='nw')
        self.click_repeatFrame.grid(row=5, column=5, ipadx=15, ipady=5, pady=5, sticky='ne', padx=(5, 0))
        self.click_repeatFrame.grid_columnconfigure(3, weight=1)

        self._click_repeatFrame = ttk.Frame(self.click_repeatFrame)
        self._click_repeatFrame.grid(row=3, column=3, pady=(5, 0))
        self._click_repeatFrame.grid_columnconfigure((3, 5), weight=1)
        self.repeatVar = tk.StringVar(value='unlimited')

        # ttk.Label(self._click_repeatFrame, text='Repeat').grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')
        self.limitedRepeatRadiobutton = ttk.Radiobutton(self._click_repeatFrame, text='Repeat', value='limited',
                                                        variable=self.repeatVar,
                                                        command=lambda: self.limitedRepeatSpinbox.focus())
        self.limitedRepeatRadiobutton.grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')

        self.limitedRepeatSpinbox = ttk.Spinbox(self._click_repeatFrame, from_=1, to=99999, width=5, wrap=True,
                                                validate='key', validatecommand=(
                self.register(lambda item: True if not len(item) or (item.isdigit() and int(item)) else False), '%P'))
        self.limitedRepeatSpinbox.grid(row=3, column=4, padx=5, pady=(0, 5), sticky='w')
        self.limitedRepeatSpinbox.set('1')
        ttk.Label(self._click_repeatFrame, text='times').grid(row=3, column=5, pady=(0, 5), sticky='w')

        # ttk.Label(self._click_repeatFrame, text='Repeat until stopped').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.unlimitedRepeatRadiobutton = ttk.Radiobutton(self._click_repeatFrame, text='Until stopped',
                                                          value='unlimited', variable=self.repeatVar)
        self.unlimitedRepeatRadiobutton.grid(row=5, column=3, padx=(0, 5), sticky='w', columnspan=3)

        # # CURSOR POSITION FRAME
        self.cursor_positionFrame = ttk.LabelFrame(self.mainFrame, text='Cursor position', labelanchor='n')
        self.cursor_positionFrame.grid(row=7, column=3, ipadx=15, ipady=5, sticky='new', columnspan=3)
        self.cursor_positionFrame.grid_columnconfigure(3, weight=1)

        self._cursor_positionFrame = ttk.Frame(self.cursor_positionFrame)
        self._cursor_positionFrame.grid(row=3, column=3, pady=(5, 0))
        self._cursor_positionFrame.grid_columnconfigure(tuple(range(3, 11)), weight=1)
        self.positionVar = tk.StringVar(value='mouse')

        # ttk.Label(self._click_positionFrame, text='Repeat').grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')
        self.mousePositionRadiobutton = ttk.Radiobutton(self._cursor_positionFrame, text='Current (0, 0)',
                                                        value='mouse', variable=self.positionVar)
        self.mousePositionRadiobutton.grid(row=3, column=3, padx=(0, 7), pady=(0, 5), sticky='w')

        # ttk.Label(self._click_positionFrame, text='Repeat until stopped').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.customPositionRadiobutton = ttk.Radiobutton(self._cursor_positionFrame,
                                                         text='Custom ({0}, {1})'.format(*STORAGE.FIXED_POSITIONS),
                                                         value='custom',
                                                         variable=self.positionVar, command=self.customPositionDialog)
        self.customPositionRadiobutton.grid(row=3, column=5, padx=(7, 0), sticky='e')

        # # RUN
        self.runFrame = ttk.Frame(self.mainFrame)
        self.runFrame.grid(row=9, column=3, columnspan=3, sticky='nsew', ipadx=15, ipady=5, pady=(15, 0))
        self.runFrame.grid_columnconfigure((3, 5), weight=1)
        self.runFrame.grid_rowconfigure((3, 5), weight=1)

        self.startClickButton = ttk.Button(self.runFrame, text='Start', command=self.startClicking)
        self.startClickButton.grid(row=3, column=3, sticky='nsew')

        self.stopClickButton = ttk.Button(self.runFrame, text='Stop', state='disabled', command=self.stopClicking)
        self.stopClickButton.grid(row=3, column=5, sticky='nsew')

        Utilities.writelog('GUI frame initialized', ('', '\n', True))

    def startClicking(self):
        hour, minute, second, millisecond = map(int, self.intervals)
        sleepTime = hour * 60 * 60 + minute * 60 + second + millisecond / 1000
        if not sleepTime and STORAGE.Setting.isAutoPopup:
            if not messagebox.askyesno('Warning',
                                       f'If you set the interval to 0s, {__project__} will run as fast as it can!\nSo, would you still like to start clicking?\n\n(This is an extra pop-up, you can disable it in the Settings)',
                                       icon='warning'):
                return

        self.startClickButton.configure(state='disabled')
        self.stopClickButton.configure(state='normal')
        self.settingButton.configure(state='disabled')
        self.title(f'Clicking - {__project__} {__version__}')

        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.configure(state='disabled')
        STORAGE.CLICKING = True
        Utilities.writelog(
            f'CLICKING STARTED\n\tinterval: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}\n\tbutton: {self.mouseButtonOptionCombobox.get().lower()}\n\ttype: {self.clickTypeOptionCombobox.get().lower()}\n\trepeat: {self.repeatVar.get()}\n\tposition: {self.positionVar.get()}{f" ({STORAGE.FIXED_POSITIONS[0]}, {STORAGE.FIXED_POSITIONS[1]})" if self.positionVar.get() == "custom" else ""}',
            ('', '\n', True))

        def click():
            if self.positionVar.get() == 'custom':
                pyautogui.moveTo(*map(int, STORAGE.FIXED_POSITIONS))

            clickType = self.clickTypeOptionCombobox.get().lower().strip()
            mouseButton = self.mouseButtonOptionCombobox.get().lower().strip()
            pyautogui.click(button=mouseButton,
                            clicks=3 if clickType == 'triple' else 2 if clickType == 'double' else 1)
            STORAGE.General.total_clicks += 1
            STORAGE.General.current_click += 1
            print('clicked')

        def runClicks():
            nonlocal sleepTime

            repeatTime = -1 if self.repeatVar.get() == 'unlimited' else int(self.limitedRepeatSpinbox.get())
            while 1:
                if not repeatTime:
                    self.stopClicking()
                    break
                if not STORAGE.CLICKING:
                    break
                try:
                    flag = time.perf_counter()
                    click()
                    stopFlag = time.perf_counter()

                    time.sleep(sleepTime)
                    allFlag = time.perf_counter()
                    print(sleepTime, stopFlag - flag, allFlag - flag)
                except pyautogui.FailSafeException:
                    keyboard.unregister_all_hotkeys()
                    Utilities.add_default_hotkeys()
                    self.stopClickButton.configure(state='disabled')
                    messagebox.showwarning('Fail-safe Triggered',
                                           f'You have triggered {__project__} fail-safe by moving the mouse to the corner of the screen.\n\n(You can disable it in the settings, but it\'s NOT RECOMMENDED)')
                    self.stopClicking()
                    keyboard.add_hotkey(STORAGE.Setting.trigger_hotkey,
                                        lambda: root.stopClicking() if STORAGE.CLICKING else root.startClicking())
                    Utilities.writelog('Fail-safe triggered. Clicking progress stopped', ('', '\n', True))

                    break
                repeatTime -= 1

        threading.Thread(target=runClicks).start()

    def stopClicking(self):
        self.startClickButton.configure(state='normal')
        self.stopClickButton.configure(state='disabled')
        self.settingButton.configure(state='normal')
        self.title(f'Stopped - {__project__} {__version__}')
        STORAGE.CLICKING = False

        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.configure(state='readonly' if widget in [self.clickTypeOptionCombobox,
                                                            self.mouseButtonOptionCombobox] else 'normal')
        Utilities.writelog(f'CLICKING STOPPED', ('', '\n', True))

    # class: menu
    def menuActions(self):
        self.menuFrame.grid(row=0, column=0, sticky='nsw', columnspan=100, rowspan=100)
        if self.menuFrame.winfo_viewable():
            self.menuFrame.grid_forget()

    # class: settings
    def settings(self):
        if isinstance(STORAGE.Setting.ON, tk.Toplevel):
            STORAGE.Setting.ON.lift()
            return
        Utilities.writelog('Settings opened', ('', '\n', True))

        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton, self.startClickButton]:
            widget.configure(state='disabled')
        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        settingWindow = STORAGE.Setting.ON = tk.Toplevel(self)
        settingWindow.title('Settings')
        settingWindow.resizable(False, False)

        settingWindow.geometry(f'+{self.winfo_x() + self.winfo_width() + 10}+{self.winfo_y()}')
        self.bind('<Configure>', lambda _: settingWindow.geometry(
            f'+{self.winfo_x() + self.winfo_width() + 10}+{self.winfo_y()}') if settingWindow.winfo_exists() else None)

        allSettingsFrame = tk.Frame(settingWindow)
        allSettingsFrame.grid(row=3, column=3, padx=10, pady=10)

        # SETTING 1: Hotkeys
        setting1_hotkey_frame = ttk.LabelFrame(allSettingsFrame, text='Hotkeys')
        setting1_hotkey_frame.grid(row=3, column=3, sticky='ew', pady=(0, 5))

        _setting1_hotkey_frame = tk.Frame(setting1_hotkey_frame)
        _setting1_hotkey_frame.grid(row=3, column=3, padx=15, pady=5)

        hotkeyDisplayEntry = tk.Entry(_setting1_hotkey_frame, width=11)
        hotkeyDisplayEntry.insert(0, '+'.join(
            [key.capitalize() for key in STORAGE.Setting.trigger_hotkey.lower().split('+')]))
        hotkeyDisplayEntry.grid(row=3, column=3, sticky='ns', padx=(0, 5))

        def inputHotkeys():
            settingWindow.focus()
            chooseHotkeysButton.configure(state='disabled')
            Utilities.writelog('Listening for hotkey input..', ('', '\n', True))

            hotkeyDisplayEntry.delete(0, tk.END)
            hotkeyDisplayEntry.insert(0, 'Listening...')
            hotkeyDisplayEntry.configure(state='disabled')

            def readHotkeys():
                hotkey = '+'.join(key.capitalize() for key in keyboard.read_hotkey().split('+'))
                Utilities.writelog(f'Hotkey detected: {hotkey} (result might be incorrect)', ('', '\n', True))

                chooseHotkeysButton.configure(state='normal')
                hotkeyDisplayEntry.configure(state='normal')
                hotkeyDisplayEntry.delete(0, tk.END)
                hotkeyDisplayEntry.insert(0, hotkey)

                invalidKeysLabel.configure(text='')
                saveButton.configure(state='normal')
                if hotkey.replace(' ', '').strip().lower() in Utilities.add_default_hotkeys(True):
                    invalidKeysLabel.configure(text='Corrupted!')
                    saveButton.configure(state='disabled')
                    Utilities.writelog('There\'s already a default hotkey with the same keys (error: corrupted hotkey)',
                                       ('', '\n', True), logType='WARNING')

            threading.Thread(target=readHotkeys).start()

        def check_key_validation(_):
            allChecked = True
            invalidKeysLabel.configure(text='')
            saveButton.configure(state='normal')
            for key in hotkeyDisplayEntry.get().lower().split('+'):
                if not pyautogui.isValidKey(key):
                    saveButton.configure(state='disabled')
                    invalidKeysLabel.configure(text='Invalid!')
                    allChecked = False
                    Utilities.writelog('Invalid manual hotkey inputted', ('', '\n', True))
            if hotkeyDisplayEntry.get().replace(' ', '').strip().lower() in Utilities.add_default_hotkeys(True):
                invalidKeysLabel.configure(text='Corrupted!')
                saveButton.configure(state='disabled')
                Utilities.writelog('There\'s already a default hotkey with the same keys (error: corrupted hotkey)',
                                   ('', '\n', True), logType='WARNING')

            if allChecked:
                print(STORAGE.Setting.trigger_hotkey)

        hotkeyDisplayEntry.bind('<KeyRelease>', check_key_validation)

        chooseHotkeysButton = ttk.Button(_setting1_hotkey_frame, text='Input', width=5, command=inputHotkeys)
        chooseHotkeysButton.grid(row=3, column=5, padx=(5, 0))

        invalidKeysLabel = tk.Label(_setting1_hotkey_frame, text='', fg='red')
        invalidKeysLabel.grid(row=3, column=7, padx=5)

        # SETTING 2: Pick position dialog
        setting2_pickposition_frame = ttk.LabelFrame(allSettingsFrame, text='Pick-position dialog')
        setting2_pickposition_frame.grid(row=5, column=3, sticky='ew', pady=(0, 5))

        _setting2_pickposition_frame = tk.Frame(setting2_pickposition_frame)
        _setting2_pickposition_frame.grid(row=3, column=3, padx=15, pady=5)

        transparencyFrame = tk.Frame(_setting2_pickposition_frame)
        transparencyFrame.grid(row=3, column=3)

        transparentVar = tk.IntVar(value=STORAGE.Setting.transparency * 10)
        tk.Label(transparencyFrame, text='Transparency:').grid(row=21, column=3, sticky='w', padx=5)
        slider1_transparent = ttk.Scale(transparencyFrame, from_=1, to=10, orient='horizontal', variable=transparentVar,
                                        command=lambda _: transparencyDisplayLabel.configure(
                                            text=int(slider1_transparent.get()) / 10))
        slider1_transparent.grid(row=21, column=5, sticky='ew')
        transparencyDisplayLabel = tk.Label(transparencyFrame, text=f'{slider1_transparent.get() / 10}')
        transparencyDisplayLabel.grid(row=21, column=7, padx=5)

        ttk.Button(_setting2_pickposition_frame, text='Open', command=lambda: self.customPositionDialog(True)).grid(
            row=5, column=3, sticky='ew', pady=5)

        # SETTING n: Miscellaneous
        setting10_miscellaneous_frame = ttk.LabelFrame(allSettingsFrame, text='Miscellaneous')
        setting10_miscellaneous_frame.grid(row=21, column=3, sticky='ew')

        _setting10_miscellaneous_frame = tk.Frame(setting10_miscellaneous_frame)
        _setting10_miscellaneous_frame.grid(row=3, column=3)

        # # n: Misc 1 - Always on top
        topmostVar = tk.IntVar()
        checkbox1_topmost = tk.Checkbutton(_setting10_miscellaneous_frame, text='Always on top', variable=topmostVar,
                                           onvalue=1, offvalue=0)
        checkbox1_topmost.select() if STORAGE.Setting.isTopmost else None
        checkbox1_topmost.grid(row=3, column=3, sticky='w')

        # # n: Misc 2 - Auto pop up
        autopopupVar = tk.IntVar()
        checkbox2_failsafe = tk.Checkbutton(_setting10_miscellaneous_frame, text='Auto extra dialog/pop-up',
                                            variable=autopopupVar, onvalue=1, offvalue=0)
        checkbox2_failsafe.select() if STORAGE.Setting.isAutoPopup else None
        checkbox2_failsafe.grid(row=5, column=3, sticky='w')

        # # n: Misc 3 - Fail-safe
        failsafeVar = tk.IntVar()
        checkbox3_failsafe = tk.Checkbutton(_setting10_miscellaneous_frame, text='Fail-safe system',
                                            variable=failsafeVar, onvalue=1, offvalue=0)
        checkbox3_failsafe.select() if STORAGE.Setting.isFailsafe else None
        checkbox3_failsafe.grid(row=7, column=3, sticky='w')

        def save():
            keyboard.unregister_all_hotkeys()
            Utilities.add_default_hotkeys()
            keyboard.add_hotkey(STORAGE.Setting.trigger_hotkey,
                                lambda: root.stopClicking() if STORAGE.CLICKING else root.startClicking())

            STORAGE.Setting.trigger_hotkey = hotkeyDisplayEntry.get()
            STORAGE.Setting.isTopmost = True if topmostVar.get() else False
            STORAGE.Setting.isFailsafe = True if failsafeVar.get() else False
            STORAGE.Setting.isAutoPopup = True if autopopupVar.get() else False
            STORAGE.Setting.transparency = int(slider1_transparent.get()) / 10

            self.attributes('-topmost', STORAGE.Setting.isTopmost)
            pyautogui.FAILSAFE = STORAGE.Setting.isFailsafe

            Utilities.writelog('All the variables are saved locally', ('', '\n', True))

        def closing():
            STORAGE.Setting.ON = False
            settingWindow.destroy()

            for _widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                            self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox,
                            self.clickTypeOptionCombobox,
                            self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                            self.mousePositionRadiobutton, self.customPositionRadiobutton, self.startClickButton]:
                _widget.configure(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                  self.mouseButtonOptionCombobox] else 'normal')

        def on_exit(saving: bool = True, on_quit: bool = False):
            if on_quit:
                if not messagebox.askyesno('Closing Settings',
                                           'Are you sure that you want to close settings? Everything won\'t be saved.',
                                           default='no', parent=settingWindow, icon='warning'):
                    return

            if saving:
                save()
                Utilities.writelog('Settings closed (saving: true)', ('', '\n', True))
            else:
                Utilities.writelog('Settings closed (saving: false)', ('', '\n', True))

            closing()

        saveSettingsFrame = tk.Frame(settingWindow)
        saveSettingsFrame.grid(row=100, column=3, sticky='ew', pady=(0, 10))
        saveSettingsFrame.grid_columnconfigure(3, weight=1)

        saveButtonStyle = ttk.Style()
        saveButtonStyle.configure('save.TButton', foreground='darkgreen', font=('', 9, 'bold'))

        saveButton = ttk.Button(saveSettingsFrame, text='Save & Quit', style='save.TButton', command=on_exit)
        saveButton.grid(row=3, column=3, ipadx=15)

        settingWindow.protocol('WM_DELETE_WINDOW', lambda: on_exit(False, True))
        Utilities.writelog('Settings window initialized', ('', '\n', True))

    # class: Position.custom
    def customPositionDialog(self, fromSetting=False):
        if not fromSetting and not STORAGE.Setting.isAutoPopup:
            return
        Utilities.writelog('Custom-position dialog opened', ('', '\n', True))

        self.focus()
        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.configure(state='disabled')

        askPositionDialog = tk.Toplevel(self)
        askPositionDialog.title('')
        askPositionDialog.geometry('+' + self.geometry().split('+', maxsplit=1)[1])
        askPositionDialog.resizable(False, False)

        askPositionDialog.grab_set()
        askPositionDialog.focus()

        positionType = tk.StringVar(value='manual')
        positions = STORAGE.FIXED_POSITIONS

        alldialogFrame = ttk.Frame(askPositionDialog)
        alldialogFrame.grid(row=3, column=3, padx=15, pady=(15, 0), ipadx=5, ipady=5)
        alldialogFrame.grid_columnconfigure(3, weight=1)

        mainCustomPositionFrame = ttk.LabelFrame(alldialogFrame, text='Manual position', labelanchor='n')
        mainCustomPositionFrame.grid(row=3, column=3, ipadx=15, ipady=5, sticky='ew')
        mainCustomPositionFrame.grid_columnconfigure(3, weight=1)

        choosePositionFrame = ttk.Frame(mainCustomPositionFrame)
        choosePositionFrame.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_radiobutton = ttk.Radiobutton(choosePositionFrame, value='manual', variable=positionType,
                                                          command=lambda: [xCustomPositionEntry.focus(),
                                                                           update_text_on_return(),
                                                                           choosePositionWithMouseButton.configure(
                                                                               state='disabled')])
        choosePositionFrame_radiobutton.grid(row=3, column=1)

        ttk.Label(choosePositionFrame, text='x=').grid(row=3, column=2, sticky='e')
        xCustomPositionEntry = ttk.Entry(choosePositionFrame, width=4)
        xCustomPositionEntry.grid(row=3, column=3, sticky='w')

        ttk.Label(choosePositionFrame, text=',  y=', anchor='e').grid(row=3, column=4, sticky='e')
        yCustomPositionEntry = ttk.Entry(choosePositionFrame, width=4)
        yCustomPositionEntry.grid(row=3, column=5, sticky='w')
        ttk.Label(choosePositionFrame, text=',  y=', anchor='e').grid(row=3, column=4, sticky='e')

        ttk.Label(alldialogFrame, text='or').grid(row=5, column=3, pady=5)

        choosePositionFrame_withMouse = ttk.LabelFrame(alldialogFrame, text='Pick position', labelanchor='n')
        choosePositionFrame_withMouse.grid(row=7, column=3, ipadx=15, ipady=5, sticky='ew')
        choosePositionFrame_withMouse.grid_columnconfigure(3, weight=1)

        _choosePositionFrame_withMouse = ttk.Frame(choosePositionFrame_withMouse)
        _choosePositionFrame_withMouse.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_withMouse_radiobutton = ttk.Radiobutton(_choosePositionFrame_withMouse, value='picker',
                                                                    variable=positionType,
                                                                    command=lambda: [askPositionDialog.focus(),
                                                                                     showPositionsLabel.configure(
                                                                                         text='Position: x/y=Custom'),
                                                                                     choosePositionWithMouseButton.configure(
                                                                                         state='normal'),
                                                                                     submitPositionButton.configure(
                                                                                         state='disabled')])
        choosePositionFrame_withMouse_radiobutton.grid(row=3, column=2, sticky='e')

        choosePositionWithMouseButton = ttk.Button(_choosePositionFrame_withMouse, text='Choose position',
                                                   command=lambda: choose_position_by_mouse(), state='disabled')
        choosePositionWithMouseButton.grid(row=3, column=3, ipadx=5)

        submitPositionFrame = ttk.Frame(alldialogFrame)
        submitPositionFrame.grid(row=9, column=3, sticky='sew', pady=(20, 5))
        submitPositionFrame.grid_columnconfigure(3, weight=1)

        showPositionsLabel = ttk.Label(submitPositionFrame, text='Position: x=None; y=None')
        showPositionsLabel.grid(row=3, column=3, padx=5, columnspan=2)

        submitPositionButton = ttk.Button(submitPositionFrame, text='Submit', state='disabled',
                                          command=lambda: submit_position())
        submitPositionButton.grid(row=5, column=3, padx=5, sticky='sew')

        redcancelStyle = ttk.Style()
        redcancelStyle.configure('cancel.TButton', foreground='red')

        cancelbutton = ttk.Button(submitPositionFrame, text='Cancel', command=lambda: on_exit(), width=7,
                                  style='cancel.TButton')
        cancelbutton.grid(row=5, column=4)

        def update_text_on_return():
            nonlocal positions
            pos = [i if i.strip() != '' else 'None' for i in (xCustomPositionEntry.get(), yCustomPositionEntry.get())]
            positions = pos[0], pos[1]
            showPositionsLabel.configure(
                text=f'Position: x={pos[0][:4]}{"..." if len(pos[0]) > 4 else ""}; y={pos[1][:4]}{"..." if len(pos[1]) > 4 else ""}')

        def checkSubmitable(event=False):
            if not event:
                askPositionDialog.focus()
            submitPositionButton.configure(state='disabled')
            if positionType.get().strip() != '':
                if xCustomPositionEntry.get().isdigit() and yCustomPositionEntry.get().isdigit():
                    submitPositionButton.configure(state='normal')

            if event and positionType.get() == 'manual':
                update_text_on_return()

        def choose_position_by_mouse():
            transparent_layer = tk.Toplevel(askPositionDialog)
            transparent_layer.overrideredirect(True)
            transparent_layer.attributes('-alpha', STORAGE.Setting.transparency)
            transparent_layer.state('zoomed')

            transparent_layer.attributes('-topmost', True)
            transparent_layer.configure(cursor='crosshair')
            transparent_layer.focus()

            def quitChoose(_):
                nonlocal positions
                positions = mousex, mousey

                showPositionsLabel.configure(text=f'Position: x={mousex}; y={mousey}')
                submitPositionButton.configure(state='normal')
                transparent_layer.destroy()

            mousex, mousey = 0, 0

            displaying = tk.Frame(transparent_layer, bg='yellow')
            displayPosition = tk.Label(displaying, text=f'x={mousex}; y={mousey}', bg='yellow',
                                       font=('Calibri', 11, 'bold'))
            displayPosition.grid(row=3, column=3, padx=15)
            displaying.grid_columnconfigure(3, weight=1)

            transparent_layer.bind('<Button-1>', quitChoose)

            while transparent_layer.winfo_exists():
                mousex, mousey = pyautogui.position()
                displayPosition.configure(text=f'x={mousex}; y={mousey}')
                displaying.place(x=10, y=10)

                if keyboard.is_pressed('esc'):
                    transparent_layer.destroy()
                    break

                transparent_layer.update()

        def submit_position():
            if not pyautogui.onScreen(*map(int, positions)):
                messagebox.showwarning('Warning', 'Your chosen position is outside the screen.',
                                       parent=askPositionDialog)
                return
            STORAGE.FIXED_POSITIONS = tuple(map(int, positions))
            self.customPositionRadiobutton.configure(text=f'Custom ({",".join(map(str, positions))})')
            askPositionDialog.destroy()

            if not fromSetting:
                for _widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                                self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox,
                                self.clickTypeOptionCombobox, self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton,
                                self.unlimitedRepeatRadiobutton, self.mousePositionRadiobutton,
                                self.customPositionRadiobutton]:
                    _widget.configure(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                      self.mouseButtonOptionCombobox] else 'normal')

            Utilities.writelog(
                f'Closed custom-position dialog. Fixed position chosen: ({",".join(map(str, positions))})',
                ('', '\n', True))

        xCustomPositionEntry.bind('<KeyRelease>', checkSubmitable)
        yCustomPositionEntry.bind('<KeyRelease>', checkSubmitable)
        xCustomPositionEntry.focus()

        def on_exit():
            askPositionDialog.destroy()
            if not fromSetting:
                for _widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                                self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox,
                                self.clickTypeOptionCombobox, self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton,
                                self.unlimitedRepeatRadiobutton, self.mousePositionRadiobutton,
                                self.customPositionRadiobutton]:
                    _widget.configure(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                      self.mouseButtonOptionCombobox] else 'normal')
            Utilities.writelog('Custom-position dialog closed. No position was chosen.', ('', '\n', True))

        askPositionDialog.protocol('WM_DELETE_WINDOW', on_exit)

    # class: Interval
    def bindHourChosen(self, value: str):
        if value == '':
            pass
        if value != '' and not value.isdigit() or value.isdigit() and len(value) > 2:
            return False
        return True

    def bindMinuteChosen(self, value: str):
        if value == '':
            pass
        if value != '':
            if len(value) > 2:
                return False
            if not value.isdigit():
                return False
            if int(value) > 59:
                return False
        return True

    def bindSecondChosen(self, value: str):
        if value == '':
            pass
        if value != '':
            if len(value) > 2:
                return False
            if not value.isdigit():
                return False
            if int(value) > 59:
                return False
        return True

    def bindMillisecondChosen(self, value: str):
        if value == '':
            pass
        else:
            if len(value) > 3:
                return False
            if not value.isdigit():
                return False
        return True

    def bindChosenAll(self, event):
        self.intervals = [
            str(int(i.get()) if i.get().isdigit() else i.get()).zfill(
                2 if self.intervalWidgets.index(i) != len(self.intervalWidgets) - 1 else 3) for i in
            self.intervalWidgets]
        if str(event.type) != '3':
            event.widget.master.focus()
            event.widget.set(self.intervals[self.intervalWidgets.index(event.widget)])
        self.showInterval.configure(
            text=f'Interval: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}')
        Utilities.writelog(
            f'Set the interval to: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}',
            ('', '\n', True))

    # class: Click options


def background_tasks():
    Utilities.writelog('Background tasks started', ('', '\n', True))
    while STORAGE.RUNNING and root.winfo_exists():
        if root.positionVar.get() == 'mouse':
            root.mousePositionRadiobutton.configure(text='Current ({0}, {1})'.format(*pyautogui.position()))
        else:
            root.mousePositionRadiobutton.configure(text='Current (0, 0)')

        if keyboard.is_pressed('esc') or keyboard.is_pressed('enter'):
            try:
                root.nametowidget(root.grab_current()).focus() if root.grab_current() else root.focus()
            except KeyError as backgroundKeyError:
                Utilities.writelog(f'{type(backgroundKeyError).__name__} {backgroundKeyError}',
                                   built_content=('', '\n', True), logType='ERROR')
            if root.limitedRepeatSpinbox.get().strip() == '':
                root.limitedRepeatSpinbox.set(1)
        root.update()

        print('background thingy')

    print('ended?')
    Utilities.writelog(f'Successfully terminated all running tasks, {__project__} {__version__} was fully closed',
                       ('', '\n}\n', True))
    return


def on_window_exit():
    if keyboard.is_pressed('shift'):
        root.withdraw()
        return
    if not keyboard.is_pressed('ctrl') and STORAGE.Setting.isAutoPopup:
        if not messagebox.askyesno(f'Closing {__project__}', f'Are you sure to close {__project__} {__version__}?'):
            return
    save_data()
    root.destroy()
    STORAGE.RUNNING = False

    Utilities.writelog(f'Closed {__project__} {__version__}. Terminating the background tasks..', ('', '\n', True))


root = Application()
threading.Thread(target=background_tasks).start()

keyboard.add_hotkey(STORAGE.Setting.trigger_hotkey,
                    lambda: root.stopClicking() if STORAGE.CLICKING else root.startClicking())
Utilities.add_default_hotkeys()

root.protocol('WM_DELETE_WINDOW', on_window_exit)
root.mainloop()
