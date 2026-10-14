# SimInf

- **Version:** 11.1.0, from CRAN (published 8 September 2026); the same as tag `v11.1.0` (commit `7a78909d`) of the repository
- **Source:** https://github.com/stewid/SimInf and https://cran.r-project.org/package=SimInf (GPL-3)
- **Needs:** R (4.6.1 was used, at `/usr/bin/R`), a C compiler (gcc 13.3.0), and the GNU Scientific Library with its headers (2.7.1; `gsl-config` must be on the `PATH`). SimInf's other dependencies (`digest`, `MASS`, `Matrix`, and the packages that come with R) were already in R's own libraries, so only SimInf itself is in `lib/`; `requirements.txt` lists what is there.

## Build

`python _envs/envs.py install siminf` does this:

```bash
mkdir -p lib bin
Rscript -e 'install.packages("SimInf", lib="lib", repos="https://cloud.r-project.org")'
cat > bin/Rscript <<'END'
#!/bin/sh
here="$(cd "$(dirname "$0")/.." && pwd)"
export R_LIBS_USER="$here/lib"
exec /usr/bin/Rscript "$@"
END
chmod +x bin/Rscript
```

The build compiles SimInf's C code and takes about a minute. `install.packages` gets the latest version of each package, which may be later than the one in `requirements.txt`; `python _envs/envs.py check siminf` says if so. `bin/Rscript` is a wrapper that puts `lib/` at the front of R's library path, so an example that runs `Rscript` in this environment finds SimInf.
