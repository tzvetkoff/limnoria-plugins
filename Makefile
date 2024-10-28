##
##@ General
##

## Print this message and exit
.PHONY: help
help:
	@awk '																								\
		BEGIN { 																						\
			printf "\nUsage:\n  make \033[36m<target>\033[0m\n"											\
		}																								\
		END {																							\
			printf "\n"																					\
		}																								\
		/^[0-9A-Za-z-]+:/ {																				\
			if (prev ~ /^## /) {																		\
				printf "  \x1b[36m%-23s\x1b[0m %s\n", substr($$1, 0, length($$1)-1), substr(prev, 3)	\
			}																							\
		}																								\
		/^##@/ {																						\
			printf "\n\033[1m%s\033[0m\n", substr($$0, 5)												\
		}																								\
		!/^\.PHONY/ {																					\
			prev = $$0																					\
		}																								\
	' $(MAKEFILE_LIST)


##
##@ Runtime
##

## Install runtime dependencies
deps:
	pip install $$(cat $(CURDIR)/**/requirements.txt | sort | uniq)


##
##@ Testing
##

## Run all plugins tests
test:
	./script/test

# vim:ft=make:ts=4:sts=4:noet
