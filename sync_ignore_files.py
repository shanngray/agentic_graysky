#!/usr/bin/env python3

"""
Script to synchronize .gitignore and .dockerignore files while maintaining
docker-specific and git-specific exclusions.
"""

DOCKER_SPECIFIC = {
    "# Docker",
    "Dockerfile",
    ".dockerignore",
}

GIT_SPECIFIC = {
    "# Git",
    ".git",
    ".gitignore",
}

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def write_file(filename, contents):
    with open(filename, 'w') as f:
        f.write("# THIS FILE IS AUTO-GENERATED - DO NOT EDIT DIRECTLY\n")
        f.write("# Use sync_ignore_files.py to update this file\n\n")
        f.write('\n'.join(sorted(contents)) + '\n')

def main():
    # Read both files
    gitignore = read_file('.gitignore')
    dockerignore = read_file('.dockerignore')

    # Create common set of ignore patterns
    common = (gitignore | dockerignore) - GIT_SPECIFIC - DOCKER_SPECIFIC

    # Create final sets for each file
    git_patterns = common | GIT_SPECIFIC
    docker_patterns = common | DOCKER_SPECIFIC

    # Write updated files
    write_file('.gitignore', git_patterns)
    write_file('.dockerignore', docker_patterns)

if __name__ == '__main__':
    main()
