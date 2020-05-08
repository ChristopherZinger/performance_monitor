from pynput import keyboard
from pynput import mouse
import time
import pygetwindow as gw
import psutil
import  os
import subprocess as sp
import win32gui,win32process
from db_manager import db_manager



class Manager:
    def __init__(self):
        self.click_count = 0
        self.key_count = 0
        self.events = []
        self.processes = []
        self.active_window = None
        self.debug_mode = False

    def append_events(self, item):
        self.events.append(item)
        #update click and key count
        if item[0] == 'MOUSE':
            self.click_count += 1
        else:
            self.key_count += 1
        #save data when key.space or key.enter or 10>clicks. Then restart the count variables
        if self.click_count > 12 or str(item[1]) == 'Key.space' or str(item[1]) == 'Key.enter' or self.key_count > 12:
            self.save_events()

    def save_events(self):
        db_manager.insert_evens_to_db(self.events)
        # reset variables
        self.events = []
        self.click_count, self.key_count = 0, 0
        print('saving data to db.')

    def get_active_window(self):
        active_window = gw.getActiveWindow()
        if active_window is not None:
            active_window_title = active_window.title
            #get pid of active window process
            threadid,active_window_pid = win32process.GetWindowThreadProcessId(
            gw.getActiveWindow()._hWnd
            )
            # firs check in pids that were already pulled outbefore
            for temp_pid in self.processes:
                if temp_pid['pid'] == active_window_pid:
                    return [temp_pid['name'], active_window_title, time.time(), None]
            # check in active processes if not in stored proccesses
            self.processes = [] # reset processes
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', ])
                    self.processes.append(pinfo)
                    if active_window_pid == pinfo['pid'] :
                        return [pinfo['name'], active_window_title, time.time(), None]
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    print('Error while listing processes pid.')
        return [None, None, time.time(), None]


    def on_click(self,x, y, button, is_pressed):
        # save click when released
        if not is_pressed:
            mouse_event = ['MOUSE',  str(button.name), 'up' , x, y ,time.time()]
            self.append_events(mouse_event)
            # check if active window was updated
            prev_window = self.active_window
            active_window = self.get_active_window()
            if not self.active_window or prev_window[1] != active_window[1]: # compare window titles
                if self.active_window is not None:
                    self.active_window[3] = active_window[2] # update end_time
                db_manager.insert_active_window_to_db(active_window, prev_window)
                self.active_window = active_window

                #print('save new active window.',self.active_window)


    def on_press(self,key):
        try:
            keyboard_event = ['KEY', str(key.char), 'down', None, None ,time.time()]
        except AttributeError:
            keyboard_event = ['KEY', str(key.name), 'down', None, None, time.time()] # key is not a letter (eg enter)
        self.append_events(keyboard_event)
        # Stop listener - debug mode
        if self.debug_mode and key == keyboard.Key.esc:
            return False



def main():
    #create manager class instanve
    manager = Manager()
    # Collect events - mouse
    try:
        with mouse.Listener(on_click=manager.on_click) as listener:
            # Collect events - key
            with keyboard.Listener(
                    on_press=manager.on_press) as listener:
                listener.join()
    except Exception as e:
        print(e)




if __name__ =='__main__':
    main()
