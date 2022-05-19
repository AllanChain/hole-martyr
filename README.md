# Hole Martyr Hunter

A simple program to find martyrs and their deeds in PKUHole.

## License and Conditions

This license of this program is based on 3-Clause BSD License, but with an additional clause:

4. The usage is limited. You can only use it personally and cannot deploy it to a server which is publicly available. You cannot advocate this program in any social media which the organization making deletion in PKUHole is in control of. You cannot post the contents it obtains publicly.

## Usage Instruction

This program is **not designed to run 24-7**. It's designed to grab information when there is a lot of deletions and you want to know what's going on.

Since it's only made for personal use, no production setup is required.

First, create `.env` file:

```
USER_TOKEN=<YOUR TOKEN>
```

Then, to start this program, just run:

```sh
poetry install
pnpm install

# If want live reloading
pnpm dev
# Else
pnpm build
pnpm serve
# End if
```

You need to have the above package managers installed.

The SQLite database is not suitable for a large amount of data. As a consequence, you should **delete the `data.db` regularly**.
