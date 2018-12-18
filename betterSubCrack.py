#!/usr/bin/env python3
#Nathan Becker
#CS3600
#Assignment1
#Substitution Cracker

from collections import Counter
import sys, os, re, time, pprint

#Start recording execution time of program
start_time=time.time()

#Take input from command line arguments, first is input file, second is output file
inputFile = 'encrypted_book.txt' #sys.argv[1] 
outputFile = 'cracked_book.txt' #sys.argv[2]

#Global Variables used to decipher the encrypted book
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ .'
JUSTLETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LETTERFREQORDER = 'ETAOIRNSHLCDUFPMBGYWVXKQJZ'

#This is used to create a word mapping file to be used by other functions
def makeWordPatternsMain():  
    print("Generating Word Pattern File...")
    allPatterns = {}
    #Open dictionary and get all the words in a list
    fo = open('dictionary.txt')
    wordList = fo.read().split('\n')
    fo.close()
    #Make a pattern for every word in the dictionary
    for word in wordList:
        pattern = getWordPattern(word)
        if pattern not in allPatterns:
            allPatterns[pattern] = [word]
        else:
            allPatterns[pattern].append(word)
    #Write all of the patterns into a file for future use in program        
    fo = open('myPatterns.py', 'w')
    fo.write('allPatterns = ')
    fo.write(pprint.pformat(allPatterns))
    fo.close()   

#Create the word pattern for a string of characters
def getWordPattern(word):
    upperCaseWord = word.upper()
    nextNum = -1
    numsList = {}
    pattern = []

    for letter in upperCaseWord:
        if letter not in numsList:
            nextNum += 1
            numsList[letter] = str(nextNum)
        pattern.append(numsList[letter])
    return '.'.join(pattern)

#Create a file to store the wordPatterns of all in the dictionary if it 
#doesn't exist already in the current folder
if not os.path.exists('myPatterns.py'):
    makeWordPatternsMain()
import myPatterns    

def main():        
    BOOKSJUSTLETTERS = ''
    BOOKSLETTERFREQORDER = ''   
    print("Reading encrypted book contents...")
    #Get all the items in the encrypted book.
    bookReader = open(inputFile, 'r')
    bookText = bookReader.read().strip()
    bookReader.close()
    
    print("Finding letter frequency of encrypted book...")
    #Find the letter frequency of the encrypted book
    bookTextUppercase = bookText.upper()   
    letterFrequency = Counter(letter for letter in bookTextUppercase if letter in LETTERS)   
    for letter in letterFrequency.most_common():
        BOOKSLETTERFREQORDER += letter[0]
        
    bookWithSpaces = ''
    print("Decrypting spaces in encrypted book...")
    #Correct highest freq letter in book to a space. Replace spaces with the subtituted letter.
    for character in bookText:
        if character.upper() == BOOKSLETTERFREQORDER[0]:
            bookWithSpaces += ' '
        elif character == ' ':
            #This replaces the wrong spaces with the substituted symbol
            bookWithSpaces += BOOKSLETTERFREQORDER[0].lower()
        else:
            #Just put the character back if not in our LETTERS
            bookWithSpaces += character           
    
    print("Finding most common setence terminator character...")
    #Make a list of most common ending letter(These are periods)
    sentencesWithSpaces = bookWithSpaces.split("\n\n");
    lastLetterList = "" 
    for sentence in sentencesWithSpaces:
        if sentence != '':
            lastLetterList = lastLetterList + sentence[-1]
            
    #Find all of the ending sentence chars (the periods)            
    mostFreqLastChars = Counter(lastLetterList)      
    mostFreqEndChar = mostFreqLastChars.most_common()[0][0]
   
    print("Decrypting periods in encrypted book...")
    bookWithSpacesAndPeriods = ''
    #Place the period correctly in book text
    for character in bookWithSpaces:
        if character == mostFreqEndChar:
            bookWithSpacesAndPeriods += '.'
        elif character == '.':
            bookWithSpacesAndPeriods += mostFreqEndChar
        else:
            bookWithSpacesAndPeriods += character
    
    print("Finding most frequent alpha characters...")     
    #Find the most frequent alpha characters now that periods and spaces are found    
    justLetterFrequency = Counter(letter for letter in bookWithSpacesAndPeriods.upper() if letter in JUSTLETTERS)
    for letter in justLetterFrequency.most_common():
        BOOKSJUSTLETTERS += letter[0]
    
    #Get a smaller set of words to use for decrypting, this will increase program speed and accuracy.
    print("Pulling sample of words from encrypted book text...")
    smallerSubsetOfWords = re.compile('\w{8,100}\w').findall(bookWithSpacesAndPeriods)
    
    #Put all of the words into a string to send to decrypter
    messageString = ''
    for word in smallerSubsetOfWords:
        messageString += word + ' '
    
    print("Finding and generating word patterns in words subset...")
    #Use simple sub hacker algorithm to decode the remaining letters, (this function inspired from online book example)
    letterMapping = getDecodingMap(messageString) 
    
    print("Generating key to decrypt the encrypted book...")
    decodingKey = ['~'] * len(JUSTLETTERS)
    for encodedChar in JUSTLETTERS:
        if len(letterMapping[encodedChar]) == 1:
            keyIndex = JUSTLETTERS.find(letterMapping[encodedChar][0])
            decodingKey[keyIndex] = encodedChar
    decodingKey = ''.join(decodingKey)
    
    crackedText = ''
    #Use the key to hack the book text
    print("Using key to decrypt the encrypted book...")
    for alphaChar in bookWithSpacesAndPeriods:
        if alphaChar.upper() in decodingKey:
            charPosition = decodingKey.find(alphaChar.upper())
            if alphaChar.isupper():
                crackedText += JUSTLETTERS[charPosition].upper()
            else:
                crackedText += JUSTLETTERS[charPosition].lower()
        else:
            crackedText += alphaChar  
            
    #Get list of dictionary words to check english percentage
    with open('dictionary.txt') as dictionary:
        wordList = dictionary.read().splitlines()

    #Check the english percentage of the longer words to get and idea
    #Of how accurate this key is
    print('Checking percentage of english...')
    numEnglishWords = 0
    wordsInCrackedText = re.compile('\w{10,100}\w').findall(crackedText)
    for word in wordsInCrackedText:
        if word.isalpha():
            if word.upper() in wordList:
                numEnglishWords = numEnglishWords + 1
    percentageOfEnglishInFirstSentence = (numEnglishWords / len(wordsInCrackedText)) * 100
    
    #Convert to the correct upper/lowercase
    
    crackedChars = list(crackedText)
    encryptedChars = list(bookText)
    
    print(len(crackedChars))
    print(len(encryptedChars))
    
    pairedLetters = list(zip(crackedChars, encryptedChars))
    
    
    fixedCrackedText = ''
    
    for crackedChar, encryptedChar in pairedLetters:
        if encryptedChar.isalpha():
            if encryptedChar.isupper():
                fixedCrackedText += crackedChar.upper()
            elif encryptedChar.islower():
                fixedCrackedText += crackedChar.lower()   
        else:
            fixedCrackedText += crackedChar
          
    crackedText = fixedCrackedText    
    
    #Write the book into an output file that was passed when executing this file as an argument.
    print("Writing decrytped book to output file...")        
    bookWriter = open(outputFile, 'w')
    bookWriter.write(crackedText)
    bookWriter.close()     
    print(f"Percentage of English Words Detected: {percentageOfEnglishInFirstSentence}%")
    #Print the final execution time
    print("Time to crack book: %s seconds" % (time.time() - start_time))

#Blank mapping for checking potential substitutions    
def getBlankMap():
    return {'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': [], 'G': [],
            'H': [], 'I': [], 'J': [], 'K': [], 'L': [], 'M': [], 'N': [],
            'O': [], 'P': [], 'Q': [], 'R': [], 'S': [], 'T': [], 'U': [],
            'V': [], 'W': [], 'X': [], 'Y': [], 'Z': []}

#create a mapping from a message encoded with a substitution cipher (This function was inspired from online book example) 
def getDecodingMap(textToHack):
    similarityMap = getBlankMap()
    #Use Regex to split the message into words without spaces
    encodedWords = re.compile('[^A-Z\s]').sub('', textToHack.upper()).split()
    #Go through all the encoded words and make a blank map for them
    for encodedWord in encodedWords:
        potentialWordMap = getBlankMap()
        #Make a word pattern and see if it exists in our long list of 
        #encoded words from the dictionary
        #Skip if we can't identify it.
        wordPattern = getWordPattern(encodedWord)
        if wordPattern not in myPatterns.allPatterns:
            continue
        #If pattern is matched, we can add it's letters to our mapping
        for candidate in myPatterns.allPatterns[wordPattern]:
            for i in range(len(encodedWord)):
                if candidate[i] not in potentialWordMap[encodedWord[i]]:
                    potentialWordMap[encodedWord[i]].append(candidate[i])
        #Figure out which letters should be in the decoding map            
        mapToFill = getBlankMap()
        for letter in JUSTLETTERS:
            if similarityMap[letter] == []:
                mapToFill[letter] = potentialWordMap[letter]
            elif potentialWordMap[letter] == []:
                mapToFill[letter] = similarityMap[letter]
            else:
                for mappedLetter in similarityMap[letter]:
                    if mappedLetter in potentialWordMap[letter]:
                        mapToFill[letter].append(mappedLetter)
        similarityMap = mapToFill
        
    reLoop = True
    while reLoop:
        reLoop = False
        correctLetters = []
        for cipherletter in JUSTLETTERS:
            if len(similarityMap[cipherletter]) == 1:
                correctLetters.append(similarityMap[cipherletter][0])
        #Determine if we need to do another itteration
        for cipherletter in JUSTLETTERS:
            for s in correctLetters:
                if len(similarityMap[cipherletter]) != 1 and s in similarityMap[cipherletter]:
                    similarityMap[cipherletter].remove(s)
                    if len(similarityMap[cipherletter]) == 1:
                        reLoop = True
    return similarityMap

#Tell the program where it needs to start
if __name__ == '__main__':
    main()