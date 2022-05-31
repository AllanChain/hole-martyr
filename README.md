# Hole Martyr Hunter

A simple program to find martyrs and their deeds in PKUHole.

## License and Conditions

This license of this program is based on the 3-Clause BSD License, but with an additional clause:

4. The usage is limited. You can only use it personally and cannot deploy it to a publicly available server. You cannot advocate this program on any social media that the organization making deletion in PKUHole is in control of. You cannot post the contents it obtains publicly.

## Why *Martyr*

From Merriam-Webster dictionary, _martyr_ means:

> A person who sacrifices something of great value and especially life itself for the sake of principle.

In cyberspace, the account itself is life. Users who post sensitive content at the risk of losing their accounts can indeed be called martyrs in cyberspace.

## How It works

This program **does not aim** to find every martyr. Instead, the aim is to watch and find martyrs at a specific time range (i.e. several minutes to an hour), usually when something big is happening.

It works just like the usual PKU Hole crawlers:
1. Fetch posts periodically and store them in the SQLite database
2. Find the `pid`s of missing posts
3. Query the database for original content

The key difference between this program and previous PKU Hole crawlers:
1. This program is **not designed to run 24-7**
   (Thus much less burden for the server)
2. Comments are not a primary consideration
3. Only personal use
4. Content visualization in "real-time"

## Why It's Designed to Work Like This

Not all deleted posts are important. The expected value of the deleted posts becomes higher only when something big is happening. If that's the case, usually keeping the main post itself is sufficient.

Also, it's actually OK if you spin up the server a bit late. People tend to re-post deleted content quite often if it's really a big deal.

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
