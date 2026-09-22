# Deploying to Vercel

The site is static HTML at the repository root. There is no build step, no
framework, and no dependencies to install. Vercel serves the files as they are.

| Setting | Value |
|---|---|
| Repository | `AiL3Tech/AI-L3-Website` |
| Production branch | `main` |
| Framework preset | **Other** |
| Root directory | `./` |
| Build command | *(leave empty)* |
| Output directory | *(leave empty)* |
| Install command | *(leave empty)* |

`vercel.json` already sets clean URLs, security headers, asset caching, and the
content type for `llms.txt`. Do not add a build command; it will only slow
deploys down.

## First-time connection

1. Go to **https://vercel.com/new**.
2. Sign in with the **GitHub account `marko-ail3tech`**. This matters: Vercel
   attributes each deployment to the Vercel user whose connected GitHub login
   matches whoever pushed the commit. If the account that pushes is not the
   account connected to Vercel, deployments can be skipped or held for
   authorization.
3. Import `AiL3Tech/AI-L3-Website`. If the repository does not appear in the
   list, the Vercel GitHub App has not been granted access to the **AiL3Tech
   organization** — click *Adjust GitHub App Permissions* and add the org.
   This is the usual reason an import looks like it silently does nothing.
4. Confirm the settings in the table above and click **Deploy**.

From then on, every push to `main` deploys to production automatically, and
every pull request gets its own preview URL. No further action is needed.

## Custom domain

In **Project → Settings → Domains**, add `ail3tech.com` and `www.ail3tech.com`,
then point DNS at Vercel as instructed there. Until that is done the site is
live on its `*.vercel.app` URL, and every canonical URL in the HTML already
points at `https://ail3tech.com`, so do not launch publicly on the preview
domain or search engines will be told the wrong home.

Note that `ail3tech.com` currently serves the existing WordPress site. Moving
the domain to Vercel replaces it. Check redirects for any live URL that is not
in `sitemap.xml` before cutting over.

## Commit identity

The repository is pinned to the account that should own these deployments:

```
git config --local user.name  marko-ail3tech
git config --local user.email marko@ail3tech.com
```

Both are already set. Verify at any time with `git config user.email`.

## Doing it from the command line instead

The dashboard route above is the one that sets up automatic deploys. If you
prefer the CLI:

```bash
npm install -g vercel     # already installed
vercel login              # interactive, opens a browser
vercel link               # connect this folder to a Vercel project
vercel git connect        # wire the GitHub repo up for auto-deploy
vercel --prod             # optional: deploy immediately
```

`vercel login` and `vercel link` are interactive and cannot be scripted safely.
Never pass a Vercel token on the command line or put one in this repository;
if automation needs one, supply it from the environment.

## Checking a deployment

After the first deploy, confirm these resolve:

- `/` and `/escalation-support` (clean URL, no `.html`)
- `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/favicon.ico`
- A shared link renders the social card from `/assets/img/og-home.png`

Then submit `https://ail3tech.com/sitemap.xml` in Google Search Console and
Bing Webmaster Tools.
