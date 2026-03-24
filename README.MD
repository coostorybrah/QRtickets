Chạy từng câu lệnh một trên gitbash (đợi lệnh trước chạy xong mới tới lệnh sau)
git clone <URL>
cd QRtickets
pip install virtualenv
python -m virtualenv env
source env/Scripts/activate
pip install -r requirement.txt
python manage.py migrate
python manage.py runserver