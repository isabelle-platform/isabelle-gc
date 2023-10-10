#!/bin/bash

git clone https://github.com/kuzmoyev/google-calendar-simple-api
cd google-calendar-simple-api
patch -p1 < ../gcsa-patch.patch
python3 setup.py install
