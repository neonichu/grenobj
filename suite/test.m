#import <Foundation/Foundation.h>

#import "BBUPost.h"

int main(int argc, char** argv) {
    NSData* data = [NSData dataWithContentsOfFile:@"posts.json"];
    
    NSError* error;
    id json = [NSJSONSerialization JSONObjectWithData:data options:0 error:&error];
    if (!json) {
        NSLog(@"Error: %@", error.localizedDescription);
        return 1;
    }

    BBUPost* post = [[BBUPost alloc] initWithDictionary:json];
    printf("%s\n", [[post description] UTF8String]);
    
    return 0;
}
