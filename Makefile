DST_DIR := public
BASE_URL := "https://www.carlpearson.net"

.PHONY: all
.DEFAULT_GOAL := all
all: html $(DST_DIR)/robots.txt $(DST_DIR)/sitemap.xml

PUBLICATIONS_DIR := publications
MD_FILES = $(shell find $(PUBLICATIONS_DIR) -type f -name '*.md')
HTML_FILES = $(patsubst %/index.md, $(DST_DIR)/%.html, $(MD_FILES))
TEMPLATE = $(SRC_DIR)/template.html
.PHONY: publications
publications: $(HTML_FILES)
	@echo $(MD_FILES)
	@echo $(HTML_FILES)


public/publications/%.html: publications/%/index.md publications/template.html
	@echo $< "->" $@
	mkdir -p public/publications
	pandoc --from markdown \
	--to html \
	--template publications/template.html \
	$< -o $@


gen/var_publications.txt: $(MD_FILES)
	pandoc --from md \
	--to txt \
	$^

# Generate the main index.html
# various links are automatically added through the --variable option
# then that file can be included with -H
# that file can probably created by pandocing all the publication
# files with a special template
$(DST_DIR)/index.html: index.md template.html
	@echo ==generate index.html
	mkdir -p $(DST_DIR)
	pandoc --from markdown \
	--to html \
	--template template.html \
	$< -o $@
	

html: public/index.html publications
	mkdir -p $(DST_DIR)
	@echo "build html"


$(DST_DIR)/robots.txt:
	@echo "make robots.txt"
	mkdir -p $(DST_DIR)
	@echo "User-agent: *" > $@
	@echo "Allow: *" >> $@
	@echo "Sitemap: $(BASE_URL)/sitemap.xml" >> $@


$(DST_DIR)/sitemap.xml:
	@echo "sitemap.xml"
	mkdir -p $(DST_DIR)
	touch $@


.PHONY: clean
clean:
	rm -rf public