# Refresh the ACE Music Space

The files served from this repository are a deterministic build of [the shared Space runtime](https://github.com/AceDataCloud/SunoHuggingFace). The Git revision and archive SHA-256 are recorded in [SOURCE.json](SOURCE.json).

1. Check out the desired reviewed commit in a clean clone of the canonical repository.
2. In this repository, run `python3 scripts/sync_space.py /path/to/SunoHuggingFace --update` and inspect the diff.
3. Commit the generated files and `SOURCE.json` together and open a pull request. CI rebuilds the pinned source and compares each file and the ZIP digest.

Run `python3 scripts/sync_space.py /path/to/SunoHuggingFace` to verify the pin locally and produce `artifacts/acemusic-static-space.zip`. The root `index.html` also works directly when served by a static HTTP server. CI uploads the ZIP as a GitHub Actions artifact. HF Hub publication is a separate operator action.
