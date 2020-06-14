from tkinter import Toplevel, Frame, Label, LabelFrame, Checkbutton, Listbox, Scrollbar, Button, OptionMenu, StringVar, IntVar
from tkinter.ttk import Progressbar
from time import ctime
from os.path import dirname
from util import FileList, DirectoryScanner, trimPath, DUPLICATE_TYPES, SORT_OPTIONS

  
# dialog to confirm file deletion
class DeleteDialog(Toplevel):

  def __init__(self, root, file, delMethod):
    Toplevel.__init__(self, root)
    self.wm_title("Confirm Delete")
    
    self.file = file
    self.delMethod = delMethod
    
    self.grid_columnconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=1)
    
    self.mainLbl = Label(self, text="Permanently delete file?")
    
    self.dataFrame = Frame(self, bg="#ffffff", bd=2, relief="groove")
    self.dataFrame.grid_columnconfigure(1, weight=1)
    
    self.nameLbl = Label(self.dataFrame, text="Name", bg="#ffffff")
    self.sizeLbl = Label(self.dataFrame, text="Size", bg="#ffffff")
    self.modLbl = Label(self.dataFrame, text="Modified", bg="#ffffff")
    self.nameVal = Label(self.dataFrame, text=self.file["name"], bg="#ffffff")
    self.sizeVal = Label(self.dataFrame, text=self.file["size"], bg="#ffffff")
    self.modVal = Label(self.dataFrame, text=ctime(self.file["modified"]), bg="#ffffff")
    
    self.trimVar = IntVar()
    self.trimVar.set(1)
    btnText = "Delete empty path"
    self.trimButton = Checkbutton(self, text=btnText, variable=self.trimVar)
    
    self.yesBtn = Button(self, text="Yes", width=10, command=self.yes)
    self.noBtn = Button(self, text="No", width=10, command=self.destroy)
    
    self.nameLbl.grid(row=0, column=0, padx=5, pady=10, sticky="w")
    self.sizeLbl.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    self.modLbl.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    self.nameVal.grid(row=0, column=1, padx=5, pady=5, sticky="e")
    self.sizeVal.grid(row=1, column=1, padx=5, pady=5, sticky="e")
    self.modVal.grid(row=2, column=1, padx=5, pady=5, sticky="e")
    
    self.mainLbl.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
    self.dataFrame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    self.trimButton.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    self.yesBtn.grid(row=3, column=0, pady=10)
    self.noBtn.grid(row=3, column=1, pady=10)
    
    self.geometry("300x225")
    self.resizable(False, False)
    self.grab_set()
    self.transient()
    
  # executed on yes click
  def yes(self, event=None):
    
    p = dirname(self.file["path"])
    self.delMethod(self.file)
    
    if self.trimVar.get() == 1:
      trimPath(p)
    
    self.destroy()


# dialog to show scan progress
class ScanDialog(Toplevel):

  def __init__(self, root, path, fileList):
    Toplevel.__init__(self, root)
    self.wm_title("Importing Directory...")
    
    self.scanner = DirectoryScanner(path, fileList)
    
    # string variables
    self.percent        = StringVar()
    self.timeRemaining  = StringVar()
    self.itemsRemaining = StringVar()
    
    # create gui elements
    self.percLabel = Label(self, textvariable=self.percent)
    self.timeLabel = Label(self, textvariable=self.timeRemaining)
    self.itemLabel = Label(self, textvariable=self.itemsRemaining)
    self.progress  = Progressbar(self, orient="horizontal", length=300, mode='indeterminate')
    self.cancelBtn = Button(self, text="Cancel", width=10, command=self.cancel)
    
    # build gui
    self.timeLabel.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    self.progress.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    self.cancelBtn.grid(row=4, column=0, padx=5, pady=5)
    
    self.resizable(False, False)
    self.grab_set()
    self.transient()
    
    self.scanner.start()
    self.progress.start()
    self.timeRemaining.set("Searching for files...")
    self.after(0, self.search)
    
  # cancel scan
  def cancel(self):
    self.scanner.stop()
    self.destroy()
    
  # waits for file search to complete,
  # then prepares gui for scan
  def search(self):
    
    if self.scanner.is_alive():
      
      # if search has completed
      if self.scanner.status == "scanning":
        self.resizable(True, True)
        self.percLabel.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.itemLabel.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.progress.grid_forget()
        self.progress = Progressbar(self, orient="horizontal", length=300, mode='determinate')
        self.progress.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.resizable(False, False)
        self.after(0, self.scan)
        
      else:
        self.after(50, self.search)
        
    else:
      self.destroy()
    
    
  # updates gui during scan
  def scan(self):
    
    if self.scanner.is_alive():
      self.percent.set(str(self.scanner.percent) + "% complete")
      self.progress["value"] = self.scanner.percent
      self.timeRemaining.set("Time remaining: " + self.scanner.timeRemaining)
      self.itemsRemaining.set("Items remaining: " + str(self.scanner.itemsRemaining))
      self.after(50, self.scan)
      
    else:
      self.destroy()
      
    
# listbox with vertical and horizontal scrollbars
class ScrollList(Frame):
  
  def __init__(self, root, onSelect=None):
    Frame.__init__(self, root)
    
    self.selectAction = onSelect
    
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)
    
    self.xscroll = Scrollbar(self)
    self.yscroll = Scrollbar(self)
    self.list = Listbox(self)
    self.list.bind("<<ListboxSelect>>", self.onSelect)
    
    self.list.config(xscrollcommand=self.xscroll.set)
    self.list.config(yscrollcommand=self.yscroll.set)
    self.list.config(activestyle="none")
    self.list.config(exportselection=False)
    self.xscroll.config(orient="horizontal")
    self.xscroll.config(command=self.list.xview)
    self.yscroll.config(command=self.list.yview)
    
    self.list.grid(row=0, column=0, sticky="nesw")
    self.xscroll.grid(row=1, column=0, sticky="ew")
    self.yscroll.grid(row=0, column=1, sticky="ns")
    
  # set this list's data
  def setData(self, data):
    self.list.delete(0, "end")
    for item in data:
      self.list.insert("end", item)
      
  # get the currently selected index
  def getSelection(self):
    ind = self.list.curselection()
    return -1 if ind == () else int(ind[0])
    
  # executed when a list item is selected
  def onSelect(self, event=None):
    if self.selectAction is not None:
      self.selectAction()
      
      
# panel to display list of files
class FilePanel(LabelFrame):

  def __init__(self, root, fileList, onNoDuplicates):
    LabelFrame.__init__(self, root, text="Files")
    
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(2, weight=1)
    
    self.fileList = fileList
    self.onNoDuplicates = onNoDuplicates
    self.activeFiles = []
    
    self.sortLbl = Label(self, text="Sort By")
    self.sortType = StringVar()
    self.sortMenu = OptionMenu(self, self.sortType, *SORT_OPTIONS)
    self.delBtn = Button(self, text="Delete", command=self.showDeleteDialog, width=10)
    self.list = ScrollList(self)
    
    self.sortMenu.config(width=10)
    self.sortType.set(SORT_OPTIONS[0])
    self.sortType.trace("w", self.sort)
    
    self.sortLbl.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    self.sortMenu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    self.delBtn.grid(row=0, column=3, padx=5, pady=5, sticky="e")
    self.list.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nesw")

  # update the list displayed on this panel
  def updateList(self, attribute, value):
    self.activeFiles = self.fileList.getDuplicates(attribute, value)
    self.sort()
  
  # sort the file list
  def sort(self, *params):
  
    self.activeFiles.sort(key=lambda x:x[self.sortType.get()])
    
    listData = []
    for file in self.activeFiles:
      row = []
      for type in SORT_OPTIONS:
        temp = type.capitalize() + ": "
        if type == "modified":
          temp += ctime(file["modified"])
        else:
          temp += str(file[type])
        row.append(temp)
      row.append("Path: " + file["path"])
      listData.append("; ".join(row))
    
    self.list.setData(listData)
    
  # show delete dialog
  def showDeleteDialog(self, event=None):
    sel = self.list.getSelection()
    if sel != -1:
      DeleteDialog(self, self.activeFiles[sel], self.delete)
    
  # delete a file
  def delete(self, file):
    self.fileList.delete(file)
    self.sort()
    
    if len(self.activeFiles) == 1:
      self.onNoDuplicates()
      self.clear()
  
# clear the gui  
  def clear(self):
    self.activeFiles = []
    self.list.setData([])
    
    
# panel to show list of duplicated attributes
class DuplicatePanel(LabelFrame):

  def __init__(self, root, fileList, onSelect):
    LabelFrame.__init__(self, root, text="Duplicated Attributes")
    
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(2, weight=1)
    
    self.fileList = fileList
    self.attribList = []
    
    self.attribLbl = Label(self, text="Attribute")
    self.attribType = StringVar()
    self.attribMenu = OptionMenu(self, self.attribType, *DUPLICATE_TYPES)
    self.list = ScrollList(self, onSelect)
    
    self.attribMenu.config(width=10)
    self.attribType.set(DUPLICATE_TYPES[0])
    self.attribType.trace("w", self.refresh)
    
    self.attribLbl.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    self.attribMenu.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    self.list.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nesw")
    
  # refresh this panel
  def refresh(self, *args):
    val = self.attribType.get()
    self.attribList = self.fileList.getDuplicatedAttributes(val)
    self.list.setData(self.attribList)
    
  # get selected attribute type
  def getType(self):
    return self.attribType.get()
    
  # get selected attribute value
  def getValue(self):
    sel = self.list.getSelection()
    return None if sel == -1 else self.attribList[sel]
  