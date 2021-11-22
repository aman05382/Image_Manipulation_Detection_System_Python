from tkinter import *
from tkinter import filedialog, ttk, messagebox
from tkinter import font
from PIL import ImageTk, Image
from detector import detect_copy_move, readImage

# Global variables
IMG_WIDTH = 400
IMG_HEIGHT = 400

# Function to return an image as a PhotoImage object given its path
def getImage(path, width, height):
    img = Image.open(path)
    img = img.resize((width, height), Image.ANTIALIAS)

    return ImageTk.PhotoImage(img)


class GUI(Frame):
    def __init__(self, parent=None):
        self.uploaded_image = None

        # Initialize the frame
        Frame.__init__(self, parent)
        self.pack()

        # Label for the results of scan
        self.resultLabel = Label(self, text="COPY MOVE DETECTOR", font = ("Pacifico", 30))
        self.resultLabel.grid(row=0, column=0, columnspan=2,pady=20)
        Grid.rowconfigure(self, 0, weight=1)

        # Get the blank image
        blank_img = getImage("images/blank.png", IMG_WIDTH, IMG_HEIGHT)

        # Displays the input image
        self.imagePanel = Label(self, image = blank_img)
        self.imagePanel.image = blank_img
        self.imagePanel.grid(row=1, column=0, padx=10,pady=10)

        # Label to display the output image
        self.resultPanel = Label(self, image = blank_img)
        self.resultPanel.image = blank_img
        self.resultPanel.grid(row=1, column=1, padx=10,pady=10)

        # Label to display the path of the input image
        self.fileLabel = Label(self, text="No file selected", fg="red", font = ("Roboto", 15))
        self.fileLabel.grid(row=2, column=0, columnspan=2)


        # Progress bar
        self.progressBar = ttk.Progressbar(self, length=500)
        self.progressBar.grid(row=3, column=0, columnspan=2)


        # Configure the style of the buttons
        s = ttk.Style()
        s.configure('my.TButton', font=('Times', 15),foreground='blue',bg='green')

        # Button to upload images
        self.uploadButton = ttk.Button(self, text="Upload Image", style="my.TButton", command=self.browseFile)
        self.uploadButton.grid(row=4, column=0, sticky="nsew", pady=30,padx=30)
        #self.uploadButton.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=5,padx=150)

        # Button to run the detection algorithm
        self.startButton = ttk.Button(self, text="Start", style="my.TButton", command=self.runProg)
        self.startButton.grid(row=4, column=1, sticky="nsew", pady=30,padx=30)
        #self.startButton.grid(row=4, column=1, columnspan=2, sticky="nsew", pady=5,padx=20)

        # Button to exit the program
        self.quitButton = ttk.Button(self, text="Exit program", command=parent.quit)
        self.quitButton.grid(row=7, column=0, columnspan=3, sticky="e", pady=50,padx=50)


    # Function to browse through the computer to upload images
    def browseFile(self):
        # Only accept jpg and png files
        filename = filedialog.askopenfilename(title="Select an image", filetype=[("Image file", "*.jpg *.png")])

        # No file selected (User closes the browsing window)
        if filename == "":
            return

        self.uploaded_image = filename
        self.progressBar['value'] = 0   # Reset the progress bar
        self.fileLabel.configure(text=filename)     # Set the path name in the fileLabel

        # Display the input image in imagePanel
        img = getImage(filename, IMG_WIDTH, IMG_HEIGHT)
        self.imagePanel.configure(image=img)
        self.imagePanel.image = img


        # Display blank image in resultPanel
        blank_img = getImage("images/blank.png", IMG_WIDTH, IMG_HEIGHT)
        self.resultPanel.configure(image=blank_img)
        self.resultPanel.image = blank_img



        # Reset the resultLabel
        self.resultLabel.configure(text="READY TO SCAN", foreground="black",font = ("Pacifico", 30))


    # Function to run the program the copy-move detection algorithm
    def runProg(self):
        # Retrieve the path of the image file
        path = self.uploaded_image

        # User has not selected an input image
        if path is None:
            messagebox.showerror('Error', "Please select image")    # Show error message
            return

        # Convert image into a numpy array
        img = readImage(path)

        # Run copy-move detection algorithm
        result = detect_copy_move(img)

        # Set the progress bar to 100%
        self.progressBar['value'] = 100

        # If copy-move is detected
        if result:
            # Retrieve the output image and display in resultPanel
            img = getImage("results.png", IMG_WIDTH, IMG_HEIGHT)
            self.resultPanel.configure(image=img)
            self.resultPanel.image = img

            # Display results in resultLabel
            self.resultLabel.configure(text="COPY-MOVE DETECTED", foreground="red")

        else:
            # Retrieve the thumbs up image and display in resultPanel
            img = getImage("images/thumbs_up.png", IMG_WIDTH, IMG_HEIGHT)
            self.resultPanel.configure(image=img)
            self.resultPanel.image = img

            # Display results in resultLabel
            self.resultLabel.configure(text="ORIGINAL IMAGE", foreground="green")



# Main Function
def main():
    # Initialize the app window
    root = Tk()
    root.title("Image Forgery Detection (Group No - 13)")
    #root.iconbitmap('images/forg.jpg')

    # img =Image.open('images/forg.jpg')
    # bg = ImageTk.PhotoImage(img)
    # label = Label(root, image=bg)
    # label.place(x = 0,y = 0,width=300,height=300)

    root.configure(bg='cyan')

    # Ensure the program closes when window is closed
    root.protocol("WM_DELETE_WINDOW", root.quit)

    root.state("zoomed")

    GUI(parent=root)

    root.mainloop()



if __name__ == "__main__":
    main()
