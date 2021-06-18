
# Riptutorial PDF/Ebook Downloader

This is a simple python script to ease the downloading of PDFs in from [riptutorial.com](https://www.riptutorial.com). With it, you can download PDFs one by one, in batches, search for keywords (e.g "python" or "java") and add some/all off the results to a queue.

## Note
This script is for those who would like to download the PDFs for use later, or to just archive them. If possible, please read them directly from the website.
***

## How to use

1. Make sure python 3 is installed in your system | [Download Python](https://www.python.org/downloads/)
2. Download/clone this repository and extract the contents.
3. Open a terminal and run the script with python <br/> `python riptutorial_pdf_downloader.py`
4. A list of options are displayed. If you wish to search for a certain category (e.g python), type `search` then press the **Enter** key
5. Type `python` and the **Enter** key again. All the pdfs with containing the word **python** will be displayed along with their ids
6. Type `add` to then a the ids of the pdfs you want to download, separated by spaces (e.g `1 22 333`) the hit **Enter**
7. Finially, type `start` and hit *Enter*, choose whether you want to skip PDFs that have already been downloaded (by inputing `y` or `n` followed by the **Enter** key) and the downloads will begin.

All pdfs will be downloaded to a `riptutorial` folder, which is located in the same place as the `riptutorial_pdf_downloader.py` script.

You can try out other options.

## Extra info
+ On the first run, the script gets a list of all available PDFs from the riptutorial server and saves them at `riptutorial/_list.json`. On subsequent runs, you would be prompted on whether the list should be gotten from the server or from the `_list.json` file.
+ When you add items to the download queue, the list of PDFs in the queue is saved at `riptutorial/_queue.json` so that in the case of an abrupt program exit or pc shutdown, the queue can be recovered. If any items were saved but not downloaded, you would be prompted at started on whether or not you want to load the saved queue.
+ The queue in `_queue.json` is saved by the PDF id which can change if the PDFs on the server's order change (maybe due to new PDFs added or old ones deleted), so if you decide to load the PDF list from the server, but choose to recover the queue, be sure to view the queue to verify that the right PDFs will be downloaded.
+ Some PDF names start with a . (e.g ".net-core.pdf"), files/folders starting with a "." on unix systems are hidden, so said PDFs names are changed to start with an underscore: "_" (so ".net-core.pdf becones "_.net-core.pdf")

***
#### Feature requests or bug reports are welcomed.