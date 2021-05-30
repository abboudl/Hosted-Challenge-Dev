#! /bin/bash

cd ./BASE-IMAGE/ && ./quickstart 0.0.0.0 31900
cd ..

ip=0.0.0.0 
port=30901
for d in */; do
  if [ "$d" != "BASE-IMAGE/" ]; then 
    cd "$d" && ./quickstart "$ip" "$port"
    cd ..
    port=$((port + 1))
  fi
done
