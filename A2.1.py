def encryptFile(shift1, shift2):
    inputFile = open("raw_text.txt", "r")
    outputFile = open("encrypted_text.txt", "w")

    for line in inputFile:
        encryptedLine = ""

        for ch in line:
            if 'a' <= ch <= 'z':
                if ch <= 'm':
                    newPos = ord(ch) + (shift1 * shift2)
                else:
                    newPos = ord(ch) - (shift1 + shift2)

                while newPos > ord('z'):
                    newPos -= 26
                while newPos < ord('a'):
                    newPos += 26

                encryptedLine += chr(newPos)

            elif 'A' <= ch <= 'Z':
                if ch <= 'M':
                    newPos = ord(ch) - shift1
                else:
                    newPos = ord(ch) + (shift2 * shift2)

                while newPos > ord('Z'):
                    newPos -= 26
                while newPos < ord('A'):
                    newPos += 26

                encryptedLine += chr(newPos)

            else:
                encryptedLine += ch

        outputFile.write(encryptedLine)

    inputFile.close()
    outputFile.close()


def decryptFile(shift1, shift2):
    inputFile = open("encrypted_text.txt", "r")
    outputFile = open("decrypted_text.txt", "w")

    for line in inputFile:
        decryptedLine = ""

        for ch in line:
            decryptedLine += ch  # placeholder logic

        outputFile.write(decryptedLine)

    inputFile.close()
    outputFile.close()


shift1 = int(input("Enter shift1 value: "))
shift2 = int(input("Enter shift2 value: "))

encryptFile(shift1, shift2)
decryptFile(shift1, shift2)
