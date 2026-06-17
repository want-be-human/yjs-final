from torchvision import datasets


def main():
    datasets.MNIST.mirrors = [
        "https://storage.googleapis.com/cvdf-datasets/mnist/",
        "https://ossci-datasets.s3.amazonaws.com/mnist/",
        "http://yann.lecun.com/exdb/mnist/",
    ]
    datasets.MNIST("/work/data", train=True, download=True)
    datasets.MNIST("/work/data", train=False, download=True)
    print("MNIST dataset is ready at /work/data", flush=True)


if __name__ == "__main__":
    main()
