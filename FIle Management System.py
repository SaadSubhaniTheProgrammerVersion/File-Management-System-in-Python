"""
these are the libraries used in the code
"""

# to save the file system root to a file
import pickle
import sys
import colorama as c

"""
    these are the global variables for the file system
"""
# current working objects of file and directory
currWorkingDir = None
currWorkingFile = None
root = None
SPACE = '    '
BRANCH = '|   '
LAST = '|___'
# Global Memory for storing the data
Memory = [None] * 100

"""
    this is the class for the file having the following attributes:
    1. name of the file
    2. size of the file
    3. pointer to the data in the memory
"""
# class to represent a file

class File:

    # Constructor
    def __init__(self, name):
        self.name = name
        self.Inodes = []

    # write to file
    def write(self, inode):
        self.Inodes.append(inode)

"""
    this is the class of the directory having the following attributes:
    1. name: name of the directory
    2. files: list of files in the directory
    3. subdirectories: list of directories in the directory
"""
# class to represent a directory

class Directory:

    # Constructor
    def __init__(self, name):
        self.name = name
        self.files = {}
        self.subdirectories = {}

    # Add file to directory
    def addFile(self, file):
        if (file.name in self.files.keys()):
            print(c.Fore.RED+"\nFile already exists"+c.Fore.RESET)
            return
        else:
            self.files[file.name] = file
            print(c.Fore.GREEN+"\nFile created successfully"+c.Fore.RESET)

    # Add subdirectory to directory

    def addSubdirectory(self, directory):
        if (directory.name in self.subdirectories.keys()):
            print(c.Fore.RED+"\nDirectory already exists"+c.Fore.RESET)

        else:
            self.subdirectories[directory.name] = directory

"""
These are the major functions for all the commands in the file system
"""
# function to print the file system tree using SPACE , BRANCH , LAST

def printTree(dir, level):
    global currWorkingDir
    if (dir == None):
        return
    if (level == 0):
        print(c.Fore.BLUE+dir.name+c.Fore.RESET)
    else:
        print(c.Fore.CYAN+SPACE * (level - 1) + BRANCH + c.Fore.RESET +
              c.Fore.GREEN + dir.name + c.Fore.RESET, end='')
        if (currWorkingDir == dir):
            print(c.Fore.RED+" <----"+c.Fore.RESET, end="")
        print()

    for file in dir.files.keys():
        print(c.Fore.CYAN+SPACE * level + LAST+c.Fore.RESET + c.Fore.YELLOW +
              dir.files[file].name+c.Fore.RESET + "\t" + str(len(dir.files[file].Inodes)) + "kB")
    for directory in dir.subdirectories.keys():
        printTree(dir.subdirectories[directory], level + 1)

# function to find the directory with its name

def findDirectory(dir, dirName):
    if (dir.name == dirName):
        return dir
    else:
        for directory in dir.subdirectories.keys():
            foundDir = findDirectory(dir.subdirectories[directory], dirName)
            if (foundDir != None):
                return foundDir
        return None

# function to create a file
def createFile(fName):
    global currWorkingDir
    if (fName == None or fName == ""):
        print(c.Fore.RED+"\nFile name cannot be empty"+c.Fore.RESET)
        return
    if (currWorkingDir == None):
        print(c.Fore.RED+"\nNo directory is selected"+c.Fore.RESET)
        return
    file = File(fName)
    currWorkingDir.addFile(file)

# function to create directory
def createDirectory(dirName):
    global currWorkingDir, root
    if (findDirectory(root, dirName) != None):
        print(c.Fore.RED+"\nDirectory already exists"+c.Fore.RESET)

        return
    if (dirName == currWorkingDir.name):
        print(c.Fore.RED+"\nDirectory with this name already exists"+c.Fore.RESET)

        return
    if (dirName == None or dirName == ""):
        print(c.Fore.RED+"\nDirectory name can not be empty"+c.Fore.RESET)

        return
    if (currWorkingDir == None):
        print(c.Fore.RED+"\nNo directory is selected"+c.Fore.RESET)

        return
    directory = Directory(dirName)
    currWorkingDir.addSubdirectory(directory)
    print(c.Fore.GREEN+"\nDirectory created successfully"+c.Fore.RESET)

def getPathOfCWD(root, dirName):
    if root == None:
        return ""
    if root.name == dirName:
        return dirName
    for directory in root.subdirectories.keys():
        path = getPathOfCWD(root.subdirectories[directory], dirName)
        if path != "":
            return root.name + "/" + path
    return ""

# function to move file from one directory to another

def moveFile(fileName):
    global currWorkingDir, root
    if currWorkingDir == None:
        print(c.Fore.RED+"\nNo directory is selected"+c.Fore.RESET)
        return
    if fileName not in currWorkingDir.files.keys():
        print(c.Fore.RED+"\nFile not found"+c.Fore.RESET)
        return
    dirName = input("\nEnter the directory name: ")
    resDir = findDirectory(root, dirName)
    if resDir == None:
        print(c.Fore.RED+"\nDirectory not found"+c.Fore.RESET)
        return
    file = currWorkingDir.files[fileName]
    resDir.addFile(file)
    del currWorkingDir.files[fileName]
    print(c.Fore.GREEN+"\nFile moved successfully"+c.Fore.RESET)

# delete file from the directory

def deleteFile(fileName):
    global currWorkingDir
    if currWorkingDir == None:
        print(c.Fore.RED+"\nNo directory is selected"+c.Fore.RESET)
        return
    if fileName not in currWorkingDir.files.keys():
        print(c.Fore.RED+"\nFile not found"+c.Fore.RESET)
        return
    # get the file
    file = currWorkingDir.files[fileName]
    for inode in file.Inodes:
        # delete the file from the disk
        del Memory[inode]
    # delete the file from the directory
    del currWorkingDir.files[fileName]
    print(c.Fore.GREEN+"\nFile deleted successfully"+c.Fore.RESET)

# function to open file using filename
def openFile(fileName):
    global currWorkingDir, currWorkingFile
    if currWorkingFile != None:
        print(c.Fore.RED+"\nFile is already open"+c.Fore.RESET)
        return
    if currWorkingDir == None:
        print(c.Fore.RED+"\nNo directory is selected"+c.Fore.RESET)
        return
    if fileName not in currWorkingDir.files.keys():
        print(c.Fore.RED+"\nFile not found"+c.Fore.RESET)
        return
    print(c.Fore.GREEN+"\nFile opened successfully"+c.Fore.RESET)
    return currWorkingDir.files[fileName]

# function to close opened file

def closeFile():
    global currWorkingFile
    currWorkingFile = None
    print(c.Fore.GREEN+"\nFile closed successfully"+c.Fore.RESET)

# function to store data in memory

def writeToGlobalMemory(line):
    global Memory
    for i in range(0, len(Memory)):
        if Memory[i] == None:
            Memory[i] = line
            return i
    print(c.Fore.RED+"\nMemory is full"+c.Fore.RESET)
    return -1

# function to write text to file

def writeToFile():
    global currWorkingFile
    if currWorkingFile == None:
        print(c.Fore.RED+"\nNo file is opened"+c.Fore.RESET)
        return
    print("\nSelect the mode of writing to file: ")
    print("1. Append")
    print("2. write_at")
    command = input("\nEnter the command: ")
    if command == "Append":
        print("\nEnter the text to append to file: ")
        data = input()
        # tokenize data at .
        tokens = data.split(".")
        for i in range(0, len(tokens)):
            if tokens[i] == "":
                continue
            Index = writeToGlobalMemory(tokens[i].strip())
            if Index == -1:
                return
            currWorkingFile.write(Index)
            print(c.Fore.GREEN+"\nData written successfully"+c.Fore.RESET)

    elif command == "write_at":
        readFromFile(True)
        print("\nEnter the Line Number to write text at: ")
        lineNo = int(input())
        if lineNo > len(currWorkingFile.Inodes):
            print(c.Fore.RED+"\nInvalid Line Number"+c.Fore.RESET)
            return
        print("\nEnter the text to write to file: ")
        data = input()

        Index = currWorkingFile.Inodes[lineNo - 1]
        Memory[Index] = data
        print(c.Fore.GREEN+"\nData written successfully"+c.Fore.RESET)

    else:
        print("\nInvalid command")

# function to read text from file at start and till specified characters
def readFrom(start, size):
    global currWorkingFile
    if currWorkingFile == None:
        print(c.Fore.RED+"\nNo file is opened"+c.Fore.RESET)
        return
    if start > len(currWorkingFile.Inodes):
        print(c.Fore.RED+"\nInvalid Line Number"+c.Fore.RESET)
        return
    for i in range(start-1, len(currWorkingFile.Inodes)):
        Index = currWorkingFile.Inodes[i]
        # get specific line from memory
        line = Memory[Index]
        # print line till size number of characters
        print(line[:size])
        size = size - len(line)
        if size <= 0:
            break

# Read text from the file
def readFromFile(mode):
    global currWorkingFile
    if mode == True:
        # read file sequentially
        print("\nReading file sequentially")
        for i in range(0, len(currWorkingFile.Inodes)):
            address = currWorkingFile.Inodes[i]
            print(i+1, "-> ", Memory[address])
    else:
        print("Number of lines in current file: ", len(currWorkingFile.Inodes))
        print("\nEnter the line number to read from: ")
        start = int(input())
        print("\nEnter the number of characters to read: ")
        size = int(input())
        readFrom(start, size)

# function to move text within the file
def moveWithinFile(s, t):
    global currWorkingFile
    if (currWorkingFile == None):
        print(c.Fore.RED+"\nNo file is opened"+c.Fore.RESET)
        return
    if (s > len(currWorkingFile.Inodes) or t > len(currWorkingFile.Inodes) or s < 1 or t < 1):
        print(c.Fore.RED+"\nInvalid line number"+c.Fore.RESET)
        return
    if (s == t):
        print(c.Fore.RED+"\nSource and destination are same"+c.Fore.RESET)
        return
    # pop the line from source
    inode = currWorkingFile.Inodes[s-1]
    # store line at destination
    currWorkingFile.Inodes[t-1] = inode
    currWorkingFile.Inodes.pop(s-1)
    print(c.Fore.GREEN+"\nLine moved successfully"+c.Fore.RESET)

def truncateFile(size):
    global currWorkingFile
    if (currWorkingFile == None):
        print(c.Fore.RED+"\nNo file is opened"+c.Fore.RESET)
        return
    if (size > len(currWorkingFile.Inodes)):
        print(c.Fore.RED+"\nInvalid size"+c.Fore.RESET)
        return

    # delete lines from the file
    for i in range(size, len(currWorkingFile.Inodes)):
        Index = currWorkingFile.Inodes[i]
        Memory[Index] = None

    currWorkingFile.Inodes = currWorkingFile.Inodes[:size]

    if (size == 0):
        print(c.Fore.GREEN+"\nComplete file truncated successfully"+c.Fore.RESET)

        return
    else:
        print(c.Fore.GREEN+"\nFile truncated successfully"+c.Fore.RESET)

        readFromFile(True)

#  function to find size of all files in the directory
def findSizeOfFiles(root):
    if (root == None):
        return 0
    size = 0
    for i in root.files.keys():
        size += len(root.files[i].Inodes)
    for i in root.subdirectories.keys():
        size += findSizeOfFiles(root.subdirectories[i])
    return size

# function to print progress bar
def printProgressBar(value, label):
    print("\n\n")
    n_bar = 50  # size of progress bar
    max = 100
    j = value/max
    sys.stdout.write('\r')
    bar = '█' * int(n_bar * j)
    bar = bar + '-' * int(n_bar * (1-j))

    sys.stdout.write(f"{label.ljust(10)} | [{bar:{n_bar}s}] {int(100 * j)}% ")
    sys.stdout.flush()
    print("\n\n")

"""
 these functions are responsible for running the complete file system
 these functions get the user input for the commands and call the respective functions
"""

def processCommand(command):

    global currWorkingDir, currWorkingFile, root
    if command == "Create File":
        fileName = input("\nEnter the file name: ")
        createFile(fileName)
    elif command == "Delete File":
        fileName = input("\nEnter the file name: ")
        deleteFile(fileName)
    elif command == "Make Directory":
        dirName = input("\nEnter the directory name: ")
        createDirectory(dirName)
    elif command == "Change Directory":
        dirName = input("\nEnter the directory name: ")
        resDir = findDirectory(root, dirName)

        if resDir == None:
            print(c.Fore.RED+"\nDirectory not found"+c.Fore.RESET)
        else:
            currWorkingDir = resDir
            print(c.Fore.GREEN+"\nThe directory has been changed to: " +
                  dirName+" "+c.Fore.RESET)
    elif command == "Move File":
        fileName = input("\nEnter the file name: ")
        moveFile(fileName)
    elif command == "Open File":
        fileName = input("\nEnter the file name: ")
        currWorkingFile = openFile(fileName)
    elif command == "Close File":
        closeFile()
    elif command == "Write_to_file":
        writeToFile()
    elif command == "Read_from_file":
        if currWorkingFile == None:
            print("\nNo file is opened")
            return
        print("\nSelect the mode of reading from file: ")
        print("1. Sequentially")
        print("2. ReadFrom")
        command = input("\nEnter the command: ")
        if command == "Sequentially":
            readFromFile(True)
        elif command == "ReadFrom":
            readFromFile(False)
        else:
            print(c.Fore.Red+"\nInvalid command"+c.Fore.RESET)

    elif command == "Move_within_file":
        readFromFile(True)
        print("\nEnter the line number to move: ")
        source = int(input())
        print("\nEnter the line number to move to: ")
        target = int(input())
        moveWithinFile(source, target)
    elif command == "Truncate_file":
        print("\nEnter the size to truncate the file to: ")
        size = int(input())
        truncateFile(size)
    elif command == "Exit":
        global memory
        print(c.Fore.GREEN+"\nExiting the File System!"+c.Fore.RESET)
        # save root in pickle
        ls = [root, Memory]
        pickle.dump(ls, open("data.pickle", "wb"))
        exit()
    else:
        print(c.Fore.RED+"\nInvalid Command"+c.Fore.RESET)

# function to print the file system menu
def Menu(currDir):
    global currWorkingDir
    currWorkingDir = currDir
    print(c.Fore.BLUE+"\n\tWelcome to the File System\n"+c.Fore.RESET)
    print("--> Create File")
    print("--> Delete File")
    print("--> Make Directory")
    print("--> Change Directory")
    print("--> Move File")
    print("--> Open File")
    print("--> Close File")
    print("--> Write_to_file")
    print("--> Read_from_file")
    print("--> Move_within_file")
    print("--> Truncate_file")
    print("--> Show memory map")
    print("--> Go to Root")
    print("--> Exit")
    print("\nEnter the command: \t", end='')
    print(c.Fore.MAGENTA + "("+getPathOfCWD(root,
          currWorkingDir.name) + ")" + c.Style.RESET_ALL)
    command = input()
    if (command == "Go to Root"):
        print(c.Fore.GREEN+"\nThe directory has been changed to: Root" + c.Fore.RESET)
        Menu(root)
    elif (command == "Show memory map"):
        printTree(root, 0)
        used = findSizeOfFiles(root)
        printProgressBar(100-used, "Available Space")
        Menu(currWorkingDir)
    else:
        processCommand(command)
        Menu(currWorkingDir)

"""
this is the main function where the file system starts
"""

if __name__ == "__main__":
    # loading the root from pickle and the global memory
    try:
        ls = pickle.load(open("data.pickle", "rb"))
        Memory = ls[1]
        root = ls[0]
        Menu(root)
    # perform file operations
    except:
        rootDir = Directory("root")
        root = rootDir
        currWorkingDir = rootDir
        Menu(rootDir)


 