#!/bin/sh

LIB=build/remoteApiBindings/lib
cd $LIB
make
cd -
cp $LIB/remoteApi.* ./lib/

