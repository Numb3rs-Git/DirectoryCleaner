from tkinter import Tk, Button, filedialog, messagebox
from gui import DuplicatePanel, FilePanel, ScanDialog, DeleteDialog
from util import FileList, cleanPath


# main window
class DirectoryCleaner(Tk):

  def __init__(self):
    Tk.__init__(self)
    
    self.wm_title("Directory Cleaner")
    
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(1, weight=1)
    self.grid_columnconfigure(2, weight=2)
    
    self.fileList = FileList()
    
    self.importBtn = Button(self, text="Import Directory...", width=20, command=self.importDir)
    self.resetBtn = Button(self, text="Reset", width=10, command=self.reset)
    self.cleanBtn = Button(self, text="Remove Empty Folders...", width=25, command=self.cleanFolder)
    self.dupPanel = DuplicatePanel(self, self.fileList, self.updateFilePanel)
    self.filePanel = FilePanel(self, self.fileList, self.dupPanel.refresh)
    
    self.importBtn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    self.resetBtn.grid(row=0, column=1, padx=5, pady=10, sticky="w")
    self.cleanBtn.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    self.dupPanel.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nesw")
    self.filePanel.grid(row=1, column=2, padx=5, pady=5, sticky="nesw")
    
    self.minsize(550, 200)
    self.geometry("700x350")
    
  # opens dialog to import a folder
  def importDir(self):
  
    path = filedialog.askdirectory()
    
    if path == "":
      return
    
    self.wait_window(ScanDialog(self, path, self.fileList))
    
    self.dupPanel.refresh()
    self.filePanel.clear()
    
  # empties filelist and resets gui
  def reset(self):
    self.fileList.empty()
    self.dupPanel.refresh()
    self.filePanel.clear()
    
  # deletes empty subfolders under some folder
  def cleanFolder(self):
    
    path = filedialog.askdirectory()
    
    if path == "":
      return
      
    nFiles = str(cleanPath(path))
    msg = " empty"
    msg += " folder" if nFiles == "1" else " folders"
    msg = str(nFiles) + msg + " deleted"
    
    messagebox.showinfo("Done", msg)
    
  # update file list panel
  def updateFilePanel(self):
    dupVal = self.dupPanel.getValue()
    dupType = self.dupPanel.getType()
    self.filePanel.updateList(dupType, dupVal)
  

if __name__ == "__main__":
  DirectoryCleaner().mainloop()