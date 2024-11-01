from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits
from random import randint, choice, shuffle
from my_crypt import decrypt, encrypt
import sqlite3

con = sqlite3.connect("./MyPass.db")
cur = con.cursor()
site_q = "SELECT * FROM sites WHERE Name=?"
pw_q = "SELECT Password FROM creds WHERE site_id=? and Login=?"
q1 = "CREATE TABLE IF NOT EXISTS sites (id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT UNIQUE NOT NULL)"
q2 = "CREATE TABLE IF NOT EXISTS creds (id INTEGER NOT NULL, site_id INTEGER, Login NOT NULL, Password NOT NULL, Date NOT NULL, PRIMARY KEY (id), FOREIGN KEY(site_id) REFERENCES sites (id))"
cur.execute(q1)
cur.execute(q2)
con.commit()


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def passgen():
    l_list = [choice(ascii_lowercase) for _ in range(randint(3, 5))]
    up_list = [choice(ascii_uppercase) for _ in range(randint(3, 5))]
    n_list = [choice(digits) for _ in range(randint(2, 4))]
    s_list = [choice("!?#$%&*()+-,.") for _ in range(randint(2, 4))]
    password_list = l_list + up_list + n_list + s_list
    shuffle(password_list)
    password = "".join(password_list)
    return password


# ---------------------------- SHOW PASSWORD ------------------------------- #
def get_pass(kw, site, login):
    db_site = cur.execute(site_q, (site,)).fetchone()
    if not db_site:
        return 2
    pw = cur.execute(pw_q, (db_site[0], login)).fetchone()
    if not pw:
        return 3
    pwd = decrypt(pw[0], kw)
    if pwd == 404:
        pwd = passgen()
    return pwd


# ---------------------------- SAVE PASSWORD -------------------------------- #
def save(kw, pw, site, login):
    passw = encrypt(pw, kw)
    db_site = cur.execute(site_q, (site,)).fetchone()
    if not db_site:
        q = "INSERT INTO sites (Name) VALUES(?)"
        cur.execute(q, (site,))
        con.commit()
        db_site = cur.execute(site_q, (site,)).fetchone()
    pw = cur.execute(pw_q, (db_site[0], login)).fetchone()
    now = datetime.now().strftime("%b %d %Y %H:%M:%S")
    if not pw:
        q = "INSERT INTO creds (site_id, Login, Password, Date) VALUES(?, ?, ?, ?)"
        cur.execute(q, (db_site[0], login, passw, now))
        con.commit()
        pw = cur.execute(pw_q, (db_site[0], login)).fetchone()
    else:
        q = "UPDATE creds SET Password=?, Date=? WHERE site_id=? AND Login=?"
        cur.execute(q, (passw, now, db_site[0], login))
        con.commit()


# ---------------------------- DELETE SITE -------------------------------- #
def del_site(site):
    db_site = cur.execute(site_q, (site,)).fetchone()
    if not db_site:
        return False
    q1 = "DELETE FROM sites WHERE Name=?"
    cur.execute(q1, (site,))
    q2 = "DELETE FROM creds WHERE site_id=?"
    cur.execute(q2, (db_site[0],))
    con.commit()


# ---------------------------- DELETE CREDS -------------------------------- #
def del_creds(site, login):
    db_site = cur.execute(site_q, (site,)).fetchone()
    if not db_site:
        return False
    q = "DELETE FROM creds WHERE site_id=? AND Login=?"
    cur.execute(q, (db_site[0], login))
    con.commit()


# ------------------------ INFO FUNCTIONS ---------------------------- #
def sitelist():
    return cur.execute("SELECT Name FROM sites ORDER BY Name").fetchall()


def loginlist(site):
    db_site = cur.execute(site_q, (site,)).fetchone()
    if not db_site:
        return []
    q = "SELECT Login FROM creds WHERE site_id=? ORDER BY Login"
    return cur.execute(q, (db_site[0],)).fetchall()


def login_info(site, login):
    db_site = cur.execute(site_q, (site,)).fetchone()
    q = pw_q.replace("Password", "Login")
    date = cur.execute(q, (db_site[0], login)).fetchone()
    if date:
        return date[0]
    return False


def close():
    cur.close()
    con.close()


if __name__ == "__main__":
    close()
