# gem5-cache

## Performance Impact of Using Caches in gem5

### Build the Docker Image

To build a Docker container with the latest gem5 repository, run the following command:

```sh
docker build -t gem5-cache .
```

This command creates a Docker image named `gem5-cache` using the Dockerfile in the current directory.

### Run the Docker Container

To run the Docker container interactively and mount the current directory into the container at `/data`, use:

```sh
docker run -it -v .:/data gem5-cache
```

This lets you work inside the container with access to your current host directory at `/data`.
