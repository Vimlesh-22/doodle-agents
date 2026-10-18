# Locked upstream dependency archives

These unmodified npm tarballs were retrieved from the npm cache populated during dependency installation. SHA512 hashes were verified against package-lock.json. Each archive contains its upstream license. They allow Docker to install dependencies offline; they contain no project credentials or runtime state.

- jose 6.2.12: MIT
- ipaddr.js 2.2.0: MIT

Do not replace these archives without updating the lockfile, rechecking integrity and rerunning tests. Container base image retrieval still needs network access.
