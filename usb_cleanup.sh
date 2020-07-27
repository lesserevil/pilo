#!/bin/bash

pushd /sys/kernel/config/usb_gadget/g1

echo "" > UDC
rm -rf configs/c.?/functions
rm -rf configs/c.?/strings/*
rm -rf configs/c.?
rm -rf functions/*
rm -rf strings/*
cd ..
rm -rf g1

popd
