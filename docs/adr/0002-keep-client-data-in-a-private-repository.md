---
status: accepted
date: 2026-10-19
decision-makers: Sergio Oriola Díaz
---

# Keep client data in a private repository

## Context and Problem Statement

The radar's code and technical documentation are meant to be public, as an open-source project
and as a demonstration of work. The engagement also produces material that belongs to the
client: its profile, its regulatory map, labelled samples, the documents sent to it and its
replies. Where does each kind of material live?

## Decision Drivers

* Nothing the client has not chosen to publish may become public, including through git
  history, which is hard to rewrite.
* The product must work for any organisation given its profile, so it should not depend on the
  first client's data.
* Client documents must be reproducible from source, like the code.

## Considered Options

* Two repositories: a public one for the product, a private one for the engagement
* One private repository, made public later after removing the client's material
* One public repository with the client's material encrypted

## Decision Outcome

Chosen option: "Two repositories", because it is the only option in which a mistake does not
publish the client's data: the public repository never contains it, so there is nothing to
remove from its history.

### Consequences

* Good, because the product is forced to take the profile as input rather than hard-code it.
* Good, because each repository can have its own access rules and continuous integration.
* Bad, because changes that touch both, such as a new field in the profile, need two commits.

### Confirmation

Before any push to the public repository, its content is checked for the client's name and
identifiers.

## Pros and Cons of the Options

### One private repository, published later

* Good, because everything is in one place while the work is in progress.
* Bad, because publishing requires rewriting history, and any file missed is exposed.

### One public repository with encrypted client material

* Good, because there is a single repository.
* Bad, because encrypted files still reveal names, sizes and change history, and a key leak
  exposes everything retroactively.
