from tkinter import ttk, messagebox, filedialog
import tkinter as tk

from itertools import permutations, chain
from PIL import Image
from tktooltip import ToolTip
import speech_recognition as sr
import pyautogui
import threading
import keyboard
import random
import mouse
import time
import json

import platform
import os

__project__ = 'JetClicker'
__version__ = '0.5.1'

__author__ = 'Hung'
__runtime__ = time.strftime('%T')
__rundate__ = time.strftime('%A %d-%b-%Y (%d/%m/%Y)')
__startFlag__ = time.perf_counter()

if not platform.system().lower().startswith('win'):
    if not messagebox.askyesno('Important Warning',
                               f'Many features here might be broken because your current OS is not supported, or outdated.\n\nInformation:\n - Operating System: {platform.system()}\n - Release: {platform.release()}\n - Version: {platform.version()}\n\nConfiguration required:\n - Operating System: Windows\n - Version/Release: 10 or above\n\nWould you like to continue using {__project__}?',
                               icon='warning', default='no'):
        quit()


class Utilities:
    @staticmethod
    def add_default_hotkeys(return_: bool = False):
        keyboard.add_hotkey('ctrl+shift+alt+r', Utilities.reset_all)
        keyboard.add_hotkey('ctrl+shift+r', Utilities.Dialogs.Terminal.dialogs)

        if return_:
            return ['+'.join(x for x in i) for i in list(chain.from_iterable(
                permutations(hk.split('+'), r=len(hk.split('+'))) for hk in
                ['ctrl+alt+s', 'ctrl+shift+alt+r', 'ctrl+alt+b']))]

        def back_to_screen():
            if not STORAGE.BACKGROUND:
                return
            STORAGE.BACKGROUND = False
            root.deiconify()

        if not STORAGE.Extension.ON:
            keyboard.add_hotkey('ctrl+alt+s', root.settings)
            keyboard.add_hotkey('ctrl+alt+b', back_to_screen)

        Utilities.writelog('Default hotkeys initialized', ('', '\n', True))

    @staticmethod
    def add_trigger_hotkey():
        keyboard.add_hotkey(STORAGE.Setting.trigger_hotkey,
                            lambda: root.stopClicking() if STORAGE.CLICKING else root.startClicking())

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
    def child_geometry(window, master, do=True):
        result = '+' + master.geometry().split('+', maxsplit=1)[1]
        if do:
            window.geometry(result)
        return result

    @staticmethod
    def reset_all(message: bool = True):
        if message and not messagebox.askyesno(f'Reset {__project__} {__version__}',
                                               f'Are you sure that you want to reset all data of {__project__}?',
                                               icon='warning'):
            return

        STORAGE.FIXED_POSITIONS = (0, 0)
        STORAGE.LOCATE_SCREEN = (False, '')

        STORAGE.General.current_click = 0
        STORAGE.General.current_scroll = 0
        STORAGE.General.total_clicks = 0
        STORAGE.General.total_scroll = 0

        STORAGE.Setting.trigger_hotkey = 'ctrl+q'
        STORAGE.Setting.clickArea = [False, 0, 0, 0, 0]
        STORAGE.Garbage.tk_clickArea = [0, 0, 0, 0]
        STORAGE.Setting.isRandomIntervalList = [False, 0, 0]
        STORAGE.Setting.isTopmost = False
        STORAGE.Setting.isFailsafe = True
        STORAGE.Setting.isAutoPopup = True
        STORAGE.Setting.wheelSize = 100
        STORAGE.Setting.confidence = 0.8
        STORAGE.Setting.transparency = 0.5
        STORAGE.Setting.isVoiceCommand = True
        STORAGE.Setting.startVoiceCommands = ['click', 'start']
        STORAGE.Setting.stopVoiceCommands = ['stop']

        STORAGE.Extension.MouseRecorder.recordTriggerHotkey = 'f5'
        STORAGE.Extension.MouseRecorder.playbackTriggerHotkey = 'f6'
        STORAGE.Extension.MouseRecorder.playbackSpeed = 1
        STORAGE.Extension.MouseRecorder.isClicksRecorded = True
        STORAGE.Extension.MouseRecorder.isMovementsRecorded = True
        STORAGE.Extension.MouseRecorder.isWheelrollsRecorded = True
        STORAGE.Extension.MouseRecorder.isInsertedEvents = False

        root.title(f'{__project__} {__version__}')
        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()
        Utilities.add_trigger_hotkey()

        if message and messagebox.askyesno(f'Restart {__project__} {__version__}',
                                           f'Resetted all data. {__project__} needs to be refreshed to see the changes.\nWould you like to refresh now?'):
            Utilities.writelog('Resetted all data', ('', '\n', True))
            Utilities.start(restart=True)

    @staticmethod
    def start(restart: bool = False):
        global root, backgroundThread
        if restart:
            for _widget in root.winfo_children():
                if isinstance(_widget, tk.Toplevel):
                    _widget.destroy()
                    STORAGE.Setting.ON = False
                    STORAGE.Extension.ON = False
                    STORAGE.Extension.MouseRecorder.ON = False
                    STORAGE.Extension.CpsCounter.ON = False
                else:
                    _widget.grid_forget()
            root.draw()
            keyboard.unregister_all_hotkeys()
            Utilities.add_trigger_hotkey()
            Utilities.add_default_hotkeys()
            root.geometry(STORAGE.Garbage.root_geometry.split('+')[0])
            Utilities.writelog('Refreshed the GUI', ('', '\n', True))
            return

        root = Application()

        Utilities.add_trigger_hotkey()
        Utilities.add_default_hotkeys()

        for file in STORAGE.PLUGINS:
            if file not in [f for f in os.listdir(r'data\plugins') if f.endswith('.txt')]:
                STORAGE.PLUGINS.remove(file)
        if [f not in STORAGE.PLUGINS for f in os.listdir(r'data\plugins') if f.endswith('.txt')]:
            Utilities.Dialogs.Custom.displayNewpluginsDialog(r'data\plugins', STORAGE.PLUGINS, root)
            root.deiconify()
        for filename in [f for f in os.listdir(r'data\plugins') if f.endswith('.txt')]:
            with open('data\\plugins\\' + filename, 'r') as filerun:
                try:
                    Utilities.writelog(f'Executing plugin: {filename}', ('', '\n', True))
                    exec(filerun.read())
                    Utilities.writelog(f'Executed plugin: {filename}', ('', '\n', True))
                except Exception as plugin_error:
                    messagebox.showerror(f'Plugin: {filename}', f'[{type(plugin_error).__name__}]: {plugin_error}')
                    Utilities.writelog(f'Error in {filename} - [{type(plugin_error).__name__}]: {plugin_error}',
                                       ('', '\n', True))

        backgroundThread = threading.Thread(target=background_tasks)
        backgroundThread.start()

        STORAGE.RUNNING = True

        root.protocol('WM_DELETE_WINDOW', on_window_exit)

        Utilities.writelog(f'All functions are initialized. Successfully launched {__project__} {__version__}',
                           ('', '\n', True))
        root.mainloop()

    @staticmethod
    def listen_to_voice(r):
        def callback(recog: sr.Recognizer, audio):
            if not STORAGE.Setting.isVoiceCommand:
                return
            try:
                print('voice detected...')
                call = recog.recognize_google(audio, language='en', show_all=True)
                print(call)
                if call:
                    cms = [i['transcript'].lower() for i in call['alternative']]
                    if any(q in i for i in cms for q in STORAGE.Setting.startVoiceCommands):
                        r.startClicking()
                    if any(q in i for i in cms for q in STORAGE.Setting.stopVoiceCommands):
                        r.stopClicking()
            except sr.exceptions.RequestError:
                if messagebox.askyesno(f'Connection error',
                                       f'Unable to make a request to Google Speech Recognition service. Would you like to retry?',
                                       icon='warning'):
                    callback(recog, audio)
            return

        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        return recognizer.listen_in_background(mic, callback)

    @staticmethod
    def insert_disabledtextwidget(widget, content, index='end'):
        widget.configure(state='normal')
        widget.insert(index, content)
        widget.configure(state='disabled')

    @staticmethod
    def set_window_icon(window: tk.Tk | tk.Toplevel, path: str = 'assets\\icons\\logo.ico'):
        window.iconbitmap(path)

    class Function:
        @staticmethod
        def seconds_to_formatted(seconds, with_hour: bool = False):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            remaining_seconds = seconds % 60
            milliseconds = int((remaining_seconds % 1) * 1000)
            remaining_seconds += milliseconds // 1000
            milliseconds %= 1000

            if with_hour:
                result = "{:02}:{:02}:{:02}.{:03}".format(hours, minutes, int(remaining_seconds), milliseconds)
            else:
                result = "{:02}:{:02}.{:03}".format(minutes, int(remaining_seconds), milliseconds)

            return result

        @staticmethod
        def is_position_inside_box(position, x1, y1, x2, y2):
            x, y = position

            return x1 <= x <= x2 and y1 <= y <= y2

        @staticmethod
        def isfloat(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        @staticmethod
        def show_files(folder_path, extension=''):
            return [f for f in os.listdir(folder_path) if f.endswith(extension)]

    class Dialogs:
        @staticmethod
        class Custom:
            @staticmethod
            def displayFileDialog(filename, folder, master):
                Utilities.writelog(f'Displaying {filename} with FileReader', ('', '\n', True))
                try:
                    Utilities.writelog(f'Opening {filename}..', ('', '\n', True))
                    with open(folder + '\\' + filename, 'r') as _file:
                        content = _file.read()
                    Utilities.writelog(f'Successfully collected contents of {filename}', ('', '\n', True))
                except FileNotFoundError:
                    messagebox.showerror('FileNotFound',
                                         f'Something went wrong while open {filename}\nMake sure that the file still exists.')
                    Utilities.writelog(f'Couldn\'t find \"{filename}\" in the directory', ('', '\n', True))
                    return False

                file_reader_toplevel = tk.Toplevel(master)
                file_reader_toplevel.title(f'{filename} - FileReader')
                file_reader_toplevel.grab_set()
                Utilities.set_window_icon(file_reader_toplevel)

                text_widget = tk.Text(file_reader_toplevel, wrap='word', state='disabled')
                text_widget.grid(row=3, column=3, sticky='nsew')

                Utilities.insert_disabledtextwidget(text_widget, content)
                _scrollbar = tk.Scrollbar(file_reader_toplevel, orient='vertical', command=text_widget.yview)
                _scrollbar.grid(row=3, column=4, sticky='ns')
                text_widget.configure(yscrollcommand=_scrollbar.set)
                Utilities.writelog(f'Displayed contents of {filename}', ('', '\n', True))

                return True

            @staticmethod
            def displayNewpluginsDialog(directory_path, storage, master, block=True):
                filelist = [f for f in os.listdir(directory_path) if f.endswith('.txt') and f not in storage]
                if not filelist:
                    return
                Utilities.writelog(f'Detected {len(filelist)} new plugins: {", ".join(filelist)}', ('', '\n', True),
                                   logType='WARNING')
                master.withdraw()
                newpluginwarningWindow = tk.Toplevel(master)
                newpluginwarningWindow.title('Warning')
                newpluginwarningWindow.grid_columnconfigure(3, weight=1)
                Utilities.set_window_icon(newpluginwarningWindow)

                tk.Label(newpluginwarningWindow, text='WARNING', foreground='red', font=('Calibri', 20, 'bold')).grid(
                    row=3, column=3)
                tk.Label(newpluginwarningWindow, text=f'We\'ve detected {len(filelist)} new plugins').grid(row=4,
                                                                                                           column=3,
                                                                                                           padx=50)
                newpluginListbox = tk.Listbox(newpluginwarningWindow, height=7)
                newpluginListbox.grid(row=5, column=3, sticky='ew', pady=15)

                warningActionFrame = tk.Frame(newpluginwarningWindow)
                warningActionFrame.grid(row=7, column=3)

                # noinspection PyUnresolvedReferences
                def closeapp():
                    root.destroy()
                    Utilities.writelog(f'Closed {__project__} {__version__}', ('', '\n}\n', True))
                    print('Closed.')
                    os._exit(0)

                def proceed(save=True):
                    if save:
                        storage.extend(filelist)
                        Utilities.writelog(f'Warning closed by user', ('', '\n', True))
                    else:
                        if not messagebox.askyesno(
                                'Warning',
                                'Make sure all your plugins are safe to run. Closing this window will execute the plugins.\n\nDo you want to proceed?',
                                icon='warning', parent=newpluginwarningWindow):
                            return
                        Utilities.writelog(f'Warning ignored by user', ('', '\n', True))
                    newpluginwarningWindow.destroy()

                ttk.Button(warningActionFrame, text='Continue', command=proceed, width=10).grid(row=3, column=3)
                ttk.Button(warningActionFrame, text='Exit', command=closeapp, width=10).grid(row=3, column=5)
                ttk.Button(warningActionFrame, text='Open plugin folder',
                           command=lambda: os.startfile(r'data\plugins')).grid(row=5, column=3, columnspan=3,
                                                                               pady=(0, 15), sticky='ew')

                for filename in filelist:
                    newpluginListbox.insert('end', filename)

                def on_select(_):
                    selected_index = newpluginListbox.curselection()
                    if selected_index:
                        selected_file = newpluginListbox.get(selected_index)
                        Utilities.Dialogs.Custom.displayFileDialog(selected_file, r'data\plugins',
                                                                   newpluginwarningWindow)

                newpluginListbox.bind('<Double-1>', on_select)
                newpluginwarningWindow.protocol('WM_DELETE_WINDOW', lambda: proceed(save=False))
                if block:
                    newpluginwarningWindow.wait_window()

        @staticmethod
        class Terminal:
            @staticmethod
            def dialogs(master=None):
                if master is None:
                    master = root
                    root.menuFrame.grid_forget()
                STORAGE.Garbage.isTerminalOn = True
                Utilities.writelog('Opened terminal/console window', ('', '\n', True))

                terminalWindow = tk.Toplevel(master)
                terminalWindow.title(f'Terminal: {__project__} {__version__} [BETA]')
                terminalWindow.resizable(False, False)
                terminalWindow.attributes('-topmost', STORAGE.Setting.isTopmost)
                Utilities.set_window_icon(terminalWindow)
                mainCommandFrame = tk.Frame(terminalWindow)
                mainCommandFrame.grid(row=3, column=3, padx=15, pady=5)

                def sendcommand(_=None):
                    Utilities.Dialogs.Terminal.processCommand(commandEntry.get().rstrip(), outputTextbox,
                                                              commandEntry)

                tk.Label(mainCommandFrame, text='Send command:').grid(row=3, column=3, columnspan=3)
                commandEntry = ttk.Combobox(mainCommandFrame)
                commandEntry.grid(row=5, column=3)
                ttk.Button(mainCommandFrame, text='Send',
                           command=sendcommand, width=5).grid(row=5,
                                                              column=5,
                                                              padx=3)
                commandEntry.bind('<Return>', sendcommand)

                commandOutputFrame = tk.Frame(terminalWindow)
                commandOutputFrame.grid(row=5, column=3)
                outputScrollbar = ttk.Scrollbar(commandOutputFrame)
                outputScrollbar.grid(row=3, column=5, sticky='ns')
                outputTextbox = tk.Text(commandOutputFrame, width=75, height=25, yscrollcommand=outputScrollbar.set)
                outputTextbox.grid(row=3, column=3)
                outputScrollbar.configure(command=outputTextbox.yview)

                def closeTerminal():
                    terminalWindow.destroy()
                    STORAGE.Garbage.isTerminalOn = False
                    Utilities.writelog('Closed terminal/console window', ('', '\n', True))

                terminalWindow.protocol('WM_DELETE_WINDOW', closeTerminal)
                commandEntry.focus()

            @staticmethod
            def processCommand(command: str, textbox: tk.Text, focus_entry=None):
                Utilities.writelog(f'Command sent: {command}', ('', '\n', True))
                return_text = '\n'
                try:
                    if not command:
                        return
                    elif command == 'exit':
                        textbox.master.master.destroy()
                        return
                    elif command.startswith('python '):
                        exec(command.replace('python ', '', 1))
                    elif command.startswith('python.eval'):
                        return_text = f'{eval(command.replace("python.eval ", "", 1))}\n' + return_text
                    elif command.startswith(f'{__project__.lower()} '):
                        command2 = command.replace(f'{__project__.lower()} ', '', 1).strip()
                        if not command2:
                            return_text = f'v{__version__} - {time.strftime("%T")} - [{__author__}]\n' + return_text
                        elif command2 in ['restart']:
                            Utilities.start(restart=True)
                            return_text = 'Updated all available frames.\n' + return_text
                        elif command2 in ['reset']:
                            return_text = 'Resetted all data.\n' + return_text
                            Utilities.reset_all(message=False)
                        elif command2 in ['add_default_hotkeys', 'add_default_hotkey']:
                            Utilities.add_default_hotkeys()
                        elif command2 in ['default_hotkeys_combinations']:
                            return_text = f'{Utilities.add_default_hotkeys(True)}\n' + return_text
                        elif command2 in ['add_trigger_hotkey', 'add_trigger_hotkeys']:
                            Utilities.add_trigger_hotkey()
                        elif command2 in ['trigger_hotkey', 'trigger_hotkeys']:
                            return_text = f'{STORAGE.Setting.trigger_hotkey}\n' + return_text
                        else:
                            return_text = f'[{__project__.lower()}] Unknown command: {command2}\n' + return_text
                    else:
                        return_text = f'Unknown command: {command}\n' + return_text
                except Exception as command_error:
                    return_text = f'[{type(command_error).__name__}]: {command_error}\n' + return_text
                textbox.after(10,
                              lambda: [Utilities.insert_disabledtextwidget(textbox, f'>>> {command}\n' + return_text),
                                       textbox.yview('end'),
                                       Utilities.writelog(f'Console returned: {return_text}', ('', '\n', True))])
                if focus_entry is not None:
                    focus_entry['values'] = list({i: None for i in [command] + list(focus_entry['values'])})[:100]
                    focus_entry.set('')
                    focus_entry.focus()


with open(r'data\data.json', 'r') as read_data:
    try:
        Utilities.writelog('Accessing data.json..', ('', '\n', True))
        DATA = json.load(read_data)
        Utilities.writelog('Successfully accessed data.json\'s contents', ('', '\n', True))
    except json.decoder.JSONDecodeError as error:
        messagebox.showerror('Decode Error',
                             'Couldn\'t read data.json file.\nPlease check the data file and try again.')
        Utilities.writelog(
            f'Couldn\'t read data.json file.\n\terror message: ({type(error).__name__}) {error}\n\terror id: {id(error)}',
            ('{\n', '\n}\n', True), logType='ERROR')
        quit()

Utilities.writelog(f'Opened {__project__} {__version__}', ('{\n', '\n', True))


class Storage:
    RUNNING = False
    BACKGROUND = False
    CLICKING = False
    FIXED_POSITIONS = tuple(map(int, DATA[0]['fixed-position']))
    LOCATE_SCREEN = DATA[0]['locate-screen']
    PLUGINS = DATA[0]['plugins']

    class General:
        total_clicks = DATA[1]['total-clicks']
        total_scroll = 0
        current_click = 0
        current_scroll = 0

    class Garbage:
        old_positionVar = ['mouse']
        old_mouseButtonOption = 'Left'
        old_scrollDirection = 'Up'
        tk_clickArea = DATA[2]['clickArea'][1]
        isMasterFocus = False
        isTerminalOn = False
        root_geometry: str = None
        clickButton = 'Left'
        clickType = 'Single'
        last_isVoiceCommand = DATA[2]['voice-commands']['is.voice-command']

        @staticmethod
        def trace_old_positionVar(value):
            STORAGE.Garbage.old_positionVar.append(value)
            STORAGE.Garbage.old_positionVar = STORAGE.Garbage.old_positionVar[-2:]

        @staticmethod
        def trace_old_mouseButtonOption_scrollDirection(value):
            if value.strip().lower() in ['up', 'down']:
                STORAGE.Garbage.old_scrollDirection = value
            else:
                STORAGE.Garbage.old_mouseButtonOption = value

    class Setting:
        ON: bool | tk.Toplevel = False

        isRandomIntervalList = DATA[2]['is.randomIntergerList']
        clickArea = DATA[2]['clickArea'][0]

        trigger_hotkey = DATA[2]['trigger-hotkey']

        isTopmost = DATA[2]['is.topmost']
        isFailsafe = DATA[2]['is.failsafe']
        isAutoPopup = DATA[2]['is.auto-popup']

        wheelSize = DATA[2]['wheelsize']
        confidence = DATA[2]['confidence']
        transparency = DATA[2]['transparency']

        isVoiceCommand = DATA[2]['voice-commands']['is.voice-command']
        startVoiceCommands = DATA[2]['voice-commands']['start-commands']
        stopVoiceCommands = DATA[2]['voice-commands']['stop-commands']

    class Extension:
        ON: bool | tk.Toplevel = False
        version = '1.0.0'

        class MouseRecorder:
            ON: bool | tk.Toplevel = False
            version = '1.0'

            recordTriggerHotkey = 'f5'
            playbackTriggerHotkey = 'f6'
            playbackSpeed = DATA[3]['extensions']['mouse-recorder']['playback-speed']

            isClicksRecorded = DATA[3]['extensions']['mouse-recorder']['is.record-clicks']
            isMovementsRecorded = DATA[3]['extensions']['mouse-recorder']['is.record-movements']
            isWheelrollsRecorded = DATA[3]['extensions']['mouse-recorder']['is.record-wheelrolls']
            isInsertedEvents = DATA[3]['extensions']['mouse-recorder']['is.insert-events']

        class CpsCounter:
            ON: bool | tk.Toplevel = False
            version = '1.0'


STORAGE = Storage
pyautogui.FAILSAFE = STORAGE.Setting.isFailsafe
pyautogui.PAUSE = 0
Utilities.writelog('Variables initialized', ('', '\n', True))


def save_data(data: list | dict = None):
    if data is None:
        data = [
            {
                'category': 'storage',
                'fixed-position': STORAGE.FIXED_POSITIONS,
                'locate-screen': STORAGE.LOCATE_SCREEN,
                'position-type': root.positionType.get(),
                'plugins': STORAGE.PLUGINS
            },
            {
                'category': 'general',
                'total-clicks': STORAGE.General.total_clicks,
                'total-scrolls': STORAGE.General.total_scroll,
                'latest-clicks': STORAGE.General.current_click,
                'latest-scrolls': STORAGE.General.current_scroll
            },
            {
                'category': 'settings',
                'is.randomIntergerList': STORAGE.Setting.isRandomIntervalList,
                'trigger-hotkey': STORAGE.Setting.trigger_hotkey,
                'is.topmost': STORAGE.Setting.isTopmost,
                'is.failsafe': STORAGE.Setting.isFailsafe,
                'is.auto-popup': STORAGE.Setting.isAutoPopup,
                'wheelsize': STORAGE.Setting.wheelSize,
                'confidence': STORAGE.Setting.confidence,
                'transparency': STORAGE.Setting.transparency,
                'clickArea': [STORAGE.Setting.clickArea, STORAGE.Garbage.tk_clickArea],
                'voice-commands': {
                    'is.voice-command': STORAGE.Setting.isVoiceCommand,
                    'start-commands': STORAGE.Setting.startVoiceCommands,
                    'stop-commands': STORAGE.Setting.stopVoiceCommands
                }
            },
            {
                'category': 'extensions',
                'version': STORAGE.Extension.version,
                'extensions': {
                    'mouse-recorder': {
                        'version': STORAGE.Extension.MouseRecorder.version,
                        'record-trigger-hotkey': STORAGE.Extension.MouseRecorder.recordTriggerHotkey,
                        'playback-trigger-hotkey': STORAGE.Extension.MouseRecorder.playbackTriggerHotkey,
                        'playback-speed': STORAGE.Extension.MouseRecorder.playbackSpeed,
                        'is.record-clicks': STORAGE.Extension.MouseRecorder.isClicksRecorded,
                        'is.record-movements': STORAGE.Extension.MouseRecorder.isMovementsRecorded,
                        'is.record-wheelrolls': STORAGE.Extension.MouseRecorder.isWheelrollsRecorded,
                        'is.insert-events': STORAGE.Extension.MouseRecorder.isInsertedEvents
                    },
                    'cps-counter': {
                        'version': STORAGE.Extension.CpsCounter.version
                    }
                }
            }
        ]

    with open(r'data\data.json', 'w') as write_data:
        json.dump(data, write_data, indent=4)

    Utilities.writelog('Data saved into data.json', ('', '\n', True))


# noinspection PyTypeChecker,PyMethodMayBeStatic
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.spinTimeLabel = None
        self._click_optionFrame = None
        self._click_repeatFrame = None
        self._cursor_positionFrame = None
        self._intervalFrame = None
        self.allMenuFrame = None
        self.click_optionFrame = None
        self.click_repeatFrame = None
        self.clickTypeOptionCombobox = None
        self.cursor_positionFrame = None
        self.customPositionRadiobutton = None
        self.extensionsButton = None
        self.infoButton = None
        self.infoImage = None
        self.intervalFrame = None
        self.intervalHourCombobox = None
        self.intervalMillisecondCombobox = None
        self.intervalMinuteCombobox = None
        self.intervals = [0, 0, 0, 100]
        self.intervalSecondCombobox = None
        self.intervalWidgets = None
        self.limitedRepeatRadiobutton = None
        self.limitedRepeatSpinbox = None
        self.mainFrame = None
        self.menuButton = None
        self.menuColor = None
        self.menuFrame = None
        self.menuImage = None
        self.mouseButtonOptionCombobox = None
        self.mouseImage = None
        self.mousePositionRadiobutton = None
        self.positionType = tk.StringVar(value=(lambda x: x if x == 'locate' else 'manual')(DATA[0]['position-type']))
        self.positionVar = tk.StringVar(value='mouse')
        self.randomPositionVar = tk.IntVar(value=0)
        self.repeatVar = None
        self.repeatVar = tk.StringVar(value='unlimited')
        self.runFrame = None
        self.settingButton = None
        self.settingImage = None
        self.showInterval = None
        self.spinTime = 1
        self.startClickButton = None
        self.stopClickButton = None
        self.terminalButton = None
        self.terminalImage = None
        self.unlimitedRepeatRadiobutton = None
        self.draw()

    def draw(self):
        self.title(f'{__project__} {__version__}')
        self.resizable(False, False)
        self.attributes('-topmost', STORAGE.Setting.isTopmost)
        self.after(250, lambda: Utilities.set_window_icon(self))

        # MAIN FRAME
        self.mainFrame = tk.Frame(self)
        self.mainFrame.grid(row=5, column=3, padx=15, pady=15)

        # # MENU FRAME
        self.menuImage = tk.PhotoImage(file=r'assets\textures\menu.png').subsample(20, 20)
        self.menuButton = tk.Button(self, image=self.menuImage, border=0, background=self.mainFrame.cget('background'),
                                    cursor='hand2',
                                    command=self.menuActions)
        self.menuButton.grid(row=0, column=0, columnspan=100, rowspan=100, sticky='nw', padx=7, pady=3)

        self.menuFrame = tk.Frame(background='gray80', width=100)
        self.menuColor = self.menuFrame.cget('background')

        # # # ALL MENU FRAME
        self.allMenuFrame = tk.Frame(self.menuFrame)
        self.allMenuFrame.grid(row=3, column=3, padx=5, pady=5)

        tk.Button(self.allMenuFrame, image=self.menuImage, border=0, background=self.menuColor,
                  activebackground=self.menuColor,
                  cursor='hand2',
                  command=self.menuActions).grid(row=1, column=3, sticky='ew')

        tk.Label(self.allMenuFrame, text='', background=self.menuColor, font=('Calibri', 1)).grid(row=3, column=3,
                                                                                                  sticky='ew')
        tk.Frame(self.allMenuFrame, background='black', height=2).grid(row=4, column=3, sticky='ew')
        tk.Frame(self.allMenuFrame, background='black', height=2).grid(row=6, column=3, sticky='ew')

        # # # MOUSE RECORD BUTTON
        self.mouseImage = tk.PhotoImage(file=r'assets\textures\mouse.png').subsample(22, 22)
        self.extensionsButton = tk.Button(self.allMenuFrame, background=self.menuColor, activebackground=self.menuColor,
                                          border=0,
                                          image=self.mouseImage, cursor='hand2', command=self.extensions)
        self.extensionsButton.grid(row=5, column=3, ipady=7, sticky='nsew')

        # # # SETTING BUTTON
        self.settingImage = tk.PhotoImage(file=r'assets\textures\setting.png').subsample(22, 22)
        self.settingButton = tk.Button(self.allMenuFrame, background=self.menuColor, activebackground=self.menuColor,
                                       border=0,
                                       image=self.settingImage, cursor='hand2', command=self.settings)
        self.settingButton.grid(row=7, column=3, ipady=7, sticky='nsew')

        # # # INFO BUTTON
        self.infoImage = tk.PhotoImage(file=r'assets\textures\info.png').subsample(19, 19)
        self.infoButton = tk.Button(self.allMenuFrame, background=self.menuColor, activebackground=self.menuColor,
                                    border=0,
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
Current scrolls: {STORAGE.General.current_scroll}
Total clicks: {STORAGE.General.total_clicks}
Total scrolls: {STORAGE.General.total_scroll}

--- MISCELLANEOUS ---
Open time: {__runtime__}
Open date: {__rundate__}
Time elapsed: {Utilities.Function.seconds_to_formatted(time.perf_counter() - __startFlag__, with_hour=True)}'''),
                                                     Utilities.writelog('Closed Credits & Info page',
                                                                        ('', '\n', True))])
        self.infoButton.grid(row=21, column=3, ipady=7, sticky='sew')
        self.terminalImage = tk.PhotoImage(file=r'assets\textures\terminal.png').subsample(23, 23)

        # # INTERVAL FRAME
        self.intervalFrame = ttk.LabelFrame(self.mainFrame, text='Click interval', labelanchor='n')
        self.intervalFrame.grid(row=3, column=3, ipadx=15, ipady=5, sticky='new', columnspan=3)
        self.intervalFrame.grid_columnconfigure(3, weight=1)

        self._intervalFrame = tk.Frame(self.intervalFrame)
        self._intervalFrame.grid(row=3, column=3, pady=(5, 0))
        self._intervalFrame.grid_columnconfigure(tuple(range(3, 11)), weight=1)

        self.intervalHourCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                 values=[str(i).zfill(2) for i in range(0, 25)], state='normal',
                                                 validate='key',
                                                 validatecommand=(self.register(self.bindHourChosen), '%P'))
        self.intervalHourCombobox.grid(row=3, column=3)
        self.intervalHourCombobox.set(str(self.intervals[0]).zfill(2))
        ttk.Label(self._intervalFrame, text='hours').grid(row=3, column=4, sticky='w', padx=(1, 6))

        self.intervalMinuteCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                   values=[str(i).zfill(2) for i in range(0, 60)], state='normal',
                                                   validate='key',
                                                   validatecommand=(self.register(self.bindMinuteChosen), '%P'))
        self.intervalMinuteCombobox.grid(row=3, column=5)
        self.intervalMinuteCombobox.set(str(self.intervals[1]).zfill(2))
        ttk.Label(self._intervalFrame, text='mins').grid(row=3, column=6, sticky='w', padx=(1, 6))

        self.intervalSecondCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                   values=[str(i).zfill(2) for i in range(0, 60)], state='normal',
                                                   validate='key',
                                                   validatecommand=(self.register(self.bindSecondChosen), '%P'))
        self.intervalSecondCombobox.grid(row=3, column=7)
        self.intervalSecondCombobox.set(str(self.intervals[2]).zfill(2))
        ttk.Label(self._intervalFrame, text='secs').grid(row=3, column=8, sticky='w', padx=(1, 6))

        self.intervalMillisecondCombobox = ttk.Combobox(self._intervalFrame, width=3,
                                                        values=[str(i).zfill(3) for i in range(0, 1000)],
                                                        state='normal', validate='key',
                                                        validatecommand=(
                                                            self.register(self.bindMillisecondChosen), '%P'))
        self.intervalMillisecondCombobox.grid(row=3, column=9)
        self.intervalMillisecondCombobox.set(str(self.intervals[3]).zfill(3))
        ttk.Label(self._intervalFrame, text='millisecs').grid(row=3, column=10, sticky='w', padx=(1, 6))

        self.showInterval = ttk.Label(self._intervalFrame,
                                      text=f'Interval: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}')
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

        self._click_optionFrame = tk.Frame(self.click_optionFrame)
        self._click_optionFrame.grid(row=3, column=3, pady=(5, 0))
        self._click_optionFrame.grid_columnconfigure((3, 5), weight=1)

        mousebuttonLabel = ttk.Label(self._click_optionFrame,
                                     text='Direction:' if self.clickTypeOptionCombobox and self.clickTypeOptionCombobox.get() == 'Scroll' else 'Mouse button:',
                                     width=12)
        mousebuttonLabel.grid(row=3, column=3, padx=(0, 5), pady=(0, 5),
                              sticky='w')
        self.mouseButtonOptionCombobox = ttk.Combobox(self._click_optionFrame, width=7,
                                                      values=['Up',
                                                              'Down'] if self.clickTypeOptionCombobox and self.clickTypeOptionCombobox.get() == 'Scroll' else [
                                                          'Left', 'Right', 'Middle'], state='readonly')
        self.mouseButtonOptionCombobox.grid(row=3, column=4, pady=(0, 5))
        self.mouseButtonOptionCombobox.set(STORAGE.Garbage.clickButton)

        ttk.Label(self._click_optionFrame, text='Click type:').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.clickTypeOptionCombobox = ttk.Combobox(self._click_optionFrame, width=7,
                                                    values=['Single', 'Double', 'Triple', 'Scroll'], state='readonly')
        self.clickTypeOptionCombobox.grid(row=5, column=4)
        self.clickTypeOptionCombobox.set(STORAGE.Garbage.clickType)

        def update_clickOptions(_=None):
            STORAGE.Garbage.clickButton = self.mouseButtonOptionCombobox.get()
            STORAGE.Garbage.clickType = self.clickTypeOptionCombobox.get()

        def scroll_option_set(_=None):
            if self.clickTypeOptionCombobox.get().strip() == 'Scroll':
                self.mouseButtonOptionCombobox.configure(values=['Up', 'Down'])
                self.mouseButtonOptionCombobox.set(STORAGE.Garbage.old_scrollDirection)
                self.customPositionRadiobutton.configure(state='disabled')
                mousebuttonLabel.configure(text=f'Direction:')
            else:
                self.mouseButtonOptionCombobox.configure(values=['Left', 'Right', 'Middle'])
                self.mouseButtonOptionCombobox.set(STORAGE.Garbage.old_mouseButtonOption)
                self.customPositionRadiobutton.configure(state='normal')
                mousebuttonLabel.configure(text='Mouse button:')

        self.mouseButtonOptionCombobox.bind('<<ComboboxSelected>>',
                                            lambda _: [STORAGE.Garbage.trace_old_mouseButtonOption_scrollDirection(
                                                self.mouseButtonOptionCombobox.get().strip()), update_clickOptions()])
        self.clickTypeOptionCombobox.bind('<<ComboboxSelected>>',
                                          lambda _: [scroll_option_set(), update_clickOptions()])

        # # CLICK REPEAT
        self.click_repeatFrame = ttk.LabelFrame(self.mainFrame, text='Click repeat', labelanchor='nw')
        self.click_repeatFrame.grid(row=5, column=5, ipadx=15, ipady=5, pady=5, sticky='ne', padx=(5, 0))
        self.click_repeatFrame.grid_columnconfigure(3, weight=1)

        self._click_repeatFrame = tk.Frame(self.click_repeatFrame)
        self._click_repeatFrame.grid(row=3, column=3, pady=(5, 0))
        self._click_repeatFrame.grid_columnconfigure((3, 5), weight=1)

        # ttk.Label(self._click_repeatFrame, text='Repeat').grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')
        self.limitedRepeatRadiobutton = ttk.Radiobutton(self._click_repeatFrame, text='Repeat', value='limited',
                                                        variable=self.repeatVar,
                                                        command=lambda: self.limitedRepeatSpinbox.focus())
        self.limitedRepeatRadiobutton.grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')

        def changeSpinTime(_=None):
            if self.limitedRepeatSpinbox.get().isdigit():
                self.spinTime = int(self.limitedRepeatSpinbox.get())
            self.spinTimeLabel.configure(text=f'time{"s" if self.spinTime > 1 else ""}')

        self.limitedRepeatSpinbox = ttk.Spinbox(self._click_repeatFrame, from_=1, to=99999, width=5, wrap=True,
                                                validate='key', validatecommand=(
                self.register(lambda item: True if not len(item) or (item.isdigit() and int(item)) else False), '%P'),
                                                command=changeSpinTime)
        self.limitedRepeatSpinbox.grid(row=3, column=4, padx=5, pady=(0, 5), sticky='w')
        self.limitedRepeatSpinbox.set(self.spinTime)
        self.limitedRepeatSpinbox.bind('<KeyRelease>', changeSpinTime)
        self.spinTimeLabel = ttk.Label(self._click_repeatFrame, text=f'time{"s" if self.spinTime > 1 else ""}', width=5)
        self.spinTimeLabel.grid(row=3, column=5, pady=(0, 5), sticky='w')

        # ttk.Label(self._click_repeatFrame, text='Repeat until stopped').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.unlimitedRepeatRadiobutton = ttk.Radiobutton(self._click_repeatFrame, text='Until stopped',
                                                          value='unlimited', variable=self.repeatVar)
        self.unlimitedRepeatRadiobutton.grid(row=5, column=3, padx=(0, 5), sticky='w', columnspan=3)

        # # CURSOR POSITION FRAME
        self.cursor_positionFrame = ttk.LabelFrame(self.mainFrame, text='Cursor position', labelanchor='n')
        self.cursor_positionFrame.grid(row=7, column=3, ipadx=15, ipady=5, sticky='new', columnspan=3)
        self.cursor_positionFrame.grid_columnconfigure(3, weight=1)

        self._cursor_positionFrame = tk.Frame(self.cursor_positionFrame)
        self._cursor_positionFrame.grid(row=3, column=3, pady=(5, 0))
        self._cursor_positionFrame.grid_columnconfigure(tuple(range(3, 11)), weight=1)

        # ttk.Label(self._click_positionFrame, text='Repeat').grid(row=3, column=3, padx=(0, 5), pady=(0, 5), sticky='w')
        self.mousePositionRadiobutton = ttk.Radiobutton(self._cursor_positionFrame, text='Current (0, 0)',
                                                        value='mouse', variable=self.positionVar, command=lambda: [
                STORAGE.Garbage.trace_old_positionVar(self.positionVar.get()), self.bindChosenAll])
        self.mousePositionRadiobutton.grid(row=3, column=3, padx=(0, 7), pady=(0, 5), sticky='w')

        # ttk.Label(self._click_positionFrame, text='Repeat until stopped').grid(row=5, column=3, padx=(0, 5), sticky='w')
        self.customPositionRadiobutton = ttk.Radiobutton(self._cursor_positionFrame,
                                                         text='Custom (Locate)' if self.positionType.get() == 'locate' else 'Custom ({0}, {1})'.format(
                                                             *STORAGE.FIXED_POSITIONS),
                                                         value='custom',
                                                         variable=self.positionVar, command=lambda: [
                STORAGE.Garbage.trace_old_positionVar(self.positionVar.get()), self.customPositionDialog()])
        self.customPositionRadiobutton.grid(row=3, column=5, padx=(7, 0), sticky='e')

        # # RUN
        self.runFrame = tk.Frame(self.mainFrame)
        self.runFrame.grid(row=9, column=3, columnspan=3, sticky='nsew', ipadx=15, ipady=5, pady=(15, 0))
        self.runFrame.grid_columnconfigure((3, 5), weight=1)
        self.runFrame.grid_rowconfigure((3, 5), weight=1)

        self.startClickButton = ttk.Button(self.runFrame, text='Start', command=self.startClicking)
        self.startClickButton.grid(row=3, column=3, sticky='nsew')

        self.stopClickButton = ttk.Button(self.runFrame, text='Stop', state='disabled', command=self.stopClicking)
        self.stopClickButton.grid(row=3, column=5, sticky='nsew')

        if STORAGE.Setting.isRandomIntervalList[0]:
            for _widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                            self.intervalMillisecondCombobox]:
                _widget.configure(state='disabled')
            self.showInterval.configure(
                text=f'Interval/r: {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[1])} ~ {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[2])}')
        Utilities.writelog('GUI frame initialized', ('', '\n', True))

    def startClicking(self):
        hour, minute, second, millisecond = map(int, self.intervals)
        sleepTime = hour * 60 * 60 + minute * 60 + second + millisecond / 1000
        if not sleepTime:
            messagebox.showwarning('Invalid interval', 'Make sure the click interval is bigger than 0s.')
            return

        clickType = self.clickTypeOptionCombobox.get().lower().strip()
        mouseButton = self.mouseButtonOptionCombobox.get().lower().strip()

        self.startClickButton.configure(state='disabled')
        self.stopClickButton.configure(state='normal')
        self.extensionsButton.configure(state='disabled', cursor='')
        self.settingButton.configure(state='disabled', cursor='')
        self.title(f'Clicking - {__project__} {__version__}')

        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.configure(state='disabled')
        STORAGE.CLICKING = True

        interval_log = f'Randomized from {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[1])} to {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[2])}' if \
            STORAGE.Setting.isRandomIntervalList[
                0] else f'{":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}'
        Utilities.writelog(
            f'CLICKING STARTED\n\tinterval: {interval_log}\n\tbutton: {"middle" if clickType == "scroll" else mouseButton}\n\ttype: {clickType}\n\trepeat: {f"limited ({self.limitedRepeatSpinbox.get()})" if self.repeatVar.get() == "limited" else self.repeatVar.get()}\n\tposition: {self.positionVar.get() if self.positionVar.get() == "mouse" else "randomized" if self.randomPositionVar.get() else f"custom ({STORAGE.FIXED_POSITIONS[0]}, {STORAGE.FIXED_POSITIONS[1]})"}\n\tarea: {f"{STORAGE.Setting.clickArea[1:3]}, {STORAGE.Setting.clickArea[3:]}" if STORAGE.Setting.clickArea[0] else "fullscreen"}',
            ('', '\n', True))
        print('started')

        def click():
            if STORAGE.Setting.clickArea[0]:
                if Utilities.Function.is_position_inside_box(pyautogui.position(),
                                                             *STORAGE.Setting.clickArea[
                                                              1:]):
                    self.title(f'Clicking - {__project__} {__version__}')
                else:
                    self.title(f'Paused - {__project__} {__version__}')
                    return
            if self.positionVar.get() == 'custom' and self.positionType.get() != 'locate' and not self.randomPositionVar.get():
                pyautogui.moveTo(*map(int, STORAGE.FIXED_POSITIONS))
            if self.positionVar.get() == 'custom' and self.positionType.get().strip() == 'manual' and self.randomPositionVar.get():
                pos = [random.randint(*sorted((x, y))) for x, y in
                       [STORAGE.Setting.clickArea[1::2], STORAGE.Setting.clickArea[2::2]]] if STORAGE.Setting.clickArea[
                    0] else [random.randint(0, c) for c in pyautogui.size()]
                pyautogui.moveTo(*pos)

            if clickType == 'scroll':
                pyautogui.scroll(STORAGE.Setting.wheelSize if mouseButton == 'up' else -STORAGE.Setting.wheelSize)
                STORAGE.General.total_scroll += 1
                STORAGE.General.current_scroll += 1
            else:
                pyautogui.click(button=mouseButton,
                                clicks=3 if clickType == 'triple' else 2 if clickType == 'double' else 1)
                STORAGE.General.total_clicks += 1
                STORAGE.General.current_click += 1
            # print('clicked')

        def runClicks():
            nonlocal sleepTime

            if not self.limitedRepeatSpinbox.get().strip().isdigit() and self.repeatVar.get() == 'limited':
                messagebox.showwarning('Invalid repeat time', 'The repeat time input must not be blank.')
                self.stopClicking()
                return
            else:
                repeatTime = -1 if self.repeatVar.get() == 'unlimited' else int(self.limitedRepeatSpinbox.get())
            while 1:
                if not repeatTime:
                    self.stopClicking()
                    break
                if not STORAGE.CLICKING:
                    self.stopClicking(broadcast=False)
                    break
                try:
                    flag = time.perf_counter()
                    if self.positionVar.get() == 'custom' and self.positionType.get() == 'locate':
                        if not os.path.isfile(STORAGE.LOCATE_SCREEN[1]):
                            messagebox.showwarning('FileNotFound Error',
                                                   f'Unable to open the image. Make sure your image path is correct.\nPath: {STORAGE.LOCATE_SCREEN[1]}')
                            self.stopClicking()
                            return
                        # noinspection PyArgumentList
                        coords = pyautogui.locateCenterOnScreen(STORAGE.LOCATE_SCREEN[1],
                                                                confidence=STORAGE.Setting.confidence)
                        if coords is not None:
                            if STORAGE.LOCATE_SCREEN[0]:
                                pyautogui.moveTo(*coords)
                            click()

                            time.sleep(
                                random.uniform(*STORAGE.Setting.isRandomIntervalList[1:]) if
                                STORAGE.Setting.isRandomIntervalList[
                                    0] else sleepTime)
                            allFlag = time.perf_counter()
                            self.showInterval.configure(text='Interval/l: ~{}'.format(
                                Utilities.Function.seconds_to_formatted(round(allFlag - flag, 3), with_hour=True)))
                            repeatTime -= 1
                        continue

                    if pyautogui.position() in pyautogui.FAILSAFE_POINTS:
                        raise pyautogui.FailSafeException
                    click()
                    stopFlag = time.perf_counter()

                    time.sleep(
                        random.uniform(*STORAGE.Setting.isRandomIntervalList[1:]) if
                        STORAGE.Setting.isRandomIntervalList[
                            0] else sleepTime)
                    allFlag = time.perf_counter()
                    print(sleepTime, stopFlag - flag, allFlag - flag)
                except pyautogui.FailSafeException:
                    keyboard.unregister_all_hotkeys()
                    Utilities.add_default_hotkeys()
                    self.stopClickButton.configure(state='disabled')
                    messagebox.showwarning('Fail-safe Triggered',
                                           f'You have triggered {__project__} fail-safe by moving the mouse to the corner of the screen.\n\n(You can disable it in the settings, but it\'s NOT RECOMMENDED)')
                    self.stopClicking()
                    Utilities.add_trigger_hotkey()
                    Utilities.writelog('Fail-safe triggered. Clicking progress stopped', ('', '\n', True))
                    break
                repeatTime -= 1

        threading.Thread(target=runClicks).start()

    def stopClicking(self, broadcast=True):
        self.startClickButton.configure(state='normal')
        self.stopClickButton.configure(state='disabled')
        self.extensionsButton.configure(state='normal', cursor='hand2')
        self.settingButton.configure(state='normal', cursor='hand2')
        self.title(f'Stopped - {__project__} {__version__}')
        STORAGE.CLICKING = False

        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.configure(state='readonly' if widget in [self.clickTypeOptionCombobox,
                                                            self.mouseButtonOptionCombobox] else 'normal')
        if broadcast:
            Utilities.writelog(f'CLICKING STOPPED', ('', '\n', True))
        print('stopped')

    # class: menu
    def menuActions(self):
        self.menuFrame.grid(row=0, column=0, sticky='nsw', columnspan=100, rowspan=100)
        if self.menuFrame.winfo_viewable():
            self.menuFrame.grid_forget()

    # class: settings
    def settings(self):
        if STORAGE.CLICKING:
            return
        if isinstance(STORAGE.Setting.ON, tk.Toplevel):
            STORAGE.Setting.ON.lift()
            return
        Utilities.writelog('Settings opened', ('', '\n', True))

        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton, self.startClickButton,
                       self.extensionsButton]:
            widget.configure(state='disabled', cursor='')
        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        settingWindow = STORAGE.Setting.ON = tk.Toplevel(self)
        settingWindow.title('Settings')
        settingWindow.resizable(False, False)
        settingWindow.attributes('-topmost', STORAGE.Setting.isTopmost)
        Utilities.set_window_icon(settingWindow)

        settingWindow.geometry(f'+{self.winfo_x() + self.winfo_width() + 10}+{self.winfo_y()}')
        self.bind('<Configure>', lambda _: settingWindow.geometry(
            f'+{self.winfo_x() + self.winfo_width() + 10}+{self.winfo_y()}') if settingWindow.winfo_exists() else None)

        allSettingsFrame = tk.Frame(settingWindow)
        allSettingsFrame.grid(row=3, column=3, padx=10, pady=10)

        # SETTING 1: Advanced settings
        setting1_advanced_frame = ttk.LabelFrame(allSettingsFrame, text='Advanced')
        setting1_advanced_frame.grid(row=1, column=3, sticky='ew', pady=(0, 5))

        _setting1_advanced_frame = tk.Frame(setting1_advanced_frame)
        _setting1_advanced_frame.grid(row=3, column=3, sticky='ew', padx=(10, 0), pady=(0, 5))
        _setting1_advanced_frame.grid_columnconfigure(3, weight=1)

        randomIntervalValue = tk.IntVar()
        randomIntervalCheckbutton = tk.Checkbutton(_setting1_advanced_frame, text='Random interval',
                                                   variable=randomIntervalValue,
                                                   command=lambda: randomIntervalToggled())
        ToolTip(randomIntervalCheckbutton, msg='[Auto-saved] Randomize the interval between each mouse action.',
                delay=0.25)
        randomIntervalCheckbutton.select() if STORAGE.Setting.isRandomIntervalList[0] else None
        randomIntervalCheckbutton.grid(row=3, column=3, sticky='w')
        randomIntervalCheckbutton.bind('<Button-3>', lambda _: randomIntervalToggled())

        def randomIntervalToggled():
            if not randomIntervalValue.get():
                self.showInterval.configure(
                    text=f'Interval: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}')
                STORAGE.Setting.isRandomIntervalList[0] = False
                return
            self.showInterval.configure(
                text=f'Interval/r: {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[1])} ~ {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[2])}')

            self.focus()
            askRandomIntervalDialog = tk.Toplevel(self)
            askRandomIntervalDialog.title('')
            Utilities.child_geometry(askRandomIntervalDialog, self)
            askRandomIntervalDialog.resizable(False, False)
            askRandomIntervalDialog.attributes('-topmost', STORAGE.Setting.isTopmost)
            Utilities.set_window_icon(askRandomIntervalDialog)

            askRandomIntervalDialog.grab_set()
            askRandomIntervalDialog.focus()

            alldialogFrame = tk.Frame(askRandomIntervalDialog)
            alldialogFrame.grid(row=3, column=3, padx=15, pady=(15, 0), ipadx=5, ipady=5)
            alldialogFrame.grid_columnconfigure(3, weight=1)

            tk.Label(alldialogFrame, text='Randomize from:').grid(row=3, column=2)

            start_randomSecondsEntry = tk.Entry(alldialogFrame, width=8, validate='key', validatecommand=(self.register(
                lambda item: True if item == '' or Utilities.Function.isfloat(item) and float(item) <= 3599 and len(
                    item.split('.')[1] if len(
                        item.split('.')) > 1 else '') <= 3 else False),
                                                                                                          '%P'))
            start_randomSecondsEntry.grid(row=3, column=3, sticky='e')
            tk.Label(alldialogFrame, text='s').grid(row=3, column=4, sticky='w')

            tk.Label(alldialogFrame, text='to').grid(row=3, column=5, padx=5)

            end_randomSecondsEntry = tk.Entry(alldialogFrame, width=8, validate='key', validatecommand=(self.register(
                lambda item: True if item == '' or Utilities.Function.isfloat(item) and float(item) <= 3600 and len(
                    item.split('.')[1] if len(
                        item.split('.')) > 1 else '') <= 3 else False),
                                                                                                        '%P'))
            end_randomSecondsEntry.grid(row=3, column=7, sticky='e')
            tk.Label(alldialogFrame, text='s').grid(row=3, column=8, sticky='w')
            if STORAGE.Setting.isRandomIntervalList[1] != STORAGE.Setting.isRandomIntervalList[2]:
                start_randomSecondsEntry.insert(0, f'{STORAGE.Setting.isRandomIntervalList[1]:.3f}')
                end_randomSecondsEntry.insert(0, f'{STORAGE.Setting.isRandomIntervalList[2]:.3f}')

            saveProgressButton = ttk.Button(askRandomIntervalDialog, text='Auto-saved', state='disabled')
            saveProgressButton.grid(row=11, column=3, pady=(3, 10))

            def bindSubmitRandomRange(_):
                if (float(start_randomSecondsEntry.get()) if start_randomSecondsEntry.get() != "" else 0) < (
                        float(end_randomSecondsEntry.get()) if end_randomSecondsEntry.get() != "" else 0):
                    STORAGE.Setting.isRandomIntervalList = [
                        False, float(start_randomSecondsEntry.get()) if start_randomSecondsEntry.get() != "" else 0,
                        float(end_randomSecondsEntry.get()) if end_randomSecondsEntry.get() != "" else 0]
                self.showInterval.configure(
                    text=f'Interval/r: {Utilities.Function.seconds_to_formatted(float(start_randomSecondsEntry.get()) if start_randomSecondsEntry.get() != "" else 0)} ~ {Utilities.Function.seconds_to_formatted(float(end_randomSecondsEntry.get()) if end_randomSecondsEntry.get() != "" else 0)}')

            start_randomSecondsEntry.bind('<KeyRelease>', bindSubmitRandomRange)
            end_randomSecondsEntry.bind('<KeyRelease>', bindSubmitRandomRange)

            def exitRandomIntervalDialog():
                if (float(start_randomSecondsEntry.get()) if start_randomSecondsEntry.get() != "" else 0) >= (
                        float(end_randomSecondsEntry.get()) if end_randomSecondsEntry.get() != "" else 0):
                    if messagebox.askyesno(
                            'Invalid Random Interval',
                            'The random interval range is invalid.\nIf you close, nothing will be saved. Would you still like to exit?',
                            icon='warning', parent=askRandomIntervalDialog):
                        if STORAGE.Setting.isRandomIntervalList[0]:
                            self.showInterval.configure(
                                text=f'Interval/r: {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[1])} ~ {Utilities.Function.seconds_to_formatted(STORAGE.Setting.isRandomIntervalList[2])}')
                        else:
                            self.showInterval.configure(
                                text=f'Interval: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}')
                            STORAGE.Setting.isRandomIntervalList[0] = False
                            randomIntervalCheckbutton.deselect()
                    else:
                        return
                askRandomIntervalDialog.destroy()
                STORAGE.Setting.isRandomIntervalList[0] = bool(randomIntervalValue.get())
                Utilities.add_default_hotkeys()
                Utilities.add_trigger_hotkey()

            askRandomIntervalDialog.protocol('WM_DELETE_WINDOW', exitRandomIntervalDialog)

        mouseScrollVar = tk.IntVar(value=STORAGE.Setting.wheelSize // 100)
        mouseScrollLengthFrame = tk.Frame(_setting1_advanced_frame)
        mouseScrollLengthFrame.grid(row=5, column=3, sticky='ew')

        wheelsize_label = tk.Label(mouseScrollLengthFrame, text='Wheel size:')
        wheelsize_label.grid(row=3, column=3, sticky='w', padx=(0, 5))
        ToolTip(wheelsize_label, msg='The size of the wheel when auto-scrolling (default=100).', delay=0.25)
        mouseScrollLengthSlider = ttk.Scale(mouseScrollLengthFrame, from_=1, to=20, orient='horizontal',
                                            variable=mouseScrollVar,
                                            command=lambda _: mouseScrollLengthDisplayLabel.configure(
                                                text=mouseScrollVar.get() * 100))
        mouseScrollLengthSlider.grid(row=3, column=5, sticky='ew')

        mouseScrollLengthDisplayLabel = tk.Label(mouseScrollLengthFrame, text=mouseScrollVar.get() * 100)
        mouseScrollLengthDisplayLabel.grid(row=3, column=7, padx=5)

        imageDetectConfidenceVar = tk.IntVar(value=STORAGE.Setting.confidence * 10)
        imageDetectConfidenceFrame = tk.Frame(_setting1_advanced_frame)
        imageDetectConfidenceFrame.grid(row=7, column=3, sticky='ew')

        detect_accuracy_label = tk.Label(imageDetectConfidenceFrame, text='Detect accuracy:')
        detect_accuracy_label.grid(row=3, column=3, sticky='w', padx=(0, 5))
        ToolTip(detect_accuracy_label, msg='The accuracy of the image detector (default=0.8).', delay=0.25)
        imageDetectConfidenceSlider = ttk.Scale(imageDetectConfidenceFrame, from_=1, to=10, orient='horizontal',
                                                variable=imageDetectConfidenceVar,
                                                command=lambda _: imageDetectConfidenceDisplayLabel.configure(
                                                    text=imageDetectConfidenceVar.get() / 10))
        imageDetectConfidenceSlider.grid(row=3, column=5, sticky='ew')

        imageDetectConfidenceDisplayLabel = tk.Label(imageDetectConfidenceFrame,
                                                     text=imageDetectConfidenceVar.get() / 10)
        imageDetectConfidenceDisplayLabel.grid(row=3, column=7, padx=5)

        clickAreaFrame = tk.Frame(_setting1_advanced_frame)
        clickAreaFrame.grid(row=9, column=3, sticky='ew')

        click_area_label = tk.Label(clickAreaFrame, text='Click area:')
        click_area_label.grid(row=3, column=3, sticky='w', padx=(0, 5))
        ToolTip(click_area_label, msg='Define a specific area on the screen where the mouse actions are made.')
        clickAreaCombobox = ttk.Combobox(clickAreaFrame, values=['Fullscreen', 'Custom'], state='readonly', width=9)
        clickAreaCombobox.current(int(STORAGE.Setting.clickArea[0]))
        clickAreaCombobox.grid(row=3, column=5)
        ToolTip(clickAreaCombobox,
                msg=lambda: create_window_as_coordinates(),
                delay=0.5)

        def create_window_as_coordinates():
            return f'Position: {real_pos[0], real_pos[1]}; {real_pos[2], real_pos[3]}' if clickAreaCombobox.get() == 'Custom' else f'Fullscreen ({"x".join(map(str, pyautogui.size()))})'

        # noinspection PyUnresolvedReferences
        def preview_range():
            if clickAreaCombobox.get().strip() == 'Custom':
                previewAreaButton.configure(state='disabled')

                previewAreaWindow = tk.Toplevel(settingWindow, highlightthickness=3, background='purple',
                                                highlightbackground='black')
                previewAreaWindow.title('Preview')
                previewAreaWindow.geometry(
                    (lambda x1, y1, x2, y2: f'{abs(x2 - x1)}x{abs(y2 - y1)}+{min(x1, x2)}+{min(y1, y2)}')(*fake_pos))
                previewAreaWindow.resizable(False, False)
                previewAreaWindow.overrideredirect(True)
                previewAreaWindow.attributes('-topmost', True)
                previewAreaWindow.attributes('-transparentcolor', 'purple')
                previewAreaWindow.grab_set()
                previewAreaWindow.focus()

                previewAreaWindow.grid_columnconfigure(3, weight=1)
                previewAreaWindow.grid_rowconfigure(3, weight=1)
                tk.Canvas(previewAreaWindow, background='purple').grid(row=3, column=3, sticky='nsew')

                closebutton = tk.Frame(previewAreaWindow, background='red', cursor='hand2', width=15, height=15)
                closebutton.bind('<Button-1>',
                                 lambda _: [previewAreaWindow.destroy(), previewAreaButton.configure(state='normal')])
                previewAreaWindow.bind('<Escape>',
                                       lambda _: [previewAreaWindow.destroy(),
                                                  previewAreaButton.configure(state='normal')])
                closebutton.grid(row=3, column=3, sticky='nw', padx=2, pady=2)
                tk.Label(previewAreaWindow, text=f'{real_pos[0], real_pos[1]}; {real_pos[2], real_pos[3]}',
                         highlightthickness=2, highlightbackground='black').grid(row=3, column=3)

        previewAreaButton = ttk.Button(clickAreaFrame, text='Preview', command=preview_range, width=7,
                                       state='normal' if STORAGE.Setting.clickArea[0] else 'disabled')
        previewAreaButton.grid(row=3, column=7, padx=(5, 0))

        real_pos = STORAGE.Setting.clickArea[1:] if clickAreaCombobox.get().strip() == 'Custom' else [0, 0, 0, 0]
        fake_pos = STORAGE.Garbage.tk_clickArea
        min_width, min_height = 50, 50

        def chooseClickingArea(_):
            if clickAreaCombobox.get().strip() != 'Custom':
                previewAreaButton.configure(state='disabled')
                return
            if keyboard.is_pressed('ctrl'):
                return
            nonlocal real_pos

            def bind_mouse_on(event):
                nonlocal isChoosing, old_pos, rect
                rect = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='black', width=3)
                isChoosing = True
                old_pos = event.x, event.y
                real_pos[0], real_pos[1] = tuple(pyautogui.position())
                fake_pos[0], fake_pos[1] = event.x, event.y

            def bind_mouse_off(event):
                nonlocal isChoosing, real_pos
                if isChoosing:
                    real_pos[2], real_pos[3] = tuple(pyautogui.position())
                    fake_pos[2], fake_pos[3] = event.x, event.y

                    if abs(real_pos[2] - real_pos[0]) >= min_width and abs(real_pos[3] - real_pos[1]) >= min_height:
                        if abs(real_pos[0] - real_pos[2]) == pyautogui.size()[0] - 1 and abs(
                                real_pos[1] - real_pos[3]) == pyautogui.size()[1] - 1:
                            clickAreaCombobox.set('Fullscreen')
                            previewAreaButton.configure(state='disabled')
                            STORAGE.Setting.clickArea[0] = False
                        else:
                            clickAreaCombobox.set('Custom')
                            previewAreaButton.configure(state='normal')
                        settingWindow.focus()
                        choose_area_window.destroy()
                    else:
                        messagebox.showwarning('Area too small', 'Your click area size is too small. Please try again.',
                                               parent=choose_area_window)
                        canvas.delete(rect)
                        choose_area_window.focus()

            def bind_mouse_movement(event):
                nonlocal isChoosing, old_pos, rect
                if isChoosing:
                    canvas.delete(rect)
                    rect = canvas.create_rectangle(old_pos[0], old_pos[1], event.x, event.y,
                                                   outline='black' if abs(event.x - old_pos[0]) >= min_width and abs(
                                                       event.y - old_pos[1]) >= min_height else 'red', width=3)

            choose_area_window = tk.Toplevel(root)
            choose_area_window.title('Choose Area Window')
            choose_area_window.state('zoomed')
            choose_area_window.overrideredirect(True)
            choose_area_window.attributes('-alpha', 0.5)
            choose_area_window.attributes('-topmost', True)
            choose_area_window.configure(cursor='crosshair')
            choose_area_window.grab_set()

            canvas = tk.Canvas(choose_area_window)
            canvas.pack(expand=tk.YES, fill=tk.BOTH)

            isChoosing = False
            old_pos = (0, 0)
            old_real_pos = real_pos
            real_pos = [0, 0, 0, 0]
            rect = None

            choose_area_window.bind('<Button-1>', bind_mouse_on)
            choose_area_window.bind('<ButtonRelease-1>', bind_mouse_off)
            choose_area_window.bind('<B1-Motion>', bind_mouse_movement)

            def exit_chooseArea(_):
                nonlocal real_pos
                choose_area_window.destroy()
                real_pos = old_real_pos

            choose_area_window.bind('<Escape>', exit_chooseArea)

        clickAreaCombobox.bind('<<ComboboxSelected>>', chooseClickingArea)

        voiceCommandVal = tk.IntVar()
        voiceCommandCheckbutton = tk.Checkbutton(_setting1_advanced_frame, text='Voice commands',
                                                 variable=voiceCommandVal,
                                                 command=lambda: voiceCommandToggled())
        ToolTip(voiceCommandCheckbutton, msg=f'[Auto-saved] Control {__project__} via voice commands (BETA).',
                delay=0.25)
        voiceCommandCheckbutton.select() if STORAGE.Setting.isVoiceCommand else None
        voiceCommandCheckbutton.grid(row=11, column=3, sticky='w')
        voiceCommandCheckbutton.bind('<Button-3>', lambda e: voiceCommandToggled(e))

        def voiceCommandToggled(event=False):
            if not event and not voiceCommandVal.get() or not event and not keyboard.is_pressed('ctrl'):
                return
            self.focus()

            voiceCommandsWindow = tk.Toplevel(self)
            voiceCommandsWindow.title('Voice Commands')
            Utilities.child_geometry(voiceCommandsWindow, self)
            voiceCommandsWindow.resizable(False, False)
            voiceCommandsWindow.attributes('-topmost', STORAGE.Setting.isTopmost)
            Utilities.set_window_icon(voiceCommandsWindow)

            left_frame = tk.Frame(voiceCommandsWindow)
            left_frame.grid(row=3, column=3)

            start_header_label = tk.Label(left_frame, text='Start', font=('Calibri', 20, 'bold'))
            start_header_label.grid(row=0, column=3, columnspan=3)

            laddvoiceCommandFrame = tk.Frame(left_frame)
            laddvoiceCommandFrame.grid(row=7, column=3, sticky='w')

            def ladd_command():
                item = addstartVoiceCommandEntry.get().strip().lower()
                if item and item not in STORAGE.Setting.startVoiceCommands + STORAGE.Setting.stopVoiceCommands:
                    STORAGE.Setting.startVoiceCommands.append(item)
                    start_listbox.insert('end', item)

            def ldelete_command():
                if len(STORAGE.Setting.startVoiceCommands) > 1:
                    STORAGE.Setting.startVoiceCommands.remove(start_listbox.get(start_listbox.curselection()))
                    start_listbox.delete(start_listbox.curselection())

            tk.Label(laddvoiceCommandFrame, text='Add:').grid(row=3, column=3)
            addstartVoiceCommandEntry = tk.Entry(laddvoiceCommandFrame, width=7)
            addstartVoiceCommandEntry.grid(row=3, column=5, padx=5)
            ttk.Button(laddvoiceCommandFrame, text='+', width=2, command=ladd_command).grid(row=3, column=7, padx=1)
            ttk.Button(laddvoiceCommandFrame, text='-', width=2, command=ldelete_command).grid(row=3, column=9)

            start_listbox = tk.Listbox(left_frame)
            start_listbox.grid(row=4, column=3)
            lscrollbar = ttk.Scrollbar(left_frame, command=start_listbox.yview)
            lscrollbar.grid(row=4, column=5, sticky='ns')
            start_listbox.configure(yscrollcommand=lscrollbar.set)

            for command in STORAGE.Setting.startVoiceCommands:
                start_listbox.insert(tk.END, command)

            right_frame = tk.Frame(voiceCommandsWindow)
            right_frame.grid(row=3, column=5)

            stop_header_label = tk.Label(right_frame, text='Stop', font=('Calibri', 20, 'bold'))
            stop_header_label.grid(row=3, column=3, columnspan=3)

            raddvoiceCommandFrame = tk.Frame(right_frame)
            raddvoiceCommandFrame.grid(row=7, column=3, sticky='w')

            def radd_command():
                item = addstopVoiceCommandEntry.get().strip().lower()
                if item and item not in STORAGE.Setting.stopVoiceCommands + STORAGE.Setting.startVoiceCommands:
                    STORAGE.Setting.stopVoiceCommands.append(item)
                    stop_listbox.insert('end', item)

            def rdelete_command():
                if len(STORAGE.Setting.stopVoiceCommands) > 1:
                    STORAGE.Setting.stopVoiceCommands.remove(stop_listbox.get(stop_listbox.curselection()))
                    stop_listbox.delete(stop_listbox.curselection())

            tk.Label(raddvoiceCommandFrame, text='Add:').grid(row=3, column=3)
            addstopVoiceCommandEntry = tk.Entry(raddvoiceCommandFrame, width=7)
            addstopVoiceCommandEntry.grid(row=3, column=5, padx=5)
            ttk.Button(raddvoiceCommandFrame, text='+', width=2,
                       command=radd_command).grid(row=3, column=7, padx=1)
            ttk.Button(raddvoiceCommandFrame, text='-', width=2, command=rdelete_command).grid(
                row=3, column=9)

            stop_listbox = tk.Listbox(right_frame)
            stop_listbox.grid(row=4, column=3)
            rscrollbar = ttk.Scrollbar(right_frame, command=stop_listbox.yview)
            rscrollbar.grid(row=4, column=5, sticky='ns')
            stop_listbox.configure(yscrollcommand=rscrollbar.set)

            for command in STORAGE.Setting.stopVoiceCommands:
                stop_listbox.insert(tk.END, command)

            ttk.Separator(voiceCommandsWindow, orient='vertical').grid(row=3, column=4, sticky='ns')
            voiceCommandsHeaderFrame = tk.Frame(voiceCommandsWindow)
            voiceCommandsHeaderFrame.grid(row=2, column=1, columnspan=5)

            tk.Label(voiceCommandsHeaderFrame, text='Voice Commands', font=('Calibri', 25, 'bold')).grid(row=3,
                                                                                                         column=3)
            tk.Label(voiceCommandsHeaderFrame,
                     text='NOTE: This feature is still in development.\nBugs and delays might occur.').grid(row=4,
                                                                                                            column=3,
                                                                                                            pady=(
                                                                                                                0, 10))

        # SETTING 2: Hotkeys
        setting2_hotkey_frame = ttk.LabelFrame(allSettingsFrame, text='Hotkeys')
        setting2_hotkey_frame.grid(row=3, column=3, sticky='ew', pady=(0, 5))

        _setting1_hotkey_frame = tk.Frame(setting2_hotkey_frame)
        _setting1_hotkey_frame.grid(row=3, column=3, padx=15, pady=5)

        hotkeyDisplayEntry = tk.Entry(_setting1_hotkey_frame, width=11)
        hotkeyDisplayEntry.insert(0, '+'.join(
            [key.capitalize() for key in STORAGE.Setting.trigger_hotkey.lower().split('+')]))
        hotkeyDisplayEntry.grid(row=3, column=3, sticky='ns', padx=(0, 5))

        def inputHotkeys():
            settingWindow.focus()
            chooseHotkeysButton.configure(state='disabled')
            Utilities.writelog('Listening for hotkey input..', ('', '\n', True))

            hotkeyDisplayEntry.delete(0, 'end')
            hotkeyDisplayEntry.insert(0, 'Listening...')
            hotkeyDisplayEntry.configure(state='disabled')

            def readHotkeys():
                hotkey = '+'.join(key.capitalize() for key in keyboard.read_hotkey().split('+'))
                Utilities.writelog(f'Hotkey detected: {hotkey} (result might be incorrect)', ('', '\n', True))

                chooseHotkeysButton.configure(state='normal')
                hotkeyDisplayEntry.configure(state='normal')
                hotkeyDisplayEntry.delete(0, 'end')
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
                print(hotkeyDisplayEntry.get())

        hotkeyDisplayEntry.bind('<KeyRelease>', check_key_validation)

        chooseHotkeysButton = ttk.Button(_setting1_hotkey_frame, text='Input', width=5, command=inputHotkeys)
        chooseHotkeysButton.grid(row=3, column=5, padx=(5, 0))

        invalidKeysLabel = tk.Label(_setting1_hotkey_frame, text='', foreground='red')
        invalidKeysLabel.grid(row=3, column=7, padx=5)

        # SETTING 3: Pick position dialog
        setting3_pickposition_frame = ttk.LabelFrame(allSettingsFrame, text='Pick-position dialog')
        setting3_pickposition_frame.grid(row=5, column=3, sticky='ew', pady=(0, 5))
        setting3_pickposition_frame.grid_columnconfigure(3, weight=1)

        _setting2_pickposition_frame = tk.Frame(setting3_pickposition_frame)
        _setting2_pickposition_frame.grid(row=3, column=3, padx=15, pady=5, sticky='ew')
        _setting2_pickposition_frame.grid_columnconfigure(3, weight=1)

        transparencyFrame = tk.Frame(_setting2_pickposition_frame)
        transparencyFrame.grid(row=3, column=3)
        transparencyFrame.grid_columnconfigure((3, 5, 7), weight=1)

        transparentVar = tk.IntVar(value=STORAGE.Setting.transparency * 10)
        transparency_label = tk.Label(transparencyFrame, text='Transparency:')
        transparency_label.grid(row=21, column=3, sticky='w', padx=5)
        ToolTip(transparency_label, msg='Set the transparency for the position picker (default=0.5).', delay=0.25)
        slider1_transparent = ttk.Scale(transparencyFrame, from_=1, to=10, orient='horizontal', variable=transparentVar,
                                        command=lambda _: transparencyDisplayLabel.configure(
                                            text=transparentVar.get() / 10))
        slider1_transparent.grid(row=21, column=5, sticky='ew')
        transparencyDisplayLabel = tk.Label(transparencyFrame, text=f'{transparentVar.get() / 10}')
        transparencyDisplayLabel.grid(row=21, column=7, padx=5)

        askCustomDialogOpenButton = ttk.Button(_setting2_pickposition_frame, text='Open',
                                               command=lambda: self.customPositionDialog(True))
        askCustomDialogOpenButton.grid(
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
        ToolTip(checkbox1_topmost, msg=f'Pin {__project__} to the front of the screen.', delay=0.25)
        checkbox1_topmost.select() if STORAGE.Setting.isTopmost else None
        checkbox1_topmost.grid(row=3, column=3, sticky='w')

        # # n: Misc 2 - Auto pop up
        autopopupVar = tk.IntVar()
        checkbox2_autopopup = tk.Checkbutton(_setting10_miscellaneous_frame, text='Auto extra dialog/pop-up',
                                             variable=autopopupVar)
        ToolTip(checkbox2_autopopup, msg='Toggle uneccessary pop-up dialogs/messagebox.', delay=0.25)
        checkbox2_autopopup.select() if STORAGE.Setting.isAutoPopup else None
        checkbox2_autopopup.grid(row=5, column=3, sticky='w')

        # # n: Misc 3 - Fail-safe
        failsafeVar = tk.IntVar()
        checkbox3_failsafe = tk.Checkbutton(_setting10_miscellaneous_frame, text='Fail-safe system',
                                            variable=failsafeVar)
        ToolTip(checkbox3_failsafe, msg='Stop all actions when mouse is on the corners (recommended).', delay=0.25)
        checkbox3_failsafe.select() if STORAGE.Setting.isFailsafe else None
        checkbox3_failsafe.grid(row=7, column=3, sticky='w')

        def save():
            STORAGE.Setting.trigger_hotkey = hotkeyDisplayEntry.get().lower().strip()
            print('added', STORAGE.Setting.trigger_hotkey)

            STORAGE.Setting.isTopmost = bool(topmostVar.get())
            STORAGE.Setting.isFailsafe = bool(failsafeVar.get())
            STORAGE.Setting.isAutoPopup = bool(autopopupVar.get())
            STORAGE.Setting.wheelSize = mouseScrollVar.get() * 100
            STORAGE.Setting.confidence = imageDetectConfidenceVar.get() / 10
            STORAGE.Setting.transparency = transparentVar.get() / 10
            STORAGE.Setting.isVoiceCommand = bool(voiceCommandVal.get())

            STORAGE.Setting.clickArea = [clickAreaCombobox.get().strip() == 'Custom'] + real_pos

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
                            self.mousePositionRadiobutton, self.customPositionRadiobutton, self.startClickButton,
                            self.extensionsButton]:
                if STORAGE.Setting.isRandomIntervalList[0] and _widget in [self.intervalHourCombobox,
                                                                           self.intervalMinuteCombobox,
                                                                           self.intervalSecondCombobox,
                                                                           self.intervalMillisecondCombobox]:
                    continue
                if _widget is self.extensionsButton:
                    _widget.configure(state='normal', cursor='hand2')
                else:
                    _widget.configure(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                      self.mouseButtonOptionCombobox] else 'normal')
            keyboard.unregister_all_hotkeys()
            Utilities.add_default_hotkeys()
            Utilities.add_trigger_hotkey()

        def on_exit(saving: bool = True, on_quit: bool = False):
            if not keyboard.is_pressed('ctrl') and on_quit:
                if not messagebox.askyesno('Closing Settings',
                                           'Are you sure that you want to close settings? Everything won\'t be saved.',
                                           default='no', parent=settingWindow, icon='warning'):
                    return

            if not on_quit:
                for _widget in [randomIntervalCheckbutton, hotkeyDisplayEntry, chooseHotkeysButton, slider1_transparent,
                                askCustomDialogOpenButton,
                                checkbox1_topmost, checkbox2_autopopup, checkbox3_failsafe, saveButton]:
                    _widget.configure(state='disabled')

            if saving:
                save()
                Utilities.writelog('Settings closed (saving: true)', ('', '\n', True))
            else:
                Utilities.writelog('Settings closed (saving: false)', ('', '\n', True))

            root.after(1 if on_quit else 1000, closing)

        saveSettingsFrame = tk.Frame(settingWindow)
        saveSettingsFrame.grid(row=100, column=3, sticky='ew', pady=(0, 10))
        saveSettingsFrame.grid_columnconfigure((3, 5), weight=1)

        saveButtonStyle = ttk.Style()
        saveButtonStyle.configure('save.TButton', foreground='darkgreen', font=('', 9, 'bold'))

        saveButton = ttk.Button(saveSettingsFrame, text='Save & Quit', style='save.TButton', command=on_exit)
        saveButton.grid(row=3, column=3, ipadx=15, sticky='nse', padx=3)

        terminalButton = ttk.Button(saveSettingsFrame, image=self.terminalImage, cursor='hand2',
                                    command=Utilities.Dialogs.Terminal.dialogs)
        terminalButton.grid(row=3, column=5, sticky='w', ipadx=5)

        settingWindow.protocol('WM_DELETE_WINDOW', lambda: on_exit(False, True))
        Utilities.writelog('Settings window initialized', ('', '\n', True))

    def extensions(self):
        STORAGE.Extension.ON = extensionsWindow = tk.Toplevel(self)
        extensionsWindow.title(f'Extensions List ({STORAGE.Extension.version})')
        Utilities.child_geometry(extensionsWindow, self)
        extensionsWindow.resizable(False, False)
        extensionsWindow.attributes('-topmost', STORAGE.Setting.isTopmost)
        self.withdraw()
        Utilities.set_window_icon(extensionsWindow)

        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        allExtensionsFrame = tk.Frame(extensionsWindow)
        allExtensionsFrame.grid(row=3, column=3, sticky='nsew')

        tk.Label(allExtensionsFrame, text='Extensions', font=('Calibri', 25, 'bold')).grid(row=0, column=3)

        extensionsFrame = tk.Frame(allExtensionsFrame)
        extensionsFrame.grid(row=5, column=3, padx=15, pady=15)
        extensionsFrame.grid_columnconfigure((3, 5, 7), weight=1)
        tk.Frame(extensionsFrame, background='black', height=3).grid(row=0, column=0, columnspan=100, sticky='ew')
        tk.Frame(extensionsFrame, background='black', width=3).grid(row=0, column=0, rowspan=100, sticky='ns')
        tk.Frame(extensionsFrame, background='black', height=3).grid(row=99, column=0, columnspan=100, sticky='ew')
        tk.Frame(extensionsFrame, background='black', width=3).grid(row=0, column=99, rowspan=100, sticky='ns')

        insideExtensionFrame = tk.Frame(extensionsFrame)
        insideExtensionFrame.grid(row=3, column=3, padx=5, pady=5)

        extension1_mouseRecorderButton = ttk.Button(insideExtensionFrame,
                                                    text=f'MouseRecorder',
                                                    cursor='hand2', command=self.mouseRecorder)
        extension1_mouseRecorderButton.grid(row=3, column=3)
        tk.Label(insideExtensionFrame, text=f'Version: {STORAGE.Extension.MouseRecorder.version}\nAuthor: {__author__}',
                 anchor='center').grid(row=5, column=3)

        tk.Frame(insideExtensionFrame, background='black', width=3).grid(row=3, column=4, sticky='ns', rowspan=100,
                                                                         padx=5)

        extension2_cpsCounterButton = ttk.Button(insideExtensionFrame,
                                                 text=f'CPS Calculator',
                                                 command=self.cpsCounter)
        extension2_cpsCounterButton.grid(row=3, column=5)
        tk.Label(insideExtensionFrame, text=f'Version: {STORAGE.Extension.CpsCounter.version}\nAuthor: {__author__}',
                 anchor='center').grid(row=5, column=5)

        def pluginManager(folder_path):
            pluginsManagerWindow = tk.Toplevel(extensionsWindow)
            pluginsManagerWindow.title('Plugins Manager')
            Utilities.set_window_icon(pluginsManagerWindow)
            Utilities.child_geometry(pluginsManagerWindow, STORAGE.Extension.ON)
            pluginsManagerWindow.grab_set()

            header_label = tk.Label(pluginsManagerWindow, text='Plugins', font=('Calibri', 25, 'bold'))
            header_label.grid(row=3, column=3, columnspan=2, pady=10)

            files_listbox = tk.Listbox(pluginsManagerWindow)
            files_listbox.grid(row=4, column=3, padx=(10, 0), pady=(10, 0), sticky='nsew')

            for file in Utilities.Function.show_files(r'data\plugins', '.txt'):
                files_listbox.insert('end', file)

            scrollbar = tk.Scrollbar(pluginsManagerWindow, orient='vertical', command=files_listbox.yview)
            scrollbar.grid(row=4, column=4, sticky='ns', padx=(0, 10))
            files_listbox.configure(yscrollcommand=scrollbar.set)

            pluginActionFrame = tk.Frame(pluginsManagerWindow)
            pluginActionFrame.grid(row=5, column=3, sticky='w', pady=5)

            def on_add():
                repetition = 0
                while os.path.isfile(
                        plugin_path := f'data\\plugins\\Untitled{f" ({repetition})" if repetition else ""}.txt'):
                    repetition += 1
                    pluginsManagerWindow.focus()

                with open(plugin_path, 'w') as newplugin:
                    newplugin.write(f'# Plugin: {plugin_path}; Index: {repetition}\n')

                files_listbox.insert('end', os.path.basename(plugin_path))
                files_listbox.yview('end')

            def on_delete(_=None):
                selected_index = files_listbox.curselection()
                if selected_index:
                    selected_file = files_listbox.get(selected_index)
                    if messagebox.askyesno('Delete plugin',
                                           f'Are you sure that you want to remove {selected_file}?\nThe file will be deleted from the disk.',
                                           icon='warning'):
                        try:
                            os.remove(f'{folder_path}\\{selected_file}')
                            files_listbox.delete(files_listbox.get(0, 'end').index(selected_file))
                        except Exception as plugin_error:
                            messagebox.showerror(f'Plugin: {selected_file}',
                                                 f'[{type(plugin_error).__name__}]: {plugin_error}')

            addPluginButton = ttk.Button(pluginActionFrame, text='+', width=2, command=on_add)
            addPluginButton.grid(row=3, column=3, padx=(10, 0))

            removePluginButton = ttk.Button(pluginActionFrame, text='-', width=2, command=on_delete)
            removePluginButton.grid(row=3, column=5)

            def on_rightclick(_):
                selected_index = files_listbox.curselection()
                if selected_index:
                    selected_file = files_listbox.get(selected_index)
                    if not Utilities.Dialogs.Custom.displayFileDialog(selected_file, folder_path, pluginsManagerWindow):
                        files_listbox.delete(files_listbox.get(0, 'end').index(selected_file))

            def on_double_leftclick(_):
                selected_index = files_listbox.curselection()
                if selected_index:
                    selected_file = files_listbox.get(selected_index)
                    with open(folder_path + '\\' + selected_file, 'r') as filerun:
                        try:
                            exec(filerun.read())
                        except Exception as plugin_error:
                            messagebox.showerror(f'Plugin: {selected_file}',
                                                 f'[{type(plugin_error).__name__}]: {plugin_error}')

            files_listbox.bind('<Double-1>', on_double_leftclick)
            files_listbox.bind('<Button-3>', on_rightclick)
            files_listbox.bind('<Delete>', on_delete)

        manageExtensionsButton = ttk.Button(allExtensionsFrame, text='Manage plugins',
                                            command=lambda: pluginManager(r'data\plugins'))
        manageExtensionsButton.grid(row=11, column=3, sticky='ew')

        def closeExtensions():
            if keyboard.is_pressed('ctrl'):
                extensionsWindow.destroy()
                on_window_exit()
                return

            self.deiconify()
            extensionsWindow.destroy()
            STORAGE.Extension.ON = False

            Utilities.add_default_hotkeys()
            Utilities.add_trigger_hotkey()

        extensionsWindow.protocol('WM_DELETE_WINDOW', closeExtensions)

    # class: MouseRecorder
    def mouseRecorder(self):
        STORAGE.Extension.MouseRecorder.ON = recorderWindow = tk.Toplevel(STORAGE.Extension.ON)
        recorderWindow.title(f'MouseRecorder {STORAGE.Extension.MouseRecorder.version}')
        Utilities.set_window_icon(recorderWindow)
        Utilities.child_geometry(recorderWindow, STORAGE.Extension.ON)
        recorderWindow.resizable(False, False)
        recorderWindow.attributes('-topmost', STORAGE.Setting.isTopmost)
        STORAGE.Extension.ON.withdraw()

        keyboard.unregister_all_hotkeys()
        Utilities.add_default_hotkeys()

        allRecorderFrame = tk.Frame(recorderWindow)
        allRecorderFrame.grid(row=3, column=3, sticky='nsew')

        playbackRecordButton = ttk.Button(allRecorderFrame, text='Play', width=9, state='disabled',
                                          command=lambda: threading.Thread(target=playRecord).start())
        playbackRecordButton.grid(row=3, column=3)

        startRecordButton = ttk.Button(allRecorderFrame, text='Record', width=9,
                                       command=lambda: stopRecord() if hook else startRecord())
        startRecordButton.grid(row=3, column=5)

        def recorderSetting():
            recorderWindow.withdraw()

            def saveRecordSettings(widget=None):
                STORAGE.Extension.MouseRecorder.playbackSpeed = playbackSpeedVar.get() / 2
                if isinstance(widget, tk.Checkbutton) and all(
                        not i for i in [recordClicksVar.get(), recordMovementsVar.get(), recordWheelrollsVar.get()]):
                    widget.select()
                STORAGE.Extension.MouseRecorder.isClicksRecorded = bool(recordClicksVar.get())
                STORAGE.Extension.MouseRecorder.isMovementsRecorded = bool(recordMovementsVar.get())
                STORAGE.Extension.MouseRecorder.isWheelrollsRecorded = bool(recordWheelrollsVar.get())
                STORAGE.Extension.MouseRecorder.isInsertedEvents = bool(insertedEventsVar.get())

            recorderSettingWindow = tk.Toplevel(recorderWindow)
            recorderSettingWindow.title('Recorder Settings')
            Utilities.child_geometry(recorderSettingWindow, recorderWindow)
            recorderSettingWindow.resizable(False, False)
            Utilities.set_window_icon(recorderSettingWindow)

            allRecorderSettingFrame = tk.Frame(recorderSettingWindow)
            allRecorderSettingFrame.grid(row=3, column=3, padx=10)

            # PLAYBACK FRAME
            playbackSettingFrame = ttk.LabelFrame(allRecorderSettingFrame, text='Playback speed')
            playbackSettingFrame.grid(row=3, column=3, sticky='ew')
            playbackSpeedVar = tk.IntVar(value=STORAGE.Extension.MouseRecorder.playbackSpeed * 2)
            playbackSpeedSlider = ttk.Scale(playbackSettingFrame, from_=1, to=6, orient='horizontal',
                                            variable=playbackSpeedVar,
                                            command=lambda _: playbackSpeedDisplayLabel.configure(
                                                text=f'x{playbackSpeedVar.get() / 2}'))
            playbackSpeedSlider.grid(row=3, column=3)
            playbackSpeedDisplayLabel = tk.Label(playbackSettingFrame, text=f'x{playbackSpeedVar.get() / 2}')
            playbackSpeedDisplayLabel.grid(row=3, column=5, padx=3)

            # RECORD TARGET FRAME
            recordTargetFrame = ttk.LabelFrame(allRecorderSettingFrame, text='Record targets')
            recordTargetFrame.grid(row=5, column=3, sticky='ew', pady=(5, 0))

            recordClicksVar = tk.IntVar()
            recordClicksCheckbutton = tk.Checkbutton(recordTargetFrame, text='Mouse clicks',
                                                     variable=recordClicksVar,
                                                     command=lambda: saveRecordSettings(recordClicksCheckbutton))
            self.after(10,
                       lambda: recordClicksCheckbutton.select() if STORAGE.Extension.MouseRecorder.isClicksRecorded else None)
            recordClicksCheckbutton.grid(row=3, column=3, sticky='w')

            recordMovementsVar = tk.IntVar()
            recordMovementsCheckbutton = tk.Checkbutton(recordTargetFrame, text='Movements',
                                                        variable=recordMovementsVar,
                                                        command=lambda: saveRecordSettings(recordMovementsCheckbutton))
            self.after(10,
                       lambda: recordMovementsCheckbutton.select() if STORAGE.Extension.MouseRecorder.isMovementsRecorded else None)
            recordMovementsCheckbutton.grid(row=5, column=3, sticky='w')

            recordWheelrollsVar = tk.IntVar()
            recordWheelrollsCheckbutton = tk.Checkbutton(recordTargetFrame, text='Scroll wheel',
                                                         variable=recordWheelrollsVar,
                                                         command=lambda: saveRecordSettings(
                                                             recordWheelrollsCheckbutton))
            self.after(10,
                       lambda: recordWheelrollsCheckbutton.select() if STORAGE.Extension.MouseRecorder.isWheelrollsRecorded else None)
            recordWheelrollsCheckbutton.grid(row=7, column=3, sticky='w')

            # MISCELLANEOUS
            miscellaneousRecordSettingFrame = ttk.LabelFrame(allRecorderSettingFrame, text='Miscellaneous')
            miscellaneousRecordSettingFrame.grid(row=7, column=3, sticky='ew', pady=(5, 0))

            insertedEventsVar = tk.IntVar()
            insertedEventsCheckbutton = tk.Checkbutton(miscellaneousRecordSettingFrame, text='Inserted events',
                                                       variable=insertedEventsVar,
                                                       command=lambda: saveRecordSettings(insertedEventsCheckbutton))

            self.after(10,
                       lambda: insertedEventsCheckbutton.select() if STORAGE.Extension.MouseRecorder.isInsertedEvents else None)
            insertedEventsCheckbutton.grid(row=5, column=3, sticky='w')

            clearEventsButton = ttk.Button(miscellaneousRecordSettingFrame,
                                           text=f'Clear{"" if events else "ed"} events', width=13,
                                           state='normal' if events else 'disabled', command=lambda: [events.clear(),
                                                                                                      clearEventsButton.configure(
                                                                                                          text='Cleared events',
                                                                                                          state='disabled')])
            clearEventsButton.grid(row=9, column=3, sticky='w', padx=5, pady=(0, 5))
            #
            ttk.Button(recorderSettingWindow, text='Auto-saved', state='disabled').grid(row=5, column=3, pady=7)

            def closeRecorderSetting():
                recorderSettingWindow.destroy()
                recorderWindow.deiconify()
                saveRecordSettings()
                if not events:
                    playbackRecordButton.configure(state='disabled')

            recorderSettingWindow.protocol('WM_DELETE_WINDOW', closeRecorderSetting)

        recorderSettingButton = tk.Button(allRecorderFrame, background=allRecorderFrame.cget('background'),
                                          activebackground=allRecorderFrame.cget('background'),
                                          border=0,
                                          image=self.settingImage, cursor='hand2', command=recorderSetting)
        recorderSettingButton.grid(row=3, column=0, padx=3)

        hook: mouse.hook | bool = False
        hookThread: threading.Thread | bool = False
        events = []

        def startRecord():
            nonlocal hook, hookThread
            startRecordButton.configure(text='Stop')
            playbackRecordButton.configure(state='disabled')
            recorderSettingButton.configure(state='disabled')
            if not STORAGE.Extension.MouseRecorder.isInsertedEvents:
                events.clear()

            def backgroundRecord():
                nonlocal hook
                hook = mouse.hook(events.append)

            hookThread = threading.Thread(backgroundRecord())
            hookThread.start()

        def stopRecord():
            nonlocal hook
            mouse.unhook(hook)
            hook = False

            hookThread.join(0)

            startRecordButton.configure(text='Start')
            playbackRecordButton.configure(state='normal')
            recorderSettingButton.configure(state='normal')

        def playRecord():
            startRecordButton.configure(state='disabled')
            playbackRecordButton.configure(text='Playing', state='disabled')
            recorderSettingButton.configure(state='disabled')
            mouse.play(events, STORAGE.Extension.MouseRecorder.playbackSpeed,
                       STORAGE.Extension.MouseRecorder.isClicksRecorded,
                       STORAGE.Extension.MouseRecorder.isMovementsRecorded,
                       STORAGE.Extension.MouseRecorder.isWheelrollsRecorded)
            startRecordButton.configure(state='normal')
            playbackRecordButton.configure(text='Play', state='normal')
            recorderSettingButton.configure(state='normal')

        def closeRecorder():
            if hook and hookThread:
                mouse.unhook(hook)
                hookThread.join(0)

            if keyboard.is_pressed('ctrl'):
                recorderWindow.destroy()
                on_window_exit()
                return
            if keyboard.is_pressed('shift'):
                self.deiconify()
                STORAGE.Extension.ON.destroy()
                keyboard.unregister_all_hotkeys()
                Utilities.add_default_hotkeys()
                Utilities.add_trigger_hotkey()
            else:
                STORAGE.Extension.ON.deiconify()

            STORAGE.Extension.MouseRecorder.ON = False
            recorderWindow.destroy()

        recorderWindow.protocol('WM_DELETE_WINDOW', closeRecorder)

    def cpsCounter(self):
        STORAGE.Extension.ON.destroy()
        STORAGE.Extension.ON = False
        Utilities.add_default_hotkeys()
        Utilities.add_trigger_hotkey()
        self.deiconify()

        def update_cps_and_timer():
            nonlocal click_count, start_time, running
            if running:
                current_time = time.perf_counter()
                elapsed_time = (current_time - start_time) if start_time else 0
                cps = click_count / elapsed_time if elapsed_time > 0 else 0
                cps_label.configure(text=f'CPS: {cps:.2f}')
                timer_label.configure(text=f'Time: {elapsed_time:.3f}s')
                cpsCounterWindow.after(1, update_cps_and_timer)

        def on_button_click():
            nonlocal click_count, running
            click_count += 1
            click_label.configure(text=f'Clicks: {click_count}')
            cpsCounterWindow.focus()

        def start_program():
            nonlocal running, start_time, click_count
            running = True
            click_count = 0
            on_button_click()
            start_time = time.perf_counter()
            stop_button.configure(state='normal')
            start_button.configure(text='Click me!', command=on_button_click)
            update_cps_and_timer()

        def stop_program():
            nonlocal running
            running = False
            stop_button.configure(state='disabled')
            start_button.configure(text='Start', command=start_program)
            cpsCounterWindow.focus()

        STORAGE.Extension.CpsCounter.ON = cpsCounterWindow = tk.Toplevel(self)
        cpsCounterWindow.title('CPS Counter')
        Utilities.set_window_icon(cpsCounterWindow)
        Utilities.child_geometry(cpsCounterWindow, self)

        cpsCounterWindow.grid_columnconfigure(3, weight=1)
        cpsCounterWindow.grid_rowconfigure(3, weight=1)
        frame = ttk.Frame(cpsCounterWindow)
        frame.grid(row=3, column=3, padx=100, pady=20)

        click_count = 0
        start_time = 0
        running = False

        click_label = ttk.Label(frame, text='Clicks: 0')
        click_label.grid(row=0, column=0)

        cps_label = ttk.Label(frame, text='CPS: 0.00')
        cps_label.grid(row=1, column=0)

        timer_label = ttk.Label(frame, text='Time: 0.000s')
        timer_label.grid(row=2, column=0, pady=(0, 3))

        start_button = ttk.Button(frame, text='Start', command=start_program)
        start_button.grid(row=3, column=0, pady=1)

        stop_button = ttk.Button(frame, text='Stop', command=stop_program, state='disabled')
        stop_button.grid(row=4, column=0)

    # class: Position.custom
    def customPositionDialog(self, fromSetting=False):
        if keyboard.is_pressed('ctrl') and not fromSetting:
            return
        if not fromSetting and not STORAGE.Setting.isAutoPopup:
            return
        Utilities.writelog('Custom-position dialog opened', ('', '\n', True))

        self.focus()
        for widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                       self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox, self.clickTypeOptionCombobox,
                       self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton, self.unlimitedRepeatRadiobutton,
                       self.mousePositionRadiobutton, self.customPositionRadiobutton]:
            widget.configure(state='disabled')

        keyboard.unregister_all_hotkeys()

        askPositionDialog = tk.Toplevel(self)
        askPositionDialog.title('')
        Utilities.set_window_icon(askPositionDialog)
        Utilities.child_geometry(askPositionDialog, self)
        askPositionDialog.resizable(False, False)
        askPositionDialog.attributes('-topmost', STORAGE.Setting.isTopmost)

        askPositionDialog.grab_set()
        askPositionDialog.focus()

        positions = STORAGE.FIXED_POSITIONS

        alldialogFrame = tk.Frame(askPositionDialog)
        alldialogFrame.grid(row=3, column=3, padx=15, pady=(15, 0), ipadx=5, ipady=5)
        alldialogFrame.grid_columnconfigure(3, weight=1)

        mainCustomPositionFrame = ttk.LabelFrame(alldialogFrame, text='Manual position', labelanchor='n')
        mainCustomPositionFrame.grid(row=3, column=3, ipadx=15, ipady=5, sticky='ew')
        mainCustomPositionFrame.grid_columnconfigure(3, weight=1)

        choosePositionFrame = tk.Frame(mainCustomPositionFrame)
        choosePositionFrame.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_radiobutton = ttk.Radiobutton(choosePositionFrame, value='manual',
                                                          variable=self.positionType,
                                                          command=lambda: bindradio_all())
        choosePositionFrame_radiobutton.grid(row=3, column=1)

        ttk.Label(choosePositionFrame, text='x=').grid(row=3, column=2, sticky='e')
        xCustomPositionEntry = ttk.Entry(choosePositionFrame, width=4)
        xCustomPositionEntry.grid(row=3, column=3, sticky='w')

        ttk.Label(choosePositionFrame, text=',  y=', anchor='e').grid(row=3, column=4, sticky='e')
        yCustomPositionEntry = ttk.Entry(choosePositionFrame, width=4)
        yCustomPositionEntry.grid(row=3, column=5, sticky='w')
        ttk.Label(choosePositionFrame, text=',  y=', anchor='e').grid(row=3, column=4, sticky='e')

        randomPositionCheckbutton = tk.Checkbutton(choosePositionFrame, text='Random position',
                                                   variable=self.randomPositionVar, command=lambda: [[
                _widget.configure(state='disabled' if self.randomPositionVar.get() else 'normal') for _widget in
                (xCustomPositionEntry, yCustomPositionEntry)],
                submitPositionButton.configure(state='normal' if self.randomPositionVar.get() else 'disabled')])
        randomPositionCheckbutton.grid(row=5, column=1, columnspan=5)

        for _i, _e in zip(positions, (xCustomPositionEntry, yCustomPositionEntry)):
            _e.insert(0, _i)
        xCustomPositionEntry.selection_range(0, 'end')

        ttk.Label(alldialogFrame, text='or').grid(row=5, column=3, pady=5)

        choosePositionFrame_withMouse = ttk.LabelFrame(alldialogFrame, text='Pick position', labelanchor='n')
        choosePositionFrame_withMouse.grid(row=7, column=3, ipadx=15, ipady=5, sticky='ew')
        choosePositionFrame_withMouse.grid_columnconfigure(3, weight=1)

        _choosePositionFrame_withMouse = tk.Frame(choosePositionFrame_withMouse)
        _choosePositionFrame_withMouse.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_withMouse_radiobutton = ttk.Radiobutton(_choosePositionFrame_withMouse, value='picker',
                                                                    variable=self.positionType,
                                                                    command=lambda: bindradio_all())
        choosePositionFrame_withMouse_radiobutton.grid(row=3, column=2, sticky='e')

        choosePositionWithMouseButton = ttk.Button(_choosePositionFrame_withMouse, text='Choose position',
                                                   command=lambda: choose_position_by_mouse(), state='disabled')
        choosePositionWithMouseButton.grid(row=3, column=3, ipadx=5)

        ##
        locatefile = STORAGE.LOCATE_SCREEN[1].strip()
        ttk.Label(alldialogFrame, text='or').grid(row=9, column=3, pady=5)

        choosePositionFrame_withLocate = ttk.LabelFrame(alldialogFrame, text='Locate on screen', labelanchor='n')
        choosePositionFrame_withLocate.grid(row=11, column=3, ipadx=15, ipady=5, sticky='ew')
        choosePositionFrame_withLocate.grid_columnconfigure(3, weight=1)

        _choosePositionFrame_withLocate = tk.Frame(choosePositionFrame_withLocate)
        _choosePositionFrame_withLocate.grid(row=3, column=3, pady=(5, 0))

        choosePositionFrame_withLocate_radiobutton = ttk.Radiobutton(_choosePositionFrame_withLocate, value='locate',
                                                                     variable=self.positionType,
                                                                     command=lambda: bindradio_all())
        choosePositionFrame_withLocate_radiobutton.grid(row=3, column=2, sticky='e')

        choosePositionwithLocateButton = ttk.Button(_choosePositionFrame_withLocate, text='Choose image',
                                                    command=lambda: choose_image_to_locate(), state='disabled')
        choosePositionwithLocateButton.grid(row=3, column=3, ipadx=5)

        def choose_image_to_locate():
            nonlocal locatefile
            old_locatefile = locatefile
            locatefile = filedialog.askopenfilename(title="Image to locate",
                                                    filetypes=(("PNG files", "*.png"), ("JPG files", "*.jpg")),
                                                    parent=askPositionDialog)
            if not locatefile:
                return
            elif not pyautogui.onScreen(*Image.open(locatefile).size):
                messagebox.showwarning('Unable to process',
                                       f'Your image resolution is too high.\n\nPath: {locatefile}\nImage size: {"x".join(map(str, Image.open(locatefile).size))}\nMaximum size: {"x".join(map(str, pyautogui.size()))}')
                locatefile = old_locatefile
                return
            showLocatePathLabel.configure(text='Path: {}'.format(
                (lambda x: '...' + x[0][-12 if len(x[0]) > 12 else 0:] + x[1])(
                    os.path.splitext(os.path.basename(locatefile)))))
            submitPositionButton.configure(state='normal')

        showLocatePathLabel = tk.Label(choosePositionFrame_withLocate, text='Path: {}'.format(
            (lambda x: '...' + x[0][-12 if len(x[0]) > 12 else 0:] + x[1])(
                os.path.splitext(os.path.basename(STORAGE.LOCATE_SCREEN[1]))) if STORAGE.LOCATE_SCREEN[
                1] else f'(.png, .jpg)'), anchor='e')
        showLocatePathLabel.grid(row=5, column=3)

        moveLocateValue = tk.IntVar()
        moveLocateCheckbutton = tk.Checkbutton(choosePositionFrame_withLocate, text='Move mouse on detection',
                                               variable=moveLocateValue)
        moveLocateCheckbutton.grid(row=7, column=3)
        moveLocateCheckbutton.select() if STORAGE.LOCATE_SCREEN[0] else None
        moveLocateCheckbutton.configure(state='disabled')
        ##

        submitPositionFrame = tk.Frame(alldialogFrame)
        submitPositionFrame.grid(row=13, column=3, sticky='sew', pady=(20, 5))
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
            pos = [i if i.strip() else 'None' for i in (xCustomPositionEntry.get(), yCustomPositionEntry.get())]
            positions = tuple([int(c) for c in pos if c.isdigit()])
            showPositionsLabel.configure(
                text=f'Position: x={pos[0][:4]}{"..." if len(pos[0]) > 4 else ""}; y={pos[1][:4]}{"..." if len(pos[1]) > 4 else ""}')

        def checkSubmitable(event=False):
            if not event:
                askPositionDialog.focus()
            submitPositionButton.configure(state='disabled')
            if self.positionType.get().strip() != '':
                if xCustomPositionEntry.get().isdigit() and yCustomPositionEntry.get().isdigit():
                    submitPositionButton.configure(state='normal')

            if event and self.positionType.get() == 'manual':
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

            displaying = tk.Frame(transparent_layer, background='yellow')
            displayPosition = tk.Label(displaying, text=f'x={mousex}; y={mousey}', background='yellow',
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

        def bindradio_all():
            nonlocal positions
            pos = tuple(map(str, positions))
            for _widget in [choosePositionFrame_radiobutton, choosePositionFrame_withMouse_radiobutton,
                            choosePositionFrame_withLocate_radiobutton]:
                if _widget.cget('value') == self.positionType.get():
                    _widgetdict = {
                        'manual': [randomPositionCheckbutton, xCustomPositionEntry, yCustomPositionEntry],
                        'picker': [choosePositionWithMouseButton],
                        'locate': [choosePositionwithLocateButton, moveLocateCheckbutton]
                    }
                    for _key in _widgetdict.keys():
                        askPositionDialog.focus()
                        if _key == 'manual':
                            askPositionDialog.after(10, xCustomPositionEntry.focus)
                            pos = tuple([c.get() if c.get().isdigit() else str(positions[i]) for i, c in
                                         enumerate((xCustomPositionEntry, yCustomPositionEntry))])
                        elif _key == 'picker':
                            submitPositionButton.configure(state='normal' if all(
                                0 <= c < s for c, s in zip(positions, pyautogui.size())) else 'disabled')
                        elif _key == 'locate':
                            submitPositionButton.configure(state='normal' if locatefile else 'disabled')

                        for __widget in _widgetdict[_key]:
                            if self.positionType.get().strip() == 'manual' and self.randomPositionVar.get() and __widget in [
                                xCustomPositionEntry, yCustomPositionEntry]:
                                __widget.configure(state='disabled')
                                continue
                            __widget.configure(
                                state='normal' if _key == self.positionType.get().strip() else 'disabled')
                    break

            positions = tuple(map(int, pos))
            if self.positionType.get() != 'locate':
                showPositionsLabel.configure(
                    text=f'Position: x={pos[0][:4]}{"..." if len(pos[0]) > 4 else ""}; y={pos[1][:4]}{"..." if len(pos[1]) > 4 else ""}')
            else:
                showPositionsLabel.configure(text='Position: x/y=locate_image')

        def submit_position():
            if self.positionType.get() != 'locate' and not pyautogui.onScreen(*map(int, positions)):
                messagebox.showwarning('Warning', 'Your chosen position is outside of the screen.',
                                       parent=askPositionDialog)
                return
            STORAGE.FIXED_POSITIONS = tuple(map(int, positions))
            if self.positionType.get() == 'locate':
                STORAGE.LOCATE_SCREEN = (bool(moveLocateValue.get()), locatefile)
                self.customPositionRadiobutton.configure(text=f'Custom (Locate)')
                self.showInterval.configure(
                    text=f'Interval/l: ~{":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}')
            else:
                self.customPositionRadiobutton.configure(text=f'Custom ({", ".join(map(str, positions))})')
            askPositionDialog.destroy()
            Utilities.add_trigger_hotkey()
            Utilities.add_default_hotkeys()

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
        bindradio_all()

        def on_exit():
            askPositionDialog.destroy()
            self.positionVar.set(STORAGE.Garbage.old_positionVar[0])
            STORAGE.Garbage.trace_old_positionVar(self.positionVar.get())
            if not fromSetting:
                for _widget in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox,
                                self.intervalMillisecondCombobox, self.mouseButtonOptionCombobox,
                                self.clickTypeOptionCombobox, self.limitedRepeatSpinbox, self.limitedRepeatRadiobutton,
                                self.unlimitedRepeatRadiobutton, self.mousePositionRadiobutton,
                                self.customPositionRadiobutton]:
                    _widget.configure(state='readonly' if _widget in [self.clickTypeOptionCombobox,
                                                                      self.mouseButtonOptionCombobox] else 'normal')
            Utilities.writelog('Custom-position dialog closed. No position was chosen', ('', '\n', True))

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

    def bindChosenAll(self, event: tk.Event | bool = False):
        self.intervals = [
            str(int(i.get()) if i.get().isdigit() else i.get()).zfill(
                2 if self.intervalWidgets.index(i) != len(self.intervalWidgets) - 1 else 3) for i in
            self.intervalWidgets]
        if event and str(event.type) != '3':
            event.widget.master.focus()
            event.widget.set(self.intervals[self.intervalWidgets.index(event.widget)])
        self.showInterval.configure(
            text=f'Interval{"/l: ~" if self.positionType.get() == "locate" and self.positionVar.get() == "custom" else ": "}{":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}')
        Utilities.writelog(
            f'Set the interval to: {":".join([i.get().zfill(2) for i in [self.intervalHourCombobox, self.intervalMinuteCombobox, self.intervalSecondCombobox]])}.{self.intervalMillisecondCombobox.get().zfill(3)}',
            ('', '\n', True))


def background_tasks():
    Utilities.writelog('Background tasks started', ('', '\n', True))
    stoplisten = lambda: None
    if STORAGE.Setting.isVoiceCommand:
        stoplisten = Utilities.listen_to_voice(root)
    while True:
        if not STORAGE.RUNNING:
            continue
        if STORAGE.Garbage.last_isVoiceCommand != STORAGE.Setting.isVoiceCommand:
            if STORAGE.Setting.isVoiceCommand:
                stoplisten = Utilities.listen_to_voice(root)
                print('start listen lol')
            else:
                stoplisten()
                print('stopped listten lol')
        STORAGE.Garbage.last_isVoiceCommand = STORAGE.Setting.isVoiceCommand

        if STORAGE.Garbage.root_geometry is None:
            STORAGE.Garbage.root_geometry = root.geometry()
        if root.positionVar.get() == 'mouse':
            root.mousePositionRadiobutton.configure(text='Current ({0}, {1})'.format(*pyautogui.position()))
        else:
            root.mousePositionRadiobutton.configure(text='Current (0, 0)')

        if not STORAGE.Garbage.isTerminalOn and (keyboard.is_pressed('esc') or keyboard.is_pressed('enter')):
            if not STORAGE.Garbage.isMasterFocus:
                try:
                    root.focus_get().master.focus()
                    STORAGE.Garbage.isMasterFocus = True
                except (AttributeError, KeyError):
                    STORAGE.Garbage.isMasterFocus = False
            if root.limitedRepeatSpinbox.get().strip() == '':
                root.limitedRepeatSpinbox.set(1)
                root.spinTimeLabel.configure(text=f'time{"s" if root.spinTime > 1 else ""}')
        else:
            STORAGE.Garbage.isMasterFocus = False
        root.update()


# noinspection PyUnresolvedReferences
def on_window_exit():
    if keyboard.is_pressed('ctrl+shift+alt'):
        Utilities.start(restart=True)
        return
    if keyboard.is_pressed('shift') and not keyboard.is_pressed('ctrl') and not STORAGE.Extension.MouseRecorder.ON:
        STORAGE.BACKGROUND = True
        root.withdraw()
        return
    if not keyboard.is_pressed('ctrl') and STORAGE.Setting.isAutoPopup:
        if not messagebox.askyesno(f'Closing {__project__}', f'Are you sure to close {__project__} {__version__}?'):
            return
    save_data()

    root.destroy()
    STORAGE.RUNNING = False

    Utilities.writelog(f'Closed {__project__} {__version__}', ('', '\n}\n', True))
    backgroundThread.join(0)
    print(f'{__project__} {__version__} was closed.')
    os._exit(0)


root: tk.Tk | Application | None = None
backgroundThread: threading.Thread | None = None
Utilities.start()
