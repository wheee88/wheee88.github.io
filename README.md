# wheee88.github.io

Personal academic homepage of **Hwanhee Cho** (Senior Researcher, Korea Railroad Research Institute), served by GitHub Pages at [wheee88.github.io](https://wheee88.github.io).

Based on the [researcher](https://github.com/ankitsultana/researcher) Jekyll template ([GNU GPL v3](LICENSE)).

## Structure

* `index.md` — main page (about, education, research interests, publications)
* `contact.md` — contact page
* `_data/publications.yml` — publication list rendered on the main page
* `_config.yml` — site title, description, navigation, social metadata

## Automatic publication updates

The publication list updates itself:

* `scripts/update_publications.py` queries [OpenAlex](https://openalex.org) for new papers on the author's profile (ORCID [0000-0002-4966-0099](https://orcid.org/0000-0002-4966-0099)) and appends anything not already in `_data/publications.yml`.
* `.github/workflows/update-publications.yml` runs the script every Monday morning (KST) and commits the result, which triggers a GitHub Pages rebuild. It can also be run on demand from the Actions tab ("Run workflow").
* Existing entries are matched by DOI / OpenAlex id and never overwritten, so manual edits (venue names, months, highlighting) are safe.
* First-author papers are highlighted automatically.

If a new paper has not appeared after a few weeks (e.g. domestic conference papers that OpenAlex indexes slowly or not at all), add it to `_data/publications.yml` by hand following the existing format.
