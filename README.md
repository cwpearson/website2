# website2

```bash
python build.py && python -m http.server --directory public
```

## Roadmap

- talk metadata
  - [x] date start
  - [x] date end
  - automatic video embeds
    - [x] youtube
    - [x] vimeo
  - [x] slides URL
    - [ ] embed doesn't do anything useful in mobile safari
    - [ ] embed if pdf using pdf.js?
  - [ ] publication cross-reference  
- publication metadata
  - [x] pdf
  - [x] slides
  - [x] poster
  - [x] code
  - automatic video embeds
    - [x] youtube
    - [x] vimeo
  - [ ] project cross-reference
  - [ ] date
- robots.txt
  - [x] allow all
  - [x] disallow AI
- Image handling
  - v1
    - [x] optimize images
  - v2
    - [ ] set height and width from all images
  - v3
    - [ ] generate responsive images
    - [ ] use responsive images
- [x] projects page
- [x] favicon
- [ ] edit this page on Github
- [x] only load math for a page if frontmatter has math = true
