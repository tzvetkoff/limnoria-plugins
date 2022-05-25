## Print this message and exit
.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | awk '														\
		/^([0-9a-z-]+):.*$$/ {															\
			if (description[0] != "") {													\
				printf("\x1b[36mmake %s\x1b[0m\n", substr($$1, 0, length($$1)-1));		\
				for (i in description) {												\
					printf("| %s\n", description[i]);									\
				}																		\
				printf("\n");															\
				split("", description);													\
				descriptionIndex = 0;													\
			}																			\
		}																				\
		/^##/ {																			\
			description[descriptionIndex++] = substr($$0, 4);							\
		}																				\
	'

## Run plugin tests
test:
	supybot-test -c --plugins-dir=$(CURDIR)

# vim:ft=make:ts=4:sts=4:noet
