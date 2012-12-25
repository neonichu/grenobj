#!/usr/bin/env python

import datetime
import dateutil.parser
import json
import sys
import urlparse

AUTHOR = 'Boris Buegling'
PREFIX = 'BBU'

###################################################################################################

class CodeGenerator:
	def __init__(self, inputDict, output = sys.stdout):
		self.inputDict = inputDict
		self.output = output

	def generate(self):
		for key, value in sorted(self.inputDict.iteritems()):
			if type(value) == dict:
				self.produceObject(key, value)
				continue

			try:
				int(value)
				self.produceNumber(key, value)
				continue
			except:
				pass

			try:
				dateutil.parser.parse(value)
				self.produceDate(key, value)
				continue
			except:
				pass

			if urlparse.urlparse(value).scheme:
				self.produceURL(key, value)
				continue

			self.produceString(key, value)

	def produceDate(self, key, value):
		self.writeline("'%s' is a date." % key)

	def produceNumber(self, key, value):
		self.writeline("'%s' is a number." % key)

	def produceObject(self, key, value):
		self.writeline("'%s' is an object." % key)

		self.__class__(value, self.output).generate()

	def produceString(self, key, value):
		self.writeline("'%s' is a string." % key)

	def produceURL(self, key, value):
		self.writeline("'%s' is an URL." % key)

	def write(self, some_string):
		self.output.write(some_string)

	def writeline(self, some_string):
		self.write('%s\n' % some_string)

###################################################################################################

class ObjectiveC_HeaderGenerator(CodeGenerator):
	def __init__(self, name, inputDict):
		self.name = '%s%s' % (PREFIX, name)

		CodeGenerator.__init__(self, inputDict, output = open('%s.h' % self.name, 'w'))

	def generate(self):
		today = datetime.date.today()

		self.writeline("""//
//  %s.h
//
//  Created by %s on %s.
//  Copyright (c) %i %s. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface %s : NSObject
""" % (self.name, AUTHOR, today, today.year, AUTHOR, self.name))

		CodeGenerator.generate(self)

		self.writeline("\n@end")

	def propertyDeclaration(self):
		return '@property (readonly)'
		
	def produceDate(self, key, value):
		self.writeline('%s NSDate* %s;' % (self.propertyDeclaration(), key))

	def produceNumber(self, key, value):
		self.writeline('%s NSNumber* %s;' % (self.propertyDeclaration(), key))

	def produceObject(self, key, value):
		sub_object = self.__class__(key.capitalize(), value)
		sub_object.generate()

		self.writeline('%s %s* %s' % (self.propertyDeclaration(), sub_object.name, key))

	def produceString(self, key, value):
		self.writeline('%s NSString* %s;' % (self.propertyDeclaration(), key))

	def produceURL(self, key, value):
		self.writeline('%s NSURL* %s;' % (self.propertyDeclaration(), key))

###################################################################################################

if __name__ == '__main__':
	obj = json.loads(open('posts.json').read())
	ObjectiveC_HeaderGenerator('Post', obj).generate()
