import os
from os.path import normcase, getmtime, isfile, isdir, abspath, basename, getsize
from hashlib import md5
from threading import Thread
from datetime import datetime, timedelta


# duplicate types
DUPLICATE_TYPES = ["name", "hash"]

# sort options
SORT_OPTIONS = ["modified", "size"]

# block size for file reading
BLOCK_SIZE = 65536


# represents a time delta as a human readable string
def timeDeltaString(delta):
  
  days = ""
  hours = ""
  minutes = ""
  seconds = ""
  secs = 0
  
  if delta.days > 0:
    days = str(delta.days)
    days += " day" if delta.days == 1 else " days"
  
  # get hours
  secs = delta.seconds
  tmp = secs // 3600
  secs = secs % 3600
  
  if tmp > 0 or days != "":
    hours = str(tmp)
    hours += " hour" if tmp == 1 else " hours"

  # return days and hours if days > 0
  if days != "":
    return days + " and " + hours
  
  tmp = secs // 60
  secs = secs % 60
  
  if tmp > 0 or hours != "":
    minutes = str(tmp)
    minutes += " minute" if tmp == 1 else " minutes"
  
  # return hours and minutes if hours > 0
  if hours != "":
    return hours + " and " + minutes
  
  seconds = str(secs)
  seconds += " second" if secs == 1 else " seconds"
  
  result = minutes + " and " if minutes != "" else ""
  return result + seconds

  
# finds and deletes empty folders under 
# (and including) a path
def cleanPath(pathStr):
  
  try:
    pathStr = str(pathStr)
    items = os.listdir(pathStr)
  except:
    return 0
    
  nFolders = 0
  for item in items:
  
    item = pathStr + "/" + item
  
    if isdir(item):
    
      nFolders += cleanPath(item)
      
      try:
        if len(os.listdir(item)) == 0:
          os.rmdir(item)
          nFolders += 1
      except:
        pass
        
  return nFolders
  

# deletes empty folders from the end of a path
def trimPath(pathStr):
    
  try:
    pathStr = str(pathStr)
    isEmpty = len(os.listdir(pathStr)) == 0
  except:
    return
    
  while isEmpty:
    try:
      os.rmdir(pathStr)
      pathStr = "/".join(pathStr.split("/")[:-1])
      isEmpty = len(os.listdir(pathStr)) == 0
    except:
      return
  
  
# stores a list of files while keeping 
# track of duplicated attributes
class FileList:

  def __init__(self):
    self.files = None
    self.lookup = None
    self.duplicates = None
    self.empty()
  
  # empties this file list
  def empty(self):
  
    self.files = {}
    self.lookup = {}
    self.duplicates = {}
    
    for type in DUPLICATE_TYPES:
      self.lookup[type] = {}
      self.duplicates[type] = set()
    
  # add a file
  def add(self, file):
  
    # if file has already been added, return
    if file["path"] in self.files:
      return
  
    # add file to main dict
    self.files[file["path"]] = file
    
    # for each duplicate type
    for type in DUPLICATE_TYPES:
      
      # if the file attribute is duplicated
      if file[type] in self.lookup[type]:
      
        # append to existing list
        self.lookup[type][file[type]].append(file)
        
        # add to duplicate list
        self.duplicates[type].add(file[type])
      
      # otherwise, create the list
      else:
        self.lookup[type][file[type]] = [file]
        
  # remove a file
  def delete(self, file):

    # if the path exists in this file list
    if file["path"] in self.files:
    
      # delete from os
      os.remove(file["path"])
    
      # remove file from main dict
      del self.files[file["path"]]
      
      # for each duplicate type
      for type in DUPLICATE_TYPES:
      
        # remove file from associated lookup table
        self.lookup[type][file[type]].remove(file)
        
        l = len(self.lookup[type][file[type]])
      
        # if a file attribute is no longer duplicated, remove from duplicates
        if l == 1:
          self.duplicates[type].remove(file[type])
          
        # if the last file with a given attribute is removed, delete the associated list
        elif l == 0:
          del self.lookup[type][file[type]]
      
  # returns a list of duplicate attributes of a specified type
  def getDuplicatedAttributes(self, type):
    
    if type in self.duplicates:
      return list(self.duplicates[type])
      
    return []
    
      
  # retrieves a list of duplicated files
  def getDuplicates(self, type, value):
  
    if type not in self.lookup:
      return []
      
    if value not in self.lookup[type]:
      return []
      
    return self.lookup[type][value]
    
  # returns true if this FileList contains
  # a file with a specified path
  def hasPath(self, filePath):
    return filePath in self.files
  
  
# scans a directory to build up a FileList
class DirectoryScanner(Thread):

  def __init__(self, dirPath, fileList):
    Thread.__init__(self)
    self.root = dirPath
    self.status = "not started"
    self.files = []
    self.fileList = fileList
    self.percent = 0
    self.timeRemaining = ""
    self.itemsRemaining = 0
    
  # stop the scan
  def stop(self):
    self.status = "stopping"
    
  # recursively search a directory to find all files
  # return total size of all files found
  def findFiles(self, path):
    
    try:
      items = os.listdir(path)
    except:
      return 0
    
    size = 0
    
    for item in items:
    
      if self.status == "stopping":
        self.files = []
        return 0
      
      item = normcase(item)
      item = path + "/" + item
      
      if isfile(item):
        
        if not self.fileList.hasPath(item):
        
          file = {}
          file["path"] = item
          file["name"] = basename(item)
          file["size"] = getsize(item)
          file["modified"] = getmtime(item)
          self.files.append(file)

          size += file["size"]
      
      else:
      
        size += self.findFiles(item)
    
    return size
    
  # scan directory and get hashes for all files
  def run(self):
  
    self.status = "searching"
    total = self.findFiles(self.root)
    self.status = "scanning"
    
    processed = 0
    startTime = datetime.now()
    self.itemsRemaining = len(self.files)
    
    for file in self.files:
    
      if self.status == "stopping":
        return
      
      try:
      
        f = open(file["path"], "rb")
        hash = md5()
        
        try:
        
          buffer = f.read(BLOCK_SIZE)
          size = len(buffer)
        
          while len(buffer) > 0 and self.status != "stopping":
            hash.update(buffer)
            buffer = f.read(BLOCK_SIZE)
            size = len(buffer)
            
          f.close()
          
          file["hash"] = hash.hexdigest()
          self.fileList.add(file)
          
        except:
          pass
        
      except:
        pass
      
      processed += file["size"]
      self.percent = int(100 * processed / total) if total > 0 else 0

      if processed > 0:
        timeRemaining = datetime.now() - startTime
        timeRemaining *= (total - processed) / processed
      else:
        timeRemaining = timedelta(0)
      
      self.timeRemaining = timeDeltaString(timeRemaining)
      
      self.itemsRemaining -= 1
      
    self.status = "stopped"