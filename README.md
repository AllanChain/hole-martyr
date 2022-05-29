# Hole Martyr Hunter

A simple program to find martyrs and their deeds in PKUHole.

## License and Conditions

This license of this program is based on 3-Clause BSD License, but with an additional clause:

4. The usage is limited. You can only use it personally and cannot deploy it to a server which is publicly available. You cannot advocate this program in any social media which the organization making deletion in PKUHole is in control of. You cannot post the contents it obtains publicly.

## How It works

This program **does not aim** to find every martyr. Instead, the aim is to watch and find martyrs at a specific time range (i.e. several minutes to an hour), usually when something big is happening.

It works just like the usual PKU Hole crawlers:
1. Fetch posts periodically and store in SQLite database
2. Find the `pid`s of missing posts
3. Query the database for original content

The key difference between this program and previous PKU Hole crawlers:
1. This program is **not designed to run 24-7**
   (Thus much less burden for the server)
2. Comments are not a primary consideration
3. Only personal use
4. Content visualization in "real time"

## Why It's Designed to Work Like This

Not all deleted posts are important. The expected value of the deleted posts becomes higher only when something big is happening. If that's the case, usually keeping the main post itself is sufficient.

## Usage Instruction

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
