# Launch MVP

## Setup

```
python3.12 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements_dev.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```


## Notes

- orgs are created in admin
- permissions not implemented
- no registration, users added in admin
- need to create and manage groups & permissions using org model hooks
- password resets in admin
- avatars to come


## questions

- user selection - in org?
- project membership vs org membership
- user has multiple orgs


## todo

- user avatar management (looks good for demos)
