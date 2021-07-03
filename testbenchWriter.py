
def remove_comments (filename, portStr):

    trimmedPort = ""
    splitStr = []

    if filename.endswith(".v"): splitStr = portStr.split("//")
    elif filename.endswith(".vhd"): splitStr = portStr.split("--")
    
    trimmedPort = splitStr[0].strip()
    if trimmedPort.endswith(','): trimmedPort = trimmedPort.strip(',')
    elif trimmedPort.endswith(';'): trimmedPort = trimmedPort.strip(';')
    return trimmedPort


def continueToToken (token, fp, line):
    while not (token in line.lower()):
        line = fp.readline().strip()
    return None


def saveToken (filename, tokenList, token):
    if token.endswith(','): token = token.strip(',')       # Clean ',' from the ends of ports (Verilog)
    elif token.endswith(';'): token = token.strip(';')     # Clean ';' from the ends of ports (VHDL)
        
    if ("--" in token) or ("//" in token):                # Check for comments after to a port declaration
        token = remove_comments(filename, token)          # Remove comment and trailing whitespace

    tokenList.append(token)
    return None


def readHDL (path, filename, paramList, portList, verbose):

    with open(path + filename, 'r') as hdl_file:

        line = hdl_file.readline().strip()

        # If Verilog
        if filename.endswith(".v"):                             # read Verilog file until the port declarations are found
            if verbose: print("\nParsing Verilog file...")
            continueToToken("module", hdl_file, line)
            line = hdl_file.readline().strip()

            while not (")(" in line):                           # Append the parameters to the paramList
                saveToken(filename, paramList, line)
                line = hdl_file.readline().strip()
            line = hdl_file.readline().strip()
        
        # If VHDL
        elif filename.endswith(".vhd"):                         # read VHDL file until the port declarations are found
            if verbose: print("\nParsing VHDL file...")
            continueToToken("generic", hdl_file, line)
            line = hdl_file.readline().strip()
        
            while not (");" in line):                           # Append the generics to the paramList
                saveToken(filename, paramList, line)
                line = hdl_file.readline().strip()

            continueToToken("port", hdl_file, line)
            line = hdl_file.readline().strip()

        # Append the ports to the portList
        while not (");" in line):
            saveToken(filename, portList, line)
            line = hdl_file.readline().strip()
        
        if verbose:
            print("Found", len(paramList), "parameters in", filename,end=":\n")
            for p in paramList:
                print('  ', p)
            print("Found", len(portList), "ports in", filename,end=":\n")
            for p in portList:
                print('  ', p)
            print("Finished parsing hdl file!",end="\n\n")
    return None


def writeVerilogfromVerilog(moduleName, paramList, portList):
        tb_file = open(moduleName + "_tb.v", "w")
        tb_file.write("/**\n * Automatically generated Verilog testbench\n */\n")

        tb_file.write("module " + moduleName + "_tb" + " ();\n\n")             # write testbench module name to file

        # Create localparams for each module parameter
        for param in paramList:
            temp = param.split()
            tb_file.write("localparam " + temp[1] + " = " + temp[3] + ";\n")
        tb_file.write('\n')

        # Create wires for each I/O port
        # *Note - Right now this only works for 1 bit signals, and assumes a 'wire' type
        for port in portList:
            temp = port.split()
            tb_file.write("wire " + temp[2] + ";" + "\t\t//" + temp[0].lower() + "\n")
        tb_file.write('\n')

        # Instantiate Unit Under Test - AKA uut
        tb_file.write("// Unit Under Test\n" + moduleName + " #(\n")
        for p in range(len(paramList)):
            temp = paramList[p].split()
            if p == len(paramList)-1:
                tb_file.write("\t." + temp[1] + "\t(" + temp[1] + ")\n")
            else:
                tb_file.write("\t." + temp[1] + "\t(" + temp[1] + "),\n")
        
        tb_file.write(") UUT (\n")

        for p in range(len(portList)):
            temp = portList[p].split()
            if p == len(portList)-1:
                tb_file.write("\t." + temp[2] + "\t(" + temp[2] + ")\n")
            else:
                tb_file.write("\t." + temp[2] + "\t(" + temp[2] + "),\n")
        tb_file.write(");\n")

        tb_file.close()             # close file when writes are done
        return None

def writeVHDLfromVHDL(moduleName, paramList, portList):
    tb_file = open(moduleName + "_tb.vhd", "w")
    tb_file.write("--\n-- Automatically generated VHDL testbench\n--\n")
    tb_file.write("library IEEE; use IEEE.std_logic_1164.all;\n-- use IEEE.numeric_std.all;\n\n")

    tb_file.write("entity " + moduleName + "_tb is\nend entity;\n\n")

    tb_file.write("architecture testbench of " + moduleName + "_tb is\n\n")

    for param in paramList:
        temp = param.split()
        tb_file.write("constant " + temp[0] + " : " + temp[2] + " := " + temp[4] + ";\n")
    tb_file.write("\n")

    for port in portList:
        temp = port.split()
        tb_file.write("signal " + temp[0] + " : " + temp[3] + ";\n")
    tb_file.write("\n")

    tb_file.write("component " + moduleName + " is\n")
    tb_file.write("\tgeneric (\n")
    for p in range(len(paramList)):
        if p == len(paramList)-1:
            tb_file.write("\t\t" + paramList[p] + "\n")
        else:
            tb_file.write("\t\t" + paramList[p] + ";\n")
    tb_file.write("\t);\n\tport (\n")
    for p in range(len(portList)):
        if p == len(portList)-1:
            tb_file.write("\t\t" + portList[p] + "\n")
        else:
            tb_file.write("\t\t" + portList[p] + ";\n")
    tb_file.write("\t);\nend component;\n\n")

    tb_file.write("begin\n\n")

    tb_file.write("-- Unit Under Test\n" + moduleName + " : UUT\n")
    tb_file.write("\tgeneric map (\n")
    for p in range(len(paramList)):
        temp = paramList[p].split()
        if p == len(paramList)-1:
            tb_file.write("\t\t" + temp[0] + " => " + temp[0] + "\n")
        else:
            tb_file.write("\t\t" + temp[0] + " => " + temp[0] + ",\n")

    tb_file.write("\t)\n\tport map (\n")
    for p in range(len(portList)):
        temp = portList[p].split()
        if p == len(portList)-1:
            tb_file.write("\t\t" + temp[0] + " => " + temp[0] + "\n")
        else:
            tb_file.write("\t\t" + temp[0] + " => " + temp[0] + ",\n")

    tb_file.write("\t);\n")

    tb_file.write("\nend architecture testbench;\n")
    tb_file.close()
    return None


def write_tb (path, filename, targetLang, paramList, portList, verbose):
    if not ((targetLang.lower() == "verilog") or (targetLang.lower() == "vhdl")):
        return None
    
    if verbose: print("Generating", targetLang, "testbench template for", filename)

    moduleName = filename.split('.')[0]             # parse module name from filename

    if targetLang.lower() == "verilog":
        if filename.endswith(".v"):
            writeVerilogfromVerilog(moduleName, paramList, portList)
    
    elif targetLang.lower() == "vhdl":
        if filename.endswith(".vhd"):
            writeVHDLfromVHDL(moduleName, paramList, portList)
    
    if verbose: print("Finished testbech generation!")
    #input("Press any key to exit...")
    return None


if __name__ == "__main__":
    path = "S:/hdl/VHDL_Course/BasicGates/"
    filename = "orGate2.v"
    verbose = False

    #tb_language = "VHDL"
    tb_language = "Verilog"
    portList = []                                   # empty list where port strings will be stored
    paramList = []                                  # empty list where parameters or generics will be stored

    readHDL(path, filename, paramList, portList, verbose)                   # stores list of port strings in portList
    write_tb(path, filename, tb_language, paramList, portList, verbose)     # uses the parsed data to write and format a testbench template