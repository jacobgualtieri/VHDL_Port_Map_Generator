"""
VHDL Port Map Generator
Author: Jacob Gualtieri
Date: 7/11/2020
For use with Python3
"""

"""
Reads the module entity from the specified file.
This data is separated into three categories: Name, Generic, and Port.
"""
def generateEntity(filename):
    foundGenerics = False
    foundPort = False
    moduleName = "null"
    generics = ""
    port = ""

    with open(filename) as fr:                  # Open the VHDL file for reading and automatically close it
        rdln = fr.readline().lower()            # Read in a lowercase line from the VHDL file

        while "entity " + moduleName + " is" not in rdln:   # Read lines until the module entity is declared
            rdln = fr.readline().lower()
            if rdln.startswith("entity"):
                moduleName = rdln.split()[1]                # Save the module name for later use
            
        while "end entity;" not in rdln:        # Parse the entity for relevant information
            if rdln.startswith("    --") or rdln.startswith("  --") or rdln.startswith("--"):
                pass
            elif "generic" in rdln:
                foundGenerics = True
            elif "port" in rdln:
                foundPort = True
            elif foundGenerics:
                generics += rdln
            elif foundPort:
                port += rdln
            if rdln.endswith(");\n") and "std_logic_vector" not in rdln and foundGenerics:
                foundGenerics = False
            if rdln.endswith(");\n") and ("std_logic_vector" not in rdln) and foundPort:
                foundPort = False
            rdln = fr.readline().lower()        # Read the next line from the VHDL file
    return moduleName, generics, port


"""
Writes the formatted Generic Map and Port Map to a new plaintext file.
This text can then be used in any VHDL module or test bench.
Minor edits to the map declarations may be required; this depends on the user's project structure.
"""
def writePortmap(name, generics, ports):
    newFilename = name + "Portmap.txt"                      # Format the new filename and name of instantiation
    instanceDefinition = name + "_inst : " + name
    fw = open(newFilename, "w+")                            # Create and open a new plaintext file

    fw.write(instanceDefinition + "\n\tgeneric map(\n")     # Write the formatted Generic information to the file
    for param_idx in range(len(generics)):
        endString = ",\n"
        if param_idx == len(generics)-1:
            endString = ")\n"
        fw.write("\t\t" + generics[param_idx][0] + " => " + generics[param_idx][2].strip(';').strip(' = ') + endString)

    fw.write("\tport map(\n")                               # Write the formatted Port Map information to the file
    for port_idx in range(len(ports)):
        if len(ports[port_idx]) > 1:
            endString = ",\n"
            if port_idx == len(ports)-1:
                endString = ");\n"
            fw.write("\t\t" + ports[port_idx][0] + " => " + ports[port_idx][0].strip(';') + endString)
    fw.close()                  # Close the newly written file
    return None


if __name__ == "__main__":
    path = input("Enter path to file: ")
    filename = input("Enter filename: ")

    if not filename.endswith(".vhd"):
        print("Only VHDL files are supported")
    else:
        try:
            name, generics, ports = generateEntity(path + filename)
            if generics != "" and ports != "":
                params = generics.strip().split('\n')
                wires = ports.strip().split('\n')
                moduleParams = []
                modulePorts = []

                for idx1 in range(len(params)-1):               # Parse the info for each generic
                    params[idx1] = params[idx1].strip()
                    paramData = params[idx1].split(':')
                    for idx2 in range(len(paramData)-1):
                        paramData[idx2] = paramData[idx2].strip()
                    moduleParams.append(paramData)

                for idx1 in range(len(wires)-1):                # Parse the info for each port
                    wires[idx1] = wires[idx1].strip()
                    wireData = wires[idx1].split(':')
                    for idx2 in range(len(wireData)-1):
                        wireData[idx2] = wireData[idx2].strip()
                        wireData[idx2] = wireData[idx2].strip("")
                    modulePorts.append(wireData)

                writePortmap(name, moduleParams, modulePorts)

            else: print("ERR: Failed to parse entity information")

        except FileNotFoundError:
            print("ERR: No file found...")