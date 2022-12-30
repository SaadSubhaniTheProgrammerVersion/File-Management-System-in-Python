"""
these are the libraries used in the code
"""

# to save the file system root to a file
import os
import sys
import pickle
import socket
from _thread import *
import colorama as c

"""
    these are the global variables for the file system
"""
# current working objects of file and directory
MEMORYMAP = ""
root = None
SPACE = '    '
BRANCH = '|   '
LAST = '|___'
BLOCKSIZE = 50
# Global Memory for storing the data
Memory = [None] * 100
users = []
openFiles = {}

Menu = c.Fore.BLUE+"\n\tWelcome to the File System\n"+c.Fore.RESET+"\n--> Create File"+"\n--> Delete File"+"\n--> Make Directory"+"\n--> Change Directory"+"\n--> Move File"+"\n--> Open File" + "\n--> Close File"+"\n--> Write_to_file"+"\n--> Read_from_file"+"\n--> Move_within_file" + \
    "\n--> Truncate_file"+"\n--> Show memory map" + \
    "\n--> Go to Root"+"\n--> Exit"+"\n\nEnter the command: \t"

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
        self.size = 0

    # write to file
    def write(self, inode):
        global Memory
        self.Inodes = self.Inodes+inode
        self.size = 0
        for index in self.Inodes:
            self.size += len(Memory[index])


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
            return c.Fore.RED+"File already exists"+c.Fore.RESET
        else:
            self.files[file.name] = file
            return c.Fore.GREEN+"File created successfully"+c.Fore.RESET

    # Add subdirectory to directory

    def addSubdirectory(self, directory):
        if (directory.name in self.subdirectories.keys()):
            return c.Fore.RED+"Directory already exists" + c.Fore.RESET

        else:
            self.subdirectories[directory.name] = directory
            return (c.Fore.GREEN+"Directory created successfully"+c.Fore.RESET)


"""
These are the major functions for all the commands in the file system
"""
# function to print the file system tree using SPACE , BRANCH , LAST


def printTree(dir, level, currWorkingDir):
    global MEMORYMAP
    if (dir == None):
        return
    if (level == 0):
        MEMORYMAP += (c.Fore.BLUE+dir.name+"\n"+c.Fore.RESET)
    else:
        MEMORYMAP += (c.Fore.CYAN+SPACE *
                      (level - 1) + BRANCH + c.Fore.RESET+c.Fore.GREEN + dir.name+c.Fore.RESET)
        if (currWorkingDir == dir):
            MEMORYMAP += (c.Fore.MAGENTA+" <----"+c.Fore.RESET) + "\n"
        else:
            MEMORYMAP += "\n"

    for file in dir.files.keys():
        MEMORYMAP += (c.Fore.CYAN+SPACE * level + LAST+c.Fore.RESET) + c.Fore.YELLOW+dir.files[file].name + c.Fore.RESET + "\t" + str(
            dir.files[file].size) + " Bytes\t" + c.Fore.RED+"BLOCKS " + str(dir.files[file].Inodes) + c.Fore.RESET+"\n"

    for directory in dir.subdirectories.keys():
        printTree(dir.subdirectories[directory], level + 1, currWorkingDir)

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
def createFile(fName, currWorkingDir):
    if (fName == None or fName == ""):
        return c.Fore.RED+"File name can not be empty"+c.Fore.RESET
    if (currWorkingDir == None):
        return c.Fore.RED+"No directory is selected"+c.Fore.RESET
    file = File(fName)
    return currWorkingDir.addFile(file)


# function to create directory
def createDirectory(dirName, currWorkingDir):
    global root
    if (findDirectory(root, dirName) != None):
        return c.Fore.RED+"Directory with this name already exists"+c.Fore.RESET

    if (dirName == currWorkingDir.name):
        return c.Fore.RED+"Directory with this name already exists"+c.Fore.RESET
    if (dirName == None or dirName == ""):

        return c.Fore.RED+"Directory name can not be empty"+c.Fore.RESET
    if (currWorkingDir == None):

        return c.Fore.RED+"No directory is selected"+c.Fore.RESET
    directory = Directory(dirName)
    return currWorkingDir.addSubdirectory(directory)


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


def moveFile(fileName, dirName):
    global currWorkingDir, root
    if currWorkingDir == None:
        return c.Fore.RED+"No directory is selected"+c.Fore.RESET
    if fileName not in currWorkingDir.files.keys():
        return c.Fore.RED+"File not found"+c.Fore.RESET
    resDir = findDirectory(root, dirName)
    if resDir == None:
        return c.Fore.RED+"Directory not found"+c.Fore.RESET
    file = currWorkingDir.files[fileName]
    resDir.addFile(file)
    del currWorkingDir.files[fileName]
    return c.Fore.GREEN+"File " + fileName+" moved successfully"+c.Fore.RESET

# delete file from the directory


def deleteFile(fileName):
    global currWorkingDir
    if currWorkingDir == None:
        return c.Fore.RED+"No directory is selected"+c.Fore.RESET
    if fileName not in currWorkingDir.files.keys():
        return c.Fore.RED+"File not found"+c.Fore.RESET
    # get the file
    file = currWorkingDir.files[fileName]
    for inode in file.Inodes:
        # delete the file from the disk
        del Memory[inode]
    # delete the file from the directory
    del currWorkingDir.files[fileName]
    return c.Fore.GREEN+"File deleted successfully"

# function to open file using filename


def openFile(fileName, currWorkingDir, mode, currWorkingFile, FileOpenMode):
    global openFiles
    if fileName not in currWorkingDir.files.keys():
        return c.Fore.RED+"File not found"+c.Fore.RESET
    if currWorkingFile != None and currWorkingFile.name != fileName:
        return c.Fore.RED+"You have Another File "+currWorkingFile.name + " already opened!"+c.Fore.RESET, currWorkingFile, FileOpenMode
    if fileName in openFiles.keys() and openFiles[fileName][1] == 'w' and openFiles[fileName][0] == currWorkingDir.name:
        return c.Fore.RED+"File "+fileName + " already opened for writing! \nPlease wait for writer to close file"+c.Fore.RESET, currWorkingFile, FileOpenMode
    if fileName in openFiles.keys() and openFiles[fileName][1] == 'r' and openFiles[fileName][0] == currWorkingDir.name and mode == 'w':
        return c.Fore.RED+"File "+fileName + " already opened for reading!\n Please wait for reader to close the file"+c.Fore.RESET, currWorkingFile, FileOpenMode
    if fileName in openFiles.keys() and openFiles[fileName][1] == 'w' and openFiles[fileName][0] == currWorkingDir.name and mode == 'r':
        return c.Fore.RED+"File "+fileName + " already opened for writing!\n Please wait for writer to close the file"+c.Fore.RESET, currWorkingFile, FileOpenMode
    if fileName in openFiles.keys() and openFiles[fileName][1] == 'r' and openFiles[fileName][0] == currWorkingDir.name:
        currWorkingFile = currWorkingDir.files[fileName]
        FileOpenMode = 'r'
        return c.Fore.GREEN+"File "+fileName + " opened for reading!"+c.Fore.RESET, currWorkingFile, FileOpenMode
    if fileName in openFiles.keys() and openFiles[fileName][1] == 'w' and openFiles[fileName][0] != currWorkingDir.name:
        if mode == "":
            return c.Fore.RED+"Enter a valid mode to open the file"+c.Fore.RESET
        if currWorkingDir == None:
            return c.Fore.RED+"No directory is selected"+c.Fore.RESET
        if fileName not in currWorkingDir.files.keys():
            return c.Fore.RED+"File not found"+c.Fore.RESET
        currWorkingFile = currWorkingDir.files[fileName]
        openFiles[fileName] = [currWorkingDir.name, mode]
        return c.Fore.GREEN+"File "+currWorkingFile.name+" opened successfully for writing"+c.Fore.RESET, currWorkingFile, mode
    if fileName in openFiles.keys() and openFiles[fileName][1] == 'r' and openFiles[fileName][0] != currWorkingDir.name:
        if mode == "":
            return c.Fore.RED+"Enter a valid mode to open the file"+c.Fore.RESET
        if currWorkingDir == None:
            return c.Fore.RED+"No directory is selected"+c.Fore.RESET
        if fileName not in currWorkingDir.files.keys():
            return c.Fore.RED+"File not found"+c.Fore.RESET
        currWorkingFile = currWorkingDir.files[fileName]
        FileOpenMode = mode
        openFiles[fileName] = [currWorkingDir.name, mode]
        return c.Fore.GREEN+"File "+currWorkingFile.name+" opened successfully for reading"+c.Fore.RESET, currWorkingFile, mode
    if mode == "":
        return c.Fore.RED+"Enter a valid mode to open the file"+c.Fore.RESET
    if currWorkingDir == None:
        return c.Fore.RED+"No directory is selected"+c.Fore.RESET
    if fileName not in currWorkingDir.files.keys():
        return c.Fore.RED+"File not found"+c.Fore.RESET
    currWorkingFile = currWorkingDir.files[fileName]
    FileOpenMode = mode
    openFiles[fileName] = [currWorkingDir.name, mode]
    text = (c.Fore.GREEN+"File "+currWorkingFile.name +
            " opened successfully"+c.Fore.RESET)
    return text, currWorkingFile, FileOpenMode

# function to close opened file


def closeFile(currWorkingFile):
    global openFiles
    if currWorkingFile == None:
        return c.Fore.RED+"No file is opened"+c.Fore.RESET
    if currWorkingFile.name in openFiles.keys():
        del openFiles[currWorkingFile.name]
    name = currWorkingFile.name
    currWorkingFile = None
    mode = ""
    return c.Fore.GREEN+"File " + name + " closed successfully"+c.Fore.RESET, currWorkingFile, mode

# function to store data in memory


def writeToGlobalMemory(line):
    global Memory
    indices = []
    size = len(line)
    for i in range(0, len(Memory)):
        if Memory[i] == None:
            Memory[i] = line[:BLOCKSIZE]
            indices.append(i)
            if size > BLOCKSIZE:
                line = line[BLOCKSIZE:]
                size = size-BLOCKSIZE
                continue
            return indices
    return -1

# function to write text to file


def writeToFile(mode, currWorkingFile, FileOpenMode, data=None, lineNo=None):
    if currWorkingFile == None:
        return c.Fore.RED+"No file is opened"+c.Fore.RESET
    if FileOpenMode == "r":
        return c.Fore.RED+"The file is open in read-only mode!\n Please wait until the file is closed by readers"+c.Fore.RESET
    if mode == "append":
        if data == None or data == "":
            return c.Fore.RED+"Data can not be empty"+c.Fore.RESET
        Indices = writeToGlobalMemory(data)
        if Indices == -1:
            return c.Fore.RED+"Memory is full"+c.Fore.RESET
        currWorkingFile.write(Indices)
        return c.Fore.GREEN+"Data written successfully"+c.Fore.RESET
    elif mode == "write_at":
        if lineNo > len(currWorkingFile.Inodes):
            return c.Fore.RED+"Line number out of range"+c.Fore.RESET
        i = 0
        x = lineNo-1
        flag = True
        Index = currWorkingFile.Inodes[lineNo-1]
        Memory[Index] = None
        for i in range(0, len(Memory)):
            if Memory[i] == None:
                Memory[i] = data[:BLOCKSIZE]
                data = data[BLOCKSIZE:]
                if flag:
                    currWorkingFile.Inodes.pop(x)
                    flag = False
                currWorkingFile.Inodes.insert(x, i)
                if data == "":
                    currWorkingFile.size = 0
                    for index in currWorkingFile.Inodes:
                        currWorkingFile.size += len(Memory[index])
                    return c.Fore.GREEN+"Data written successfully"+c.Fore.RESET
                x += 1
                i += 1
    else:
        return c.Fore.RED+"Invalid command"+c.Fore.RESET

# function to read text from file at start and till specified characters


def readFrom(start, size, currWorkingFile, FileOpenMode):
    if currWorkingFile == None:
        return c.Fore.RED+"No file is opened"+c.Fore.RESET
    if FileOpenMode == "w":
        return c.Fore.RED+"The file is open in write-only mode"+c.Fore.RESET
    if start > len(currWorkingFile.Inodes):
        return c.Fore.RED+"Line number out of range"+c.Fore.RESET
    data = ""
    for i in range(start-1, len(currWorkingFile.Inodes)):
        Index = currWorkingFile.Inodes[i]
        # get specific line from memory
        line = Memory[Index]
        # print line till size number of characters
        data += line[:size]+"\n"
        size = size - len(line)
        if size <= 0:
            break
    return data

# Read text from the file


def readFromFile(mode, currWorkingFile, FileOpenMode, start=None, size=None):
    data = ""
    if FileOpenMode == "w":
        return c.Fore.RED+"The file is open in write-only mode"+c.Fore.RESET
    if mode == True:
        if currWorkingFile == None:
            return c.Fore.RED+"No file is opened"+c.Fore.RESET
        # read file sequentially
        for i in range(0, len(currWorkingFile.Inodes)):
            address = currWorkingFile.Inodes[i]
            data += str(i+1) + "-> " + "".join(Memory[address]) + "\n"
        return data
    else:
        return readFrom(start, size, currWorkingFile, FileOpenMode)


# function to move text within the file
def moveWithinFile(s, t, currWorkingFile):
    if (currWorkingFile == None):
        return c.Fore.RED+"No file is opened"+c.Fore.RESET
    if (s > len(currWorkingFile.Inodes) or t > len(currWorkingFile.Inodes) or s < 1 or t < 1):
        return "Line number out of range"
    if (s == t):
        return c.Fore.RED+"Source and destination are same"+c.Fore.RESET
    # pop the line from source
    inode = currWorkingFile.Inodes[s-1]
    # store line at destination
    currWorkingFile.Inodes[t-1] = inode
    currWorkingFile.Inodes.pop(s-1)
    # updating the size of file
    currWorkingFile.size = 0
    for index in currWorkingFile.Inodes:
        currWorkingFile.size += len(Memory[index])
    return c.Fore.GREEN+"Text moved successfully"+c.Fore.RESET


def truncateFile(size, currWorkingFile):
    if (currWorkingFile == None):
        return c.Fore.RED+"No file is opened"+c.Fore.RESET
    if (size > currWorkingFile.size or size < 0):
        return c.Fore.RED+"Invalid size"+c.Fore.RESET

    if (size == 0):
        for index in currWorkingFile.Inodes:
            Memory[index] = None
        currWorkingFile.Inodes = []
        currWorkingFile.size = 0
        return c.Fore.GREEN+"File " + currWorkingFile.name+" truncated successfully"+c.Fore.RESET
    else:
        # calculate block numbers to be truncated
        blockNo = size//BLOCKSIZE
        if size % BLOCKSIZE != 0:
            blockNo += 1
        # truncate blocks
        for i in range(blockNo, len(currWorkingFile.Inodes)):
            Memory[currWorkingFile.Inodes[i]] = None
        currWorkingFile.Inodes = currWorkingFile.Inodes[:blockNo]
        # truncate characters
        data = Memory[currWorkingFile.Inodes[blockNo-1]]
        # subtract size from blocksize
        s = (size % BLOCKSIZE)
        Memory[currWorkingFile.Inodes[blockNo-1]] = data[:s]
        # update size of file
        currWorkingFile.size = 0
        for index in currWorkingFile.Inodes:
            currWorkingFile.size += len(Memory[index])
        return c.Fore.GREEN+"File " + currWorkingFile.name+" truncated successfully"+c.Fore.RESET


#  function to find size of all files in the directory
def findSizeOfFiles(root):
    global Memory
    if (root == None):
        return 0
    size = 0
    for i in root.files.keys():
        for index in root.files[i].Inodes:
            size += len(Memory[index])
    for i in root.subdirectories.keys():
        size += findSizeOfFiles(root.subdirectories[i])
    return size


"""
 these functions are responsible for running the complete file system
 these functions get the user input for the commands and call the respective functions
"""

# function to execute the thread files and commands


def execute(line, currWorkingDir, currWorkingFile, FileOpenMode):
    global root, Memory, MEMORYMAP
    res = ""
    line = line.lower()
    # iterate over the lines
    line = line.split()
    if "write_to_file" in line and "write_at" in line:
        data = line[3:]
        # join data without spaces
        data = " ".join(data)
        lineNo = int(line[2])
        res = "Write to file (lineNo,data): "+str(lineNo)+" --> "
        res += writeToFile("write_at", currWorkingFile,
                           FileOpenMode, data, lineNo)
    elif "write_to_file" in line:
        data = line[2:]
        data = " ".join(data)
        res = "Write to file (data): --> "
        res += writeToFile("append", currWorkingFile, FileOpenMode, data, None)
    elif len(line) == 2:
        command, arg = line
        if command == "create_file":
            res = createFile(arg, currWorkingDir)
        elif command == "delete_file":
            res = deleteFile(arg)
        elif command == "make_directory":
            res = createDirectory(arg, currWorkingDir)
        elif command == "change_directory":
            resDir = findDirectory(root, arg)
            if resDir == None:
                res = c.Fore.RED+"Directory not found\n"+c.Fore.RESET
            else:
                currWorkingDir = resDir
                res = c.Fore.GREEN+"The directory has been changed to: " + arg+"\n"+c.Fore.RESET
        elif command == "truncate_file":
            res = truncateFile(int(arg), currWorkingFile)
        elif command == "read_from_file":
            res = c.Fore.GREEN+"Read from file Sequentially --> \n"+c. Fore.RESET
            res += readFromFile(True, currWorkingFile,
                                FileOpenMode, None, None)
        else:
            res = c.Fore.RED+"Invalid command\n"+c.Fore.RESET
    elif len(line) == 1:
        command = line[0]
        if command == "close_file":
            res, currWorkingFile, FileOpenMode = closeFile(currWorkingFile)
        elif command == "show_memory_map":
            res = "Memory Map:\n"
            printTree(root, 0, currWorkingDir)
            if MEMORYMAP != "":
                res = MEMORYMAP+"\n"
                MEMORYMAP = ""
        elif command == "go_to_root":
            currWorkingDir = root
            res = c.Fore.GREEN+"The directory has been changed to: root\n"+c.Fore.RESET
        else:
            res = c.Fore.RED+"Invalid command\n" + c.Fore.RESET
    elif len(line) == 3:
        command, arg1, arg2 = line
        if command == "move_file":
            res = moveFile(arg1, arg2)
        elif command == "read_from":
            res = "Read from file (start,size): "+arg1+" "+arg2+" --> "
            res += readFromFile(False, currWorkingFile,
                                FileOpenMode, int(arg1), int(arg2))
        elif command == "move_within_file":
            res = "Move within file (source,target): " + \
                arg1+" "+arg2+" --> "
            res += moveWithinFile(int(arg1), int(arg2), currWorkingFile)
        elif command == "open_file":
            if arg1 not in currWorkingDir.files.keys():
                res = c.Fore.RED+"File not found\n" + c.Fore.RESET
                return res, currWorkingDir, currWorkingFile, FileOpenMode
            # call open file function
            res, currWorkingFile, FileOpenMode = openFile(
                arg1, currWorkingDir, arg2, currWorkingFile, FileOpenMode)
        else:
            res = c.Fore.RED+"Invalid command\n" + c.Fore.RESET
    else:
        res = c.Fore.RED+"Invalid command\n" + c.Fore.RESET
    return res, currWorkingDir, currWorkingFile, FileOpenMode


def multi_threaded_client(connection):
    global root, Menu, openFiles
    connection.send(str.encode(
        'Please enter your name: '))
    name = connection.recv(2048)
    name = name.decode('utf-8')
    users.append(name)
    print(f'User {name} has connected!')
    print(users)
    currentWorkingDir = root
    currentWorkingFile = None
    OpenFileMode = None
    connection.send(str.encode(
        c.Fore.GREEN+"You have joined the Server Successfully"+c.Fore.RESET+Menu))
    while True:
        data = connection.recv(2048)
        data = data.decode('utf-8')
        response, currentWorkingDir, currentWorkingFile, OpenFileMode = execute(
            data, currentWorkingDir, currentWorkingFile, OpenFileMode)
        if not data or data == "Exit" or data == "exit":
            print(name + ' disconnected!')
            users.remove(name)
            print("\nCurrent Users in the File System: ", users)
            # dump the memory and root to pickle
            with open("data.pickle", "wb") as f:
                pickle.dump([root, Memory], f)
            break
        print(openFiles)
        connection.sendall(str.encode(
            response+Menu+c.Fore.MAGENTA+getPathOfCWD(root, currentWorkingDir.name)+c.Fore.RESET+"\n"))
    connection.close()


"""
this is the main function where the file system starts
"""

if __name__ == "__main__":

    # loading the root from pickle and the global memory
    try:
        ls = pickle.load(open("data.pickle", "rb"))
        Memory = ls[1]
        root = ls[0]
        currWorkingDir = root
    # perform file operations
    except:
        rootDir = Directory("root")
        root = rootDir
        currWorkingDir = rootDir

    ServerSideSocket = socket.socket()
    host = '127.0.0.1'
    port = 2004
    ThreadCount = 0
    try:
        ServerSideSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print('Socket is listening..')
    ServerSideSocket.listen(5)

    while True:
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(multi_threaded_client, (Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    ServerSideSocket.close()
