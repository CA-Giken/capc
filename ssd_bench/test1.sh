#!/bin/bash

rm -fr tmp

LOOP=0
while ((LOOP < 100))
do
  mkdir -p tmp/$LOOP
  T0=$(date +%s%3N)
  VOL=0
  while ((VOL < 100))
  do
    cp -a data* tmp/$LOOP/$VOL
    ((VOL=VOL+1))
  done
  T1=$(date +%s%3N)
  ((DT=T1-T0))
  echo $LOOP $DT
  ((LOOP=LOOP+1))
done

