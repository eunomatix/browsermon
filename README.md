# BrowserMon - Simple Python Application

BrowserMon is a straightforward Python application that monitors web browsers. To run this application, follow the instructions below:

# Setup
## For linux	
1) ```git clone -b release https://github.com/eunomatix/browsermon.git```
In order to run BrowserMon you must switch to Super User/root User
2) ```su```
3) ```chmod +x linux_install.sh```
4) ```./linux_install.sh```

To verify that the service is up and running: 
	```systemctl status browsermon.service```

To stop the service temporarily 
	```systemctl stop browsermon.service```

To Uninstall: 
	Run the ```./linux_uninstall.sh``` as root

binaries for Linux coming soon ... 
## For Windows x64
1) Go to browsermon repository > Actions > Latest Version > Download the ```browsermon.exe```
2) After downloading extract the folder in ```C:\browsermon```
3) To install the service open powershell as admin in the ```C:\browsermon```  and run the following commands <br>
	```.\browsermon.exe --startup=auto install```
    <br>
	```.\browsermon.exe start```
4) ```browsermon.conf``` file should be located in ```C:\browsersmon``` otherwise service will run with defaults configurations. 

You can verify that service is running by opening **Services** through search and checking for ```browsermon``` 

To stop the service: 
	You can do that through the **Services** app in windows or you could run ```browsermon.exe stop``` 
To remove the service 
		Make sure to first stop the service. 
	```browsermon.exe remove```

You can also clone the repository and install browsermon in fewer steps
1) ```git clone -b release https://github.com/eunomatix/browsermon.git```
2) Run the ```win_install.ps1``` as administrator 