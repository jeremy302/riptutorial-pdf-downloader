
import os
import re
import math
import json
from requests import Session

session = Session()

def get_url(path): 
    return "https://riptutorial.com" + ('/' if not path.startswith('/') else '')+path

pdfs = []
queue = []
current_id = 0
list_filename,queue_filename="_list.json","_queue.json"

class PDF:
    id: int
    title: str
    page_link: str
    pdf_link: str

    def __init__(self, id: int, title: str, page_link: str):
        self.id = id
        self.title = title
        self.page_link = page_link
        self.pdf_link = ""

    def __repr__(self) -> str:
        width = 45
        str_id = '[%s]' % self.id
        remaining_width = width-len(str_id)
        title = self.title if len(
            self.title) <= remaining_width else self.title[::remaining_width-3]+'...'
        return f'{str_id} {title}'.ljust(width)

    def get_filename(self):
        filename = self.title[0:self.title.rfind('(')].strip()
        return filename+".pdf" if filename else self.title+".pdf"

    def get_pdf_link(self, force=False):
        if not force and self.pdf_link:
            return True
        try:
            response = session.get(get_url(self.page_link))
        except:
            response = None
        if not (response and response.ok):
            print(
                "Failed to retrieve PDF link. Check your internet connection and try again.")
            return False
        elif not response.text:
            print("Server sent empty response. Try again later.")
            return False

        pdf_html = response.text
        match = re.search(
            r"<a\s*href=\"(?P<link>\/Download\/.+?)\">", pdf_html)
        self.pdf_link = match.groupdict()['link']
        save_list()
        return True

    def download(self, force=False):
        filename = self.get_filename()
        filepath = "riptutorial/"+('_' if filename.startswith('.') else '') + filename
        if (not force) and os.path.exists(filepath):
            print("PDF file already exists.")
            return True
        with open(filepath, "wb") as file:
            try:
                pdf_response = session.get(get_url(self.pdf_link))
            except:
                pdf_response = None
            if not (pdf_response and pdf_response.ok):
                print(
                    "Failed to retrieve PDF data. Check your internet connection and try again.")
                try: os.remove(filepath)
                except: pass
                return False
            file.write(pdf_response.content)
            print("PDF download complete.");
        return True

    def valid(self):
        return (type(self.id) == int and type(self.title) == str and
                type(self.pdf_link) == str and type(self.page_link) == str)
        #and type(self.to_download)==bool)

    @classmethod
    def create(cls, title: str, page_link: str):
        global current_id

        current_id += 1
        pdf = PDF(id=current_id, title=title, page_link=page_link)
        pdfs.append(pdf)


def get_all_pdfs():
    print("Loading PDF list from server")
    try:
        response = session.get(get_url("ebook"))
    except:
        response = None

    if not (response and response.ok):
        print("Failed to retrieve PDFs. Check your internet connection and try again.")
        input("\nPress Enter to exit")
        exit(-1)
    elif not response.text:
        print("Server sent empty response. Try again later.")
        input("\nPress Enter to exit")
        exit(-1)

    pdfs_html = response.text

    pdfs_iter = re.finditer(
        r"<a\s*href=\"(?P<link>\/ebook\/.+?)\">(?P<title>.+?)<\/a>", pdfs_html)
    for pdf_match in pdfs_iter:
        groups = pdf_match.groupdict()
        PDF.create(title=groups.get("title", ""),
                   page_link=groups.get("link", ""))
    save_list()


def display_pdfs(pdfs=[], columns=2):
    rows = [pdfs[columns*i:(columns*i)+columns]
            for i in range(math.ceil(len(pdfs)/columns))]
    for row in rows:
        for pdf in row:
            print(repr(pdf), end="")
        print("\n")


def show_all():
    print("There are a total of %d PDF(s)" %(len(pdfs)))
    display_pdfs(pdfs)


def search():
    query = input("Input keywords/id to search for: ").strip().lower()
    result = [pdf for pdf in pdfs
                  if all(m in pdf.title.lower()+str(pdf.id) for m in query.split(' '))]
    print("%d PDF(s) matched your search:"%(len(result)))
    display_pdfs(result)


def view_queue():
    print("%d PDF(s) in queue: "%(len(queue)))
    display_pdfs(queue)


def add_to_queue():
    str_ids = input(
        "Enter IDs of PDF(s) to add (separated by spaces):\n>> ").strip()
    if not re.match("^(\d*\s*)*$", str_ids):
        print("Invalid input")
        return
    ids = [int(id_) for id_ in str_ids.split(' ') if id_]
    invalid_ids = []
    for id_ in ids:
        pdf = next((pdf for pdf in pdfs if pdf.id == id_), None)
        if pdf:
            if pdf not in queue:
                queue.append(pdf)
        else:
            invalid_ids.append(id_)
    if invalid_ids:
        print("These IDs were invalid: %s" %
              (', '.join([str(v) for v in invalid_ids])))

    print("%d PDF(s) were added to the queue" % (len(ids)-len(invalid_ids)))
    save_queue()


def remove_queue():
    str_ids = input(
        "Enter IDs of PDF(s) to add (separated by spaces):\n>> ").strip()
    if not re.match("^(\d*\s*)*$", str_ids):
        print("Invalid input")
        return
    ids = [int(id_) for id_ in str_ids.split(' ') if id_]
    invalid_ids = []
    for id_ in ids:
        pdf = next((pdf for pdf in queue if pdf.id == id_), None)
        if pdf:
            queue.remove(pdf)
        else:
            invalid_ids.append(id_)
    if invalid_ids:
        print("These IDs were not in queue: %s" %
              (', '.join([str(v) for v in invalid_ids])))

    print("%d PDF(s) were removed from the queue" % (len(ids)-len(invalid_ids)))
    save_queue()


def download():
    print("Starting download...")
    can_skip = input(
        "Would you link to skip PDFs that have already been downloaded? [y/n]: ").strip().lower() == "y"
    for pdf in list(queue):
        print("\nCurrent item: [%d] %s" % (pdf.id, pdf.title))
        print("Getting link...")
        got_link = pdf.get_pdf_link()
        if not got_link:
            return
        print("Downloading from: %s" % (get_url(pdf.pdf_link)))

        ok = pdf.download(not can_skip)
        
        if not ok:
            print("An error occured. Stopping download...")
            break
        else:
            queue.remove(pdf)
            save_queue()
    save_list()
    print("Download Complete!")


def show_options():
    while True:
        cmd = input("\nSelect an option:\n\t" +
                    "[all]    Show All\n\t" +
                    "[search] Search\n\t" +
                    "[view]   View Download Queue\n\t" +
                    "[add]    Add to Queue\n\t" +
                    "[remove] Remove From Queue\n\t" +
                    "[start]  Start Download\n\t" +
                    "[quit]   Quit\n"
                    ">> ")
        print('\n')

        if cmd == "all":
            show_all()
        elif cmd == "search":
            search()
        elif cmd == "view":
            view_queue()
        elif cmd == "add":
            add_to_queue()
        elif cmd == "remove":
            remove_queue()
        elif cmd == "start":
            download()
        elif cmd == "quit":
            exit(1)
        else:
            print("Invalid Command!\a")


def save_list():
    if not os.path.exists("riptutorial"):
        os.mkdir("riptutorial")

    with open("riptutorial/"+list_filename, "w") as file:
        json.dump([pdf.__dict__ for pdf in pdfs], file)


def save_queue():
    if not os.path.exists("riptutorial"):
        os.mkdir("riptutorial")
    if not len(queue):
        try: os.remove("riptutorial/"+queue_filename)
        except: pass
        finally: return

    with open("riptutorial/_queue.json", "w") as file:
        json.dump([pdf.id for pdf in queue],file)


def load_list():
    pdfs_dict = []

    if os.path.exists("riptutorial/"+list_filename):
        can_load = input("There is a local PDF list copy. Should it be loaded? [y/n]: ").strip().lower() == "y"
        if can_load:
            with open("riptutorial/"+list_filename, "r") as file:
                try:
                    pdfs_dict = json.load(file)
                except:
                    print("Error loading PDF list")
            if pdfs_dict:
                for pdf_dict in pdfs_dict:
                    pdf = PDF(0, "", "")
                    pdf.__dict__.update(pdf_dict)
                    if pdf.valid():
                        pdfs.append(pdf)
        if not pdfs:
            print("Local list contains no valid PDF info")
            get_all_pdfs()
        else:
            print("Loaded %d of %d from local list" %
                  (len(pdfs), len(pdfs_dict)))
    else:
        get_all_pdfs()


def load_queue():
    queue_list = []

    if os.path.exists("riptutorial/_queue.json"):
        can_load = input("There is an unfinished download queue. Should it be loaded? [y/n]: ").strip().lower() == "y"

        if can_load:
            with open("riptutorial/_queue.json", "r") as file:
                try:
                    queue_list = json.load(file)
                except: pass
            if queue_list:
                for pdf_id in queue_list:
                    pdf = next((pdf for pdf in pdfs if pdf.id == pdf_id), None)
                    if pdf:
                        queue.append(pdf)
    if queue_list:
        print("Loaded %d of %d from saved queue" % (len(queue), len(queue_list)))

load_list()
load_queue()
show_options()
