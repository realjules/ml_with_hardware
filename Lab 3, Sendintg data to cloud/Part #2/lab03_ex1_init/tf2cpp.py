#!/usr/bin/python3
import sys
import os

if len( sys.argv ) != 2 :
  print("usage is: tf2cpp model.tflite");
  sys.exit(1)

os.system(f"xxd -i {sys.argv[1]} > tmp_zuppy_zerry.txt")
fd_in = open( 'tmp_zuppy_zerry.txt', 'r')
fd_out = open('model.cpp', 'w')

fd_out.write("#include \"model.h\"\n")
fd_out.write("const unsigned char g_model[] = {\n")
a = fd_in.readline()
while( 1 ):
  a = fd_in.readline()
  if a == '': break
  b = a.split()
  if b[0] != 'unsigned':
    fd_out.write(a)
  else:
    fd_out.write("const int g_model_len = " + b[-1] +"\n")

fd_in.close()
fd_out.close()
os.system("rm -f tmp_zuppy_zerry.txt")
