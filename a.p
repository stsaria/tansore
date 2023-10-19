0 6 * * * root systemctl stop tansore
0 6 * * * root rm /home/yes/tansore/tansore.py && wget -P /home/yes/tansore https://github.com/stsaria/tansore/raw/main/tansore.py
0 6 * * * root rm /home/yes/tansore/main.py && wget -P /home/yes/tansore https://github.com/stsaria/tansore/raw/main/main.py
0 6 * * * root rm /home/yes/tansore/etc.py && wget -P /home/yes/tansore https://github.com/stsaria/tansore/raw/main/etc.py
0 6 * * * root rm /home/yes/tansore/gui.py && wget -P /home/yes/tansore https://github.com/stsaria/tansore/raw/main/gui.py
0 6 * * * root rm /home/yes/tansore/mail.py && wget -P /home/yes/tansore https://github.com/stsaria/tansore/raw/main/mail.py
0 6 * * * root rm /home/yes/tansore/install.py && wget -P /home/yes/tansore https://github.com/stsaria/tansore/raw/main/install.py
0 6 * * * root chown -R yes  && systemctl start tansore