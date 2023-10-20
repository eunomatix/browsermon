# ****************************************************************************
# **
# ** Copyright (C) 2023 EUNOMATIX
# ** This program is free software: you can redistribute it and/or modify
# ** it under the terms of the GNU General Public License as published by
# ** the Free Software Foundation, either version 3 of the License, or
# ** any later version.
# **
# ** This program is distributed in the hope that it will be useful,
# ** but WITHOUT ANY WARRANTY; without even the implied warranty of
# ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# ** GNU General Public License for more details.
# **
# ** You should have received a copy of the GNU General Public License
# ** along with this program. If not, see <https://www.gnu.org/licenses/>.
# **
# ** Contact: info@eunomatix.com
# **
# **************************************************************************/
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
        mp.freeze_support()
        import controller
        controller = controller.BrowsermonController()
        controller.run()
