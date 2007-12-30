#!/usr/bin/python
"""
sh /tmp/win3d.kill; FvwmCommand Module win3d.py

tail -f /tmp/*d.log
"""
import os, traceback, math, time
os.chdir("/my/proj/headtrack")

import sys
sys.path.append("Fvwmpy-2.0")

import Fvwm
from Fvwm import FvwmModule, WINDOW_NONE, Types
from Tracker import Tracker

logFile = open("/tmp/win3d.log", "a")
def log(*msg):
    print >>logFile, ' '.join(map(str, msg))
    logFile.flush()
log("kill %s" % os.getpid())
f = open("/tmp/win3d.kill", "w")
f.write("kill %s" % os.getpid())
f.close()

class DebugTracker(Tracker):
    def feed_pkt(self, pkt):
        log("track: %s" % pkt)
        return Tracker.feed_pkt(self, pkt)

class Win3d(FvwmModule):
    def send(self, command, window=WINDOW_NONE, cont=1):
        log("send: %s" % command)
        return FvwmModule.send(self, command, window, cont)
    def get_windowlist(self):
        #debug version
	t = DebugTracker()
	def callback(self, pkt, tracker=t):
	    if Types[pkt.msgtype] == 'M_END_WINDOWLIST':self.stop()
	    else: tracker.feed_pkt(pkt)
	cache = self._FvwmModule__override(callback)
	self.send('Send_WindowList');self.start();self.__restore(cache)
	return t
    
    def __init__(self, argv):
        FvwmModule.__init__(self, argv)
        self.set_mask()
        self.send("Set_Mask 4294967295")

        self.send("Move 2963p 178p", window=0x3e00004)

# pager sends this
##   SetMessageMask(fd,
##                  M_VISIBLE_NAME |
##                  M_ADD_WINDOW|
##                  M_CONFIGURE_WINDOW|
##                  M_DESTROY_WINDOW|
##                  M_FOCUS_CHANGE|
##                  M_NEW_PAGE|
##                  M_NEW_DESK|
##                  M_RAISE_WINDOW|
##                  M_LOWER_WINDOW|
##                  M_ICONIFY|
##                  M_ICON_LOCATION|
##                  M_DEICONIFY|
##                  M_RES_NAME|
##                  M_RES_CLASS|
##                  M_CONFIG_INFO|
##                  M_END_CONFIG_INFO|
##                  M_MINI_ICON|
##                  M_END_WINDOWLIST|
##                  M_RESTACK);
##   SetMessageMask(fd,
##                  MX_VISIBLE_ICON_NAME|
##                  MX_PROPERTY_CHANGE);

        

        self.register("M_CONFIGURE_WINDOW", self.ConfigureWindow)
        
        log("windowlist")
        #self.tracker = self.get_windowlist()
        self.tracker = Tracker()
        log("windowlist done")

#        for win in self.tracker.get_windows():
#            log((win, win.name, win.x, win.y, win.width, win.height, win.desk))

        self.send("Send_WindowList")

        # pager sends this
        self.send("NOP FINISHED STARTUP")
        self.lastSend = None

    def start(self):
        self._Fvwm__done = 0
        while not self._Fvwm__done:
            t = time.time()
            if t - .1 > self.lastSend:
                log("mv")
                self.lastSend = t
                self.send("Move %dp 178p" % (2960+math.sin(t)*150),
                          window=0x3e00004)
            time.sleep(.01)
            self.do_dispatch()


    def RaiseWindow(self, pkt):
        pass
        #self.unhandled_packet(pkt)
        #log(("raise", pkt.db_entry, pkt.top_id, pkt.frame_id))

    def NewPage(self, pkt):
        self.unhandled_packet(pkt)
        log((pkt.desk,))

    def AddWindow(self, p):
        if p.top_id == p.frame_id == 1:
            return
        self.unhandled_packet(p)
        log(("add", p.x, p.y, p.width, p.height, p.top_id, p.frame_id))

    def ConfigureWindow(self, p):
        self.unhandled_packet(p)
        log(("cfg", p.x, p.y, p.width, p.height, p.top_id, p.frame_id))

    def DestroyWindow(self, p):
        log(("destroy", p.top_id, p.frame_id, p.db_entry))

    def unhandled_packet(self, pkt):
        log(("up", pkt))
        self.tracker.feed_pkt(pkt)

if __name__ == '__main__':
    try:
        Win3d(sys.argv).start()
    except Exception, e:
        log(traceback.format_exc())
        raise
