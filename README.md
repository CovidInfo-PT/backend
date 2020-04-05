#Documentation for COVID Project

## Company Validator - Python

### Geohashing
Installed using `pip install python-geohash`. 
Documentation [here](https://github.com/hkwi/python-geohash).

**1. Regarding the precision**

By default, it encodes with a precision of 12.

All the precisions can be found bellow:

```
#   km      
1   ± 2500
2   ± 630
3   ± 78
4   ± 20
5   ± 2.4
6 	 ± 0.61
7   ± 0.076
8   ± 0.019
9   ± 0.0024
10  ± 0.00060
11  ± 0.000074
```

We will save the data with a precision of 8.

**2. How to get the data needed to produce the geoshash?**

To generate a geohash we need the latitude and longitude of a certain spot. Since we are not asking them to the users, we must use some method to get this data.

The users will submit the google maps url of a certain company, so we will use this link. To do so:

1.	Get the extendend url of a google maps url (the user can submit a short version of the url);
2. Extract the coordinates from the complete url of a place;
3. Apply the geohash fucntion over the coordiantes.

Code sample:

``` python
def gmaps_url_to_coordinates(self):
        try:
            # if the link is a shorten one, we need to get the longer version
            complete_url = requests.get(self.gmaps_url).url
            splitted_url = complete_url.strip().split("@")[1].split(",")
            latitude = splitted_url[0]
            longitude = splitted_url[1]
            return float(latitude), float(longitude)
        except:
            self.errors.append("Couldn't decode gmaps url")
            return -1, -1
```
    
**3. File ordering according to the geohash**

In the initial versions of this project we will serve static files. We will have several json files that group companies from near places. 

To do this, all the companies that have the same 4 bytes of their geohashes will be inside the same json, wich means that they are, at most, 20 km far from one another.

### Images

Since we want to reduce the usage of the network between our server and the client, we decided to host the images in an external service.

To do so, we decided to host them on imgurl. We needed to create an account to use the api. This api will allow us to submit images using python.

Account details:

| Key | Value |
| --- | --- |
|username | covidproximo |
|email | covidinfopt@gmail.com|
|password | xxx |
| Api - clientID | xxx |
| Api -client secret | xxx |

But we have a problem, since the images are on the google drive. To solve this, we must:

1. Make the directory hosting the pictures public (accessible by url);
2. Get the image url on the google drive ;
3. Extract the file ID from the image ;
4. Use google drive download url with the file ID we obtained  to download de image (to bytes);
5. Upload the image we downloaded (in bytes) to the imgur api;
6. If everything is fine, the uplaod will return a link pointing to our image.


[Code sample] Get the image from the google drive:

``` python
# get the image from the google drive
    m_bytes = bytes()
    try:
         # get the image id
        img_id = self.image_url_drive.strip().split("id=")[1]  
        # get bytes from the image
        r = requests.get("{}{}".format(self.GDRIVE_DOWNLOAD_BASE_LINK, img_id), stream=True)
        if r.status_code == 200:
            for chunk in r:
                m_bytes += (chunk)
    except Exception as e: 
        self.errors.append("unable to download image - {}!".format(e))
```

[Code sample] Upload image (in bytes) to imgur:

``` python
# post the image on imgur
    try:
        data = {"image": m_bytes, "type":"file", "name":self.company_name}
        headers = {'Authorization': 'Client-ID XXXXX'}
        r = requests.post(self.IMGUR_UPLOAD_API_CAL, data = data, headers=headers)
        # if upload resulted in an error
        if "error" in r.json()["data"]:
            self.errors.append("Error on uploading image to imgur - {}!".format(r.json()["data"]["error"]))
        # if all ok
        imgur_link_to_img = r.json()["data"]["link"]
        self.company_dic["imagens"] = {"logotipo":imgur_link_to_img, "foto_exterior":""}
    except:
        self.errors.append("unable to upload image to imgur!")
```


## Form Validator - Python

This class will validate the CSV containing all the data provided by Google Form where the users add new companies. For now, it is configured to recive a csv file, but the goal is for this class to be a cron job that automatically pull the form data and processes it.

Once it receives the data, it parses it into a list containing several lists, that hold all the data of single line.

We will iterate over all the lines of the csv and the first step we take is to produce a hash that corresponds to the companies signature.

``` python
company_hash = hashlib.sha256((row[3] + row[4]).encode('utf-8')).hexdigest() 
# row[3] - parish of the company
# row[4] - name of the company
```

If this hash is already in the file `added_companies_hashes`, we will ignore this entry, since the company is already in the 'database'.

Else, the data (a single line representing a company) is passed to the company validator.

 
If the data is valid and and there where no errors generating the company, We will parse the company dictionary to a json.

Then, we will get the county geohash, taht will be used to group the different companies. We are using the first 4 bytes of the geohash as the county_geohash.

If there is a json file with that county identifier, the company json will be added to that json. Else, we will create a new jsons (<county\_geohash>.json) with the json data regarding the company that we validated.

We will also add the company\_hash to the file `added_companies_hashes`.


## Backups

Right now, the backups are create by a python cron job. This jobs creates a zip of all the files we want to back up and sends it to AWS S3 Buckets. This zip contains the timestamp representing the moment when this backup was created.

Besides being uploaded directly to S3 buckets, the zip remains in the directory relative to the backups.

Documents that mus be backed up:

* All jsons that contain information regarding the counties and companies;
* The file containing the list of the companies that were already creaetd;
* The logs of the application.

Regarding to the access to S3 buckets, env variables are used to store the access key and the secret key needed to authenticate the upload.

These variables must be setted before running the cron job.

``` python
export COVID_AWS_S3_ACCESS_KEY=xxxxxxxx
export COVID_AWS_S3_SECRET_KEY=yyyyyyyy
```

We can load this variables into python, using:

``` bash
ACCESS_KEY = os.getenv('COVID_AWS_S3_ACCESS_KEY') 
SECRET_KEY = os.getenv('COVID_AWS_S3_SECRET_KEY')
```

The cron job must run, at least, once a day.

Note: All the python modules needed are inside `venv_backups`


## Deployment

To deploy our solution, we are using the VM provided by prof. João Paulo Barraca, over `78.46.194.121`.

Let's take a look into all the steps needed to deploy our solution.

**1. Install NGINX:**


* Install : `apt install nginx`
* Start the nginx service: `service nginx start`
* Verify if the service is running: `ps ax | grep nginx`
* The default configuration is available on: `/etc/nginx/sites-available/default`

For now, if you go to `http://78.46.194.121/` you should get the nginx default web page.	


**2. Configure Gunicorn:**

(We followed [this](digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04) tutorial)

Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for UNIX. It's a pre-fork worker model. The Gunicorn server is broadly compatible with various web frameworks, simply implemented, light on server resources, and fairly speedy.

We are using Gunicorn as server to improve the number of clients we can accept and to improve the overall performance of our server.

To install Gunicorn on venv: `python3 -m pip install -U gunicorn==19.7.1`

Due to some witchcraft and sorcery, the Gunicorn binary file couldn't be found on `venv/bin`, so we had to install Gunicorn in ubuntu `apt install gunicorn3` and used this bin to run our service. 

1. If you haven't done so, open the port where you want the server your application (in our case: port 9000): `sudo ufw allow 9000`
2. Try to run the project in this port: `python3 manage.py runserver 0.0.0.9000` 
3. If everything was ok, you can now proceed to using the uwsgi, to test the wgsi.py file: `uwsgi --http :9000 --wsgi-file covid_rest_api/wsgi.py` (you should be able to access your application on port 9000)
4. Now, test the Gunicorn: `gunicorn covid_rest_api.wsgi --bind 0.0.0.0:9000` (you should be able to access your application on port 9000)

All this commands were called inside the base covid\_rest\_api dir!

Now, we will create a service to instanciate a Gunicorn Server. This will allow us to deploy this server in a much simpler way.

1. Create the service file: `vim /etc/systemd/system/gunicorn_covid_rest_api.service`
2. The file will contain the following:

``` 
[Unit]
Description=gunicorn covid rest api daemon
After=network.target

[Service]
Group=www-data
WorkingDirectory=/home/covid_rest_api
ExecStart=/bin/bash -c "source venv/bin/activate && /usr/bin/gunicorn3 --access-logfile - --workers 3 --bind unix:/home/covid_rest_api/covid	_rest_api.sock covid_rest_api.wsgi:application"
[Install]
WantedBy=multi-user.target
```

Note that, the code to be executed will be the one on *ExecStart=*. First of all we activate our projects venv, and then, we call Gunicorn to launch our server.

Some information on this service:

* To start the service: `systemctl start gunicorn_covid_rest_api`
* To check its status: `systemctl status gunicorn_covid_rest_api`

Everytime we change this service definition file, we must reload the services: `systemctl daemon-reload`

* If occurs an error when launching the service, we can also check it by: `journalctl -u gunicorn_covid_rest_api`

* To stop the service: `systemctl stop gunicorn_covid_rest_api`

Whenever the Gunicorn is running, it creates a socket on `covid_rest_api/covid_rest_api.sock`. All the other programs and services will communicate with Gunicorn through this socket.

**3. NGINX + Gunicorn:**


After configuring the Gunicorn Service, it's time to configure the NGINX. To do so:

1. Create the configuration file: `vim /etc/nginx/sites-available/covid_rest_api`
2. The basic configuration should be: 

```
server {
    listen 9000;
    server_name 78.46.194.121;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/covid_rest_api;
    }
        location / {
        include proxy_params;
        proxy_pass http://unix:/home/covid_rest_api/covid_rest_api.sock;
    }
}
```

3. After the confirguration file has been created in the *sites-available* directory. We should create a symbolic link to the *sites-enabled* directory: `ln -s /etc/nginx/sites-available/covid_rest_api /etc/nginx/sites-enabled`.
4. Check if the nginx configuration files are correct: `sudo nginx -t`
5. If no errors are reported restart nginx : `sudo systemctl restart nginx`
6. Close the port opened for the initial tests and allow the ports for NGINX: `sudo ufw delete allow 9000` + `sudo ufw allow 'Nginx Full'`
7. Start the NGINX server:  `sudo systemctl start nginx`.


In case of getting errors when trying to acess the application, check the NGINX error log `tail /var/log/nginx/error.log`.

One of the errors that migh appear is the following: `*1 connect() to unix:/root/covid_rest_api/covid_rest_api.sock failed (13: Permission denied) while connecting to upstream`

This error occurs because the user doesn't have permission to read some of the directories in the directory tree to the socket file. To avoid this error, check if the user has read and write permissions in all the directories leading to the communication socket with the gunicorn.


Now, we have to change the configuration of the nginx server. We can select which applications we will serve according to the dns from where the request came from.
We can use this configuration:

```
# if we make a request toapi.proxi-mo.pt -> return the api
server {
    listen 80;
    listen [::]:80;
    server_name api.proxi-mo.pt;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/covid_rest_api;
    }
        location / {
        include proxy_params;
        proxy_pass http://unix:/home/covid_rest_api/covid_rest_api.sock;
    }
}


# if we make a request to http://78.46.194.121/ -> return nginx custom html
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
                try_files $uri $uri/ =404;
        }
}
```


