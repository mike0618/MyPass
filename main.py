import curses
from threading import Thread
from time import sleep
import engine
import pyperclip


class TUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.maxy, self.maxx = self.stdscr.getmaxyx()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.black_white = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.green_black = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        self.cyan_black = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        self.mag_black = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        self.mag_mag = curses.color_pair(5)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_GREEN)
        self.gr_gr = curses.color_pair(6)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_CYAN)
        self.cy_cy = curses.color_pair(7)
        self.stdscr.clear()
        self.stdscr.border()
        title = " MyPass "
        self.k_lbl = " Key word: "
        self.w_lbl = " Web site: "
        self.l_lbl = "    Login: "
        self.p_lbl = " Password: "
        self.llen = len(self.k_lbl)
        self.maxx_i = self.maxx - self.llen - 3
        self.stdscr.addstr(0, (self.maxx - len(title)) // 2, title, curses.A_BOLD)
        self.stdscr.addstr(2, 1, self.k_lbl)
        self.stdscr.addstr(4, 1, self.w_lbl)
        self.stdscr.addstr(6, 1, self.l_lbl)
        self.stdscr.addstr(8, 1, self.p_lbl)
        self.stdscr.refresh()
        self.kw = self.input_engine(2, hidden=True)
        self.site = ""
        self.login = ""
        self.pw = ""
        self.pwin = curses.newwin(1, self.maxx_i, 8, self.llen + 1)
        self.cd_win = curses.newwin(1, self.maxx - 2, 10, 1)
        self.cd = False
        self.s_lst = []
        self.l_lst = []
        self.main()

    def main(self):
        while True:
            key = self.stdscr.getkey().lower()
            if self.cd:
                self.cd = False
                sleep(0.11)
            match key:
                case "q":
                    break
                case "k":
                    self.kw = self.input_engine(2, hidden=True)
                case "w":
                    self.input_site()
                case "l":
                    self.input_login()
                case "p":
                    self.get_pass(True)
                case "c":
                    self.get_pass()
                case "g":
                    p = engine.passgen()
                    self.pw = self.input_engine(8, inp=p)
                case "s":
                    self.save_pw()
                case "d":
                    self.delete()
                case "h":
                    self.help()
                # case "t":
                #     self.test()
                case _:
                    self.cd = False
        engine.close()

    def countdown(self):
        self.cd = True
        length = self.maxx - 3
        clr = self.cy_cy
        for x in range(1, 101):
            if not self.cd:
                break
            if x > 66:
                clr = self.mag_mag
            elif x > 33:
                clr = self.gr_gr
            s = "#" * round(length * (x / 100))
            self.cd_win.addstr(0, 0, s, clr)
            self.cd_win.refresh()
            sleep(0.1)
        self.pwin.clear()
        self.pwin.refresh()
        self.cd_win.clear()
        self.cd_win.refresh()
        self.pw = ""
        try:
            pyperclip.copy("")
        except pyperclip.PyperclipException:
            ...

    def message(self, title, msg, q=""):
        ans = False
        margy = int(self.maxy * 0.1)
        margx = int(self.maxx * 0.1)
        win = curses.newwin(self.maxy - 2 * margy, self.maxx - 2 * margx, margy, margx)
        win.attron(self.cyan_black | curses.A_BOLD)
        win.border()
        win.addstr(0, 2, title)
        n = 0
        for n, s in enumerate(msg.splitlines()):
            win.addstr(n + 2, 2, s.strip())
        win.attroff(self.cyan_black | curses.A_BOLD)
        win.attron(self.mag_black | curses.A_BOLD)
        if q:
            win.addstr(win.getmaxyx()[0] - 2, 2, f"Press 'y' to {q}")
        else:
            win.addstr(win.getmaxyx()[0] - 2, 2, "Press any key to close")
        win.attroff(self.mag_black | curses.A_BOLD)
        win.refresh()
        key = self.stdscr.getkey()
        if q and key.isprintable() and key.lower() == "y":
            ans = True
            win.attron(self.cyan_black | curses.A_BOLD)
            win.addstr(": DONE!")
            win.attroff(self.cyan_black | curses.A_BOLD)
            win.refresh()
            sleep(1)
        win.clear()
        win.refresh()
        self.stdscr.addstr(8, 1 + self.llen, " " * (self.maxx_i - 1))
        self.stdscr.touchwin()
        self.stdscr.refresh()
        return ans

    def help(self):
        title = " Help "
        msg = """k  - enter a key word
        w  - enter or select a website
        l  - enter or select a login
        p  - show the password
        c  - copy the password
        g  - generate and edit a new password
        s  - save a new password to the DB
        d  - delete login or website
        ↓↑ - navigate in the select window
        q  - quit the program"""
        self.message(title, msg)

    def input_engine(self, row, inp="", hidden=False):
        win = curses.newwin(3, self.maxx_i + 2, row - 1, self.llen)
        win.clear()
        win.attron(self.mag_black | curses.A_BOLD)
        win.border()
        win.attroff(self.mag_black | curses.A_BOLD)
        win.refresh()
        win_txt = curses.newwin(1, self.maxx_i, row, self.llen + 1)
        win_txt.clear()
        win_txt.attron(self.mag_black)
        if inp:
            win_txt.addstr(inp, self.mag_black | curses.A_BOLD)
            win_txt.refresh()
        while True:
            key = self.stdscr.getkey()
            if key.isprintable() and len(key) == 1 and len(inp) < self.maxx_i - 1:
                inp += key
                if hidden:
                    key = "*"
                win_txt.addstr(key, self.mag_black | curses.A_BOLD)
                win_txt.refresh()
            elif key == "KEY_BACKSPACE" or (len(key) == 1 and ord(key) == 127):
                inp = inp[:-1]
                s = inp
                if hidden:
                    s = "*" * len(inp)
                win_txt.addstr(0, 0, " " * (self.maxx_i - 1))
                win_txt.addstr(0, 0, s, self.mag_black | curses.A_BOLD)
                win_txt.refresh()
            else:
                break
        win_txt.attroff(self.mag_black)
        del win_txt
        del win
        s = inp + " " * (self.maxx_i - len(inp))
        if hidden:
            s = "*" * 18 + " " * (self.maxx_i - 18)
        self.stdscr.addstr(row, 1 + self.llen, s, curses.A_BOLD | self.mag_black)
        self.stdscr.touchwin()
        self.stdscr.refresh()
        return inp

    def input_site(self):
        self.s_lst = [s[0] for s in engine.sitelist()]
        self.site = self.select_entry(self.s_lst, 4)

    def input_login(self):
        self.l_lst = [lg[0] for lg in engine.loginlist(self.site)]
        self.login = self.select_entry(self.l_lst, 6)

    def insert_entries(self, win, lst):
        lst_y, _ = win.getmaxyx()
        for i in range(lst_y):
            win.addstr(i, 0, " " * (self.maxx_i - 1))
        half = lst_y // 2
        starti = 0
        n = 0
        ind = self.s_ind
        if self.s_ind < 1:
            n = -1
            ind = 0
        if self.s_ind > half:
            starti = self.s_ind - half
        lst1 = lst[starti:ind]
        lst2 = lst[ind:]
        for n, s in enumerate(lst1):
            win.addstr(n, 0, s)
        for m, s in enumerate(lst2):
            y = n + m + 1
            if y + 1 > lst_y:
                break
            if not m and self.s_ind > -1:
                win.addstr(y, 0, s, self.green_black | curses.A_BOLD)
            else:
                win.addstr(y, 0, s)
        win.refresh()

    def lst_engine(self, lst0, win_lst, win_txt, row):
        lst = list(lst0)
        self.s_ind = -1
        self.insert_entries(win_lst, lst)
        w_str = ""
        while True:
            key = self.stdscr.getkey()
            if key.isprintable() and len(key) == 1 and len(w_str) < self.maxx_i - 1:
                w_str += key
                win_txt.addstr(key, self.green_black | curses.A_BOLD)
                win_txt.refresh()
                lst = [s for s in lst0 if s.startswith(w_str)]
                self.s_ind = -1
                self.insert_entries(win_lst, lst)
            elif key == "KEY_BACKSPACE" or (len(key) == 1 and ord(key) == 127):
                w_str = w_str[:-1]
                win_txt.addstr(0, 0, " " * (self.maxx_i - 1))
                win_txt.addstr(0, 0, w_str, self.green_black | curses.A_BOLD)
                win_txt.refresh()
                lst = [s for s in lst0 if s.startswith(w_str)]
                self.s_ind = -1
                self.insert_entries(win_lst, lst)
            elif key == "KEY_DOWN":
                if self.s_ind < len(lst) - 1:
                    self.s_ind += 1
                    self.insert_entries(win_lst, lst)
            elif key == "KEY_UP":
                if self.s_ind > 0:
                    self.s_ind -= 1
                    self.insert_entries(win_lst, lst)
            else:
                if self.s_ind > -1:
                    entry = lst[self.s_ind]
                else:
                    entry = w_str
                break
        del win_lst
        del win_txt
        self.stdscr.addstr(
            row,
            1 + self.llen,
            entry + " " * (self.maxx_i - len(entry)),
            self.green_black | curses.A_BOLD,
        )
        self.stdscr.touchwin()
        self.stdscr.refresh()
        return entry

    def select_entry(self, lst, row):
        self.stdscr.addstr(8, 1 + self.llen, " " * (self.maxx_i - 1))
        self.stdscr.refresh()
        win = curses.newwin(3, self.maxx_i + 2, row - 1, self.llen)
        win.attron(self.green_black | curses.A_BOLD)
        win.border()
        win.refresh()
        win.attroff(self.green_black | curses.A_BOLD)
        win_txt = curses.newwin(1, self.maxx_i, row, self.llen + 1)
        win_lst = curses.newwin(
            self.maxy - row - 5, self.maxx_i, row + 3, self.llen + 1
        )
        win_lst_b = curses.newwin(
            self.maxy - row - 3, self.maxx_i + 2, row + 2, self.llen
        )
        win_lst_b.attron(self.green_black | curses.A_BOLD)
        win_lst_b.border()
        win_lst_b.addstr(0, 2, " Select entry ")
        win_lst_b.refresh()
        win_lst_b.attroff(self.green_black | curses.A_BOLD)
        del win_lst_b
        del win
        return self.lst_engine(lst, win_lst, win_txt, row)

    def get_pass(self, show=False):
        self.pwin.clear()
        pw = pw1 = engine.get_pass(self.kw, self.site, self.login)
        if pw1 == 2:
            pw1 = "This website does not exist"
        elif pw1 == 3:
            pw1 = "This login does not exist"
        elif not show:
            try:
                pyperclip.copy(pw)
                pw1 = "The password has been copied"
            except pyperclip.PyperclipException as err:
                # pw1 = " ".join([line.strip() for line in str(err).splitlines()])[
                #     : self.maxx_i - 2
                # ].strip()
                pw1 = "Pyperclip does not work without display"
        self.pwin.addstr(pw1, self.mag_black | curses.A_BOLD)
        self.pwin.refresh()
        if pw not in (2, 3):
            Thread(target=self.countdown).start()

    def save_pw(self):
        self.stdscr.addstr(8, 1 + self.llen, " " * (self.maxx_i - 1))
        self.stdscr.refresh()
        if not (self.site and self.login and self.pw):
            return False
        if self.site in self.s_lst and self.login in self.l_lst:
            if not self.message(
                " Replace ",
                f"You are about to replace password for\nWebsite: {self.site}\n  Login: {self.login}",
                "replace Password",
            ):
                self.pw = ""
                return False
        else:
            self.l_lst.append(self.login)
        if self.site not in self.s_lst:
            self.s_lst.append(self.site)
        engine.save(self.kw, self.pw, self.site, self.login)
        self.message(
            " Saved ",
            f"Password for\nWebsite: {self.site}\n  Login: {self.login}\nhas been saved",
        )
        self.pw = ""

    def delete(self):
        if self.site and self.login:
            msg = f"You are about to delete Login:\n{self.login}\nfor Website:\n{self.site}"
            self.do_delete(msg, 6, engine.del_creds)
        elif self.site:
            msg = f"You are about to delete Website:\n{self.site}"
            self.do_delete(msg, 4, engine.del_site)
        self.stdscr.touchwin()
        self.stdscr.refresh()

    def do_delete(self, msg, row, del_func):
        creds = (self.site,)
        inst = "Website"
        if "Login" in msg.split(":")[0]:
            creds = (self.site, self.login)
            inst = "Login"
        if self.message(" Delete ", msg, f"delete {inst}"):
            del_func(*creds)
            self.login = ""
            if inst == "Website":
                self.site = ""
            ds = "DELETED" + " " * (self.maxx_i - 7)
            self.stdscr.addstr(row, 1 + self.llen, ds, curses.A_BOLD | self.mag_black)

    def test(self):
        while True:
            key = self.stdscr.getkey()
            if key.isprintable():
                self.stdscr.addstr(12, 12, " " * self.maxx_i)
                if key == "q":
                    break
                self.stdscr.addstr(12, 12, key)
            else:
                self.stdscr.addstr(12, 12, str(ord(key)))


if __name__ == "__main__":
    curses.wrapper(TUI)
