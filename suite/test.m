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
    
    NSLog(@"JSON: %@", json);
    
	return 0;
}
