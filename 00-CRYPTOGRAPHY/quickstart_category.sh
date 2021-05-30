#! /bin/bash

ip=0.0.0.0 
port=30000
for d in */; do
  cd "$d" && ./quickstart "$ip" "$port"
  cd ..
  port=$((port + 1))
done
