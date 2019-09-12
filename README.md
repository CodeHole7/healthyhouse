# Radonmeters

## Deploying
You should install
<br>
"Vagrant" and "VirtualBox" applications.
<br>
for working with this project.

If these packages were installed,<br> 
please go to project's root folder and create `.env` file in the `config` folder.<br>
`cp env.example config/.env`

After this call the next command in the console:
- `vagrant up`

When installation will be done, please do next actions in the console:
- ``vagrant ssh``

We need to have two additional libs in system for running PDF file generator.
- ``sudo apt-get install libcairo2-dev`` Needed for install Cairo & Pango.

- ``sudo apt-get install libdmtx0a`` Needed for datamatrix

*Possible problems during environment setup in Ubuntu*:
(1) **Problem**: It appears your machine doesn't support NFS, or there is not an adapter to enable NFS on this machine for Vagrant. Please verify that `nfsd` is installed on your machine, and try again. If you're on Windows, NFS isn't supported. If the problem persists, please contact Vagrant support.
**Solution** `apt install nfs-kernel-server nfs-common`

## Initialization of the project
<b>Go to project root and install all needed requirements.</b>
- ``pip install -r requirements/local.txt``

<b>The next command can reset your changes in the database to initial state.</b>
- ``python manage.py init_project``

This command will do the next actions:
- Initialize migrations;
- Initialize countries;
- Initialize categories;
- Initialize default product class;
- Initialize default partner;
- Initialize products;
- Initialize flatpages;

load locations
``./manage.py loaddata locations`

## Run Server
- ``python manage.py runserver 0.0.0.0:8000``


## Celery
For running ``Celery``, please run the next commands:
- ``celery -A radonmeters.apps.taskapp worker -l info``
- ``celery -A radonmeters.apps.taskapp beat -l info``


Congratulations, now you can be access to site, dashboard and admin panel:


## Admin's links:
- http://127.0.0.1:8000/dashboard/
- http://127.0.0.1:8000/admin/


## Additional steps
- After server has been up you need to change the Site object (via admin panel).



## How to build frontend (on development)
1. Open terminal in the project root dir. After that you should install all ``yarn`` and ``bower`` packages. All tasks and other helpers are in folder ``gulp``.
2. Type ``yarn install``. **On your computer already should be installed ``nodejs``.
3. Type ``bower install``.
3.1 **Type once ``echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p``. It's needed for the normal working of watchers.**
4. Type ``yarn run develop``. Source files haven't been compressed and concatenated.
5. You can change source files and your build automatically will be changed. Watchers will watch for them. Also, your page will have been reloaded automatically.
  * Type ``yarn run watch`` for watching your files.
  * Type ``yarn run serve`` for watching files and running and browser sync.



## Gulp and project build
- ``/gulpfile.js`` - main file for Gulp with general tasks.
- ``/gulp/paths.js`` - all paths for ``src`` and ``dist`` files.
- ``/gulp/helpers.js`` - common helper methods. Used in tasks.
- ``/gulp/handlers.js`` - handler methods (on error, on change, on delete, on logging). Used in tasks.
- ``/gulp/tasks/`` - tasks which separated by logic.


# API

## URLs for website.

### Profile
- /api/v1/profile/orders/                          # GET,
- /api/v1/profile/dosimeters/<dosimeter_id>/       # GET, OPTIONS, PUT, PATCH

## URLs for Android app. 

### Order
- /api/v1/order/orders/?status=created
- /api/v1/order/products/?id=created
- /api/v1/order/add_bar_code/  {id=<line_id>, device_barcode={key: value}}
- /api/v1/order/done/  {id=<order_id>}

Create order with IsPartner permission
- api/v1/data-import/orders/

# Use ansible for update servers :

* ``cd ansible``
* ``ansible-playbook universal.yml --extra-vars="target=develop"`` (for develop)
* ``ansible-playbook universal.yml --extra-vars="target=staging"`` (for staging)
* ``ansible-playbook universal.yml --extra-vars="target=beta"`` (for  beta https://beta.radonmeters.com)
* ``ansible-playbook universal.yml --extra-vars="target=gmscientific"`` (for gmscientific https://gmscientific.radonmeters.com)
* ``ansible-playbook universal.yml --extra-vars="target=production"`` (for production https://radonmeters.com)
* ``ansible-playbook universal.yml --extra-vars="target=radosure-develop"`` (for radosure-develop https://radosure.dev.steel.kiwi)


# First initialization service keys
* Add appropriate variables to env:
    - DEFAULT_SERVICES_GOOGLE_KEY 
    - DEFAULT_SERVICES_RETUR_LINK
    - DEFAULT_SERVICES_TRUSTPILOT_TEMPLATE_ID
    - DEFAULT_SERVICES_TRUSTPILOT_BUSINESSUNIT
    - DEFAULT_SERVICES_TRUSTPILOT_LINK
* ./manage.py init_service_keys 

# Server separation
On server radosure you need to add env variable
`DJANGO_MAIN_PERMISSION=radosure` 
for mark radosure permission

# Translations
### First init
1. Create locale folder
`mkdir radonmeters/locale/`
2. Copy en default po file for prevent Plural-Forms exception
`cp -r radonmeters/default_locale/en radonmeters/locale`
3. Create other translations
`./manage.py makemessages -l en -l da -l nn -l sv`

##### Compiles .po files created by makemessages to .mo files for use with the built-in gettext support
`./manage.py makemessages -l en -l da -l nn -l sv`
`./manage.py compilemessages -l en -l da -l nn -l sv`

# Export and import database
## Export database dump
`pg_dump --no-owner prod-radonmeters | gzip > /home/admin/backup/db/prod-radonmeters-$(date +%Y-%m-%d-%H%M%S).sql.gz`

## Import database
`createdb prod-radonmeters`
`gunzip -c filename.sql.gz | psql prod-radonmeters`