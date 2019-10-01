import sqlparse
import os, sys
import csv
import re
import numbers

Data = {}
def readtable():
    file = open('metadata.txt','r')
    Start = False
    Name = "none";
    for line in file:
        item = line.strip()
        if item == "<begin_table>":
            Start = True
        elif Start == True and Name == "none":
            Name = item
            Data[Name] = []
        elif item == "<end_table>":
            Start = False
            Name = "none"
        else:
            Data[Name].append(item)

readtable()
# print(Data)

value = []
def parseStatement(statement):
    sType = sqlparse.sql.Statement(statement).get_type()
    sIdentifiers = sqlparse.sql.IdentifierList(statement).get_identifiers()
    
    for i in sIdentifiers:
        value.append(str(i))
    # print(value)

query = sys.argv[1]
statement = sqlparse.parse(query)[0].tokens
parseStatement(statement)

def solve_unconditioned(value):
	tables = value[3].split(',')
	fields = value[1].split(',')
	
	for f in fields:
		f = f.split('(')
		f = f[-1].split(')')[0]
		valid = False
		if f in Data[tables[0]]:
			index = Data[tables[0]].index(f)
			valid = True
		if len(tables) > 1:
			if f in Data[tables[1]]:
				index = Data[tables[1]].index(f)
				valid = True
			if f in Data[tables[1]] and f in Data[tables[0]]:
				print("AMBIGUOUS FIELD " + f)
				return
		f = f.split('.')
		if f[0] in tables and f[1] in Data[tables[tables.index(f[0])]]:
			valid = True
		if valid == False and f[-1] != '*':
			print("INVALID FIELD " + f[-1])
			return

	table = []
	for t in tables:
		if t in Data.keys():
			fname = t + '.csv'
			tab = []
			with open(fname, 'rt',) as f:
				reader = csv.reader(f)
				your_list = list(reader)
				table.append(your_list)
		else:
			print("No such table exits")
			return

	if len(tables) == 1:
		dis = 0
		for f in fields:
			operator = f.split('(')
			if len(operator) == 1:
				if dis == 1:
					print("INVALID DISTINCT QUERY")
					return
				dis = -1
				continue
			col = operator[1].split(')')
			col[0] = col[0].split('.')[-1]
			if operator[0] == "distinct" and col[0] in Data[tables[0]]:
				if dis == 0:
					dis = 1
				if dis == -1:
					print("INVALID DISTINCT QUERY")
					return
			else:
				if dis == 1:
					print("INVALID DISTINCT QUERY")
					return
				dis = -1
		if dis == 1:
			dist = set()
			for record in range(len(table[0])):
				temp = []
				for f in fields:
					operator = f.split('(')
					col = operator[1].split(')')
					col[0] = col[0].split('.')[-1]
					ind = Data[tables[0]].index(col[0])
					if col[0] in Data[tables[0]]:
						temp.append(table[0][record][ind])
				dist.add(tuple(temp))
			for d in dist:
				for x in d:
					print(x,end=' ')
				print()
			return

		for f in fields:
			if f == '*':
				for i in Data[tables[0]]:
					print(tables[0] + '.' + i,end = ' ')
			elif f in Data[tables[0]] :
				print(tables[0] + '.' + f,end = ' ')
			else:
				operator = f.split('(')
				col = operator[1].split(')')
				col[0] = col[0].split('.')[-1]
				if operator[0] == "max" and col[0] in Data[tables[0]]:
					print("max(" + tables[0] + '.' + col[0] + ")",end = ' ')
				elif operator[0] == "min" and col[0] in Data[tables[0]]:
					print("min(" + tables[0] + '.' + col[0] + ")",end = ' ')
				elif operator[0] == "avg" and col[0] in Data[tables[0]]:
					print("avg(" + tables[0] + '.' + col[0] + ")",end = ' ')
				elif operator[0] == "sum" and col[0] in Data[tables[0]]:
					print("sum(" + tables[0] + '.' + col[0] + ")",end = ' ')
				else:
					print("\nNO FIELD " + f + " EXISTS IN " + tables[0])
					return
		print()
		for record in range(len(table[0])):
			individual = 0
			for f in fields:
				ft = f.split('.')
				if f == '*':
					individual = 1
					for i in table[0][record]:
						print(i,end = ' ')
				elif f in Data[tables[0]]:
					individual = 1
					ind = Data[tables[0]].index(f)
					print(table[0][record][ind],end = ' ')
				elif ft[0] == tables[0] and ft[1] in Data[tables[0]]:
					individual = 1
					ind = Data[tables[0]].index(ft[1])
					print(table[0][record][ind],end = ' ')
				else:
					operator = f.split('(')
					col = operator[1].split(')')
					col[0] = col[0].split('.')[-1]
					ind = Data[tables[0]].index(col[0])
					if operator[0] == "max" and col[0] in Data[tables[0]]:
						maximum = table[0][0][ind]
						for record1 in range(len(table[0])):
							maximum = max(int(maximum),int(table[0][record1][ind]))
						print(maximum,end=" ")
					elif operator[0] == "min" and col[0] in Data[tables[0]]:
						minimum = table[0][0][ind]
						for record1 in range(len(table[0])):
							minimum = min(int(minimum),int(table[0][record1][ind]))
						print(minimum,end=" ")
					elif operator[0] == "avg" and col[0] in Data[tables[0]]:
						average = 0
						for record1 in range(len(table[0])):
							average = average + int(table[0][record1][ind])
						print(average/len(table[0]),end=" ")
					elif operator[0] == "sum" and col[0] in Data[tables[0]]:
						summ = 0
						for record1 in range(len(table[0])):
							summ = summ + int(table[0][record1][ind])
						print(summ,end=" ")
			print()
			if individual == 0:
				break

	if len(tables) == 2:
		for f in fields:
			f = f.split('.')[-1]
			if f != '*' and f not in Data[tables[0]] and f not in Data[tables[1]]:
				print("\nNO FIELD " + f + " EXISTS IN " + tables[0] + " and " + tables[1])
				return

		for f in fields:
			ft = f.split('.')
			if f == '*':
				for i in Data[tables[0]]:
					print(tables[0] + '.' + i,end = ' ')
			elif f in Data[tables[0]] or ( len(ft) > 1 and ft[0] == tables[0] and ft[1] in Data[tables[0]]):
				print(f,end = ' ')
		for f in fields:
			ft = f.split('.')
			if f == '*':
				for i in Data[tables[1]]:
					print(tables[1] + '.' + i,end = ' ')
			elif f in Data[tables[1]] or ( len(ft) > 1 and ft[0] == tables[1] and ft[1] in Data[tables[1]]):
				print(f,end = ' ')
		print()

		for record in range(len(table[0])):
			for record2 in range(len(table[1])):
				for f in fields:
					f = f.split('(')
					f = f[-1].split(')')[0]
					ft = f.split('.')
					if f == '*':
						for i in table[0][record]:
							print(i,end = ' ')
					elif f in Data[tables[0]]:
						ind = Data[tables[0]].index(f)
						print(table[0][record][ind],end = ' ')
					elif len(ft) > 1 and ft[0] == tables[0] and ft[1] in Data[tables[0]]:
						ind = Data[tables[0]].index(ft[1])
						print(table[0][record][ind],end = ' ')
				for f in fields:
					f = f.split('(')
					f = f[-1].split(')')[0]
					ft = f.split('.')
					if f == '*':
						for i in table[1][record2]:
							print(i,end = ' ')
					elif f in Data[tables[1]]:
						ind = Data[tables[1]].index(f)
						print(table[1][record2][ind],end = ' ')
					elif len(ft) > 1 and ft[0] == tables[1] and ft[1] in Data[tables[1]]:
						ind = Data[tables[1]].index(ft[1])
						print(table[1][record2][ind],end = ' ')
				print()
	return

def solve_conditioned(value):
	tables = value[3].split(',')
	fields = value[1].split(',')
	where = value[4].split(' ')
	
	for f in fields:
		f = f.split('(')
		f = f[-1].split(')')[0]
		valid = False
		if f in Data[tables[0]]:
			index = Data[tables[0]].index(f)
			valid = True
		if len(tables) > 1:
			if f in Data[tables[1]]:
				index = Data[tables[1]].index(f)
				valid = True
			if f in Data[tables[1]] and f in Data[tables[0]]:
				print("AMBIGUOUS FIELD " + f)
				return
		f = f.split('.')
		if f[0] in tables and f[1] in Data[tables[tables.index(f[0])]]:
			valid = True
		if valid == False and f[-1] != '*':
			print("INVALID FIELD " + f[-1])
			return

	table = []
	for t in tables:
		if t in Data.keys():
			fname = t + '.csv'
			tab = []
			with open(fname, 'rt',) as f:
				reader = csv.reader(f)
				your_list = list(reader)
				table.append(your_list)
		else:
			print("No such table exits")
			return

	if len(tables) == 1:
		dis = 0
		for f in fields:
			operator = f.split('(')
			if len(operator) == 1:
				if dis == 1:
					print("INVALID DISTINCT QUERY")
					return
				dis = -1
				continue
			col = operator[1].split(')')
			col[0] = col[0].split('.')[-1]
			if operator[0] == "distinct" and col[0] in Data[tables[0]]:
				if dis == 0:
					dis = 1
				if dis == -1:
					print("INVALID DISTINCT QUERY")
					return
			else:
				if dis == 1:
					print("INVALID DISTINCT QUERY")
					return
				dis = -1
		if dis == 1:
			dist = set()
			for record in range(len(table[0])):
				temp = []
				for f in fields:
					operator = f.split('(')
					col = operator[1].split(')')
					col[0] = col[0].split('.')[-1]
					ind = Data[tables[0]].index(col[0])
					if col[0] in Data[tables[0]]:
						temp.append(table[0][record][ind])
				dist.add(tuple(temp))
			for d in dist:
				for x in d:
					print(x,end=' ')
				print()
			return

		for f in fields:
			if f == '*':
				for i in Data[tables[0]]:
					print(tables[0] + '.' + i,end = ' ')
			elif f in Data[tables[0]] :
				print(tables[0] + '.' + f,end = ' ')
			else:
				print("\nNO FIELD " + f + " EXISTS IN " + tables[0])
				return
		print()

		for record in range(len(table[0])):
			if(len(where)!= 4 and len(where)!= 8):
				print("INVALID WHERE QUERY")
				return
			satisfy = False
			comp = [0,0]
			w = where[1]
			wt = w.split('.')
			if w in Data[tables[0]]:
				ind = Data[tables[0]].index(w)
				comp[0] = table[0][record][ind]
			elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
				ind = Data[tables[0]].index(wt[1])
				comp[0] = table[0][record][ind]
			else:
				print("INVALID WHERE QUERY FIELD " + w)
				return

			w = where[3]
			wt = w.split('.')
			if w in Data[tables[0]]:
				ind = Data[tables[0]].index(w)
				comp[1] = table[0][record][ind]
			elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
				ind = Data[tables[0]].index(wt[1])
				comp[1] = table[0][record][ind]
			else:
				try:
					comp[1] = int(where[3])
				except:
					print("INVALID CONDITIONAL QUERY PARAMETER " + where[3])
					return

			if (where[2] == "<" and int(comp[0]) < int(comp[1]) ):
				satisfy = True
			elif (where[2] == "<=" and int(comp[0]) <= int(comp[1]) ):
				satisfy = True
			elif (where[2] == ">" and int(comp[0]) > int(comp[1]) ):
				satisfy = True
			elif (where[2] == ">=" and int(comp[0]) >= int(comp[1]) ):
				satisfy = True
			elif (where[2] == "=" and int(comp[0]) == int(comp[1]) ):
				satisfy = True

			if (len(where) == 8):
				w = where[5]
				wt = w.split('.')
				if w in Data[tables[0]]:
					ind = Data[tables[0]].index(w)
					comp[0] = table[0][record][ind]
				elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
					ind = Data[tables[0]].index(wt[1])
					comp[0] = table[0][record][ind]

				w = where[7]
				wt = w.split('.')
				if w in Data[tables[0]]:
					ind = Data[tables[0]].index(w)
					comp[1] = table[0][record][ind]
				elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
					ind = Data[tables[0]].index(wt[1])
					comp[1] = table[0][record][ind]
				else:
					try:
						comp[1] = int(where[7])
					except:
						print("INVALID CONDITIONAL QUERY PARAMETER " + where[3])
						return

				if (where[6] == "<" and int(comp[0]) >= int(comp[1]) and where[4] == "and"):
					satisfy = False
				elif (where[6] == "<=" and int(comp[0]) > int(comp[1]) and where[4] == "and"):
					satisfy = False
				elif (where[6] == ">" and int(comp[0]) <= int(comp[1]) and where[4] == "and"):
					satisfy = False
				elif (where[6] == ">=" and int(comp[0]) < int(comp[1]) and where[4] == "and"):
					satisfy = False
				elif (where[6] == "=" and int(comp[0]) != int(comp[1]) and where[4] == "and"):
					satisfy = False

				if (where[6] == "<" and int(comp[0]) < int(comp[1]) and where[4] == "or"):
					satisfy = True
				elif (where[6] == "<=" and int(comp[0]) <= int(comp[1]) and where[4] == "or"):
					satisfy = True
				elif (where[6] == ">" and int(comp[0]) > int(comp[1]) and where[4] == "or"):
					satisfy = True
				elif (where[6] == ">=" and int(comp[0]) >= int(comp[1]) and where[4] == "or"):
					satisfy = True
				elif (where[6] == "=" and int(comp[0]) == int(comp[1]) and where[4] == "or"):
					satisfy = True

			if(satisfy == False):
				continue
			individual = 0
			for f in fields:
				ft = f.split('.')
				if f == '*':
					individual = 1
					for i in table[0][record]:
						print(i,end = ' ')
				elif f in Data[tables[0]]:
					individual = 1
					ind = Data[tables[0]].index(f)
					print(table[0][record][ind],end = ' ')
				elif ft[0] == tables[0] and ft[1] in Data[tables[0]]:
					individual = 1
					ind = Data[tables[0]].index(ft[1])
					print(table[0][record][ind],end = ' ')
			print()
			if individual == 0:
				break

	if len(tables) == 2:
		for f in fields:
			f = f.split('.')[-1]
			if f != '*' and f not in Data[tables[0]] and f not in Data[tables[1]]:
				print("\nNO FIELD " + f + " EXISTS IN " + tables[0] + " and " + tables[1])
				return

		for f in fields:
			ft = f.split('.')
			if f == '*':
				for i in Data[tables[0]]:
					print(tables[0] + '.' + i,end = ' ')
			elif f in Data[tables[0]] or ( len(ft) > 1 and ft[0] == tables[0] and ft[1] in Data[tables[0]]):
				print(f,end = ' ')
		for f in fields:
			ft = f.split('.')
			if f == '*':
				for i in Data[tables[1]]:
					print(tables[1] + '.' + i,end = ' ')
			elif f in Data[tables[1]] or ( len(ft) > 1 and ft[0] == tables[1] and ft[1] in Data[tables[1]]):
				print(f,end = ' ')
		print()

		for record in range(len(table[0])):
			for record2 in range(len(table[1])):
				if(len(where)!= 4 and len(where)!= 8):
					print("INVALID WHERE QUERY")
					return
				satisfy = False
				comp = [0,0]
				w = where[1]
				wt = w.split('.')
				if w in Data[tables[0]]:
					ind = Data[tables[0]].index(w)
					comp[0] = table[0][record][ind]
				elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
					ind = Data[tables[0]].index(wt[1])
					comp[0] = table[0][record][ind]
				elif w in Data[tables[1]]:
					ind = Data[tables[1]].index(w)
					comp[0] = table[1][record][ind]
				elif len(wt) > 1 and wt[0] == tables[1] and wt[1] in Data[tables[1]]:
					ind = Data[tables[1]].index(wt[1])
					comp[0] = table[1][record][ind]

				w = where[3]
				wt = w.split('.')
				if w in Data[tables[0]]:
					ind = Data[tables[0]].index(w)
					comp[1] = table[0][record][ind]
				elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
					ind = Data[tables[0]].index(wt[1])
					comp[1] = table[0][record][ind]
				elif w in Data[tables[1]]:
					ind = Data[tables[1]].index(w)
					comp[1] = table[1][record][ind]
				elif len(wt) > 1 and wt[0] == tables[1] and wt[1] in Data[tables[1]]:
					ind = Data[tables[1]].index(wt[1])
					comp[1] = table[1][record][ind]
				else:
					try:
						comp[1] = int(where[3])
					except:
						print("INVALID CONDITIONAL QUERY PARAMETER " + where[3])
						return

				if (where[2] == "<" and int(comp[0]) < int(comp[1]) ):
					satisfy = True
				elif (where[2] == "<=" and int(comp[0]) <= int(comp[1]) ):
					satisfy = True
				elif (where[2] == ">" and int(comp[0]) > int(comp[1]) ):
					satisfy = True
				elif (where[2] == ">=" and int(comp[0]) >= int(comp[1]) ):
					satisfy = True
				elif (where[2] == "=" and int(comp[0]) == int(comp[1]) ):
					satisfy = True

				if (len(where) == 8):
					w = where[5]
					wt = w.split('.')
					if w in Data[tables[0]]:
						ind = Data[tables[0]].index(w)
						comp[0] = table[0][record][ind]
					elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
						ind = Data[tables[0]].index(wt[1])
						comp[0] = table[0][record][ind]
					elif w in Data[tables[1]]:
						ind = Data[tables[1]].index(w)
						comp[0] = table[1][record][ind]
					elif len(wt) > 1 and wt[0] == tables[1] and wt[1] in Data[tables[1]]:
						ind = Data[tables[1]].index(wt[1])
						comp[0] = table[1][record][ind]

					w = where[7]
					wt = w.split('.')
					if w in Data[tables[0]]:
						ind = Data[tables[0]].index(w)
						comp[1] = table[0][record][ind]
					elif len(wt) > 1 and wt[0] == tables[0] and wt[1] in Data[tables[0]]:
						ind = Data[tables[0]].index(wt[1])
						comp[1] = table[0][record][ind]
					elif w in Data[tables[1]]:
						ind = Data[tables[1]].index(w)
						comp[1] = table[1][record][ind]
					elif len(wt) > 1 and wt[0] == tables[1] and wt[1] in Data[tables[1]]:
						ind = Data[tables[1]].index(wt[1])
						comp[1] = table[1][record][ind]
					else:
						try:
							comp[1] = int(where[7])
						except:
							print("INVALID CONDITIONAL QUERY PARAMETER " + where[3])
							return

					if (where[6] == "<" and int(comp[0]) >= int(comp[1]) and where[4] == "and"):
						satisfy = False
					elif (where[6] == "<=" and int(comp[0]) > int(comp[1]) and where[4] == "and"):
						satisfy = False
					elif (where[6] == ">" and int(comp[0]) <= int(comp[1]) and where[4] == "and"):
						satisfy = False
					elif (where[6] == ">=" and int(comp[0]) < int(comp[1]) and where[4] == "and"):
						satisfy = False
					elif (where[6] == "=" and int(comp[0]) != int(comp[1]) and where[4] == "and"):
						satisfy = False

					if (where[6] == "<" and int(comp[0]) < int(comp[1]) and where[4] == "or"):
						satisfy = True
					elif (where[6] == "<=" and int(comp[0]) <= int(comp[1]) and where[4] == "or"):
						satisfy = True
					elif (where[6] == ">" and int(comp[0]) > int(comp[1]) and where[4] == "or"):
						satisfy = True
					elif (where[6] == ">=" and int(comp[0]) >= int(comp[1]) and where[4] == "or"):
						satisfy = True
					elif (where[6] == "=" and int(comp[0]) == int(comp[1]) and where[4] == "or"):
						satisfy = True

				if(satisfy == False):
					continue
				for f in fields:
					f = f.split('(')
					f = f[-1].split(')')[0]
					ft = f.split('.')
					if f == '*':
						for i in table[0][record]:
							print(i,end = ' ')
					elif f in Data[tables[0]]:
						ind = Data[tables[0]].index(f)
						print(table[0][record][ind],end = ' ')
					elif len(ft) > 1 and ft[0] == tables[0] and ft[1] in Data[tables[0]]:
						ind = Data[tables[0]].index(ft[1])
						print(table[0][record][ind],end = ' ')
				for f in fields:
					f = f.split('(')
					f = f[-1].split(')')[0]
					ft = f.split('.')
					if f == '*':
						for i in table[1][record2]:
							print(i,end = ' ')
					elif f in Data[tables[1]]:
						ind = Data[tables[1]].index(f)
						print(table[1][record2][ind],end = ' ')
					elif len(ft) > 1 and ft[0] == tables[1] and ft[1] in Data[tables[1]]:
						ind = Data[tables[1]].index(ft[1])
						print(table[1][record2][ind],end = ' ')
				print()
	return

if len(value) == 4:
	solve_unconditioned(value)
elif len(value) == 5:
	solve_conditioned(value)
else:
	print("INVALID QUERY")
