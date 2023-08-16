import win32serviceutil
import win32service
import win32event
import servicemanager
import socket 

import controller

class browserMonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "browsermon"
    _svc_display_name_ = "browsermon"
    _svc_description_ = "browser monitor service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        win32service.SERVICE_AUTO_START
        self.controller = controller.BrowsermonController()
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.controller.launcherObj.shared_lock.release() 

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.controller.run()
