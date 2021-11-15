#!/bin/bash

mkdir -p ./aws-lambda/python
pip3 install -t ./aws-lambda/python xlsxwriter
cd ./aws-lambda/python && zip -r ../inventory-lambda.zip .
cd .. && zip -g inventory-lambda.zip lambda_function.py
