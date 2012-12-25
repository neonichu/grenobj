LDFLAGS+=-framework Foundation

.PHONY: all clean

all: test

clean:
	rm -f *.o test

%.h: ../grenobj.py
	$<

test: test.m BBUPost.h BBUAuthor.h
	$(CC) $(LDFLAGS) -o $@ $<
