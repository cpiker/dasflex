# Federated Catalog Integration

**TODO: Add command line query examples using das2py scripts as the client**

When initially setup, a single das2 server's data catalog.json file is an
isolated root node.  Your software just has to know by some out of band
means to go to (for example):
```
  https://example.domain.org/das/server/catalog.json
```
to get a list of data resources.  To tie your server's catalog into the 
federated das2 catalog system, read on.

## Configuration Option: SITE_CATALOG_TAG

Das2 uses the 'tag' URI scheme (RFC-4151) to generate globaly unique, human
readable, identifiers for each isolated root catalog. 

These are used instead of DOIs since not all das2 sources merit publication. 
Nothing  prevents a das2 catalog from having a DOI, it's just that the data
path resolution system doesn't depend on DOIs.  These global tags can then 
be entered into "tag --to--> uri" resolver lists.  

Each server's catalog could be tagged, but a better option is to just have
one site wide catalog, and to tag that instead.  To keep the tag short, try
using the shortest domain name you can directly influence, and the oldest
year for which you are confident there are no conflicting tags.  Here's an
example:
```
  SITE_CATALOG_TAG = "tag:physics.uiowa.edu,2006"
```
In the example above, suppose that you could request DNS sub-entries for
"physics.uiowa.edu" but for organizational reasons, not directly in
"uiowa.edu".  In this case the even shorter tag:
```
  tag:uiowa.edu,2006    *# bad tag*
```
would *not* meet the claim of ownership for the purposes of RFC-4151. 

The following example demonstrates how the site tag combines with the
data source ID to create a globally unique source ID.
```
voyager/1/mag/electroncyclotron  # data source path
tag:physics.uiowa.edu,2006       # SITE_CATALOG_TAG
```
Full global data source tag:
```
tag:physics.uiowa.edu,2006:/voyager/1/mag/electroncyclotron
```

After setting the SITE_CATALOG_TAG for your servers, run the `das2_site_cat`
script to generate a site wide catalog suitable for hosting as static files
on one of your servers.  For example:

```bash
$ mkdir mysite && cd mysite
$ das2_site_cat https://server1.place.edu/das/server/sources.json \
  https://server2.place.edu/das/server/sources.json
```

will generate a series of `*.json` files merging data source references from
all your servers.

## Configuration Option: SITE_ID

Your data sources may be linked in to the federated das2 catalog.  Linking
to the global catalog adds new references to your existing catalog files.
To request a link, either:

   1) open an issue at  https://github.com/das-developers/das-cat
   2) or send email to  das-developers@uiowa.edu.  

The global catalog tag is:
```
   tag:das2.org,2012
```
This catalog object may be found at two urls for live fail-over:
```
   https://das2.org/catalog/das.json
   https://raw.githubusercontent.com/das-developers/das-cat/master/cat/das.json
```

After linked into the federated das2 catalog, your data sources will 
be assocated with a new global tag.  For example a data source found
through the site local path:
```
  tag:physics.uiowa.edu,2006:/juno/wav/survey
```
will also be reachable using one of the paths:
```
  tag:das2.org,2012:site:/SITE_ID/juno/wav/survey  (production)
  tag:das2.org,2012:test:/SITE_ID/juno/wav/survey  (test sources)
```
Where `SITE_ID` is a string you request.

Like SERVER_ID above, this should be a simple single token.  It only needs to
be unique within the `tag:das2.org,2012` namespace.  Since space physics is
not a huge community (compared to the Internet in general) there's no need to
use an elaborate site ID.  Here's a few examples of picking good ones based
on organizational URLs:

| Organization URL           | SITE_ID  |
|----------------------------|----------|
| jsoc.swri.org              |  swri    |
| physics.uiowa.edu          |  uiowa   |
| ufa.cas.cz                 |  ufa_cas |
| voparis-maser-das.obspm.fr |  obspm   |

For documentation (if nothing else) set this configuration option to to the
site ID you requested when linking to the federated catalog:
```
SITE_ID = mysite
```
