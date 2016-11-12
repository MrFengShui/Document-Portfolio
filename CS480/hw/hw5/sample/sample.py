import sys, re

first_set = {}

def readFile(fileName):
	text_file, txt = open(fileName, "r"), ''
	txt = ''.join(text_file.readlines())
	text_file.close()
	return txt

def splitString(strSplit):
	splitString = re.split('(\n| |,|==|<=|>=|=|;|<|>|\(|\)|\*|\|\||{|}|\[|\]|\||!=|!|/|-|\+|\xa1\xfa)', strSplit) 
	sep = " "
	splitString = sep.join(splitString)
	return splitString

def scanner(stream):
	splitStr = splitString(stream)
	splitSpace = splitStr.split()
	print splitSpace # the result of first part

def readCFG():
	print '+' * 50 + ' First LL(1) ' + '+' * 50
	strGram = readFile("testGrammer.txt")
	print strGram
	non_terminateStr = []
	terminateStr = []
	CFG_eachLine = []
	lastCFG_eachLine = []
	dictCFG = {}
	singleton = 1
	start_non_ter = ""

	strGram_allLine =  strGram.split('\n')

	for x_strGram_allLine in xrange(0, len(strGram_allLine)-1):
		strGram_allLine[x_strGram_allLine] = splitString(strGram_allLine[x_strGram_allLine])
		CFG_eachLine = strGram_allLine[x_strGram_allLine].split()

		if start_non_ter == "":
			start_non_ter = CFG_eachLine[0]

		terminateStr = [[]]

		for x_CFG_eachLine in xrange(1, len(CFG_eachLine)):	# put eachLine into terminate
			if CFG_eachLine[x_CFG_eachLine] == '\xa1\xfa':
				pass
			else:
				if CFG_eachLine[x_CFG_eachLine] == '|':
					terminateStr.append([])
				else:
					terminateStr[len(terminateStr)-1].append(CFG_eachLine[x_CFG_eachLine])

		if CFG_eachLine[0] == '|':
			lastCFG_eachLine = strGram_allLine[len(dictCFG.keys())-1].split()

			if singleton == 1:
				dictCFG[lastCFG_eachLine[0]] = dictCFG[lastCFG_eachLine[0]]
				singleton = 0

			dictCFG[lastCFG_eachLine[0]] += terminateStr
			dictCFG.update({lastCFG_eachLine[0]: dictCFG[lastCFG_eachLine[0]]})
		else:
			dictCFG.update({CFG_eachLine[0]: terminateStr})

	non_terminateStr = dictCFG.keys()
	return dictCFG

def determingFIRST(dictCFG, input_Nonterm, insert_First, listFirst): 	# input_Nonterm is FIRST(X), insert_First is FIRST(Y1)
	eps = 0
	non_terminateStr = dictCFG.keys()

	for x_len_orStr in xrange(0, len(dictCFG[insert_First])):	
		if dictCFG[insert_First][x_len_orStr][0] == '\xa6\xc5':			
			eps += 1

	for x_len_orStr in xrange(0, len(dictCFG[insert_First])):
		checkTerminateStr = dictCFG[insert_First][x_len_orStr][0]
		if eps:
			try:
				determingFIRST(dictCFG, input_Nonterm, dictCFG[insert_First][x_len_orStr][eps], listFirst)
			except:
				pass
		if checkTerminateStr == insert_First:
			pass
		else:
			if checkTerminateStr not in non_terminateStr:
				if (input_Nonterm != insert_First) & (dictCFG[insert_First][x_len_orStr][0] == '\xa6\xc5'): # deal with epsilon
					pass
				else:
					listFirst += [dictCFG[insert_First][x_len_orStr][0]]
			else:
				determingFIRST(dictCFG, input_Nonterm, checkTerminateStr, listFirst)

	listFirst = list(set(listFirst))
	first_set.update({input_Nonterm: listFirst})
	listFirst = []
	eps = 0
	return first_set

def firstLL1():
	dictCFG = readCFG()
	non_terminateStr = dictCFG.keys()
	listFirst = []

	print '+' * 50 + ' READ CFG ' + '+' * 50
	print dictCFG
	print '+' * 50 + ' FIRSTLL1 ' + '+' * 50
	
	for x_len_Nonter in xrange(0, len(dictCFG.keys())):
		first_set = determingFIRST(dictCFG, dictCFG.keys()[x_len_Nonter], dictCFG.keys()[x_len_Nonter], listFirst)
		listFirst = []

	print first_set


def followLL1():
	pass

def parse_table():
	pass

def parseLL1():
	pass

if __name__ == '__main__':
	txt = ''.join(sys.stdin.readlines())
	print '+' * 50 + ' Scan Result ' + '+' * 50
	scanner(txt)
	firstLL1()
	