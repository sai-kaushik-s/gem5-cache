#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <source_cpp_file>"
  exit 1
fi

SRC_FILE=$1

BASE_NAME=$(basename "$SRC_FILE" .cpp)

mkdir -p bin

g++ -static -static-libgcc -I /gem5/include -o bin/"$BASE_NAME" "$SRC_FILE" /gem5/util/m5/build/x86/out/libm5.a

if [ $? -eq 0 ]; then
  echo "Build successful: bin/$BASE_NAME"
else
  echo "Build failed"
fi
