#!/usr/bin/env python

import ConfigParser
import datetime
import dateutil.parser
import json
import os
import sys
import urlparse

config = ConfigParser.ConfigParser()
config.read(os.path.expandvars('$HOME/.grenobj'))

AUTHOR = config.get('grenobj', 'author')
PREFIX = config.get('grenobj', 'prefix')

############################################################################################

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

############################################################################################

class NullCodeGenerator(CodeGenerator):
    def produceDate(self, key, value):
        pass

    def produceNumber(self, key, value):
        pass

    def produceObject(self, key, value):
        pass

    def produceString(self, key, value):
        pass

    def produceURL(self, key, value):
        pass

############################################################################################

class ObjectiveC_ForwardGenerator(NullCodeGenerator):
    def produceObject(self, key, value):
        self.writeline("@class %s%s;" % (PREFIX, key.capitalize()))

############################################################################################

class ObjectiveC_Generator(CodeGenerator):
    def __init__(self, name, inputDict, extension):
        self.extension = extension
        self.name = '%s%s' % (PREFIX, name)

        CodeGenerator.__init__(self, inputDict, 
            output = open('%s.%s' % (self.name, self.extension), 'w'))

    def generateHeader(self):
        today = datetime.date.today()

        self.writeline("""//
//  %s.%s
//
//  Created by %s on %s.
//  Copyright (c) %i %s. All rights reserved.
//""" % (self.name, self.extension, AUTHOR, today, today.year, AUTHOR))

############################################################################################

class ObjectiveC_HeaderGenerator(ObjectiveC_Generator):
    def __init__(self, name, inputDict):
        ObjectiveC_Generator.__init__(self, name, inputDict, 'h')

    def generate(self):
        self.generateHeader()

        self.writeline("\n#import <Foundation/Foundation.h>\n")

        ObjectiveC_ForwardGenerator(self.inputDict, self.output).generate()

        self.writeline("\n@interface %s : NSObject\n" % self.name)

        CodeGenerator.generate(self)

        self.writeline("""
@property (readonly) NSDictionary* externalRepresentation;

-(id)initWithDictionary:(NSDictionary*)dictionary;

@end""")

    def propertyDeclaration(self):
        return '@property (readonly)'
        
    def produceDate(self, key, value):
        self.writeline('%s NSDate* %s;' % (self.propertyDeclaration(), member_for_key(key)))

    def produceNumber(self, key, value):
        self.writeline('%s NSNumber* %s;' % (self.propertyDeclaration(), 
            member_for_key(key)))

    def produceObject(self, key, value):
        sub_object = self.__class__(key.capitalize(), value)
        sub_object.generate()

        self.writeline('%s %s* %s;' % (self.propertyDeclaration(), sub_object.name, 
            member_for_key(key)))

    def produceString(self, key, value):
        self.writeline('%s NSString* %s;' % (self.propertyDeclaration(), 
            member_for_key(key)))

    def produceURL(self, key, value):
        self.writeline('%s NSURL* %s;' % (self.propertyDeclaration(), member_for_key(key)))

############################################################################################

class ObjectiveC_ImportGenerator(NullCodeGenerator):
    def produceObject(self, key, value):
        self.writeline('#import "%s%s.h"' % (PREFIX, key.capitalize()))

############################################################################################

class ObjectiveC_ExternalRepGenerator(NullCodeGenerator):
    def produceDate(self, key, value):
        self.writeline('\tdict[@"%s"] = self.%s;' % (key, member_for_key(key)))

    def produceNumber(self, key, value):
        self.produceDate(key, value)

    def produceObject(self, key, value):
        self.writeline('\tdict[@"%s"] = [self.%s externalRepresentation];' \
            % (key, member_for_key(key)))

    def produceString(self, key, value):
        self.produceDate(key, value)

    def produceURL(self, key, value):
        self.produceDate(key, value)

############################################################################################

class ObjectiveC_ImplGenerator(ObjectiveC_Generator):
    def __init__(self, name, inputDict):
        ObjectiveC_Generator.__init__(self, name, inputDict, 'm')

    def generate(self):
        self.generateHeader()

        self.writeline('\n#import "%s.h"' % self.name)

        ObjectiveC_ImportGenerator(self.inputDict, self.output).generate()

        self.writeline("""
@implementation %s

-(NSString*)description {
    return [[NSString alloc] initWithData:self.JSONData encoding:NSUTF8StringEncoding];
}

-(NSDictionary*)externalRepresentation {
    NSMutableDictionary* dict = [NSMutableDictionary dictionary];""" % self.name)

        ObjectiveC_ExternalRepGenerator(self.inputDict, self.output).generate()

        self.writeline("""\treturn dict;
}

-(id)initWithDictionary:(NSDictionary*)dictionary {
    self = [super init];
    if (self) {""")

        CodeGenerator.generate(self)

        self.writeline("""\t}
    return self;
}

-(NSData*)JSONData {
    return [NSJSONSerialization dataWithJSONObject:self.externalRepresentation
                                           options:NSJSONWritingPrettyPrinted
                                             error:nil];
}

@end""")

    def produceDate(self, key, value):
        self.writeline('\t\t_%s = dictionary[@"%s"];' % (member_for_key(key), key))

    def produceNumber(self, key, value):
        self.produceDate(key, value)

    def produceObject(self, key, value):
        sub_object = self.__class__(key.capitalize(), value)
        sub_object.generate()

        self.writeline('\t\t_%s = [[%s alloc] initWithDictionary:dictionary[@"%s"]];' \
            % (member_for_key(key), sub_object.name, key))

    def produceString(self, key, value):
        self.produceDate(key, value)

    def produceURL(self, key, value):
        self.produceDate(key, value)

############################################################################################

def grenobj(json_file, root_class_name):
    obj = json.loads(open(json_file).read())
    ObjectiveC_HeaderGenerator(root_class_name, obj).generate()
    ObjectiveC_ImplGenerator(root_class_name, obj).generate()

def member_for_key(key):
    if key == 'description':
        return 'desc'
    return key

############################################################################################

if __name__ == '__main__':
    grenobj('posts.json', 'Post')
