import glob
import os
import string
import tkinter as tk
import multiprocessing
import threading
import tkinter
# import cv

from PIL import Image, ImageTk


ALPHABET = string.ascii_lowercase + ''.join([str(x) for x in range(0, 10)])


def solve_captcha(filename):
    # root = tk.Tk()
    # img = ImageTk.PhotoImage(Image.open(filename))
    # panel = tk.Label(root, image=img)
    # panel.pack(side="bottom", fill="both", expand="yes")
    # root.after(3*1000, root.quit)
    # root.mainloop()
    img = cv.imread(filename)
    cv.imshow(img)
    # with Image.open(filename) as img:
    #     img.show()


def main():
    root = tkinter.Tk()

    for filename in glob.glob('images/captcha-*.jpg'):
        basename = filename.rsplit('.', 1)[0]
        if os.path.exists(basename + '.txt'):
            continue
        print(filename)
        with Image.open(filename) as img:
            root.geometry('%dx%d' % (img.size[0], img.size[1]))
            tkpi = ImageTk.PhotoImage(img)
        label_image = tkinter.Label(root, image=tkpi)
        label_image.place(x=0, y=0, width=img.size[0], height=img.size[1])
        root.title(filename)

        while True:
            # my_code_thread = threading.Thread(target=solve_captcha, args=(filename,))
            # my_code_thread.start()

            solution = input('Captcha: ')
            if not len(solution) == 5:
                print('not right length')
                continue
            matches = [x in ALPHABET for x in solution]
            if not all(matches):
                print('Not right alphabet', ALPHABET, matches)
                continue
            break
        with open(basename + '.txt', 'w') as f:
            f.write(solution)

    root.quit()

if __name__ == '__main__':
    main()
