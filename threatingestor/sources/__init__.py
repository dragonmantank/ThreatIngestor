import re
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

import iocextract

import threatingestor.artifacts


TRUNCATE_LENGTH = 140


class Source:
    """Base class, see method documentation"""

    def __init__(self, name=None):
        """Args should be url, auth, etc, whatever is needed to set up the object."""
        self.name = name
        raise NotImplementedError()

    def run(self, saved_state):
        """Run and return (saved_state, list(Artifact)).

        Attempts to pick up where we left off using saved_state, if supported."""
        raise NotImplementedError()

    def process_element(self, content, reference_link, include_nonobfuscated=False):
        """Take a single source content/url and return a list of Artifacts"""

        # truncate content to a reasonable length for reference_text
        reference_text = content[:TRUNCATE_LENGTH] + ('...' if len(content) > TRUNCATE_LENGTH else '')

        artifact_list = []

        # collect URLs and domains
        scraped = iocextract.extract_urls(content)
        for url in scraped:
            # dump anything with ellipses, these get through the regex
            if u'\u2026' in url:
                continue

            artifact = threatingestor.artifacts.URL(url, self.name,
                                                    reference_link=reference_link,
                                                    reference_text=reference_text)

            # dump urls that appear to have the same domain as reference_url
            if artifact.domain() == urlparse(reference_link).netloc:
                continue

            if artifact.is_obfuscated() or include_nonobfuscated:
                # do URL collection
                artifact_list.append(artifact)

                # do domain collection in the same pass
                if artifact.is_domain():
                    artifact_list.append(
                            threatingestor.artifacts.Domain(artifact.domain(), self.name,
                                                            reference_link=reference_link,
                                                            reference_text=reference_text))

        # collect IPs
        scraped = iocextract.extract_ips(content)
        for ip in scraped:
            artifact = threatingestor.artifacts.IPAddress(ip, self.name,
                                                          reference_link=reference_link,
                                                          reference_text=reference_text)

            try:
                if artifact.ipaddress().is_private or artifact.ipaddress().is_loopback:
                    # don't care
                    continue

            except ValueError:
                # invalid IP
                continue

            artifact_list.append(artifact)

        # collect yara rules
        scraped = iocextract.extract_yara_rules(content)
        for rule in scraped:
            artifact = threatingestor.artifacts.YARASignature(rule, self.name,
                                                              reference_link=reference_link,
                                                              reference_text=reference_text)

            artifact_list.append(artifact)

        # collect hashes
        scraped = iocextract.extract_hashes(content)
        for hash_ in scraped:
            artifact = threatingestor.artifacts.Hash(hash_, self.name,
                                                     reference_link=reference_link,
                                                     reference_text=reference_text)

            artifact_list.append(artifact)

        # generate generic task
        title = "Manual Task: {u}".format(u=reference_link)
        description = 'URL: {u}\nTask autogenerated by ThreatIngestor from source: {s}'.format(s=self.name, u=reference_link)
        artifact = threatingestor.artifacts.Task(title, self.name,
                                                 reference_link=reference_link,
                                                 reference_text=description)
        artifact_list.append(artifact)

        return artifact_list
