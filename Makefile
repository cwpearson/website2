DST_DIR := public
BASE_URL := "https://www.carlpearson.net"

.PHONY: all
.DEFAULT_GOAL := all
all: css index nav html $(DST_DIR)/robots.txt $(DST_DIR)/sitemap.xml

PUBLICATIONS_DIR := publications
POSTS_DIR := posts
MD_FILES = $(shell find $(PUBLICATIONS_DIR) $(POSTS_DIR) -type f -name '*.md')
HTML_FILES = $(patsubst %.md, $(DST_DIR)/%.html, $(MD_FILES))

.PHONY: html
html: $(HTML_FILES)
	@echo $(MD_FILES)
	@echo $(HTML_FILES)

$(DST_DIR)/css/%.css: %.css
	mkdir -p $(DST_DIR)/css
	cp -r $< $@

.PHONY: css
css: $(DST_DIR)/css/nav.css


public/posts/%.html: posts/%.md posts/template.html
	@echo $< "->" $@
	mkdir -p public/posts
	pandoc --from markdown \
	--to html \
	--template posts/template.html \
	$< -o $@


public/publications/%.html: publications/%.md publications/template.html
	@echo $< "->" $@
	mkdir -p public/publications
	pandoc --from markdown \
	--to html \
	--template publications/template.html \
	$< -o $@


$(DST_DIR)/nav.html: nav.md
		@echo == $< "->" $@ ==
		pandoc --to html \
		$< -o $@

nav: $(DST_DIR)/nav.html

# Generate the main index.html
# various links are automatically added through the --variable option
# then that file can be included with -H
# that file can probably created by pandocing all the publication
# files with a special template
$(DST_DIR)/index.html: index.md css template.html  $(DST_DIR)/nav.html
	@echo == generate index.html ==
	mkdir -p $(DST_DIR)
	pandoc --from markdown \
	--to html \
	--template template.html \
	-B $(DST_DIR)/nav.html \
	-c css/nav.css \
	$< -o $@


index: public/index.html
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