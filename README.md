# Underbakke Lab website

The site for the Underbakke Lab at Iowa State University.

- `docs/` is the finished website. GitHub Pages serves this folder.
- `content/` holds the text: `news.md`, `publications.md`, `people.json`, and one file per plain page.
- `build.py` turns `content/` into `docs/`. Run `python3 build.py` after any change to `content/`.

## Adding a news post

Add a block to the top of `content/news.md`:

    ## Title of the post
    date: November 11, 2026
    image: assets/news/photo.jpg | Short description of the photo

    Text of the post. Links look like [this](https://example.com).

The `image:` line is optional.

## Photos

Most photos still load from Squarespace's image servers (the addresses in `build.py` starting with
`images.squarespace-cdn.com`). They must be copied into `docs/assets/` before the Squarespace
account is closed.
