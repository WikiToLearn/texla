import utility

a= open('test.tex','r').read()

l = utility.environments_tokenizer(a) 
for i in l:
	print (i)
