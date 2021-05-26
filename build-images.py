#! /usr/bin/env python3

import argparse
import os
import pathlib
import subprocess
import sys

THIS_DIR = pathlib.Path(__file__).parent

IMAGE_PREFIX = "joshuawatt"


def get_image_tag(name, tag):
    return "%s/%s:%s" % (IMAGE_PREFIX, name, tag)


def build_crops(tag, push):
    tag = get_image_tag("crops-ubuntu-20.04", tag)

    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "1"

    dockerfile = (
        THIS_DIR
        / "yocto-dockerfiles"
        / "dockerfiles"
        / "ubuntu"
        / "ubuntu-20.04"
        / "ubuntu-20.04-base"
        / "Dockerfile"
    )

    subprocess.run(
        [
            "docker",
            "build",
            "-t",
            tag,
            "-f",
            dockerfile,
            THIS_DIR / "yocto-dockerfiles",
        ],
        env=env,
        check=True,
    )

    if push:
        subprocess.run(["docker", "push", tag], check=True)


def build_labgrid(image, push=False):
    p = subprocess.run(
        ["python3", "./setup.py", "--version"],
        cwd=THIS_DIR / "labgrid",
        stdout=subprocess.PIPE,
        check=True,
    )

    version = p.stdout.decode("utf-8").rstrip().splitlines()[-1]

    tag = "%s/%s" % (IMAGE_PREFIX, image)

    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "1"

    subprocess.run(
        [
            "docker",
            "build",
            "-t",
            tag,
            "-f",
            THIS_DIR / "labgrid" / "dockerfiles" / "Dockerfile",
            "--target",
            image,
            "--build-arg",
            "VERSION=%s" % version,
            THIS_DIR / "labgrid",
        ],
        env=env,
        check=True,
    )

    if push:
        subprocess.run(["docker", "push", tag], check=True)


def build_coordinator(push=False):
    build_labgrid("labgrid-coordinator", push)


def build_exporter(push=False):
    build_labgrid("labgrid-exporter", push)


def build_pdudaemon(tag, push):
    tag = get_image_tag("pdudaemon", tag)
    subprocess.run(
        [
            "docker",
            "build",
            "-t",
            tag,
            "-f",
            THIS_DIR / "pdudaemon" / "Dockerfile.dockerhub",
            THIS_DIR / "pdudaemon",
        ],
        check=True,
    )

    if push:
        subprocess.run(["docker", "push", tag], check=True)


def build_go_http_tunnel(tag, push):
    tag = get_image_tag("go-http-tunnel", tag)

    subprocess.run(
        [
            "docker",
            "build",
            "-t",
            tag,
            "-f",
            THIS_DIR / "dockerfiles" / "go-http-tunnel" / "Dockerfile",
            THIS_DIR / "dockerfiles" / "go-http-tunnel",
        ],
        check=True,
    )

    if push:
        subprocess.run(["docker", "push", tag], check=True)


def main():
    parser = argparse.ArgumentParser(description="Build container images")
    parser.add_argument("tag", help="Image tag")
    parser.add_argument("--push", help="Push images to server", action="store_true")

    args = parser.parse_args()

    build_crops(args.tag, args.push)
    build_pdudaemon(args.tag, args.push)
    build_go_http_tunnel(args.tag, args.push)


if __name__ == "__main__":
    sys.exit(main())
