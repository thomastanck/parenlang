#!/usr/bin/env bash
cd "${0%/*}"

VERBOSE_FLAGS="--hist --dump --metadata"
# EXTRA_FLAGS=$VERBOSE_FLAGS
EXTRA_FLAGS=""
BENCH_FLAGS="--fast $EXTRA_FLAGS"

echo 'FlatParser benchmark'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import tiny     ' 'for p in tiny     .parens: parenlang.FlatParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import someshort' 'for p in someshort.parens: parenlang.FlatParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import medium   ' 'for p in medium   .parens: parenlang.FlatParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import long     ' 'for p in long     .parens: parenlang.FlatParser().parse(p)'
echo ''

echo 'RecursiveParser benchmark'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import tiny     ' 'for p in tiny     .parens: parenlang.RecursiveParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import someshort' 'for p in someshort.parens: parenlang.RecursiveParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import medium   ' 'for p in medium   .parens: parenlang.RecursiveParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import long     ' 'for p in long     .parens: parenlang.RecursiveParser().parse(p)'
echo ''

echo 'GeneratorBasedParser benchmark'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import tiny     ' 'for p in tiny     .parens: parenlang.GeneratorBasedParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import someshort' 'for p in someshort.parens: parenlang.GeneratorBasedParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import medium   ' 'for p in medium   .parens: parenlang.GeneratorBasedParser().parse(p)'
python3 -m perf timeit $BENCH_FLAGS -s 'import parenlang; from samples import long     ' 'for p in long     .parens: parenlang.GeneratorBasedParser().parse(p)'
echo''
