CFLAGS+=-pedantic -Wall -Werror
LDFLAGS+=-framework Foundation

.PHONY: all clean

all: test
	./test >tmp.json
	./json-diff.sh posts.json tmp.json
	@rm -f tmp.json

clean:
	rm -f *.o test tmp.json

%.h: ../grenobj.py
	@$<

BBUAuthor.m: BBUAuthor.h
BBUPost.m: BBUPost.h

test: test.m BBUPost.m BBUAuthor.m
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^
