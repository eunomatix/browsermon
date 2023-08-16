import sys
import platform
import multiprocessing as mp 

SYSTEM = platform.system()

if __name__ == '__main__':
    if SYSTEM == "Windows":
        import browsermon_service
        mp.freeze_support()
        if len(sys.argv) == 1:
            browsermon_service.servicemanager.Initialize()
            browsermon_service.servicemanager.PrepareToHostSingle(browsermon_service.browserMonService)
            browsermon_service.servicemanager.StartServiceCtrlDispatcher()
        else:
            browsermon_service.win32serviceutil.HandleCommandLine(browsermon_service.browserMonService)
    elif SYSTEM == "Linux": 
        import controller
        controller = controller.BrowsermonController()
        controller.run()
