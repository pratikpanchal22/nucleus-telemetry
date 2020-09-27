### Start with development:

```
cd to-desired-location  
git clone https://github.com/pratikpanchal22/nucleus-telemetry.git   
```

### Create & activate virtual environment

```
cd nucleus-telemetry
python3 -m venv ./venv
source venv/bin/activate
```

##### Install dependencies

```
pip3 install -r requirements.txt
```

##### Run application

```
python3 nucleus-telemetry/nucleus-telemetry.py
```

##### Deactivate virtual environment

```
deactivate
```
----------------------------------------------------------------------------------
### Add application as a service

```
cp nucleus-telemetry/nucleus-telemetry.service /etc/systemd/system/.
```

Edit the User and Exec parameters to match the actual user the application needs to run as
Edit the Exec parameter to match the correct path for python3 and nucleus-telemetry.py

##### Start the service:  
```
systemctl start nucleus-telemetry.service
``` 
  
##### Enable the service to start automatically on boot:  
```
systemctl enable nucleus-telemetry.service  
```
  
##### To restart the service:  
```
systemctl restart nucleus-telemetry.service
```
or
```
systemctl stop nucleus-telemetry.service
...
systemctl start nucleus-telemetry.service
```

