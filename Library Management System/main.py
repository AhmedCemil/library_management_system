import customtkinter as ctk
import config.locale as locale
from PIL import Image
from tkinter import messagebox
from tabulate import tabulate
from config.settings import *

# Ahmed Cemil Bilgin tarafından Global AI Hub: Akbank Python Bootcamp için hazırlanmıştır.
# Teslim tarihi: 19.02.2024

class Book:
    def __init__(self, title, author, first_release_year, number_of_pages):
        self.title = title
        self.author = author
        self.first_release_year = first_release_year
        self.number_of_pages = number_of_pages

    def __str__(self):
        return f"{self.title}: {self.author}, {self.first_release_year}, {self.number_of_pages} pages"


class Library:
    def __init__(self, filename, parent):
        self.filename = filename
        self.parent = parent
        self.books = []
        self.file = None
        try:
            self.file = open(self.filename, "a+")
        except FileNotFoundError:
            messagebox.showerror(f"""{locale.get("File Not Found Error")}""", f"""{locale.get("Error")}: {self.filename} {locale.get("file not found")}.\n{locale.get("Program will be closed")}.""")
            self.exit_program_on_error()
        except PermissionError:
            messagebox.showerror(f"""{locale.get("Permission Error")}""", f"""{locale.get("Error")}: {locale.get("Permission denied")}: '{self.filename}'.\n{locale.get("Program will be closed")}.""")
            self.exit_program_on_error()

        self._read_books()

    def __del__(self):
        self.write_books()
        self.file.close()

    def exit_program_on_error(self):
        # CustomTkinter root.quit()
        self.parent.on_close()

    def _read_books(self):
        books = []
        if self.file is not None:
            self.file.seek(0)
            for line in self.file:
                if line == "\n":
                    pass
                title, author, first_release_year, number_of_pages = (
                    line.strip().split(",")
                )
                books.append(
                    Book(
                        title, author, first_release_year, number_of_pages
                    )
                )
        self.books = books

    def write_books(self):
        self.file.seek(0)
        self.file.truncate()
        for book in self.books:
            self.file.write(
                f"{book.title.replace("\n","")},{book.author.replace("\n","")},{book.first_release_year.replace("\n","")},{book.number_of_pages.replace("\n","")}"
            )
            if self.books.index(book) != len(self.books) - 1:
                self.file.write("\n")

    # custom prettier table
    def make_pretty_table(self, headers, data):
        headers_lengths = [0] * len(headers)
        # calculating how many spaces should be add after every item
        for line in [headers] + data:
                for i in range(len(headers)):
                    headers_lengths[i] = len(line[i]) if headers_lengths[i] <= len(line[i]) else headers_lengths[i]
        # add spaces to every item in headers if necessary
        for i in range(len(headers)):
            headers[i] += " " * (headers_lengths[i] - len(headers[i]))
        # add spaces to every book item in books if necessary
        for line in data:
                for i in range(len(headers)):
                    line[i] += " " * (headers_lengths[i] - len(line[i]))

        return_str = ""
        for line in [headers] + data:
                for i in range(len(headers)):
                    return_str += line[i] + " | "
                return_str += "\n"
        return return_str

    def list_books(self):
        if not self.books:
            return_str = locale.get("No books found in the library.")
        else:
            return_str = f"""*** {locale.get("Library Books' List")} ***\n"""
            headers = [locale.get("Line"), locale.get("Title"), locale.get("Author"), locale.get("First Release Year"), locale.get("Number of Pages")]
            data = []
            for i, book in enumerate(self.books):
                data.append([str(i+1), book.title, book.author, book.first_release_year, book.number_of_pages])
            return_str = tabulate(data, headers=headers)
        return return_str

    def add_book(self, book):
        self.books.append(book)
        self.write_books()
        self._read_books()
        return f"""{locale.get("Book")} '{book.title}' {locale.get("added successfully!")}"""

    def remove_book(self, title):
        # this code for searching title inside books titles. This way user can write any part of the title of the book.
        # count = 1
        # for book in self.books:
        #     if title in book.title:
        #         count += 1
        # if count > 1:
        #     return f"Found {title} {count} times. Please write full title of the book."

        for i, book in enumerate(self.books):
            if book.title == title:
                del self.books[i]
                self.write_books()
                self._read_books()
                return True, f"""{locale.get("Book")} '{title}' {locale.get("removed successfully!")}"""
        return False, f"""{locale.get("Book")} '{title}' {locale.get("not found in the library.")}"""


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=CTK_COLOR)
        self.configure(cursor="wait")
        self.bind("<Destroy>", self.on_close)

        # window setup
        self.iconbitmap(LOGO_FOLDER_PATH + r"\lib_light.ico")
        self.title(locale.get("Form Title"))
        # self.geometry("1920x1080+100+100")
        self.geometry("1100x600+200+50")
        self.resizable(width=False, height=False)
        self.after(200, self.after_initialize)

        # layout
        self.rowconfigure(index=0, weight=1, uniform="form_layout")
        self.rowconfigure(index=1, weight=10, uniform="form_layout")
        self.columnconfigure(index=(0, 1, 2), weight=1, uniform="form_layout")

        # objects
        self.lib = Library(filename="books.txt", parent=self)
        self.scenerio = [1, 0]

        # widgets
        self.placement = Placement(self)
        self.menu_panel = MenuPanel(self)
        self.add_book_panel = AddBookPanel(self)
        self.remove_book_panel = RemoveBookPanel(self)
        self.terminal_panel = TerminalPanel(self)

        self.select_page(1, True)

    # functions
    def lang_update(self, *args):
        self.title(locale.get("Form Title"))
        self.menu_panel.lang_update()
        self.add_book_panel.lang_update()
        self.remove_book_panel.lang_update()
        self.terminal_panel.lang_update()

    def after_initialize(self):
        self.configure(cursor="")

    def select_page(self, index, initialize = False):
        self.menu_panel.visibility(index == 1)
        self.add_book_panel.visibility(index == 2)
        self.remove_book_panel.visibility(index == 3)
        self.scenerio = [index, 0]
        self.terminal_panel.clear_textbox()
        if index == 1 and not initialize:
            self.terminal_panel.add_to_terminal("\n" + self.terminal_panel.terminal_menu_string())

    def func_restart(self):
        # clear and reset everything
        self.lib._read_books()
        self.select_page(1)
        self.terminal_panel.initialize()
        self.scenerio = [1, 0]
    
    def on_close(self, event=None):
        # del self.lib
        self.quit()


class Placement(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=FRAME_FG_COLOR, height=100)
        self.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.rowconfigure(index=0, weight=1, uniform="placement_layout")
        self.columnconfigure(
            index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), weight=1, uniform="placement_layout"
        )
        self.parent = parent

        # variables
        self.lang_combobox_string = ctk.StringVar(value=locale.CURRENT_LANGUAGE.upper())
        self.restart_button_string = ctk.StringVar(value="Restart")
        self.app_logo_image = ctk.CTkImage(
            light_image=Image.open(LOGO_FOLDER_PATH + r"\lib_light.png"),
            dark_image=Image.open(LOGO_FOLDER_PATH + r"\lib_dark.png"),
            size=(52, 35),
        )

        # objects
        self.restart_button = ctk.CTkButton(
            master=self,
            command=self.func_restart,
            text=locale.get(self.restart_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.restart_button.grid(
            row=0, column=0, columnspan=2, sticky="nsew", padx=4, pady=4
        )

        self.change_theme_button = ctk.CTkButton(
            master=self,
            command=self.theme_change,
            text="Light" if ctk.get_appearance_mode() == "Dark" else "Dark",
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE),
            text_color=LABEL_TEXT_COLOR,
            fg_color="transparent",
            hover_color=BUTTON_HOVER_COLOR,
            width=len("Light" if ctk.get_appearance_mode() == "Dark" else "Dark") * 10,
            corner_radius=BUTTON_CORNER_RADIUS,
        )
        self.change_theme_button.grid(row=0, column=12, sticky="nsew", padx=4, pady=4)

        self.app_logo_label = ctk.CTkLabel(
            master=self,
            bg_color="transparent",
            text="",
            image=self.app_logo_image,
            wraplength=0,
        )
        self.app_logo_label.grid(row=0, column=13, sticky="nsew", padx=4, pady=4)

        self.lang_combobox = ctk.CTkComboBox(
            master=self,
            values=locale.LANGUAGE_LIST.keys(),
            command=self.lang_change,
            variable=self.lang_combobox_string,
            width=60,
            border_width=0,
            dropdown_fg_color=(WHITE, APP_DARK_PURPLE),
            dropdown_text_color=LABEL_TEXT_COLOR,
            state="readonly",
        )
        self.lang_combobox.grid(row=0, column=14, padx=4, pady=4)

    # functions
    def lang_change(self, *args):
        locale.change(self.lang_combobox.get())
        self.lang_update()

    def lang_update(self, *args):
        self.restart_button.configure(
            text=locale.get(self.restart_button_string.get())
        )
        self.lang_combobox_string.set(value=locale.CURRENT_LANGUAGE.upper())
        self.change_theme_button.configure(
            text=locale.get("Light" if ctk.get_appearance_mode() == "Dark" else "Dark"),
            width=len("Light" if ctk.get_appearance_mode() == "Dark" else "Dark") * 10,
        )
        self.parent.lang_update()

    def theme_change(self, *args):
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("Dark")
            self.parent.iconbitmap(LOGO_FOLDER_PATH + r"\lib_dark.ico")
        else:
            ctk.set_appearance_mode("Light")
            self.parent.iconbitmap(LOGO_FOLDER_PATH + r"\lib_light.ico")
        self.lang_update()

    def func_restart(self):
        self.parent.func_restart()


class MenuPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            master=parent,
            border_width=1,
            fg_color=FRAME_FG_COLOR,
            corner_radius=FRAME_CORNER_RADIUS,
        )
        self.grid(row=1, column=0, sticky="nsew")
        self.parent = parent

        # layout
        self.rowconfigure(
            index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1, uniform="menu_panel_layout"
        )
        self.columnconfigure(index=0, weight=1, uniform="menu_panel_layout")

        # variables
        self.menu_title_label_string = ctk.StringVar(value="Menu")
        self.list_books_button_string = ctk.StringVar(value="List books")
        self.add_book_button_string = ctk.StringVar(value="Add book")
        self.remove_book_button_string = ctk.StringVar(value="Remove book")

        # objects
        self.menu_title_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.menu_title_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.menu_title_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.list_books_button = ctk.CTkButton(
            master=self,
            command=self.func_list_books,
            text=locale.get(self.list_books_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.list_books_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.add_book_button = ctk.CTkButton(
            master=self,
            command=self.func_add_book,
            text=locale.get(self.add_book_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.add_book_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.remove_book_button = ctk.CTkButton(
            master=self,
            command=self.func_remove_book,
            text=locale.get(self.remove_book_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.remove_book_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

    # functions
    def visibility(self, enabled):
        if enabled:
            self.grid(row=1, column=0, sticky="nsew")
        else:
            self.grid_remove()

    def func_list_books(self):
        self.parent.terminal_panel.add_to_terminal("\n" + self.parent.lib.list_books())
        self.parent.scenerio = [1, 0]
        self.parent.terminal_panel.clear_textbox()
        self.parent.terminal_panel.add_to_terminal("\n" + self.parent.terminal_panel.terminal_menu_string())

    def func_add_book(self):
        self.parent.select_page(2)

    def func_remove_book(self):
        self.parent.select_page(3)

    def lang_update(self):
        self.menu_title_label.configure(
            text=locale.get(self.menu_title_label_string.get())
        )
        self.list_books_button.configure(
            text=locale.get(self.list_books_button_string.get())
        )
        self.add_book_button.configure(
            text=locale.get(self.add_book_button_string.get())
        )
        self.remove_book_button.configure(
            text=locale.get(self.remove_book_button_string.get())
        )


class AddBookPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            master=parent,
            border_width=1,
            fg_color=FRAME_FG_COLOR,
            corner_radius=FRAME_CORNER_RADIUS,
        )
        self.grid(row=1, column=0, sticky="nsew")
        self.parent = parent

        # layout
        self.rowconfigure(
            index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1,
            uniform="add_book_panel_layout",
        )
        self.columnconfigure(index=0, weight=1, uniform="add_book_panel_layout")

        # variables
        self.add_book_title_label_string = ctk.StringVar(value="Add Book Page")
        self.book_title_label_string = ctk.StringVar(value="Title")
        self.book_author_label_string = ctk.StringVar(value="Author")
        self.book_first_release_year_label_string = ctk.StringVar(
            value="First release year"
        )
        self.book_number_of_pages_label_string = ctk.StringVar(value="Number of pages")
        self.apply_add_button_string = ctk.StringVar(value="Add")
        self.return_to_menu_button_string = ctk.StringVar(value="Return to menu")

        # objects
        self.add_book_title_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.add_book_title_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.add_book_title_label.grid(
            row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_title_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.book_title_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.book_title_label.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_title_textbox = ctk.CTkTextbox(
            master=self,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=BUTTON_FG_COLOR,
            text_color=LABEL_TEXT_COLOR,
            border_color=LABEL_TEXT_COLOR,
            activate_scrollbars=False,
            font=ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight="bold"),
            border_width=0,
            border_spacing=0,
        )
        self.book_title_textbox.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=4
        )

        self.book_author_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.book_author_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.book_author_label.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_author_textbox = ctk.CTkTextbox(
            master=self,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=BUTTON_FG_COLOR,
            text_color=LABEL_TEXT_COLOR,
            border_color=LABEL_TEXT_COLOR,
            activate_scrollbars=False,
            font=ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight="bold"),
            border_width=0,
            border_spacing=0,
        )
        self.book_author_textbox.grid(
            row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=4
        )

        self.book_first_release_year_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.book_first_release_year_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.book_first_release_year_label.grid(
            row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_first_release_year_textbox = ctk.CTkTextbox(
            master=self,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=BUTTON_FG_COLOR,
            text_color=LABEL_TEXT_COLOR,
            border_color=LABEL_TEXT_COLOR,
            activate_scrollbars=False,
            font=ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight="bold"),
            border_width=0,
            border_spacing=0,
        )
        self.book_first_release_year_textbox.grid(
            row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=4
        )

        self.book_number_of_pages_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.book_number_of_pages_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.book_number_of_pages_label.grid(
            row=7, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_number_of_pages_textbox = ctk.CTkTextbox(
            master=self,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=BUTTON_FG_COLOR,
            text_color=LABEL_TEXT_COLOR,
            border_color=LABEL_TEXT_COLOR,
            activate_scrollbars=False,
            font=ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight="bold"),
            border_width=0,
            border_spacing=0,
        )
        self.book_number_of_pages_textbox.grid(
            row=8, column=0, columnspan=2, sticky="nsew", padx=10, pady=4
        )

        self.apply_add_button = ctk.CTkButton(
            master=self,
            command=self.func_apply_add,
            text=locale.get(self.apply_add_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.apply_add_button.grid(row=9, column=0, sticky="nsew", padx=10, pady=10)

        self.return_to_menu_button = ctk.CTkButton(
            master=self,
            command=self.func_return_to_menu,
            text=locale.get(self.return_to_menu_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.return_to_menu_button.grid(
            row=9, column=1, sticky="nsew", padx=10, pady=10
        )

    # functions
    def visibility(self, enabled):
        if enabled:
            self.grid(row=1, column=0, sticky="nsew")
            self.initialize_page()
        else:
            self.grid_remove()

    def initialize_page(self):
        self.book_title_textbox.delete("0.0", "end")  # delete all text
        self.book_author_textbox.delete("0.0", "end")  # delete all text
        self.book_first_release_year_textbox.delete("0.0", "end")  # delete all text
        self.book_number_of_pages_textbox.delete("0.0", "end")  # delete all text

    def func_apply_add(self):
        author = self.book_author_textbox.get("0.0", "end").replace("\n", "")
        title = self.book_title_textbox.get("0.0", "end").replace("\n", "")
        book_first_release_year = self.book_first_release_year_textbox.get("0.0", "end").replace("\n", "")
        book_number_of_pages = self.book_number_of_pages_textbox.get("0.0", "end").replace("\n", "")

        if "" in [author, title, book_first_release_year, book_number_of_pages]:
            return

        try:
            int(book_first_release_year)
        except ValueError:
            self.parent.terminal_panel.add_to_terminal(
                "\nPlease enter only integer value in first release year input."
            )
            return

        try:
            int(book_number_of_pages)
        except ValueError:
            self.parent.terminal_panel.add_to_terminal(
                f"""\n{locale.get("Please enter only integer value in number of pages input.")}"""
            )
            return

        for book in self.parent.lib.books:
            if (
                title
                in book.title
            ):
                self.parent.terminal_panel.add_to_terminal(
                    f"""\n{locale.get("The book is already in the library, please remove it first or add different book.")}"""
                )
                return

        book = Book(title, author, book_first_release_year, book_number_of_pages)

        self.parent.terminal_panel.add_to_terminal(self.parent.lib.add_book(book))
        self.func_return_to_menu()

    def func_return_to_menu(self):
        self.parent.select_page(1)

    def lang_update(self):
        self.add_book_title_label.configure(
            text=locale.get(self.add_book_title_label_string.get())
        )
        self.book_title_label.configure(
            text=locale.get(self.book_title_label_string.get())
        )
        self.book_author_label.configure(
            text=locale.get(self.book_author_label_string.get())
        )
        self.book_first_release_year_label.configure(
            text=locale.get(self.book_first_release_year_label_string.get())
        )
        self.book_number_of_pages_label.configure(
            text=locale.get(self.book_number_of_pages_label_string.get())
        )
        self.apply_add_button.configure(
            text=locale.get(self.apply_add_button_string.get())
        )
        self.return_to_menu_button.configure(
            text=locale.get(self.return_to_menu_button_string.get())
        )


class RemoveBookPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            master=parent,
            border_width=1,
            fg_color=FRAME_FG_COLOR,
            corner_radius=FRAME_CORNER_RADIUS,
        )
        self.grid(row=1, column=0, sticky="nsew")
        self.parent = parent

        # layout
        self.rowconfigure(
            index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1,
            uniform="remove_book_panel_layout",
        )
        self.columnconfigure(index=0, weight=1, uniform="remove_book_panel_layout")

        # variables
        self.remove_book_title_label_string = ctk.StringVar(value="Remove Book Page")
        self.book_title_label_string = ctk.StringVar(value="Title")
        self.apply_remove_button_string = ctk.StringVar(value="Remove")
        self.return_to_menu_button_string = ctk.StringVar(value="Return to menu")

        # objects
        self.remove_book_title_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.remove_book_title_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.remove_book_title_label.grid(
            row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_title_label = ctk.CTkLabel(
            master=self,
            text=locale.get(self.book_title_label_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.book_title_label.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.book_title_textbox = ctk.CTkTextbox(
            master=self,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=BUTTON_FG_COLOR,
            text_color=LABEL_TEXT_COLOR,
            border_color=LABEL_TEXT_COLOR,
            activate_scrollbars=False,
            font=ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight="bold"),
            border_width=0,
            border_spacing=0,
        )
        self.book_title_textbox.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=4
        )

        self.apply_remove_button = ctk.CTkButton(
            master=self,
            command=self.func_apply_remove,
            text=locale.get(self.apply_remove_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.apply_remove_button.grid(row=9, column=0, sticky="nsew", padx=10, pady=10)

        self.return_to_menu_button = ctk.CTkButton(
            master=self,
            command=self.func_return_to_menu,
            text=locale.get(self.return_to_menu_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.return_to_menu_button.grid(
            row=9, column=1, sticky="nsew", padx=10, pady=10
        )

    # functions
    def visibility(self, enabled):
        if enabled:
            self.grid(row=1, column=0, sticky="nsew")
            self.initialize_page()
        else:
            self.grid_remove()

    def initialize_page(self):
        self.book_title_textbox.delete("0.0", "end")  # delete all text

    def func_apply_remove(self):
        isDone, _str = self.parent.lib.remove_book(
            self.book_title_textbox.get("0.0", "end").replace("\n", "")
        )
        self.parent.terminal_panel.add_to_terminal(_str)
        if isDone:
            self.func_return_to_menu()

    def func_return_to_menu(self):
        self.parent.select_page(1)

    def lang_update(self):
        self.remove_book_title_label.configure(
            text=locale.get(self.remove_book_title_label_string.get())
        )
        self.book_title_label.configure(
            text=locale.get(self.book_title_label_string.get())
        )
        self.apply_remove_button.configure(
            text=locale.get(self.apply_remove_button_string.get())
        )
        self.return_to_menu_button.configure(
            text=locale.get(self.return_to_menu_button_string.get())
        )


class TerminalPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            master=parent,
            border_width=1,
            fg_color=FRAME_FG_COLOR,
            corner_radius=FRAME_CORNER_RADIUS,
        )
        self.grid(row=1, column=1, columnspan=2, sticky="nsew")
        self.parent = parent

        self.book_title = ""
        self.book_author = ""
        self.book_first_release_year = ""
        self.book_number_of_pages = ""

        # layout
        self.rowconfigure(
            index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1,
            uniform="terminal_panel_layout",
        )
        self.columnconfigure(index=0, weight=1, uniform="terminal_panel_layout")

        # variables
        self.terminal_string = ctk.StringVar(value=self.terminal_menu_string())
        self.send_button_string = ctk.StringVar(value="Send")
        self.clear_button_string = ctk.StringVar(value="Clear")

        # objects
        self.scrollable_frame = ctk.CTkScrollableFrame(
            master=self,
        )
        self.scrollable_frame.grid(
            row=0,
            rowspan=8,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=10,
            pady=(10, 0),
        )
        self.terminal = ctk.CTkLabel(
            master=self.scrollable_frame,
            textvariable=self.terminal_string,
            justify="left",
            font=ctk.CTkFont(family=TERMINAL_FONT, size=TERMINAL_LABEL_FONT_SIZE, weight="bold"),
            text_color=LABEL_TEXT_COLOR,
            corner_radius=0,
            anchor="nw",
            bg_color="transparent",
        )
        self.terminal.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.send_textbox = ctk.CTkTextbox(
            master=self,
            corner_radius=0,
            fg_color=BUTTON_FG_COLOR,
            text_color=LABEL_TEXT_COLOR,
            border_color=LABEL_TEXT_COLOR,
            activate_scrollbars=False,
            font=ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight="bold"),
            border_width=0,
            border_spacing=0,
        )
        self.send_textbox.grid(
            row=8, column=0, columnspan=2, sticky="nsew", padx=10, pady=0
        )

        self.send_button = ctk.CTkButton(
            master=self,
            command=self.func_send,
            text=locale.get(self.send_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.send_button.grid(row=9, column=0, sticky="nsew", padx=10, pady=10)

        self.clear_button = ctk.CTkButton(
            master=self,
            command=self.clear_textbox,
            text=locale.get(self.clear_button_string.get()),
            font=ctk.CTkFont(family=FONT, size=BUTTON_FONT_SIZE, weight="bold"),
            text_color=BUTTON_TEXT_COLOR,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            corner_radius=BUTTON_CORNER_RADIUS,
            anchor="w",
        )
        self.clear_button.grid(row=9, column=1, sticky="nsew", padx=10, pady=10)

    # functions
    def terminal_menu_string(self):
        return f"*** {locale.get("MENU")} ***{" "*100}\n1) {locale.get("List Books")}\n2) {locale.get("Add Book")}\n3) {locale.get("Remove Book")}\n4) {locale.get("Quit")}\n{locale.get("Enter your choice")} (1-4): "

    def initialize(self):
        self.terminal_string.set(self.terminal_menu_string())
        self.clear_textbox()

    def clear_textbox(self):
        self.send_textbox.delete("0.0", "end")  # delete all text

    def func_send(self):
        _str = self.send_textbox.get("0.0", "end").replace("\n", "")
        if _str == "":
            return
        self.terminal_string.set(
            self.terminal_string.get() + _str
        )
        self.clear_textbox()
        if self.parent.scenerio[0] == 1:  # Menu
            if self.parent.scenerio[1] == 0 and _str not in "1234":
                self.add_to_terminal(f"{locale.get("Please enter 1 to 4.")}\n")
                self.add_to_terminal(self.terminal_menu_string())
                return

            elif self.parent.scenerio[1] == 0 and _str == "1":  # List Books
                self.parent.menu_panel.func_list_books()
                return
            
            elif self.parent.scenerio[1] == 0 and _str == "2":  # Add Book
                self.parent.menu_panel.func_add_book()
                self.add_to_terminal(f"""{locale.get("Enter book's title")}: """)
                return
            
            elif self.parent.scenerio[1] == 0 and _str == "3":  # Remove Book
                self.parent.menu_panel.func_remove_book()
                self.add_to_terminal(f"""{locale.get("Enter book's title")}: """)
                return
            
            elif self.parent.scenerio[1] == 0 and _str == "4": #  Quit
                self.parent.on_close()
        
        elif self.parent.scenerio[0] == 2:  # Add Book Page
            if self.parent.scenerio[1] == 0:  # Title
                self.book_title = _str
                self.add_to_terminal(f"""{locale.get("Enter book's author")}: """)
                self.parent.scenerio[1] = 1

            elif self.parent.scenerio[1] == 1:  # Author
                self.book_author = _str
                self.add_to_terminal(f"""{locale.get("Enter book's first released year")}: """)
                self.parent.scenerio[1] = 2

            elif self.parent.scenerio[1] == 2:  # First Release Year
                self.book_first_release_year = _str
                try:
                    int(_str)
                except ValueError:
                    self.add_to_terminal(locale.get("Please enter only integer value in first release year input."))
                    self.add_to_terminal(f"""\n{locale.get("Enter book's first released year")}: """)
                    return
                self.add_to_terminal(f"""{locale.get("Enter book's number of pages")}: """)
                self.parent.scenerio[1] = 3

            elif self.parent.scenerio[1] == 3:  # Number of Pages
                self.book_number_of_pages = _str
                try:
                    int(_str)
                except ValueError:
                    self.parent.terminal_panel.add_to_terminal(locale.get("Please enter only integer value in number of pages input."))
                    self.add_to_terminal(f"""\n{locale.get("Enter book's number of pages")}: """)
                    return
                
                for book in self.parent.lib.books:
                    if (self.book_title in book.title):
                        self.add_to_terminal(
                            f"""{locale.get("The book is already in the library, please remove it first or add different book.")}"""
                        )
                        self.parent.select_page(1)
                        return

                book = Book(self.book_title, self.book_author, self.book_first_release_year, self.book_number_of_pages)
                self.add_to_terminal(self.parent.lib.add_book(book))
                self.parent.select_page(1)
        
        elif self.parent.scenerio[0] == 3:  # Remove Book page
            isDone, _str = self.parent.lib.remove_book(_str)
            self.parent.terminal_panel.add_to_terminal(_str)
            if isDone:
                self.parent.select_page(1)
            else:
                self.add_to_terminal(f"""{locale.get("Enter book's title")}: """)


                

    def add_to_terminal(self, _str):
        self.terminal_string.set(f"{self.terminal_string.get()}\n{_str}")

    def lang_update(self):
        self.send_button.configure(
            text=locale.get(self.send_button_string.get())
        )
        self.clear_button.configure(
            text=locale.get(self.clear_button_string.get())
        )


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()
