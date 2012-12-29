#!/bin/sh

#
## $ brew install node
## $ npm -g install json-diff
#

NODE_DIR=`npm config get prefix`
OUT=`node $NODE_DIR/lib/node_modules/json-diff/bin/json-diff.js $@`

if [ "$OUT" != " undefined" ]
then
	echo "$OUT"
	exit 1 
fi
