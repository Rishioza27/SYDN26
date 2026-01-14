def encryptFile(shift1, shift2):
    try:
        inputFile = open("raw_text.txt", "r")
    except:
        print("raw_text.txt file not found.")
        return

    outputFile = open("encrypted_text.txt", "w")

    for line in inputFile:
        encryptedLine = ""

        for ch in line:

            # lowercase letters
            if 'a' <= ch <= 'z':
                if ch <= 'm':      # rule 1
                    newPos = ord(ch) + (shift1 * shift2)
                    rule = "1"
                else:              # rule 2
                    newPos = ord(ch) - (shift1 + shift2)
                    rule = "2"

                while newPos > ord('z'):
                    newPos -= 26
                while newPos < ord('a'):
                    newPos += 26

                encryptedLine += rule + chr(newPos)

            # uppercase letters
            elif 'A' <= ch <= 'Z':
                if ch <= 'M':      # rule 3
                    newPos = ord(ch) - shift1
                    rule = "3"
                else:              # rule 4
                    newPos = ord(ch) + (shift2 * shift2)
                    rule = "4"

                while newPos > ord('Z'):
                    newPos -= 26
                while newPos < ord('A'):
                    newPos += 26

                encryptedLine += rule + chr(newPos)

            else:
                encryptedLine += ch

        outputFile.write(encryptedLine)

    inputFile.close()
    outputFile.close()


def decryptFile(shift1, shift2):
    try:
        inputFile = open("encrypted_text.txt", "r")
    except:
        print("encrypted_text.txt file not found.")
        return

    outputFile = open("decrypted_text.txt", "w")

    for line in inputFile:
        decryptedLine = ""
        i = 0

        while i < len(line):
            ch = line[i]

            if ch in "1234":

                # basic safety check
                if i + 1 >= len(line):
                    print("Encrypted file format error.")
                    return

                letter = line[i + 1]

                if ch == "1":
                    orig = ord(letter) - (shift1 * shift2)
                    while orig < ord('a'):
                        orig += 26
                    decryptedLine += chr(orig)

                elif ch == "2":
                    orig = ord(letter) + (shift1 + shift2)
                    while orig > ord('z'):
                        orig -= 26
                    decryptedLine += chr(orig)

                elif ch == "3":
                    orig = ord(letter) + shift1
                    while orig > ord('Z'):
                        orig -= 26
                    decryptedLine += chr(orig)

                elif ch == "4":
                    orig = ord(letter) - (shift2 * shift2)
                    while orig < ord('A'):
                        orig += 26
                    decryptedLine += chr(orig)

                i += 2
            else:
                decryptedLine += ch
                i += 1

        outputFile.write(decryptedLine)

    inputFile.close()
    outputFile.close()

# Verification function
def verifyDecryption():
    file1 = open("raw_text.txt", "r")
    file2 = open("decrypted_text.txt", "r")

    originalText = file1.read()
    decryptedText = file2.read()

    file1.close()
    file2.close()

    if originalText == decryptedText:
        print("Decryption successful. Files match.")
    else:
        print("Decryption failed. Files do not match.")

shift1Input = input("Enter shift1 value: ")
shift2Input = input("Enter shift2 value: ")

if not shift1Input.isdigit() or not shift2Input.isdigit():
    print("Shift values must be whole numbers.")
else:
    shift1 = int(shift1Input)
    shift2 = int(shift2Input)

    if shift1 <= 0 or shift2 <= 0:
        print("Shift values must be positive.")
    else:
        encryptFile(shift1, shift2)
        decryptFile(shift1, shift2)
        verifyDecryption()
