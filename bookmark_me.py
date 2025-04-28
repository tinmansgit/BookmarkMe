# BookmarkMe v1.0 20250414.07:30
import json
import re
import tkinter as tk
from tkinter import ttk, messagebox
import bookmarkme_logger
from bookmarkme_logger import log_error, log_debug

bookmarks_file = '~/bin/Python/BookmarkMe/mybms.json'

class Bookmark:
    def __init__(self, id=0, title='', category='', url=''):
        self.id = int(id)
        self.title = title
        self.category = category
        self.url = url

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'category': self.category, 'url': self.url}

    @classmethod
    def from_dict(cls, data):
        return cls(id=data.get('id', 0), title=data.get('title', ''), category=data.get('category', ''), url=data.get('url', ''))


class BookmarkManager:
    def __init__(self, file_path=bookmarks_file):
        self.file_path = file_path
        log_debug(f"Initializing BookmarkManager with file: {self.file_path}")
        self.bookmarks = self.load_bookmarks()

    def load_bookmarks(self):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                log_debug(f"Bookmarks loaded successfully from {self.file_path}")
                return [Bookmark.from_dict(item) for item in data]
        except FileNotFoundError as e:
            log_error(f"File not found: {self.file_path} - {e}")
            return []
        except json.JSONDecodeError as e:
            log_error(f"JSON decode error in file: {self.file_path} - {e}")
            return []

    def save_bookmarks(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump([bm.to_dict() for bm in self.bookmarks], f, indent=4)
            log_debug(f"Bookmarks saved successfully to {self.file_path}")
        except Exception as e:
            log_error(f"Failed to save bookmarks to {self.file_path}: {e}")

    def get_next_id(self):
        if not self.bookmarks:
            log_debug("No bookmarks found, starting IDs at 1")
            return 1
        else:
            next_id = max(bm.id for bm in self.bookmarks) + 1
            log_debug(f"Next bookmark ID generated: {next_id}")
            return next_id

    def add_bookmark(self, title, category, url):
        log_debug(f"Adding bookmark: title='{title}', category='{category}', url='{url}'")
        next_id = self.get_next_id()
        bookmark = Bookmark(next_id, title, category, url)
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        log_debug(f"Bookmark added with ID: {next_id}")

    def search_bookmarks(self, query):
        log_debug(f"Searching bookmarks with query: {query}")
        results = []
        for bookmark in self.bookmarks:
            if (re.search(query, bookmark.title, re.IGNORECASE) or 
                re.search(query, bookmark.category, re.IGNORECASE) or 
                re.search(query, bookmark.url, re.IGNORECASE)):
                results.append(bookmark)
        log_debug(f"Found {len(results)} results for query '{query}'")
        return results

    def delete_bookmark(self, bookmark_id):
        log_debug(f"Deleting bookmark with ID: {bookmark_id}")
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.id == bookmark_id:
                del self.bookmarks[i]
                self.save_bookmarks()
                log_debug(f"Bookmark with ID {bookmark_id} deleted successfully")
                return True
        log_error(f"Bookmark with ID {bookmark_id} not found for deletion")
        return False

    def edit_bookmark(self, bookmark_id, title, category, url):
        log_debug(f"Editing bookmark with ID: {bookmark_id}")
        for bookmark in self.bookmarks:
            if bookmark.id == bookmark_id:
                bookmark.title = title
                bookmark.category = category
                bookmark.url = url
                self.save_bookmarks()
                log_debug(f"Bookmark with ID {bookmark_id} updated successfully")
                return True
        log_error(f"Bookmark with ID {bookmark_id} not found for editing")
        return False

class BookmarkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BookmarkMe")
        try:
            icon = tk.PhotoImage(file="~/bin/Python/BookmarkMe/bookmark-me_icon.png")
            self.iconphoto(False, icon)
        except Exception as e:
            log_error(f"Failed to load icon: {e}")
        self.geometry("600x400")
        self.configure(bg='black')
        log_debug("Starting BookmarkApp")
        self.manager = BookmarkManager()
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('.', background='black', foreground='white', fieldbackground='black')
        self.style.configure("TButton", background='black', foreground='white')
        self.style.map("TButton", background=[('active', 'gray')])
        self.style.configure("TNotebook", background='black', foreground='white')
        self.style.configure("TNotebook.Tab", foreground="black", background="black")
        self.style.configure("Treeview", background="black", fieldbackground="black", foreground="white")
        self.style.configure("Treeview.Heading", background="black", foreground="white")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.create_list_tab()
        self.create_add_tab()
        self.create_search_tab()
        self.create_edit_tab()
        self.create_delete_tab()

    def create_add_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text='Add Bookmark')
        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky='w')
        self.add_title = ttk.Entry(frame, width=50)
        self.add_title.grid(row=0, column=1, pady=5)
        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky='w')
        self.add_category = ttk.Entry(frame, width=50)
        self.add_category.grid(row=1, column=1, pady=5)
        ttk.Label(frame, text="URL:").grid(row=2, column=0, sticky='w')
        self.add_url = ttk.Entry(frame, width=50)
        self.add_url.grid(row=2, column=1, pady=5)
        add_button = ttk.Button(frame, text="Add Bookmark", command=self.do_add_bookmark)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

    def do_add_bookmark(self):
        title = self.add_title.get().strip()
        category = self.add_category.get().strip()
        url = self.add_url.get().strip()
        log_debug(f"do_add_bookmark called with title: '{title}', category: '{category}', url: '{url}'")
        if title == "" or url == "":
            log_error("Failed to add bookmark: title or URL missing")
            messagebox.showerror("Error", "Please provide at least a title and a URL.")
            return
        self.manager.add_bookmark(title, category, url)
        messagebox.showinfo("Success", "Bookmark added successfully!")
        self.add_title.delete(0, tk.END)
        self.add_category.delete(0, tk.END)
        self.add_url.delete(0, tk.END)
        self.refresh_list()

    def create_search_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text='Search Bookmark')
        ttk.Label(frame, text="Search Query:").grid(row=0, column=0, sticky='w')
        self.search_query = ttk.Entry(frame, width=50)
        self.search_query.grid(row=0, column=1, pady=5)
        search_button = ttk.Button(frame, text="Search", command=self.do_search)
        search_button.grid(row=0, column=2, padx=10)
        self.search_list = tk.Listbox(frame, width=80, bg="black", fg="white", selectbackground="gray")
        self.search_list.grid(row=1, column=0, columnspan=3, pady=10, sticky='nsew')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.search_list.yview)
        self.search_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=3, sticky='ns')

    def do_search(self):
        query = self.search_query.get().strip()
        log_debug(f"do_search called with query: '{query}'")
        self.search_list.delete(0, tk.END)
        if not query:
            log_error("Search query empty, prompting user for input.")
            messagebox.showerror("Error", "Enter a search query.")
            return
        results = self.manager.search_bookmarks(query)
        if not results:
            self.search_list.insert(tk.END, "No matching bookmarks found.")
            log_debug("No matching bookmarks found.")
        else:
            for bm in results:
                display_text = f'ID:{bm.id} | Title: {bm.title} | Category: {bm.category} | URL: {bm.url}'
                self.search_list.insert(tk.END, display_text)
            log_debug(f"Displayed {len(results)} search results.")

    def create_edit_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text='Edit Bookmark')
        ttk.Label(frame, text="Bookmark ID:").grid(row=0, column=0, sticky='w')
        self.edit_id = ttk.Entry(frame, width=10)
        self.edit_id.grid(row=0, column=1, pady=5, sticky='w')
        ttk.Label(frame, text="New Title:").grid(row=1, column=0, sticky='w')
        self.edit_title = ttk.Entry(frame, width=50)
        self.edit_title.grid(row=1, column=1, pady=5)
        ttk.Label(frame, text="New Category:").grid(row=2, column=0, sticky='w')
        self.edit_category = ttk.Entry(frame, width=50)
        self.edit_category.grid(row=2, column=1, pady=5)
        ttk.Label(frame, text="New URL:").grid(row=3, column=0, sticky='w')
        self.edit_url = ttk.Entry(frame, width=50)
        self.edit_url.grid(row=3, column=1, pady=5)
        edit_button = ttk.Button(frame, text="Edit Bookmark", command=self.do_edit_bookmark)
        edit_button.grid(row=4, column=0, columnspan=2, pady=10)

    def do_edit_bookmark(self):
        try:
            bookmark_id = int(self.edit_id.get())
            log_debug(f"Editing bookmark with ID: {bookmark_id}")
        except ValueError:
            log_error("Invalid bookmark ID provided for editing.")
            messagebox.showerror("Error", "Please enter a valid Bookmark ID.")
            return
        title = self.edit_title.get().strip()
        category = self.edit_category.get().strip()
        url = self.edit_url.get().strip()
        if title == "" or url == "":
            log_error("Edit bookmark failed: title or url missing.")
            messagebox.showerror("Error", "Please provide at least a new title and URL.")
            return
        success = self.manager.edit_bookmark(bookmark_id, title, category, url)
        if success:
            messagebox.showinfo("Success", "Bookmark updated successfully!")
            log_debug(f"Bookmark with ID {bookmark_id} updated successfully.")
            self.edit_id.delete(0, tk.END)
            self.edit_title.delete(0, tk.END)
            self.edit_category.delete(0, tk.END)
            self.edit_url.delete(0, tk.END)
            self.refresh_list()
        else:
            log_error(f"Bookmark with ID {bookmark_id} not found during edit operation.")
            messagebox.showerror("Error", f"No bookmark found with ID {bookmark_id}")

    def create_delete_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text='Delete Bookmark')
        ttk.Label(frame, text="Bookmark ID:").grid(row=0, column=0, sticky='w')
        self.del_id = ttk.Entry(frame, width=10)
        self.del_id.grid(row=0, column=1, pady=5, sticky='w')
        delete_button = ttk.Button(frame, text="Delete Bookmark", command=self.do_delete_bookmark)
        delete_button.grid(row=1, column=0, columnspan=2, pady=10)

    def do_delete_bookmark(self):
        try:
            bookmark_id = int(self.del_id.get())
            log_debug(f"Attempting to delete bookmark with ID: {bookmark_id}")
        except ValueError:
            log_error("Invalid bookmark ID provided for deletion.")
            messagebox.showerror("Error", "Please enter a valid Bookmark ID.")
            return
        confirmed = messagebox.askyesno("Confirm", f"Are you sure you want to delete bookmark ID {bookmark_id}?")
        if not confirmed:
            log_debug("Bookmark deletion cancelled by user.")
            return
        success = self.manager.delete_bookmark(bookmark_id)
        if success:
            messagebox.showinfo("Deleted", "Bookmark deleted successfully!")
            log_debug(f"Bookmark with ID {bookmark_id} deleted.")
            self.del_id.delete(0, tk.END)
            self.refresh_list()
        else:
            log_error(f"No bookmark found with ID {bookmark_id} during deletion.")
            messagebox.showerror("Error", f"No bookmark found with ID {bookmark_id}")

    def create_list_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text='All Bookmarks')
        self.list_tree = ttk.Treeview(frame, columns=('ID', 'Title', 'Category', 'URL'), show='headings')
        self.list_tree.heading('ID', text='ID')
        self.list_tree.heading('Title', text='Title')
        self.list_tree.heading('Category', text='Category')
        self.list_tree.heading('URL', text='URL')
        self.list_tree.column('ID', width=50, anchor='center')
        self.list_tree.column('Title', width=150)
        self.list_tree.column('Category', width=100)
        self.list_tree.column('URL', width=200)
        self.list_tree.pack(expand=True, fill='both', side='left')
        self.list_tree.bind("<Double-1>", lambda event: self.copy_url())
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.list_tree.yview)
        self.list_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.refresh_list()

    def refresh_list(self):
        log_debug("Refreshing bookmarks list.")
        for i in self.list_tree.get_children():
            self.list_tree.delete(i)
        for bm in self.manager.bookmarks:
            self.list_tree.insert('', tk.END, values=(bm.id, bm.title, bm.category, bm.url))
        log_debug("Bookmarks list refreshed.")

    def copy_url(self):
        selected = self.list_tree.focus()
        if not selected:
            log_error("Copy URL failed: No bookmark selected.")
            messagebox.showerror("Error", "Please select a bookmark first.")
            return
        data = self.list_tree.item(selected, 'values')
        if len(data) < 4:
            log_error("Copy URL failed: Invalid selection data.")
            messagebox.showerror("Error", "Invalid selection.")
            return
        url = data[3]
        if url:
            self.clipboard_clear()
            self.clipboard_append(url)
            log_debug(f"Copied URL to clipboard: {url}")
            messagebox.showinfo("Copied", f"URL copied to clipboard:\n{url}")
        else:
            log_error("Copy URL failed: No URL found in the selected bookmark.")
            messagebox.showerror("Error", "No URL found for the selected bookmark.")

if __name__ == '__main__':
    log_debug("Launching Bookmark Application.")
    app = BookmarkApp()
    app.mainloop()
    log_debug("Bookmark Application closed.")
