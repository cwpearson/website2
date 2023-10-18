# website2

```bash
python build.py && python -m http.server --directory public
```

## Roadmap

- [ ] talk metadata
  - [x] date start
  - [x] date end
  - [ ] slides URL
    - [ ] embed if pdf using pdf.js?
- [x] robots.txt
- [ ] Image handling
  - v1
    - [x] optimize images
  - v2
    - [ ] set height and width from all images
  - v3
    - [ ] generate responsive images
    - [ ] use responsive images
- [x] projects page
- [ ] fill publication template from metadata
  - [ ] code
  - [ ] slides
  - [ ] paper
- [x] favicon
- [ ] edit this page on Github
- [x] only load math for a page if frontmatter has math = true
- [ ] projects cross-references
- [ ] tags cross-references