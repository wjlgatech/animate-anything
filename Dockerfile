# Reproducible render of /animate-anything examples — manim + LaTeX + ffmpeg baked in.
# Build:  docker build -t animate-anything .
# Render: docker run --rm -v "$PWD/out:/work/media" animate-anything \
#           manim -qh examples/geometric_series.py GeometricSeries
FROM manimcommunity/manim:stable
USER root
WORKDIR /work
COPY . /work
# Default: lint + render both goldens to /work/media (mount it out).
CMD bash -lc 'for f in examples/*.py; do python3 scripts/animate.py lint "$f" --gate 80; done && \
              manim -qh examples/odd_squares.py OddSquares && \
              manim -qh examples/geometric_series.py GeometricSeries'
