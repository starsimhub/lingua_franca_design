"""
Run the original odin model and write its reference results and timing.

    python run.py

Needs the odin environment (see `_envs/odin`).
"""
import os
import csv
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
import tools

model = os.path.join(here, 'original', 'seir_array_odin.R')
states = ['S', 'E', 'I', 'R']
ages = ['0-1', '1-5', '5-15', '15-30', '30+']
stop = 365 # Days, as in the deSolve version the odin tests compare it with (`t = c(0, 365)`)

# The lines that compile and run the model are those of odin's tests (`odin::odin(path)`, `$new()`, `$run(t)`);
# the rest times the run and writes one row per day, with one column per variable and age group (`S[1]` to `R[5]`)
driver = r'''
args <- commandArgs(TRUE)
options(odin.verbose = FALSE)
path <- args[1]
seconds_compile <- system.time(gen <- odin::odin(path))[["elapsed"]]
mod <- gen$new()
t <- 0:as.integer(args[3])
y <- mod$run(t)
seconds <- numeric(0)
for (i in 1:5) {
    seconds <- c(seconds, system.time(mod$run(t))[["elapsed"]])
}
write.csv(y, args[2], row.names = FALSE)
cat(sprintf("COMPILE %.6f\nSECONDS %.6f\n", seconds_compile, median(seconds)))
'''


def simulate():
    """ Compile the model and run it, returning one row per day, and what was printed """
    with tempfile.TemporaryDirectory() as tmp:
        script, out = os.path.join(tmp, 'driver.R'), os.path.join(tmp, 'out.csv')
        with open(script, 'w') as f:
            f.write(driver)
        printed = tools.run(['Rscript', script, model, out, str(stop)], 'odin', cwd=tmp)
        with open(out) as f:
            rows = [{key:float(val) for key,val in row.items()} for row in csv.DictReader(f)]
    return rows, printed


if __name__ == '__main__':
    out, printed = simulate()
    found = dict(line.split() for line in printed.splitlines() if line.split(' ')[0] in ['COMPILE', 'SECONDS'])

    rows = []
    for key in states:
        for i,age in enumerate(ages):
            rows += [dict(time=row['t'], series=f'{key}_{age}', value=row[f'{key}[{i+1}]']) for row in out]
        rows += [dict(time=row['t'], series=key, value=sum(row[f'{key}[{i+1}]'] for i in range(len(ages)))) for row in out]

    tools.write_results(here, rows)
    seconds = tools.time_run(lambda: simulate())
    inner, compile = float(found['SECONDS']), float(found['COMPILE'])
    tools.write_timing(here, seconds, f'Rscript, as one command: starting R, generating and compiling the C code with odin::odin (about {compile:.1f} s), and one run of 365 days with deSolve::dede (the run itself, `mod$run(0:365)`, takes about {1000*inner:.1f} ms)')
    print(f'Wrote {len(rows)} rows; one run takes {seconds:.3f} s as a command, {1000*inner:.2f} ms inside R')
