import marshal, sys
data = open("bytecode.pyc","rb").read()
code = marshal.loads(data[16:])
print(code)
ns = {}
exec(code, ns, ns)
print(ns)